"""
관로 손실 계산 모듈
Hazen-Williams 공식을 사용한 관로 마찰 손실 계산
"""

import math
import sys
import os

# 상대 임포트 대신 절대 경로로 config 임포트
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GRAVITY, WATER_DENSITY, PIPE_ROUGHNESS


def calculate_friction_loss(flow_rate_m3h, pipe_diameter_mm, pipe_length_m, roughness_coefficient=None, pipe_material=None):
    """
    Hazen-Williams 공식을 사용한 관로 마찰 손실 계산
    
    Parameters:
    -----------
    flow_rate_m3h : float
        유량 (㎥/hr)
    pipe_diameter_mm : float
        관경 (mm)
    pipe_length_m : float
        관 길이 (m)
    roughness_coefficient : float, optional
        Hazen-Williams 조도계수 (C값)
    pipe_material : str, optional
        관 재질 (PVC, PE, 강관, HDPE, 주철관)
        roughness_coefficient가 없을 때 사용
    
    Returns:
    --------
    float
        마찰 손실 수두 (m)
    
    Raises:
    -------
    ValueError
        입력값이 유효하지 않을 때
    
    Notes:
    ------
    Hazen-Williams 공식:
    h_f = 10.67 × L × Q^1.85 / (C^1.85 × D^4.87)
    - h_f: 마찰 손실 수두 (m)
    - L: 관 길이 (m)
    - Q: 유량 (㎥/s)
    - C: 조도계수
    - D: 관경 (m)
    """
    # 입력값 유효성 검사
    if flow_rate_m3h <= 0:
        raise ValueError("유량은 0보다 커야 합니다.")
    if pipe_diameter_mm <= 0:
        raise ValueError("관경은 0보다 커야 합니다.")
    if pipe_length_m <= 0:
        raise ValueError("관 길이는 0보다 커야 합니다.")
    
    # 조도계수 결정
    if roughness_coefficient is not None:
        C = roughness_coefficient
    elif pipe_material is not None:
        if pipe_material not in PIPE_ROUGHNESS:
            raise ValueError(f"지원하지 않는 관 재질입니다: {pipe_material}. 지원 재질: {list(PIPE_ROUGHNESS.keys())}")
        C = PIPE_ROUGHNESS[pipe_material]
    else:
        # 기본값으로 PVC 사용
        C = PIPE_ROUGHNESS['PVC']
    
    # 단위 변환
    Q_m3s = flow_rate_m3h / 3600  # ㎥/hr → ㎥/s
    D_m = pipe_diameter_mm / 1000  # mm → m
    
    # Hazen-Williams 공식 계산
    # h_f = 10.67 × L × Q^1.85 / (C^1.85 × D^4.87)
    numerator = 10.67 * pipe_length_m * (Q_m3s ** 1.85)
    denominator = (C ** 1.85) * (D_m ** 4.87)
    
    friction_loss = numerator / denominator
    
    return friction_loss


def calculate_velocity(flow_rate_m3h, pipe_diameter_mm):
    """
    관내 유속 계산
    
    Parameters:
    -----------
    flow_rate_m3h : float
        유량 (㎥/hr)
    pipe_diameter_mm : float
        관경 (mm)
    
    Returns:
    --------
    float
        유속 (m/s)
    
    Raises:
    -------
    ValueError
        입력값이 유효하지 않을 때
    
    Notes:
    ------
    유속 계산 공식:
    V = Q / A
    - V: 유속 (m/s)
    - Q: 유량 (㎥/s)
    - A: 단면적 (㎡) = π × (D/2)²
    """
    # 입력값 유효성 검사
    if flow_rate_m3h <= 0:
        raise ValueError("유량은 0보다 커야 합니다.")
    if pipe_diameter_mm <= 0:
        raise ValueError("관경은 0보다 커야 합니다.")
    
    # 단위 변환
    Q_m3s = flow_rate_m3h / 3600  # ㎥/hr → ㎥/s
    D_m = pipe_diameter_mm / 1000  # mm → m
    
    # 단면적 계산
    radius = D_m / 2
    area = math.pi * (radius ** 2)
    
    # 유속 계산
    velocity = Q_m3s / area
    
    return velocity


# 간단한 사용 예시
if __name__ == "__main__":
    # 예시 1: PVC 관로 마찰 손실 계산
    try:
        flow = 100  # ㎥/hr
        diameter = 150  # mm
        length = 100  # m
        
        friction_loss = calculate_friction_loss(flow, diameter, length, pipe_material="PVC")
        velocity = calculate_velocity(flow, diameter)
        
        print("=== 관로 손실 계산 예시 ===")
        print(f"유량: {flow} ㎥/hr")
        print(f"관경: {diameter} mm")
        print(f"관 길이: {length} m")
        print(f"관 재질: PVC (C={PIPE_ROUGHNESS['PVC']})")
        print(f"마찰 손실 수두: {friction_loss:.2f} m")
        print(f"관내 유속: {velocity:.2f} m/s")
        print("=" * 30)
        
    except ValueError as e:
        print(f"계산 오류: {e}")
    
    # 예시 2: 직접 조도계수 지정
    try:
        friction_loss2 = calculate_friction_loss(50, 100, 50, roughness_coefficient=140)
        print(f"직접 조도계수 지정 (C=140): {friction_loss2:.2f} m")
    except ValueError as e:
        print(f"계산 오류: {e}")