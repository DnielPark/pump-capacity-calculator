# src/config.py
"""
펌프 용량 계산기 설정 파일
물리 상수, 조도계수, 기본값 정의
"""

# 물리 상수
GRAVITY = 9.8  # 중력가속도 (m/s²)
WATER_DENSITY = 1000  # 물 밀도 (kg/m³)

# Hazen-Williams 조도계수 (C값)
PIPE_ROUGHNESS = {
    'PVC': 150,
    'PE': 140,
    '강관': 130,
    'HDPE': 140,
    '주철관': 120
}

# 기본값
DEFAULT_SAFETY_MARGIN = 1.5  # 여유 수두 (m)
DEFAULT_RESIDUAL_PRESSURE = 1.5  # 잔압 (kgf/cm²)
DEFAULT_PUMP_EFFICIENCY = 0.70  # 펌프 효율 (70%)
DEFAULT_MOTOR_EFFICIENCY = 0.85  # 모터 효율 (85%)
DEFAULT_MOTOR_SAFETY_FACTOR = 1.15  # 모터 여유율

# 전기 사양
VOLTAGE_3PHASE = 380  # 삼상 전압 (V)
VOLTAGE_1PHASE = 220  # 단상 전압 (V)
POWER_FACTOR_3PHASE = 0.85  # 삼상 역률
POWER_FACTOR_1PHASE = 0.80  # 단상 역률

# 단위 환산
KGF_CM2_TO_METER = 10  # 1 kgf/cm² ≈ 10m 수두