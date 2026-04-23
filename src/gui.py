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
        self.root.geometry("1000x800")
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

        # 메인 레이아웃 생성
        self.create_main_layout()

        # 모드 변경 이벤트 바인딩
        self.mode_var.trace('w', self.on_mode_changed)

    def create_main_layout(self):
        """메인 레이아웃 생성 (좌우 분할)"""
        # 타이틀 생성
        self.create_title()

        # 메인 컨테이너를 좌우로 분할
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # 왼쪽 프레임 (입력 영역) - 스크롤 가능
        left_frame = ttk.Frame(main_container)
        left_canvas = tk.Canvas(left_frame)
        left_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=left_canvas.yview)
        left_scroll_frame = ttk.Frame(left_canvas)

        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        # 스크롤바 설정
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_canvas.create_window((0, 0), window=left_scroll_frame, anchor="nw")

        # 스크롤 프레임 업데이트 함수
        def configure_scroll_region(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))

        left_scroll_frame.bind("<Configure>", configure_scroll_region)

        # 오른쪽 프레임 (결과 영역)
        right_frame = ttk.Frame(main_container)

        # PanedWindow에 추가
        main_container.add(left_frame, weight=1)  # 왼쪽 40%
        main_container.add(right_frame, weight=2)  # 오른쪽 60%

        # 왼쪽 영역 UI 생성
        self.create_left_panel(left_scroll_frame)

        # 오른쪽 영역 UI 생성
        self.create_right_panel(right_frame)

    def create_title(self):
        """타이틀 영역 생성"""
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)

        title_label = tk.Label(
            title_frame,
            text="하수도 펌프 용량 계산기",
            font=("Helvetica", 20, "bold")
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="일반 양정 모드와 압송 관로 모드 지원",
            font=("Helvetica", 13)
        )
        subtitle_label.pack()

    def create_left_panel(self, parent):
        """왼쪽 패널 (입력 영역) 생성"""
        # 모드 선택
        self.create_mode_selection(parent)

        # 기본 정보 입력
        self.create_basic_inputs(parent)

        # 전기 사양 선택
        self.create_electrical_selection(parent)

        # 버튼 영역
        self.create_buttons(parent)

    def create_right_panel(self, parent):
        """오른쪽 패널 (결과 영역) 생성"""
        self.create_result_display(parent)

    def create_mode_selection(self, parent):
        """계산 모드 선택 영역 생성"""
        mode_frame = ttk.Frame(parent)
        mode_frame.pack(fill=tk.X, padx=10, pady=8)

        # 제목 라벨 추가
        title_label = tk.Label(
            mode_frame,
            text="계산 모드 선택",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(anchor=tk.W, padx=5, pady=(0, 10))

        # 내용 프레임
        content_frame = ttk.Frame(mode_frame)
        content_frame.pack(fill=tk.X, padx=5, pady=5)

        # 라디오 버튼 프레임
        radio_frame = ttk.Frame(content_frame)
        radio_frame.pack()

        # 일반 양정 모드
        standard_radio = tk.Radiobutton(
            radio_frame,
            text="일반 양정 모드",
            variable=self.mode_var,
            value='standard',
            font=("Helvetica", 13)
        )
        standard_radio.grid(row=0, column=0, padx=25, pady=8, sticky=tk.W)

        # 압송 관로 모드
        pressure_radio = tk.Radiobutton(
            radio_frame,
            text="압송 관로 모드",
            variable=self.mode_var,
            value='pressure',
            font=("Helvetica", 13)
        )
        pressure_radio.grid(row=0, column=1, padx=25, pady=8, sticky=tk.W)

    def create_basic_inputs(self, parent):
        """기본 정보 입력 영역 생성"""
        basic_frame = ttk.Frame(parent)
        basic_frame.pack(fill=tk.X, padx=10, pady=8)

        # 제목 라벨 추가
        title_label = tk.Label(
            basic_frame,
            text="기본 정보 입력",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(anchor=tk.W, padx=5, pady=(0, 10))

        # 내용 프레임
        content_frame = ttk.Frame(basic_frame)
        content_frame.pack(fill=tk.X, padx=5, pady=5)

        # 설계 유량
        tk.Label(content_frame, text="설계 유량 (㎥/hr):", font=("Helvetica", 13)).grid(
            row=0, column=0, padx=8, pady=8, sticky=tk.W
        )
        flow_entry = tk.Entry(content_frame, textvariable=self.flow_var, width=15, font=("Helvetica", 14))
        flow_entry.grid(row=0, column=1, padx=8, pady=8)
        tk.Label(content_frame, text="예: 100", font=("Helvetica", 12)).grid(
            row=0, column=2, padx=8, pady=8, sticky=tk.W
        )

        # 실양정
        tk.Label(basic_frame, text="실양정 (m):", font=("Helvetica", 13)).grid(
            row=1, column=0, padx=8, pady=8, sticky=tk.W
        )
        head_entry = tk.Entry(content_frame, textvariable=self.head_var, width=15, font=("Helvetica", 14))
        head_entry.grid(row=1, column=1, padx=8, pady=8)
        tk.Label(basic_frame, text="예: 20", font=("Helvetica", 12)).grid(
            row=1, column=2, padx=8, pady=8, sticky=tk.W
        )

        # 펌프 대수
        tk.Label(basic_frame, text="펌프 대수:", font=("Helvetica", 13)).grid(
            row=2, column=0, padx=8, pady=8, sticky=tk.W
        )
        pumps_spinbox = tk.Spinbox(
            basic_frame,
            from_=1,
            to=5,
            textvariable=self.pumps_var,
            width=13,
            font=("Helvetica", 14)
        )
        pumps_spinbox.grid(row=2, column=1, padx=8, pady=8)

        # 일반 양정 모드: 관로 손실
        tk.Label(basic_frame, text="관로 손실 (m):").grid(
            row=3, column=0, padx=5, pady=5, sticky=tk.W
        )
        pipe_loss_entry = tk.Entry(basic_frame, textvariable=self.pipe_loss_var, width=15)
        pipe_loss_entry.grid(row=3, column=1, padx=5, pady=5)
        tk.Label(basic_frame, text="일반 양정 모드용").grid(
            row=3, column=2, padx=5, pady=5, sticky=tk.W
        )

        # 압송 관로 모드: 관 길이
        tk.Label(basic_frame, text="압송 거리 (m):").grid(
            row=4, column=0, padx=5, pady=5, sticky=tk.W
        )
        pipe_length_entry = tk.Entry(basic_frame, textvariable=self.pipe_length_var, width=15)
        pipe_length_entry.grid(row=4, column=1, padx=5, pady=5)
        tk.Label(basic_frame, text="압송 모드용").grid(
            row=4, column=2, padx=5, pady=5, sticky=tk.W
        )

        # 압송 관로 모드: 관경
        tk.Label(basic_frame, text="관경 (mm):").grid(
            row=5, column=0, padx=5, pady=5, sticky=tk.W
        )
        pipe_diameter_entry = tk.Entry(basic_frame, textvariable=self.pipe_diameter_var, width=15)
        pipe_diameter_entry.grid(row=5, column=1, padx=5, pady=5)
        tk.Label(basic_frame, text="예: 150").grid(
            row=5, column=2, padx=5, pady=5, sticky=tk.W
        )

        # 압송 관로 모드: 관 재질
        tk.Label(basic_frame, text="관 재질:", font=("Helvetica", 13)).grid(
            row=6, column=0, padx=8, pady=8, sticky=tk.W
        )
        material_combo = ttk.Combobox(
            content_frame,
            textvariable=self.pipe_material_var,
            values=['PVC', 'PE', '강관', 'HDPE', '주철관'],
            width=12,
            state='readonly'
        )
        material_combo.grid(row=6, column=1, padx=8, pady=8)

        # 옵션: 여유 수두
        tk.Label(basic_frame, text="여유 수두 (m):").grid(
            row=7, column=0, padx=5, pady=5, sticky=tk.W
        )
        safety_entry = tk.Entry(basic_frame, textvariable=self.safety_var, width=15)
        safety_entry.grid(row=7, column=1, padx=5, pady=5)
        tk.Label(basic_frame, text="기본값: 1.5").grid(
            row=7, column=2, padx=5, pady=5, sticky=tk.W
        )

        # 옵션: 펌프 효율
        tk.Label(basic_frame, text="펌프 효율:").grid(
            row=8, column=0, padx=5, pady=5, sticky=tk.W
        )
        efficiency_entry = tk.Entry(basic_frame, textvariable=self.efficiency_var, width=15)
        efficiency_entry.grid(row=8, column=1, padx=5, pady=5)
        tk.Label(basic_frame, text="기본값: 0.70").grid(
            row=8, column=2, padx=5, pady=5, sticky=tk.W
        )

        # 옵션: 모터 여유율
        tk.Label(basic_frame, text="모터 여유율:").grid(
            row=9, column=0, padx=5, pady=5, sticky=tk.W
        )
        motor_safety_entry = tk.Entry(basic_frame, textvariable=self.motor_safety_var, width=15)
        motor_safety_entry.grid(row=9, column=1, padx=5, pady=5)
        tk.Label(basic_frame, text="기본값: 1.15").grid(
            row=9, column=2, padx=5, pady=5, sticky=tk.W
        )

    def create_electrical_selection(self, parent):
        """전기 사양 선택 영역 생성"""
        electrical_frame = ttk.Frame(parent)
        electrical_frame.pack(fill=tk.X, padx=10, pady=8)

        # 제목 라벨 추가
        title_label = tk.Label(
            electrical_frame,
            text="전기 사양 선택",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(anchor=tk.W, padx=5, pady=(0, 10))

        # 내용 프레임
        content_frame = ttk.Frame(electrical_frame)
        content_frame.pack(fill=tk.X, padx=5, pady=5)

        # 라디오 버튼 프레임
        radio_frame = ttk.Frame(content_frame)
        radio_frame.pack()

        # 삼상 전기
        phase3_radio = tk.Radiobutton(
            radio_frame,
            text="삼상 380V",
            variable=self.electrical_var,
            value='3phase',
            font=("Helvetica", 13)
        )
        phase3_radio.grid(row=0, column=0, padx=25, pady=8, sticky=tk.W)
        
        # 단상 전기
        phase1_radio = tk.Radiobutton(
            radio_frame,
            text="단상 220V",
            variable=self.electrical_var,
            value='1phase',
            font=("Helvetica", 13)
        )
        phase1_radio.grid(row=0, column=1, padx=25, pady=8, sticky=tk.W)

    def create_buttons(self, parent):
        """버튼 영역 생성"""
        button_frame = ttk.Frame(parent, padding="10")
        button_frame.pack(fill=tk.X)

        # 계산하기 버튼 (강조)
        self.calc_button = tk.Button(
            button_frame,
            text="계산하기",
            command=self.calculate,
            bg='#3498db',
            fg='white',
            font=('Helvetica', 14, 'bold'),
            padx=25,
            pady=12,
            relief=tk.RAISED,
            borderwidth=2
        )
        self.calc_button.pack(side=tk.LEFT, padx=15)

        # 새 계산 버튼
        reset_button = tk.Button(
            button_frame,
            text="새 계산",
            command=self.reset_inputs,
            bg='#95a5a6',
            fg='white',
            font=('Helvetica', 14),
            padx=25,
            pady=12,
            relief=tk.RAISED,
            borderwidth=2
        )
        reset_button.pack(side=tk.LEFT, padx=15)

        # 종료 버튼
        exit_button = tk.Button(
            button_frame,
            text="종료",
            command=self.root.quit,
            bg='#e74c3c',
            fg='white',
            font=('Helvetica', 14),
            padx=25,
            pady=12,
            relief=tk.RAISED,
            borderwidth=2
        )
        exit_button.pack(side=tk.RIGHT, padx=15)

    def create_result_display(self, parent):
        """결과 표시 영역 생성"""
        result_frame = ttk.Frame(parent)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 제목 라벨 추가
        title_label = tk.Label(
            result_frame,
            text="계산 결과",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(anchor=tk.W, padx=5, pady=(0, 10))

        # 내용 프레임
        content_frame = ttk.Frame(result_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 결과 Text 위젯 (하나만 생성)
        self.result_text = tk.Text(
            content_frame,
            font=('Helvetica', 12),
            wrap=tk.WORD,
            bg='#f8f9fa',
            padx=20,
            pady=20,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 스크롤바
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scrollbar.set)

        # 태그 스타일 정의 (글꼴 크기 증가)
        self.result_text.tag_configure('title', font=('Helvetica', 18, 'bold'), foreground='#2c3e50')
        self.result_text.tag_configure('section', font=('Helvetica', 14, 'bold'), foreground='#34495e')
        self.result_text.tag_configure('label', font=('Helvetica', 12), foreground='#7f8c8d')
        self.result_text.tag_configure('value', font=('Helvetica', 12, 'bold'), foreground='#2980b9')
        self.result_text.tag_configure('highlight', font=('Helvetica', 14, 'bold'), foreground='#e74c3c', background='#fff5f5')
        self.result_text.tag_configure('separator', foreground='#bdc3c7')

        # 초기 메시지
        welcome_msg = """

 하수도 펌프 용량 계산기

 왼쪽 입력 폼을 채우고
 '계산하기' 버튼을 눌러주세요.

 계산 결과가 여기에 표시됩니다.

"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert('1.0', welcome_msg, 'section')
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



    def display_result(self, result):
        """결과 표시 함수"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)

        # 타이틀
        self.result_text.insert(tk.END, "펌프 용량 계산 결과\n\n", 'title')

        # 구분선
        self.result_text.insert(tk.END, "─" * 50 + "\n\n", 'separator')

        # 기본 정보 섹션
        self.result_text.insert(tk.END, "📋 기본 정보\n", 'section')

        # 모드 이름 변환
        mode_name = '일반 양정' if result['mode'] == 'standard' else '압송 관로'
        self.insert_result_line("계산 모드", mode_name)

        # 펌프 대수 (기본값 1)
        num_pumps = result.get('num_pumps', 1)
        self.insert_result_line("펌프 대수", f"{num_pumps}대")
        self.result_text.insert(tk.END, "\n")

        # 주요 결과 섹션 (강조)
        self.result_text.insert(tk.END, "⚡️ 주요 계산 결과\n", 'section')
        self.insert_result_line("전양정", f"{result['total_head']:.2f} m", highlight=True)
        self.insert_result_line("펌프당 유량", f"{result['flow_per_pump']:.2f} ㎥/hr")
        self.insert_result_line("펌프 동력", f"{result['pump_power']:.2f} kW", highlight=True)
        self.insert_result_line("펌프 효율", f"{result['efficiency']*100:.0f}%")
        self.result_text.insert(tk.END, "\n")

        # 모터 사양 섹션
        self.result_text.insert(tk.END, "🔌 모터 사양\n", 'section')
        self.insert_result_line("모터 용량", f"{result['motor_power']:.2f} kW", highlight=True)
        self.insert_result_line("모터 여유율", f"{result['motor_safety_factor']}")

        # 전기 방식
        electrical_str = "삼상 380V" if result['electrical_type'] == '3phase' else "단상 220V"
        self.insert_result_line("전기 방식", electrical_str)
        self.insert_result_line("전류", f"{result['current']:.2f} A", highlight=True)
        self.result_text.insert(tk.END, "\n")

        # 압송 모드 추가 정보
        if 'friction_loss' in result:
            self.result_text.insert(tk.END, "🔧 압송 관로 상세\n", 'section')
            self.insert_result_line("마찰 손실", f"{result['friction_loss']:.2f} m")
            self.insert_result_line("잔압 환산", f"{result['residual_head']:.2f} m")
            self.insert_result_line("유속", f"{result['velocity']:.2f} m/s")
            self.result_text.insert(tk.END, "\n")

        # 하단 구분선
        self.result_text.insert(tk.END, "─" * 50 + "\n", 'separator')

        # 스크롤을 맨 위로
        self.result_text.see('1.0')
        self.result_text.config(state=tk.DISABLED)

    def show_error(self, message):
        """에러 메시지 표시"""
        from tkinter import messagebox
        messagebox.showerror("오류", message)

    def insert_result_line(self, label, value, highlight=False):
        """결과 라인 삽입 헬퍼 함수"""
        self.result_text.insert(tk.END, f" {label}: ", 'label')
        if highlight:
            self.result_text.insert(tk.END, f"{value}\n", 'highlight')
        else:
            self.result_text.insert(tk.END, f"{value}\n", 'value')

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
        welcome_msg = """


 👋 환영합니다!

 왼쪽 입력 폼을 채우고
 '계산하기' 버튼을 눌러주세요.

 계산 결과가 여기에 표시됩니다.


"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', welcome_msg, 'section')
        self.result_text.config(state=tk.DISABLED)


def main():
    """메인 함수"""
    root = tk.Tk()
    app = PumpCalculatorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()