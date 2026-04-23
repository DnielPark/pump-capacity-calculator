#!/usr/bin/env python3
"""
펌프 용량 계산기 GUI 프로그램
tkinter를 사용한 사용자 친화적인 인터페이스
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 상대 임포트 대신 절대 경로로 필요한 모듈 임포트
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calc.pump_calc import calculate_complete_pump_spec


class PumpCalculatorGUI:
    """펌프 용량 계산기 GUI 클래스"""
    
    def __init__(self, root):
        """GUI 초기화"""
        self.root = root
        self.root.title("하수도 펌프 용량 계산기")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # 변수 초기화
        self.mode_var = tk.StringVar(value='standard')
        self.electrical_var = tk.StringVar(value='3phase')
        
        # 입력 필드 변수
        self.flow_var = tk.StringVar()
        self.head_var = tk.StringVar()
        self.pumps_var = tk.IntVar(value=1)
        
        # 압송 모드 변수
        self.pipe_loss_var = tk.StringVar(value='0')
        self.pipe_length_var = tk.StringVar()
        self.pipe_diameter_var = tk.StringVar()
        self.pipe_material_var = tk.StringVar(value='PVC')
        
        # 옵션 변수
        self.safety_var = tk.StringVar(value='1.5')
        self.efficiency_var = tk.StringVar(value='0.70')
        self.motor_safety_var = tk.StringVar(value='1.15')
        
        # UI 생성
        self.create_title()
        self.create_mode_selection()
        self.create_basic_inputs()
        self.create_electrical_selection()
        self.create_buttons()
        self.create_result_display()
        
        # 모드 변경 이벤트 바인딩
        self.mode_var.trace('w', self.on_mode_changed)
    
    def create_title(self):
        """타이틀 영역 생성"""
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame,
            text="하수도 펌프 용량 계산기",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="일반 양정 모드와 압송 관로 모드 지원",
            font=("Helvetica", 10)
        )
        subtitle_label.pack()
    
    def create_mode_selection(self):
        """계산 모드 선택 영역 생성"""
        mode_frame = ttk.LabelFrame(
            self.root,
            text="계산 모드 선택",
            padding="10"
        )
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 라디오 버튼 프레임
        radio_frame = ttk.Frame(mode_frame)
        radio_frame.pack()
        
        # 일반 양정 모드
        standard_radio = ttk.Radiobutton(
            radio_frame,
            text="일반 양정 모드",
            variable=self.mode_var,
            value='standard'
        )
        standard_radio.grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)
        
        # 압송 관로 모드
        pressure_radio = ttk.Radiobutton(
            radio_frame,
            text="압송 관로 모드",
            variable=self.mode_var,
            value='pressure'
        )
        pressure_radio.grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)
    
    def create_basic_inputs(self):
        """기본 정보 입력 영역 생성"""
        basic_frame = ttk.LabelFrame(
            self.root,
            text="기본 정보 입력",
            padding="10"
        )
        basic_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 설계 유량
        ttk.Label(basic_frame, text="설계 유량 (㎥/hr):").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W
        )
        flow_entry = ttk.Entry(basic_frame, textvariable=self.flow_var, width=15)
        flow_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(basic_frame, text="예: 100").grid(
            row=0, column=2, padx=5, pady=5, sticky=tk.W
        )
        
        # 실양정
        ttk.Label(basic_frame, text="실양정 (m):").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W
        )
        head_entry = ttk.Entry(basic_frame, textvariable=self.head_var, width=15)
        head_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(basic_frame, text="예: 20").grid(
            row=1, column=2, padx=5, pady=5, sticky=tk.W
        )
        
        # 펌프 대수
        ttk.Label(basic_frame, text="펌프 대수:").grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.W
        )
        pumps_spinbox = ttk.Spinbox(
            basic_frame,
            from_=1,
            to=5,
            textvariable=self.pumps_var,
            width=13
        )
        pumps_spinbox.grid(row=2, column=1, padx=5, pady=5)
        
        # 일반 양정 모드: 관로 손실
        ttk.Label(basic_frame, text="관로 손실 (m):").grid(
            row=3, column=0, padx=5, pady=5, sticky=tk.W
        )
        pipe_loss_entry = ttk.Entry(basic_frame, textvariable=self.pipe_loss_var, width=15)
        pipe_loss_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(basic_frame, text="일반 양정 모드용").grid(
            row=3, column=2, padx=5, pady=5, sticky=tk.W
        )
        
        # 압송 관로 모드: 관 길이
        ttk.Label(basic_frame, text="압송 거리 (m):").grid(
            row=4, column=0, padx=5, pady=5, sticky=tk.W
        )
        pipe_length_entry = ttk.Entry(basic_frame, textvariable=self.pipe_length_var, width=15)
        pipe_length_entry.grid(row=4, column=1, padx=5, pady=5)
        ttk.Label(basic_frame, text="압송 모드용").grid(
            row=4, column=2, padx=5, pady=5, sticky=tk.W
        )
        
        # 압송 관로 모드: 관경
        ttk.Label(basic_frame, text="관경 (mm):").grid(
            row=5, column=0, padx=5, pady=5, sticky=tk.W
        )
        pipe_diameter_entry = ttk.Entry(basic_frame, textvariable=self.pipe_diameter_var, width=15)
        pipe_diameter_entry.grid(row=5, column=1, padx=5, pady=5)
        ttk.Label(basic_frame, text="예: 150").grid(
            row=5, column=2, padx=5, pady=5, sticky=tk.W
        )
        
        # 압송 관로 모드: 관 재질
        ttk.Label(basic_frame, text="관 재질:").grid(
            row=6, column=0, padx=5, pady=5, sticky=tk.W
        )
        material_combo = ttk.Combobox(
            basic_frame,
            textvariable=self.pipe_material_var,
            values=['PVC', 'PE', '강관', 'HDPE', '주철관'],
            width=12,
            state='readonly'
        )
        material_combo.grid(row=6, column=1, padx=5, pady=5)
        
        # 옵션: 여유 수두
        ttk.Label(basic_frame, text="여유 수두 (m):").grid(
            row=7, column=0, padx=5, pady=5, sticky=tk.W
        )
        safety_entry = ttk.Entry(basic_frame, textvariable=self.safety_var, width=15)
        safety_entry.grid(row=7, column=1, padx=5, pady=5)
        ttk.Label(basic_frame, text="기본값: 1.5").grid(
            row=7, column=2, padx=5, pady=5, sticky=tk.W
        )
        
        # 옵션: 펌프 효율
        ttk.Label(basic_frame, text="펌프 효율:").grid(
            row=8, column=0, padx=5, pady=5, sticky=tk.W
        )
        efficiency_entry = ttk.Entry(basic_frame, textvariable=self.efficiency_var, width=15)
        efficiency_entry.grid(row=8, column=1, padx=5, pady=5)
        ttk.Label(basic_frame, text="기본값: 0.70").grid(
            row=8, column=2, padx=5, pady=5, sticky=tk.W
        )
        
        # 옵션: 모터 여유율
        ttk.Label(basic_frame, text="모터 여유율:").grid(
            row=9, column=0, padx=5, pady=5, sticky=tk.W
        )
        motor_safety_entry = ttk.Entry(basic_frame, textvariable=self.motor_safety_var, width=15)
        motor_safety_entry.grid(row=9, column=1, padx=5, pady=5)
        ttk.Label(basic_frame, text="기본값: 1.15").grid(
            row=9, column=2, padx=5, pady=5, sticky=tk.W
        )
    
    def create_electrical_selection(self):
        """전기 사양 선택 영역 생성"""
        electrical_frame = ttk.LabelFrame(
            self.root,
            text="전기 사양 선택",
            padding="10"
        )
        electrical_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 라디오 버튼 프레임
        radio_frame = ttk.Frame(electrical_frame)
        radio_frame.pack()
        
        # 삼상 전기
        phase3_radio = ttk.Radiobutton(
            radio_frame,
            text="삼상 380V",
            variable=self.electrical_var,
            value='3phase'
        )
        phase3_radio.grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)
        
        # 단상 전기
        phase1_radio = ttk.Radiobutton(
            radio_frame,
            text="단상 220V",
            variable=self.electrical_var,
            value='1phase'
        )
        phase1_radio.grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)
    
    def create_buttons(self):
        """버튼 영역 생성"""
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        # 계산하기 버튼
        calculate_button = ttk.Button(
            button_frame,
            text="계산하기",
            command=self.calculate,
            width=15
        )
        calculate_button.pack(side=tk.LEFT, padx=10)
        
        # 새 계산 버튼
        reset_button = ttk.Button(
            button_frame,
            text="새 계산",
            command=self.reset_inputs,
            width=15
        )
        reset_button.pack(side=tk.LEFT, padx=10)
        
        # 종료 버튼
        exit_button = ttk.Button(
            button_frame,
            text="종료",
            command=self.root.quit,
            width=15
        )
        exit_button.pack(side=tk.RIGHT, padx=10)
    
    def create_result_display(self):
        """결과 표시 영역 생성"""
        result_frame = ttk.LabelFrame(
            self.root,
            text="계산 결과",
            padding="10"
        )
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 결과 텍스트 영역
        self.result_text = tk.Text(
            result_frame,
            height=15,
            width=70,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(self.result_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)
        
        # 초기 메시지
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert('1.0', "계산 결과가 여기에 표시됩니다\n\n"
                                     "입력을 완료한 후 '계산하기' 버튼을 클릭하세요.")
        self.result_text.config(state=tk.DISABLED)
    
    def on_mode_changed(self, *args):
        """모드 변경 시 호출되는 함수"""
        mode = self.mode_var.get()
        # TODO: 모드에 따라 입력 필드 활성화/비활성화
        # Phase 2에서 구현 예정
        pass
    
    def calculate(self):
        """계산 실행 함수"""
        try:
            # 1. 입력값 가져오기 및 검증
            # 필수 입력값
            flow_str = self.flow_var.get().strip()
            head_str = self.head_var.get().strip()
            
            if not flow_str or not head_str:
                raise ValueError("유량과 실양정을 입력하세요")
            
            flow_rate = float(flow_str)
            static_head = float(head_str)
            num_pumps = int(self.pumps_var.get())
            
            # 2. 빈 값 또는 0 이하 체크
            if flow_rate <= 0:
                raise ValueError("유량은 0보다 커야 합니다")
            if static_head < 0:
                raise ValueError("실양정은 0 이상이어야 합니다")
            if num_pumps <= 0:
                raise ValueError("펌프 대수는 0보다 커야 합니다")
            
            # 3. 옵션 값 가져오기
            safety_margin = float(self.safety_var.get()) if self.safety_var.get().strip() else 1.5
            pump_efficiency = float(self.efficiency_var.get()) if self.efficiency_var.get().strip() else 0.70
            motor_safety_factor = float(self.motor_safety_var.get()) if self.motor_safety_var.get().strip() else 1.15
            
            # 옵션 값 검증
            if safety_margin < 0:
                raise ValueError("여유 수두는 0 이상이어야 합니다")
            if pump_efficiency <= 0 or pump_efficiency > 1:
                raise ValueError("펌프 효율은 0 초과 1 이하이어야 합니다")
            if motor_safety_factor <= 0:
                raise ValueError("모터 여유율은 0보다 커야 합니다")
            
            # 4. 모드별 파라미터 처리
            mode = self.mode_var.get()
            calc_params = {
                'mode': mode,
                'flow_rate': flow_rate,
                'static_head': static_head,
                'electrical_type': self.electrical_var.get(),
                'num_pumps': num_pumps,
                'safety_margin': safety_margin,
                'pump_efficiency': pump_efficiency,
                'motor_safety_factor': motor_safety_factor,
            }
            
            if mode == 'standard':
                # 일반 양정 모드
                pipe_loss_str = self.pipe_loss_var.get().strip()
                pipe_loss = float(pipe_loss_str) if pipe_loss_str else 0.0
                
                if pipe_loss < 0:
                    raise ValueError("관로 손실은 0 이상이어야 합니다")
                
                calc_params['pipe_loss'] = pipe_loss
                
            else:  # mode == 'pressure'
                # 압송 관로 모드
                pipe_length_str = self.pipe_length_var.get().strip()
                pipe_diameter_str = self.pipe_diameter_var.get().strip()
                
                if not pipe_length_str or not pipe_diameter_str:
                    raise ValueError("압송 모드에서는 거리와 관경을 입력하세요")
                
                pipe_length = float(pipe_length_str)
                pipe_diameter = float(pipe_diameter_str)
                
                if pipe_length <= 0:
                    raise ValueError("압송 거리는 0보다 커야 합니다")
                if pipe_diameter <= 0:
                    raise ValueError("관경은 0보다 커야 합니다")
                
                calc_params['pipe_length'] = pipe_length
                calc_params['pipe_diameter'] = pipe_diameter
                calc_params['pipe_material'] = self.pipe_material_var.get()
            
            # 5. 계산 실행
            result = calculate_complete_pump_spec(**calc_params)
            
            # 6. 결과 표시
            self.display_result(result)
            
        except ValueError as e:
            self.show_error(f"입력 오류: {str(e)}")
        except Exception as e:
            self.show_error(f"계산 오류: {str(e)}")
    
    def reset_inputs(self):
        """입력 필드 초기화"""
        self.flow_var.set('')
        self.head_var.set('')
        self.pumps_var.set(1)
        self.pipe_loss_var.set('0')
        self.pipe_length_var.set('')
        self.pipe_diameter_var.set('')
        self.pipe_material_var.set('PVC')
        self.safety_var.set('1.5')
        self.efficiency_var.set('0.70')
        self.motor_safety_var.set('1.15')
        self.mode_var.set('standard')
        self.electrical_var.set('3phase')
        
        self.update_result_display("입력 필드가 초기화되었습니다.\n"
                                 "새로운 값을 입력한 후 '계산하기' 버튼을 클릭하세요.")
    
    def display_result(self, result):
        """결과 표시 함수"""
        # 결과 Text 위젯 초기화
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        
        # 결과 포맷팅
        output = "=" * 50 + "\n"
        output += " 펌프 용량 계산 결과\n"
        output += "=" * 50 + "\n\n"
        
        # 모드 이름 변환
        mode_name = '일반 양정' if result['mode'] == 'standard' else '압송 관로'
        
        # 전기 방식 이름 변환
        if result['electrical_type'] == '3phase':
            electrical_name = f'삼상 {result["voltage"]}V'
        else:
            electrical_name = f'단상 {result["voltage"]}V'
        
        output += f"계산 모드: {mode_name}\n"
        output += f"전양정: {result['total_head']:.2f} m\n"
        output += f"펌프당 유량: {result['flow_per_pump']:.2f} ㎥/hr\n"
        output += f"펌프 동력: {result['pump_power']:.2f} kW\n"
        output += f"모터 용량: {result['motor_power']:.2f} kW\n"
        output += f"전기 방식: {electrical_name}\n"
        output += f"전류: {result['current']:.2f} A\n"
        
        # 압송 모드 추가 정보
        if result['mode'] == 'pressure':
            output += f"\n[압송 관로 상세]\n"
            output += f"마찰 손실: {result['friction_loss']:.2f} m\n"
            output += f"잔압 환산: {result['residual_head']:.2f} m\n"
            output += f"유속: {result['velocity']:.2f} m/s\n"
        
        output += "\n" + "=" * 50
        
        # 결과 표시
        self.result_text.insert('1.0', output)
        self.result_text.config(state=tk.DISABLED)
    
    def show_error(self, message):
        """에러 메시지 표시"""
        from tkinter import messagebox
        messagebox.showerror("오류", message)
    
    def reset_inputs(self):
        """입력 필드 초기화"""
        self.flow_var.set('')
        self.head_var.set('')
        self.pumps_var.set(1)
        self.pipe_loss_var.set('0')
        self.pipe_length_var.set('')
        self.pipe_diameter_var.set('')
        self.pipe_material_var.set('PVC')
        self.safety_var.set('1.5')
        self.efficiency_var.set('0.70')
        self.motor_safety_var.set('1.15')
        self.mode_var.set('standard')
        self.electrical_var.set('3phase')
        
        # 결과 영역 초기화
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', "계산 결과가 여기에 표시됩니다\n\n"
                                     "입력을 완료한 후 '계산하기' 버튼을 클릭하세요.")
        self.result_text.config(state=tk.DISABLED)


def main():
    """메인 함수"""
    root = tk.Tk()
    app = PumpCalculatorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()