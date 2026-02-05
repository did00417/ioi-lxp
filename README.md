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

브랜치 테스트
develop

### config - 테스트 데이터 파일 규칙
1. header_data.jon -> 공용으로 사용할 헤더 데이터
2. test_<도메인명>_data.json -> 각자 테스트할 도메인에서 사용할 데이터
3. url.json -> 공용으로 사용할 url 모아둔 파일

### conftest.py 규칙
1. 헤더, url은 공용으로 사용
2. test_<도메인명>_data.json 에서 저장한 테스트 데이터 불러오는 fixture 함수 각자 만들어서 사용
