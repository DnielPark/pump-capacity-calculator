# Pump Capacity Calculator

하수도 펌프 용량 계산기 - 압송관로/일반양정 모드 지원

## 📋 기능

- **압송관로 모드**: 압송관로 시스템용 펌프 용량 계산
- **일반양정 모드**: 일반 양정 시스템용 펌프 용량 계산
- **다양한 단위 지원**: m³/h, L/s, GPM 등
- **결과 내보내기**: PDF, Excel, CSV 형식으로 계산 결과 저장
- **사용자 친화적 UI**: 직관적인 웹 인터페이스

## 🚀 설치 방법

```bash
# 레포지토리 클론
git clone https://github.com/DnielPark/pump-capacity-calculator.git
cd pump-capacity-calculator

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 📁 프로젝트 구조

```
pump-capacity-calculator/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── docs/
│   └── 개발계획서.md
└── src/
    ├── __init__.py
    ├── calc/          # 계산 엔진
    │   └── __init__.py
    ├── ui/           # 사용자 인터페이스
    │   └── __init__.py
    └── export/       # 결과 내보내기
        └── __init__.py
```

## 🛠️ 기술 스택

- **Python 3.8+**
- **Streamlit** (웹 UI)
- **Pandas** (데이터 처리)
- **NumPy** (수치 계산)
- **ReportLab** (PDF 생성)
- **openpyxl** (Excel 생성)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여하기

버그 리포트, 기능 제안, 풀 리퀘스트는 언제나 환영합니다!

1. 이슈를 생성하거나 기존 이슈를 확인하세요
2. 포크하고 브랜치를 만드세요
3. 변경사항을 커밋하고 푸시하세요
4. 풀 리퀘스트를 생성하세요