# 엘리스 QA 트랙 최종 프로젝트
엘리스 LXP의 기능, 성능, 보안 등 다양한 품질 요소 검토를 위한 테스트 자동화 프로젝트 입니다.

## 🚀 설치 및 실행 가이드

- 가상환경 확인 : `venv` 폴더가 없으면 자동으로 생성
- 가상환경 활성화 : 파이썬 가상환경을 자동으로 연결
- pip 업데이트 : 최신 패키지 매니저 상태 유지
- 라이브러리 설치 : `requirements.txt`

### 터미널 종류 별 실행 방법

1. cmd  
   `setup.bat`

2. powershell  
   `.\setup.bat`

3. git bash  
   `./setup.bat`

## 📚 기술 스택

- Python 3.11
- Requests
- JSON 데이터 처리

## 📁 폴더 별 가이드

```bash
IOI-LXP/
├─ part1_api_automation/       # API 자동화 테스트 코드 폴더
│   ├─ api/                          
│   │   └─ api_client.py       # API 클라이언트 관련 공통 모듈
│   ├─ config/                 # 테스트에 사용할 데이터 관리
│   ├─ reports/                # 테스트 실행 리포트
│   ├─ tests/                  
│   │   └─ test_<도메인명>.py   # 실제 Pytest 테스트 케이스
│   ├─ utils/                  # 공통 유틸리티 함수 및 도구
│   │   ├─ config_loader.py    # config 폴더 데이터 불러오는 함수
│   │   └─ file_manager.py     # JSON 파일 읽기 함수
│   ├─ conftest.py             # 테스트 초기 설정 관리(fixture 등)
│   └─ pytest.ini              # Pytest 실행 옵션
│
├─ part2_load_test/
│   ├─ dashboard/              # 
│   ├─ results/                # 
│   └─ scripts/                # 
│
├─ requirements.txt            # 프로젝트 Python 패키지 명시
└─ setup.bat                   # 가상 환경 & 라이브러리 설치 파일
```

## 🌟 api_automation 폴더 규칙

### config/
1. url.json -> 공용으로 사용할 url 모아둔 파일
2. header_data.json -> 공용으로 사용할 헤더 데이터
3. test_<도메인명>_data.json -> 각자 테스트할 도메인에서 사용할 데이터

### utils/config_loader.py
1. load_test_data("도메인명")의 도메인명은 test_<도메인명>_data.json의 도메인명과 통일
2. test_data.json의 파라미터 데이터에서 환경 변수 설정할 시 .env의 변수 명과 통일

### conftest.py
1. 헤더, url은 공용으로 사용
2. 각 도메인 별 테스트 데이터 불러오는 fixture 함수 load_test_data()로 각자 만들어서 사용
