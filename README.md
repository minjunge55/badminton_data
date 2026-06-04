# 🏸 배드민턴 경기 분석 시스템

KFF 배드민턴 경기 데이터 시각화 및 분석 도구

---

## 📁 폴더 구조

```
badminton_data/
├── 단식/
│   ├── 안세영/
│   │   ├── 32강_vs_TUR_arin.csv
│   │   └── 16강_vs_INA_sindhu.csv
│   └── 김가은/
│       └── 16강_vs_THA_chuchowang.csv
├── 복식/
│   ├── 강민혁_기동주/
│   │   └── 16강_vs_JPN_호키고바야시.csv
│   └── 이소희_백하나/
│       └── 32강_vs_INA_PRATIWI_RAMADHANTI.csv
└── 혼복/
    └── 김재현_장하정/
        └── 32강_vs_INA_Jafar_Pasaribu.csv
```

---

## 🛠 분석 도구

| 파일 | 용도 |
|------|------|
| `singles_capture.html` | 단식 분석 카드 (브라우저에서 열기) |
| `doubles_capture.html` | 복식/혼복 분석 카드 (브라우저에서 열기) |
| `generate_cards.py` | 단식 PNG 자동 생성 |
| `generate_doubles.py` | 복식/혼복 PNG 자동 생성 |

---

## 🚀 빠른 시작

### 1. 설치 (최초 1회)
```bash
pip install playwright
python -m playwright install chromium
```

### 2. 단식 카드 생성
```bash
python generate_cards.py <CSV파일> <선수명> <상대선수> <라운드>

# 예시
python generate_cards.py 안세영_32강.csv 안세영 "TUR_arin" 32강
```

### 3. 복식/혼복 카드 생성
```bash
python generate_doubles.py <CSV파일> <선수1> <선수2> <상대팀> <라운드>

# 복식 예시
python generate_doubles.py 강민혁기동주_16강.csv 강민혁 기동주 "JPN_호키고바야시" 16강

# 혼복 예시
python generate_doubles.py 김재현장하정_32강.csv 김재현 장하정 "INA_Jafar_Pasaribu" 32강
```

출력: `cards_output/` 폴더에 PNG 자동 저장

---

## 📊 카드 구성

### 단식
- **1번 캡처**: 득점존/실점존 코트맵 + 실수기술 + 경기결과
- **2번 캡처**: 25초 클락 타일

### 복식/혼복
- **1번 캡처**: 선수1 득점유형 + 실점유형 + 실수기술 + 경기결과
- **2번 캡처**: 선수1 25초 클락
- **3번 캡처**: 선수2 득점유형 + 실점유형 + 실수기술 + 경기결과
- **4번 캡처**: 선수2 25초 클락

---

## 📋 CSV 포맷

### 단식
```
이름;위치;기간;피리어드;Rally;Result;실수 기술;Zone;ColorTag
1set;36169;13335;...;Mistake Lose;Smash;;Color2
```

### 복식/혼복 (신규 포맷)
```
이름,위치,기간,Result,득점상황,실점상황,Home player,Technics
1set (1),87459,9249,Away Mistakes Win,,,,
```
- Home1 = 선수1, Home2 = 선수2

---

## 📈 분석 항목

| 항목 | 설명 |
|------|------|
| 득점/실점 | 팀 전체 및 득점률 |
| 득점 유형 | 공격 / 중간볼 / 초구 / 수비 상황 |
| 실점 유형 | 수비 / 중간볼 / 공격 / 초구 상황 |
| 코트 히트맵 | 득점존(상대코트) / 실점존(본인코트) |
| 실수 기술 | 선수별 실수 기술 횟수 |
| 25초 클락 | 랠리 간격 측정, 평균/초과 횟수 |
| 경기 결과 | 상대실수득점 / 공격성공 / 상대공격실점 / 본인실수실점 |

---

## 🗂 데이터 추가 방법

새 경기 데이터 추가 시:
```
badminton_data/<종목>/<선수명>/
  └── <라운드>_vs_<상대>.csv
```

예: `badminton_data/단식/안세영/8강_vs_KOR_김가은.csv`

