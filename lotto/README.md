# 로또 번호 생성기 BY 서연

Tkinter 기반 GUI로 동작하는 로또(6/45) 번호 생성 프로그램입니다.

## 실행 방법

```bash
python lotto.py
```

## 프로그램 구조 (`lotto.py`)

| 함 수 | 역 할 |
|---|---|
| `generate_lotto_numbers(count, exclude, include)` | 핵심 로직. 1~45 중 `exclude`를 제외하고 `include`를 고정 포함시켜, `count`게임만큼 정렬된 6개 번호 리스트를 생성. 고정 번호가 6개 초과이거나 제외/고정 번호가 겹치면 `ValueError` 발생 |
| `parse_numbers(text)` | 쉼표로 구분된 입력 문자열("1, 7, 22")을 정수 리스트로 변환 |
| `on_generate(...)` | "생성하기" 버튼 클릭 시 실행되는 이벤트 핸들러. 입력창 값을 읽어 `generate_lotto_numbers`를 호출하고 결과를 리스트박스에 출력, 에러 시 메시지박스로 표시 |
| `main()` | Tkinter 창(`root`)과 위젯(게임 수/제외 번호/고정 번호 입력창, 결과 리스트박스, 생성 버튼)을 구성하고 `mainloop()` 실행 |

### 데이터 흐름

```
사용자 입력 (Entry 위젯)
      │
      ▼
parse_numbers()  ──▶ exclude, include 리스트
      │
      ▼
generate_lotto_numbers()  ──▶ 게임별 번호 리스트
      │
      ▼
result_box (Listbox)에 출력 / 오류 시 messagebox
```

## 주요 기능

- 원하는 게임 수만큼 번호 생성 (기본 1게임)
- 특정 번호 제외 지정
- 특정 번호 고정 포함 지정
- 입력값 검증 (고정 번호 6개 초과, 제외/고정 중복 시 오류 안내)

## 요구 사항

- Python 3.x (표준 라이브러리 `tkinter`만 사용, 별도 설치 불필요)
