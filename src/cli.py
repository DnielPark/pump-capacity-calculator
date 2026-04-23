#!/usr/bin/env python3
"""
펌프 용량 계산기 CLI 프로그램
커맨드라인에서 펌프 용량을 계산할 수 있는 인터페이스
"""

import argparse
import sys
import os

# 상대 임포트 대신 절대 경로로 필요한 모듈 임포트
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calc.pump_calc import calculate_complete_pump_spec


def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='펌프 용량 계산기 - 일반 양정 모드와 압송 관로 모드 지원',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 일반 양정 모드
  python src/cli.py --mode standard --flow 100 --head 20 --electrical 3phase --pumps 2 --pipe-loss 5
  
  # 압송 관로 모드  
  python src/cli.py --mode pressure --flow 100 --head 20 --electrical 1phase --length 500 --diameter 150
  
  # 상세 옵션 지정
  python src/cli.py --mode standard --flow 150 --head 25 --electrical 3phase --safety 2.0 --efficiency 0.75
        """
    )
    
    # 필수 인자
    parser.add_argument('--mode', required=True, choices=['standard', 'pressure'],
                       help='계산 모드: standard(일반 양정) 또는 pressure(압송 관로)')
    parser.add_argument('--flow', type=float, required=True,
                       help='유량 (㎥/hr)')
    parser.add_argument('--head', type=float, required=True,
                       help='실양정 (m)')
    parser.add_argument('--electrical', required=True, choices=['3phase', '1phase'],
                       help='전기 방식: 3phase(삼상) 또는 1phase(단상)')
    
    # 일반 양정 모드 옵션
    parser.add_argument('--pipe-loss', type=float, default=0.0,
                       help='관로 손실 (m, 일반 양정 모드용, 기본값: 0)')
    
    # 압송 관로 모드 옵션
    parser.add_argument('--length', type=float,
                       help='압송 거리 (m, 압송 관로 모드 필수)')
    parser.add_argument('--diameter', type=float,
                       help='관경 (mm, 압송 관로 모드 필수)')
    parser.add_argument('--material', default='PVC',
                       choices=['PVC', 'PE', '강관', 'HDPE', '주철관'],
                       help='관 재질 (압송 관로 모드용, 기본값: PVC)')
    
    # 공통 옵션
    parser.add_argument('--pumps', type=int, default=1,
                       help='펌프 대수 (기본값: 1)')
    parser.add_argument('--safety', type=float, default=1.5,
                       help='여유 수두 (m, 기본값: 1.5)')
    parser.add_argument('--efficiency', type=float, default=0.70,
                       help='펌프 효율 (기본값: 0.70)')
    parser.add_argument('--motor-safety', type=float, default=1.15,
                       help='모터 여유율 (기본값: 1.15)')
    
    return parser.parse_args()


def validate_arguments(args):
    """인자 유효성 검사"""
    # 기본 유효성 검사
    if args.flow <= 0:
        raise ValueError("유량은 0보다 커야 합니다.")
    if args.head < 0:
        raise ValueError("실양정은 0 이상이어야 합니다.")
    if args.pumps <= 0:
        raise ValueError("펌프 대수는 0보다 커야 합니다.")
    if args.safety < 0:
        raise ValueError("여유 수두는 0 이상이어야 합니다.")
    if args.efficiency <= 0 or args.efficiency > 1:
        raise ValueError("펌프 효율은 0 초과 1 이하이어야 합니다.")
    if args.motor_safety <= 0:
        raise ValueError("모터 여유율은 0보다 커야 합니다.")
    
    # 모드별 필수 인자 검사
    if args.mode == 'pressure':
        if args.length is None:
            raise ValueError("압송 관로 모드에서는 --length가 필수입니다.")
        if args.diameter is None:
            raise ValueError("압송 관로 모드에서는 --diameter가 필수입니다.")
        if args.length <= 0:
            raise ValueError("압송 거리는 0보다 커야 합니다.")
        if args.diameter <= 0:
            raise ValueError("관경은 0보다 커야 합니다.")
    
    # 일반 양정 모드 검사
    if args.mode == 'standard':
        if args.pipe_loss < 0:
            raise ValueError("관로 손실은 0 이상이어야 합니다.")


def format_result(result):
    """계산 결과를 보기 좋게 포맷팅"""
    # 모드 이름 변환
    mode_name = '일반 양정' if result['mode'] == 'standard' else '압송 관로'
    
    # 전기 방식 이름 변환
    if result['electrical_type'] == '3phase':
        electrical_name = f'삼상 {result["voltage"]}V'
    else:
        electrical_name = f'단상 {result["voltage"]}V'
    
    output = []
    output.append("=" * 40)
    output.append(" 펌프 용량 계산 결과")
    output.append("=" * 40)
    output.append(f"계산 모드: {mode_name}")
    output.append(f"전양정: {result['total_head']:.2f} m")
    output.append(f"펌프당 유량: {result['flow_per_pump']:.2f} ㎥/hr")
    output.append(f"펌프 동력: {result['pump_power']:.2f} kW")
    output.append(f"모터 용량: {result['motor_power']:.2f} kW")
    output.append(f"전기 방식: {electrical_name}")
    output.append(f"전류: {result['current']:.2f} A")
    
    # 압송 모드 추가 정보
    if result['mode'] == 'pressure':
        output.append(f"마찰 손실: {result['friction_loss']:.2f} m")
        output.append(f"잔압 환산: {result['residual_head']:.2f} m")
        output.append(f"유속: {result['velocity']:.2f} m/s")
    
    output.append("=" * 40)
    
    return '\n'.join(output)


def main():
    """메인 함수"""
    try:
        # 인자 파싱
        args = parse_arguments()
        
        # 인자 유효성 검사
        validate_arguments(args)
        
        # 계산 파라미터 준비
        calc_params = {
            'mode': args.mode,
            'flow_rate': args.flow,
            'static_head': args.head,
            'electrical_type': args.electrical,
            'num_pumps': args.pumps,
            'safety_margin': args.safety,
            'pump_efficiency': args.efficiency,
            'motor_safety_factor': args.motor_safety,
        }
        
        # 모드별 파라미터 추가
        if args.mode == 'standard':
            calc_params['pipe_loss'] = args.pipe_loss
        else:  # pressure mode
            calc_params['pipe_length'] = args.length
            calc_params['pipe_diameter'] = args.diameter
            calc_params['pipe_material'] = args.material
        
        # 계산 실행
        result = calculate_complete_pump_spec(**calc_params)
        
        # 결과 출력
        print(format_result(result))
        
    except ValueError as e:
        print(f"입력 오류: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"계산 오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()