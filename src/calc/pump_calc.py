"""
펌프 용량 계산 메인 모듈
일반 양정 모드와 압송 관로 모드 계산 함수
"""

import sys
import os

# 상대 임포트 대신 절대 경로로 필요한 모듈 임포트
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    GRAVITY, WATER_DENSITY,
    DEFAULT_SAFETY_MARGIN, DEFAULT_PUMP_EFFICIENCY,
    DEFAULT_RESIDUAL_PRESSURE, KGF_CM2_TO_METER,
    VOLTAGE_3PHASE, VOLTAGE_1PHASE,
    DEFAULT_MOTOR_SAFETY_FACTOR
)

# 로컬 모듈 임포트
from .pipe_loss import calculate_friction_loss, calculate_velocity
from .motor_spec import calculate_motor_power, calculate_current_3phase, calculate_current_1phase


def calculate_standard_mode(flow_rate, static_head, pipe_loss=0, safety_margin=None,
                           pump_efficiency=None, num_pumps=1):
    """
    일반 양정 모드 펌프 용량 계산
    
    Parameters:
    -----------
    flow_rate : float
        유량 (㎥/hr)
    static_head : float
        실양정 (m)
    pipe_loss : float, optional
        관로 손실 수두 (m, 기본값 0)
    safety_margin : float, optional
        여유 수두 (m, 기본값 config.DEFAULT_SAFETY_MARGIN)
    pump_efficiency : float, optional
        펌프 효율 (기본값 config.DEFAULT_PUMP_EFFICIENCY)
    num_pumps : int, optional
        펌프 대수 (기본값 1)
    
    Returns:
    --------
    dict
        계산 결과 딕셔너리:
        {
            'total_head': 전양정 (m),
            'flow_per_pump': 펌프당 유량 (㎥/hr),
            'pump_power': 펌프 동력 (kW),
            'efficiency': 사용한 효율
        }
    
    Raises:
    -------
    ValueError
        입력값이 유효하지 않을 때
    
    Notes:
    ------
    계산 공식:
    1. 전양정 = 실양정 + 관로손실 + 여유수두
    2. 펌프당 유량 = 전체유량 / 펌프대수
    3. 펌프 동력(kW) = (펌프당유량 × 전양정 × 9.8 × 밀도) / (3600 × 효율)
    
    사용 예시:
    >>> result = calculate_standard_mode(100, 20, pipe_loss=5)
    >>> result['total_head']
    26.5  # 20 + 5 + 1.5(기본 여유수두)
    """
    # 입력값 유효성 검사
    if flow_rate <= 0:
        raise ValueError("유량은 0보다 커야 합니다.")
    if static_head < 0:
        raise ValueError("실양정은 0 이상이어야 합니다.")
    if pipe_loss < 0:
        raise ValueError("관로 손실은 0 이상이어야 합니다.")
    if num_pumps <= 0:
        raise ValueError("펌프 대수는 0보다 커야 합니다.")
    
    # 기본값 설정
    margin = safety_margin if safety_margin is not None else DEFAULT_SAFETY_MARGIN
    efficiency = pump_efficiency if pump_efficiency is not None else DEFAULT_PUMP_EFFICIENCY
    
    # 추가 유효성 검사
    if margin < 0:
        raise ValueError("여유 수두는 0 이상이어야 합니다.")
    if efficiency <= 0 or efficiency > 1:
        raise ValueError("펌프 효율은 0 초과 1 이하이어야 합니다.")
    
    # 1. 전양정 계산
    total_head = static_head + pipe_loss + margin
    
    # 2. 펌프당 유량 계산
    flow_per_pump = flow_rate / num_pumps
    
    # 3. 펌프 동력 계산
    # 공식: P = (Q × H × g × ρ) / (3600 × η)
    # Q: ㎥/hr, H: m, g: 9.8 m/s², ρ: 1000 kg/m³, η: 효율
    pump_power = (flow_per_pump * total_head * GRAVITY * WATER_DENSITY) / (3600 * efficiency * 1000)
    
    return {
        'total_head': total_head,
        'flow_per_pump': flow_per_pump,
        'pump_power': pump_power,
        'efficiency': efficiency
    }


def calculate_pressure_mode(flow_rate, static_head, pipe_length, pipe_diameter,
                           pipe_material=None, roughness_coefficient=None,
                           residual_pressure=None, safety_margin=None,
                           pump_efficiency=None, num_pumps=1):
    """
    압송 관로 모드 펌프 용량 계산
    
    Parameters:
    -----------
    flow_rate : float
        유량 (㎥/hr)
    static_head : float
        실양정 (m)
    pipe_length : float
        압송 거리 (m)
    pipe_diameter : float
        관경 (mm)
    pipe_material : str, optional
        관 재질 ('PVC', 'PE', '강관', 'HDPE', '주철관')
    roughness_coefficient : float, optional
        Hazen-Williams 조도계수 (C값)
    residual_pressure : float, optional
        잔압 (kgf/cm², 기본값 config.DEFAULT_RESIDUAL_PRESSURE)
    safety_margin : float, optional
        여유 수두 (m, 기본값 config.DEFAULT_SAFETY_MARGIN)
    pump_efficiency : float, optional
        펌프 효율 (기본값 config.DEFAULT_PUMP_EFFICIENCY)
    num_pumps : int, optional
        펌프 대수 (기본값 1)
    
    Returns:
    --------
    dict
        계산 결과 딕셔너리:
        {
            'total_head': 전양정 (m),
            'friction_loss': 마찰손실 (m),
            'residual_head': 잔압환산 (m),
            'flow_per_pump': 펌프당 유량 (㎥/hr),
            'pump_power': 펌프 동력 (kW),
            'velocity': 유속 (m/s),
            'efficiency': 사용한 효율
        }
    
    Raises:
    -------
    ValueError
        입력값이 유효하지 않을 때
    
    Notes:
    ------
    계산 공식:
    1. 마찰 손실 = pipe_loss.calculate_friction_loss()
    2. 잔압 환산 = 잔압 × 10 (kgf/cm² → m)
    3. 전양정 = 실양정 + 마찰손실 + 잔압환산 + 여유수두
    4. 펌프당 유량 = 전체유량 / 펌프대수
    5. 펌프 동력(kW) = (펌프당유량 × 전양정 × 9.8 × 밀도) / (3600 × 효율)
    6. 유속 = pipe_loss.calculate_velocity()
    
    사용 예시:
    >>> result = calculate_pressure_mode(100, 20, 500, 150, pipe_material='PVC')
    >>> result['total_head']
    31.87  # 20 + 1.37(마찰) + 15(잔압) + 1.5(여유)
    """
    # 입력값 유효성 검사
    if flow_rate <= 0:
        raise ValueError("유량은 0보다 커야 합니다.")
    if static_head < 0:
        raise ValueError("실양정은 0 이상이어야 합니다.")
    if pipe_length <= 0:
        raise ValueError("압송 거리는 0보다 커야 합니다.")
    if pipe_diameter <= 0:
        raise ValueError("관경은 0보다 커야 합니다.")
    if num_pumps <= 0:
        raise ValueError("펌프 대수는 0보다 커야 합니다.")
    
    # 기본값 설정
    residual = residual_pressure if residual_pressure is not None else DEFAULT_RESIDUAL_PRESSURE
    margin = safety_margin if safety_margin is not None else DEFAULT_SAFETY_MARGIN
    efficiency = pump_efficiency if pump_efficiency is not None else DEFAULT_PUMP_EFFICIENCY
    
    # 추가 유효성 검사
    if residual < 0:
        raise ValueError("잔압은 0 이상이어야 합니다.")
    if margin < 0:
        raise ValueError("여유 수두는 0 이상이어야 합니다.")
    if efficiency <= 0 or efficiency > 1:
        raise ValueError("펌프 효율은 0 초과 1 이하이어야 합니다.")
    
    # 1. 마찰 손실 계산
    friction_loss = calculate_friction_loss(
        flow_rate, pipe_diameter, pipe_length,
        roughness_coefficient=roughness_coefficient,
        pipe_material=pipe_material
    )
    
    # 2. 잔압 환산 (kgf/cm² → m)
    residual_head = residual * KGF_CM2_TO_METER
    
    # 3. 전양정 계산
    total_head = static_head + friction_loss + residual_head + margin
    
    # 4. 펌프당 유량 계산
    flow_per_pump = flow_rate / num_pumps
    
    # 5. 펌프 동력 계산
    pump_power = (flow_per_pump * total_head * GRAVITY * WATER_DENSITY) / (3600 * efficiency * 1000)
    
    # 6. 유속 계산
    velocity = calculate_velocity(flow_rate, pipe_diameter)
    
    return {
        'total_head': total_head,
        'friction_loss': friction_loss,
        'residual_head': residual_head,
        'flow_per_pump': flow_per_pump,
        'pump_power': pump_power,
        'velocity': velocity,
        'efficiency': efficiency
    }


# 간단한 사용 예시
if __name__ == "__main__":
    print("=== 펌프 용량 계산 예시 ===")
    
    # 예시 1: 일반 양정 모드
    try:
        print("\n1. 일반 양정 모드:")
        result1 = calculate_standard_mode(
            flow_rate=100,  # ㎥/hr
            static_head=20,  # m
            pipe_loss=5,  # m
            num_pumps=2
        )
        print(f"   유량: 100 ㎥/hr, 실양정: 20m, 관로손실: 5m, 펌프 2대")
        print(f"   전양정: {result1['total_head']:.2f} m")
        print(f"   펌프당 유량: {result1['flow_per_pump']:.2f} ㎥/hr")
        print(f"   펌프 동력: {result1['pump_power']:.2f} kW")
        
    except ValueError as e:
        print(f"   계산 오류: {e}")
    
    # 예시 2: 압송 관로 모드
    try:
        print("\n2. 압송 관로 모드:")
        result2 = calculate_pressure_mode(
            flow_rate=100,  # ㎥/hr
            static_head=20,  # m
            pipe_length=500,  # m
            pipe_diameter=150,  # mm
            pipe_material='PVC',
            num_pumps=1
        )
        print(f"   유량: 100 ㎥/hr, 실양정: 20m")
        print(f"   관로: 150mm PVC, 길이 500m")
        print(f"   전양정: {result2['total_head']:.2f} m")
        print(f"   마찰 손실: {result2['friction_loss']:.2f} m")
        print(f"   잔압 환산: {result2['residual_head']:.2f} m")
        print(f"   유속: {result2['velocity']:.2f} m/s")
        print(f"   펌프 동력: {result2['pump_power']:.2f} kW")
        
    except ValueError as e:
        print(f"   계산 오류: {e}")
    
    print("\n" + "=" * 40)


def calculate_complete_pump_spec(mode, flow_rate, static_head, electrical_type,
                                num_pumps=1,
                                # 일반 양정 모드 전용
                                pipe_loss=0,
                                # 압송 관로 모드 전용
                                pipe_length=None, pipe_diameter=None, pipe_material='PVC',
                                residual_pressure=None,
                                # 공통 옵션
                                safety_margin=None, pump_efficiency=None,
                                motor_safety_factor=None):
    """
    펌프 및 모터 사양 완전 계산 (통합 함수)
    
    Parameters:
    -----------
    mode : str
        계산 모드 ('standard' 또는 'pressure')
    flow_rate : float
        유량 (㎥/hr)
    static_head : float
        실양정 (m)
    electrical_type : str
        전기 방식 ('3phase' 또는 '1phase')
    num_pumps : int, optional
        펌프 대수 (기본값 1)
    
    # 일반 양정 모드 전용
    pipe_loss : float, optional
        관로 손실 (m, 기본값 0)
    
    # 압송 관로 모드 전용
    pipe_length : float, optional
        압송 거리 (m, 압송 모드일 때 필수)
    pipe_diameter : float, optional
        관경 (mm, 압송 모드일 때 필수)
    pipe_material : str, optional
        관 재질 (기본값 'PVC')
    residual_pressure : float, optional
        잔압 (kgf/cm², 기본값 config.DEFAULT_RESIDUAL_PRESSURE)
    
    # 공통 옵션
    safety_margin : float, optional
        여유 수두 (m, 기본값 config.DEFAULT_SAFETY_MARGIN)
    pump_efficiency : float, optional
        펌프 효율 (기본값 config.DEFAULT_PUMP_EFFICIENCY)
    motor_safety_factor : float, optional
        모터 여유율 (기본값 config.DEFAULT_MOTOR_SAFETY_FACTOR)
    
    Returns:
    --------
    dict
        통합 계산 결과 딕셔너리:
        {
            # 펌프 계산 결과
            'mode': 계산모드,
            'total_head': 전양정(m),
            'flow_per_pump': 펌프당유량(㎥/hr),
            'pump_power': 펌프동력(kW),
            'efficiency': 펌프효율,
            
            # 모터 사양
            'motor_power': 모터용량(kW),
            'motor_safety_factor': 사용된여유율,
            
            # 전기 사양
            'electrical_type': 전기방식,
            'current': 전류(A),
            'voltage': 전압(V),
            
            # 압송 모드 추가 정보 (압송 모드인 경우만)
            'friction_loss': 마찰손실(m), # 압송 모드만
            'residual_head': 잔압환산(m), # 압송 모드만
            'velocity': 유속(m/s), # 압송 모드만
        }
    
    Raises:
    -------
    ValueError
        입력값이 유효하지 않을 때
    
    Notes:
    ------
    사용 예시:
    >>> # 일반 양정 모드 + 삼상 전기
    >>> result1 = calculate_complete_pump_spec(
    ...     mode='standard',
    ...     flow_rate=100,
    ...     static_head=20,
    ...     electrical_type='3phase',
    ...     pipe_loss=5,
    ...     num_pumps=2
    ... )
    
    >>> # 압송 관로 모드 + 단상 전기
    >>> result2 = calculate_complete_pump_spec(
    ...     mode='pressure',
    ...     flow_rate=100,
    ...     static_head=20,
    ...     electrical_type='1phase',
    ...     pipe_length=500,
    ...     pipe_diameter=150,
    ...     pipe_material='PVC'
    ... )
    """
    # 모드 유효성 검사
    if mode not in ['standard', 'pressure']:
        raise ValueError("mode는 'standard' 또는 'pressure'이어야 합니다.")
    
    # 전기 방식 유효성 검사
    if electrical_type not in ['3phase', '1phase']:
        raise ValueError("electrical_type은 '3phase' 또는 '1phase'이어야 합니다.")
    
    # 압송 모드 필수 파라미터 검사
    if mode == 'pressure':
        if pipe_length is None:
            raise ValueError("압송 모드에서는 pipe_length가 필수입니다.")
        if pipe_diameter is None:
            raise ValueError("압송 모드에서는 pipe_diameter가 필수입니다.")
    
    # 1. 펌프 계산 (모드에 따라)
    if mode == 'standard':
        # 일반 양정 모드
        pump_result = calculate_standard_mode(
            flow_rate=flow_rate,
            static_head=static_head,
            pipe_loss=pipe_loss,
            safety_margin=safety_margin,
            pump_efficiency=pump_efficiency,
            num_pumps=num_pumps
        )
        
        # 압송 모드 관련 값은 None으로 설정
        friction_loss = None
        residual_head = None
        velocity = None
        
    else:  # mode == 'pressure'
        # 압송 관로 모드
        pump_result = calculate_pressure_mode(
            flow_rate=flow_rate,
            static_head=static_head,
            pipe_length=pipe_length,
            pipe_diameter=pipe_diameter,
            pipe_material=pipe_material,
            residual_pressure=residual_pressure,
            safety_margin=safety_margin,
            pump_efficiency=pump_efficiency,
            num_pumps=num_pumps
        )
        
        # 압송 모드 관련 값 추출
        friction_loss = pump_result['friction_loss']
        residual_head = pump_result['residual_head']
        velocity = pump_result['velocity']
    
    # 2. 모터 용량 계산
    motor_power = calculate_motor_power(
        pump_result['pump_power'],
        safety_factor=motor_safety_factor
    )
    
    # 3. 전류 계산 (전기 방식에 따라)
    if electrical_type == '3phase':
        current = calculate_current_3phase(motor_power)
        voltage = VOLTAGE_3PHASE
    else:  # '1phase'
        current = calculate_current_1phase(motor_power)
        voltage = VOLTAGE_1PHASE
    
    # 4. 결과 통합
    result = {
        # 펌프 계산 결과
        'mode': mode,
        'total_head': pump_result['total_head'],
        'flow_per_pump': pump_result['flow_per_pump'],
        'pump_power': pump_result['pump_power'],
        'efficiency': pump_result['efficiency'],
        
        # 모터 사양
        'motor_power': motor_power,
        'motor_safety_factor': motor_safety_factor if motor_safety_factor is not None else DEFAULT_MOTOR_SAFETY_FACTOR,
        
        # 전기 사양
        'electrical_type': electrical_type,
        'current': current,
        'voltage': voltage,
    }
    
    # 압송 모드 추가 정보
    if mode == 'pressure':
        result['friction_loss'] = friction_loss
        result['residual_head'] = residual_head
        result['velocity'] = velocity
    
    return result


# 통합 함수 테스트 예시
if __name__ == "__main__":
    print("\n=== 통합 함수 테스트 예시 ===")
    
    # 예시 1: 일반 양정 모드 + 삼상 전기
    try:
        print("\n1. 일반 양정 모드 + 삼상 전기:")
        result1 = calculate_complete_pump_spec(
            mode='standard',
            flow_rate=100,
            static_head=20,
            electrical_type='3phase',
            pipe_loss=5,
            num_pumps=2
        )
        print(f"   모드: {result1['mode']}")
        print(f"   전양정: {result1['total_head']:.2f} m")
        print(f"   펌프 동력: {result1['pump_power']:.2f} kW")
        print(f"   모터 용량: {result1['motor_power']:.2f} kW")
        print(f"   전기 방식: {result1['electrical_type']}")
        print(f"   전류: {result1['current']:.2f} A")
        print(f"   전압: {result1['voltage']} V")
        
    except ValueError as e:
        print(f"   계산 오류: {e}")
    
    # 예시 2: 압송 관로 모드 + 단상 전기
    try:
        print("\n2. 압송 관로 모드 + 단상 전기:")
        result2 = calculate_complete_pump_spec(
            mode='pressure',
            flow_rate=100,
            static_head=20,
            electrical_type='1phase',
            pipe_length=500,
            pipe_diameter=150,
            pipe_material='PVC'
        )
        print(f"   모드: {result2['mode']}")
        print(f"   전양정: {result2['total_head']:.2f} m")
        print(f"   마찰 손실: {result2['friction_loss']:.2f} m")
        print(f"   펌프 동력: {result2['pump_power']:.2f} kW")
        print(f"   모터 용량: {result2['motor_power']:.2f} kW")
        print(f"   전기 방식: {result2['electrical_type']}")
        print(f"   전류: {result2['current']:.2f} A")
        print(f"   유속: {result2['velocity']:.2f} m/s")
        
    except ValueError as e:
        print(f"   계산 오류: {e}")
    
    print("\n" + "=" * 40)