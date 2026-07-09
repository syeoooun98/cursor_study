# BMI 계산기

Tkinter로 만든 간단한 BMI(체질량지수) 계산 GUI 프로그램입니다.

## 기능

- 키(cm)와 몸무게(kg)를 입력하면 BMI를 계산합니다.
- BMI 값에 따라 저체중 / 정상체중 / 비만 / 고도비만으로 판정합니다.
- 판정 결과를 시각적인 눈금 그래프로 표시합니다.

## 실행 방법

```bash
python gui.py
```

## 파일 구성

- `main.py` — BMI 계산 및 판정 로직 (`calc_bmi`, `classify_bmi`)
- `gui.py` — Tkinter 기반 GUI 화면
