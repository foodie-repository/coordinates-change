# 지번주소 좌표 변환 도구

엑셀 파일의 지번주소를 위도/경도 좌표로 변환하는 Python 스크립트 모음입니다. 다양한 지오코딩 API를 지원하여 상황에 맞게 선택할 수 있습니다.

## 특징

- **4가지 API 옵션**: Kakao, Nominatim, VWorld, Google Sheets
- **uv 기반 프로젝트**: 빠른 패키지 관리 및 가상환경
- **엑셀 파일 지원**: pandas와 openpyxl을 사용한 엑셀 처리
- **중복 방지**: 이미 처리된 주소는 자동으로 건너뛰기
- **상세한 로그**: 실시간 진행 상황 및 결과 요약

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/foodie-repository/coordinates-change.git
cd coordinates-change
```

### 2. 의존성 설치

이 프로젝트는 `uv`를 사용합니다. uv가 설치되어 있지 않다면 먼저 설치하세요.

```bash
# uv 설치 (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 Homebrew로 설치
brew install uv
```

프로젝트 의존성 설치:

```bash
# uv가 자동으로 가상환경을 생성하고 패키지를 설치합니다
uv sync
```

## 스크립트 종류

### 1. Kakao Local API (`add_coordinates_kakao.py`)

**특징:**
- 가장 정확한 한국 주소 검색
- API 키 필요 (무료)
- 일일 30만건 무료 할당량

**API 키 발급:**
1. [카카오 개발자 사이트](https://developers.kakao.com/) 접속
2. 로그인 → "내 애플리케이션" → "애플리케이션 추가하기"
3. 앱 생성 후 "앱 키" 탭에서 **REST API 키** 복사

**실행:**
```bash
uv run python add_coordinates_kakao.py
```

### 2. Nominatim/OpenStreetMap (`add_coordinates_nominatim.py`)

**특징:**

- 완전 무료, API 키 불필요
- OpenStreetMap 기반
- 한국 주소 검색 정확도는 카카오보다 낮음
- 속도 제한: 초당 1회 요청

**실행:**
```bash
uv run python add_coordinates_nominatim.py
```

### 3. VWorld API (`add_coordinates_vworld.py`)

**특징:**

- 국토교통부 제공
- 인증키 불필요
- 한국 주소 특화
- 무료

**실행:**
```bash
uv run python add_coordinates_vworld.py
```

### 4. Google Sheets 연동 (`google_sheets_coordinates.py`)

**특징:**
- Google Sheets에서 직접 읽고 쓰기
- OAuth2 인증 필요
- 클라우드 기반 협업 가능

**실행:**
```bash
uv run python google_sheets_coordinates.py
```

## 사용 방법

### 입력 파일 준비

엑셀 파일에 다음 컬럼이 있어야 합니다:

| 지번주소 | 위도 | 경도 |
| ------- | ---- | ---- |
| 서울특별시 송파구 풍납동 260-4 | | |
| 서울특별시 송파구 오금동 165 | | |

- **지번주소**: 변환할 주소
- **위도**: 변환된 위도가 저장될 컬럼 (비어있어도 됨)
- **경도**: 변환된 경도가 저장될 컬럼 (비어있어도 됨)

### 실행 예시

```bash
# 1. 프로젝트 디렉토리로 이동
cd /Users/foodie/myproject/좌표-변환

# 2. 스크립트 실행 (카카오 API 사용)
uv run python add_coordinates_kakao.py

# 또는 가상환경 활성화 후 실행
source .venv/bin/activate
python add_coordinates_kakao.py
```

### 출력 예시

```
카카오 REST API 키를 입력하세요: your_api_key_here

🚀 주소 좌표 변환을 시작합니다...

📖 파일 읽는 중: /Users/foodie/Downloads/서울.xlsx
📊 총 568개의 주소를 처리합니다.
--------------------------------------------------
🔍 [1/568] 검색 중: 서울특별시 송파구 풍납동 260-4
✅ 성공: 위도=37.5321, 경도=127.1234
🔍 [2/568] 검색 중: 서울특별시 송파구 오금동 165
✅ 성공: 위도=37.5012, 경도=127.1345
...
--------------------------------------------------
💾 결과 저장 중: /Users/foodie/Downloads/서울_좌표추가.xlsx

==================================================
📊 처리 결과
==================================================
✅ 성공: 560개
❌ 실패: 8개
📁 저장 위치: /Users/foodie/Downloads/서울_좌표추가.xlsx
==================================================
```

## 주요 기능

### 1. 자동 주소 검색

- 각 API를 통해 지번주소를 위도/경도로 변환
- 실패 시 자동으로 다음 주소로 진행

### 2. 중복 처리 방지

- 이미 좌표가 입력된 행은 자동으로 건너뛰기
- 중단 후 재실행 시 처리되지 않은 주소만 처리

### 3. API 제한 고려

- 각 API의 호출 제한을 고려한 자동 대기 시간
- Kakao: 0.1초, Nominatim: 1초

### 4. 상세한 로그

- 실시간 처리 진행 상황 표시
- 성공/실패 건수 요약 제공

## 프로젝트 구조

```
coordinate-converter/
├── add_coordinates_kakao.py       # 카카오 API 스크립트
├── add_coordinates_nominatim.py   # Nominatim API 스크립트
├── add_coordinates_vworld.py      # VWorld API 스크립트
├── google_sheets_coordinates.py   # Google Sheets 연동 스크립트
├── pyproject.toml                 # 프로젝트 설정 및 의존성
├── uv.lock                        # 잠금 파일
└── README.md                      # 이 파일
```

## 기술 스택

- **Python**: 3.11+
- **패키지 관리**: uv
- **주요 라이브러리**:
  - `pandas` (2.3.3+): 데이터 처리
  - `requests` (2.32.5+): HTTP 요청
  - `openpyxl` (3.1.5+): 엑셀 파일 처리
  - `geopy` (2.4.1+): Nominatim 지오코딩
  - `gspread` (6.2.1+): Google Sheets 연동
  - `oauth2client` (4.1.3+): Google API 인증

## API 비교

| API | 정확도 | 속도 | 비용 | API 키 | 특징 |
| --- | ------ | ---- | ---- | ------ | ---- |
| **Kakao** | ⭐⭐⭐⭐⭐ | 빠름 | 무료 (30만건/일) | 필요 | 한국 주소 최적화 |
| **Nominatim** | ⭐⭐⭐ | 느림 | 완전 무료 | 불필요 | 오픈소스, 글로벌 |
| **VWorld** | ⭐⭐⭐⭐ | 보통 | 완전 무료 | 불필요 | 국토교통부 공식 |
| **Google Sheets** | - | - | - | OAuth2 | 클라우드 협업 |

## 에러 처리

### API 에러

- 네트워크 에러나 API 응답 오류 시 해당 주소 건너뛰기
- 에러 발생 시 상세 메시지 출력

### 주소 검색 실패

- 주소를 찾을 수 없는 경우 경고 메시지 출력
- 해당 행의 위도/경도는 빈 값으로 유지

## 문제 해결

### "API 키가 유효하지 않습니다" (Kakao)

- 카카오 개발자 사이트에서 API 키 재확인
- REST API 키 사용 여부 확인 (JavaScript 키 ✗)

### "응답이 없습니다"

- 인터넷 연결 확인
- API 서버 상태 확인

### 특정 주소 검색 실패

- 주소 정확성 확인
- 통폐합된 주소나 신규 주소는 검색되지 않을 수 있음
- 다른 API로 시도해보기

### uv 관련 문제

```bash
# 가상환경 재생성
rm -rf .venv
uv sync

# 특정 패키지 재설치
uv add --reinstall pandas
```

## 주의사항

1. **API 키 보안**: API 키는 공개 저장소에 커밋하지 마세요
2. **API 할당량**: 각 API의 무료 할당량 확인
3. **처리 시간**: 대량 데이터는 API 속도 제한으로 시간이 소요됨
4. **인터넷 연결**: API 호출을 위해 인터넷 연결 필요

## 라이선스

MIT License

## 기여

이슈나 풀 리퀘스트를 환영합니다!

## 참고 자료

- [Kakao Local API 문서](https://developers.kakao.com/docs/latest/ko/local/dev-guide)
- [Nominatim API 문서](https://nominatim.org/release-docs/develop/api/Overview/)
- [VWorld API 문서](https://www.vworld.kr/dev/v4dv_geocoderguide2_s001.do)
- [uv 공식 문서](https://docs.astral.sh/uv/)
