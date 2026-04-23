"""
모터 사양 계산 모듈
모터 용량 및 전류 계산 함수
"""

import math
import sys
import os

# 상대 임포트 대신 절대 경로로 config 임포트
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    VOLTAGE_3PHASE, VOLTAGE_1PHASE,
    POWER_FACTOR_3PHASE, POWER_FACTOR_1PHASE,
    DEFAULT_MOTOR_EFFICIENCY, DEFAULT_MOTOR_SAFETY_FACTOR
)


def calculate_motor_power(pump_power_kw, safety_factor=None):
    """
    필요 모터 용량 계산
    
    Parameters:
    -----------
    pump_power_kw : float
        펌프 동력 (kW)
    safety_factor : float, optional
        모터 여유율 (기본값: config.DEFAULT_MOTOR_SAFETY_FACTOR)
    
    Returns:
    --------
    float
        모터 용량 (kW)
    
    Raises:
    -------
    ValueError
        입력값이 유효하지 않을 때
    
    Notes:
    ------
    공식: 모터용량 = 펌프동력 × 여유율
    
    사용 예시:
    >>> calculate_motor_power(5.0)
    5.75  # 5.0 × 1.15
    """
    # 입력값 유효성 검사
    if pump_power_kw <= 0:
        raise ValueError("펌프 동력은 0보다 커야 합니다.")
    
    # 여유율 결정
    if safety_factor is None:
        factor = DEFAULT_MOTOR_SAFETY_FACTOR
    else:
        if safety_factor <= 0:
            raise ValueError("여유율은 0보다 커야 합니다.")
        factor = safety_factor
    
    # 모터 용량 계산
    motor_power = pump_power_kw * factor
    
    return motor_power


def calculate_current_3phase(power_kw, voltage=None, power_factor=None, motor_efficiency=None):
    """
    삼상 전류 계산
    
    Parameters:
    -----------
    power_kw : float
        동력 (kW)
    voltage : float, optional
        전압 (V, 기본값: config.VOLTAGE_3PHASE)
    power_factor : float, optional
        역률 (기본값: config.POWER_FACTOR_3PHASE)
    motor_efficiency : float, optional
        모터 효율 (기본값: config.DEFAULT_MOTOR_EFFICIENCY)
    
    Returns:
    --------
    float
        전류 (A)
    
    Raises:
    -------
    ValueError
        입력값이 유효하지 않을 때
    
    Notes:
    ------
    삼상 전류 계산 공식:
    I = (P × 1000) / (√3 × V × cosθ × η)
    - I: 전류 (A)
    - P: 동력 (kW)
    - V: 전압 (V)
    - cosθ: 역률
    - η: 모터 효율
    
    사용 예시:
    >>> calculate_current_3phase(5.75)
    11.52  # 5.75kW → 약 11.52A
    """
    # 입력값 유효성 검사
    if power_kw <= 0:
        raise ValueError("동력은 0보다 커야 합니다.")
    
    # 기본값 설정
    V = voltage if voltage is not None else VOLTAGE_3PHASE
    cos_theta = power_factor if power_factor is not None else POWER_FACTOR_3PHASE
    eta = motor_efficiency if motor_efficiency is not None else DEFAULT_MOTOR_EFFICIENCY
    
    # 추가 유효성 검사
    if V <= 0:
        raise ValueError("전압은 0보다 커야 합니다.")
    if cos_theta <= 0 or cos_theta > 1:
        raise ValueError("역률은 0 초과 1 이하이어야 합니다.")
    if eta <= 0 or eta > 1:
        raise ValueError("모터 효율은 0 초과 1 이하이어야 합니다.")
    
    # 삼상 전류 계산
    # I = (P × 1000) / (√3 × V × cosθ × η)
    sqrt3 = math.sqrt(3)  # 정밀도 향상을 위해 math.sqrt(3) 사용
    numerator = power_kw * 1000  # kW → W
    denominator = sqrt3 * V * cos_theta * eta
    
    current = numerator / denominator
    
    return current


def calculate_current_1phase(power_kw, voltage=None, power_factor=None, motor_efficiency=None):
    """
    단상 전류 계산
    
    Parameters:
    -----------
    power_kw : float
        동력 (kW)
    voltage : float, optional
        전압 (V, 기본값: config.VOLTAGE_1PHASE)
    power_factor : float, optional
        역률 (기본값: config.POWER_FACTOR_1PHASE)
    motor_efficiency : float, optional
        모터 효율 (기본값: config.DEFAULT_MOTOR_EFFICIENCY)
    
    Returns:
    --------
    float
        전류 (A)
    
    Raises:
    -------
    ValueError
        입력값이 유효하지 않을 때
    
    Notes:
    ------
    단상 전류 계산 공식:
    I = (P × 1000) / (V × cosθ × η)
    - I: 전류 (A)
    - P: 동력 (kW)
    - V: 전압 (V)
    - cosθ: 역률
    - η: 모터 효율
    
    사용 예시:
    >>> calculate_current_1phase(5.75)
    37.88  # 5.75kW → 약 37.88A
    """
    # 입력값 유효성 검사
    if power_kw <= 0:
        raise ValueError("동력은 0보다 커야 합니다.")
    
    # 기본값 설정
    V = voltage if voltage is not None else VOLTAGE_1PHASE
    cos_theta = power_factor if power_factor is not None else POWER_FACTOR_1PHASE
    eta = motor_efficiency if motor_efficiency is not None else DEFAULT_MOTOR_EFFICIENCY
    
    # 추가 유효성 검사
    if V <= 0:
        raise ValueError("전압은 0보다 커야 합니다.")
    if cos_theta <= 0 or cos_theta > 1:
        raise ValueError("역률은 0 초과 1 이하이어야 합니다.")
    if eta <= 0 or eta > 1:
        raise ValueError("모터 효율은 0 초과 1 이하이어야 합니다.")
    
    # 단상 전류 계산
    # I = (P × 1000) / (V × cosθ × η)
    numerator = power_kw * 1000  # kW → W
    denominator = V * cos_theta * eta
    
    current = numerator / denominator
    
    return current


# 간단한 사용 예시
if __name__ == "__main__":
    print("=== 모터 사양 계산 예시 ===")
    
    # 예시: 5kW 펌프
    pump_power = 5.0  # kW
    
    try:
        # 1. 모터 용량 계산
        motor_power = calculate_motor_power(pump_power)
        print(f"펌프 동력: {pump_power} kW")
        print(f"모터 용량 (여유율 {DEFAULT_MOTOR_SAFETY_FACTOR}): {motor_power:.2f} kW")
        
        # 2. 삼상 전류 계산
        current_3phase = calculate_current_3phase(motor_power)
        print(f"삼상 전류 ({VOLTAGE_3PHASE}V, 역률 {POWER_FACTOR_3PHASE}): {current_3phase:.2f} A")
        
        # 3. 단상 전류 계산
        current_1phase = calculate_current_1phase(motor_power)
        print(f"단상 전류 ({VOLTAGE_1PHASE}V, 역률 {POWER_FACTOR_1PHASE}): {current_1phase:.2f} A")
        
        print("=" * 40)
        
    except ValueError as e:
        print(f"계산 오류: {e}")
    
    # 추가 예시: 사용자 정의 값
    try:
        print("\n=== 사용자 정의 값 예시 ===")
        custom_motor = calculate_motor_power(7.5, safety_factor=1.2)
        custom_current = calculate_current_3phase(custom_motor, voltage=400, power_factor=0.9)
        print(f"7.5kW 펌프, 여유율 1.2 → 모터: {custom_motor:.2f} kW")
        print(f"400V, 역률 0.9 → 전류: {custom_current:.2f} A")
        
    except ValueError as e:
        print(f"계산 오류: {e}")