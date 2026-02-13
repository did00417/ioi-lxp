# 💎 Elice LXP QA Project

본 프로젝트는 엘리스 LMS 플랫폼인 **LXP(Learning Experience Platform)**의 품질 보증(QA)을 위한 API 테스트 및 자동화 프로젝트입니다. -- test

---

## 🎯 프로젝트 소개

LXP 서비스의 주요 기능에 대한 API 검증, 테스트 케이스 설계, 자동화 구현 및 부하 테스트를 수행하여 시스템의 안정성과 신뢰성을 확보합니다.

### 📝 수행 과제

1. **API 필터링**: 검증에 필요한 핵심 API 식별 및 분류
2. **API 기능 테스트용 테스트 케이스(TC) 설계**:
   - ✅ **Positive Test**: 정상 요청 시 `200 OK` 및 데이터 정확성 확인
   - ❌ **Negative Test**: 필수값 누락, 유효하지 않은 값 입력 시 에러 핸들링 확인
3. **테스트 자동화**: 구현된 시나리오의 반복 실행 및 결과 리포팅 자동화
4. **API 부하 테스트**:
   - 대규모 수강생 동시 응시 상황(**Spike Traffic**) 시나리오 수행
   - 백엔드 성능 한계치 측정 및 병목 구간(Bottleneck) 파악

### 📍 API 기능 테스트 범위

| 메뉴명        | 주요 검증 기능 (Example)            | 비고                               |
| :------------ | :---------------------------------- | :--------------------------------- |
| **클래스 홈** | 오늘의 일정 조회, 배너 로딩 등      | 기본 진입점 검증                   |
| **학습 과목** | 과목 목록 조회, 상세 페이지 진입 등 | Part 2 부하 테스트 연계 항목       |
| **수업 일정** | 캘린더 조회, 라이브 강의실 참여 등  | 날짜 필터링 파라미터 확인          |
| **게시판**    | 게시글 목록 조회 및 상세 읽기       | 권한 외(쓰기/삭제) 접근 차단 검증  |
| **대시보드**  | 출석률, 학습 진도율 데이터 조회     | 사용자별 개인화 데이터 정합성 검증 |

---

## 👥 팀원 정보 및 역할

| 이름       | 역할 | 담당 도메인 |
| :--------- | :--: | :---------- |
| **안효진** | 팀장 | 학습 과목   |
| **신동빈** | 팀원 | 수업 일정   |
| **양유진** | 팀원 | 게시판      |
| **양정은** | 팀원 | 클래스 홈   |
| **이수진** | 팀원 | 대시보드    |

---

## 🚀 설치 및 실행 가이드

스크립트 실행 시 다음 과정이 자동으로 진행됩니다:

- **가상환경(venv)** 확인 및 자동 생성
- 가상환경 활성화 및 **pip** 최신화
- `requirements.txt` 기반 필수 라이브러리 설치

### 🖥️ 환경별 실행 방법

| OS / 터미널                | 실행 명령어   |
| :------------------------- | :------------ |
| **Windows (CMD)**          | `setup.bat`   |
| **PowerShell**             | `.\setup.bat` |
| **Git Bash / Mac / Linux** | `./setup.sh`  |

---

## 📚 기술 스택

- Python 3.11
- pytest
- Requests
- JSON 데이터 처리
- Allure Report
- Jenkins Pipeline
- JMeter

## 📁 폴더 별 가이드

```bash
IOI-LXP/
├─ part1_api_automation/       (API 자동화 테스트 코드 폴더)
│   ├─ api/
│   │   └─ api_client.py       (API 클라이언트 관련 공통 모듈)
│   ├─ config/                 (테스트에 사용할 데이터 관리)
│   ├─ reports/                (테스트 실행 리포트)
│   ├─ tests/
│   │   └─ test_<도메인명>.py   (실제 Pytest 테스트 케이스)
│   ├─ utils/                  (공통 유틸리티 함수 및 도구)
│   │   ├─ config_loader.py    (config 폴더 데이터 불러오는 함수)
│   │   └─ json_reader.py      (JSON 파일 읽기 함수)
│   ├─ conftest.py             (테스트 초기 설정 관리(fixture 등))
│   └─ pytest.ini              (Pytest 실행 옵션)
│
├─ part2_load_test/
│   ├─ dashboard/              (JMeter HTML 대시보드 리포트 폴더)
│   ├─ results/                (실행 결과 데이터)
│   └─ scripts/                (JMeter 스크립트 파일)
│
├─ Jenkinsfile                 (CI/CD를 위한 Jenkins용 파일)
├─ requirements.txt            (프로젝트 Python 패키지 명시)
└─ setup.bat/sh                (가상 환경 & 라이브러리 설치 파일)
```

## 🌟 part1_api_automation 규칙

### config/

1. url.json -> 공용으로 사용할 url 모아둔 파일
2. header_data.json -> 공용으로 사용할 헤더 데이터
3. test\_<도메인명>\_data.json -> 각자 테스트할 도메인에서 사용할 데이터

### utils/config_loader.py

1. `load_test_data("도메인명")`의 도메인명은 test_<**도메인명**>_data.json 파일의 도메인명과 통일해야 합니다.
2. config 폴더 안의 json 파일에서 환경 변수를 설정할 시 .env의 변수 명과 통일해야 합니다.

### conftest.py

1. 헤더와 url 관련 fixture은 공용으로 사용합니다.
2. 각 도메인 별 테스트 데이터 불러오는 fixture 함수는 utils/config_loader.py의 `load_test_data()`를 이용해 각자 만들어서 사용합니다.

### .env (git ignore)

개인 정보가 포함된 데이터는 .env 파일에 작성합니다.

```bash
ELICE_VALID_TOKEN={각자의 인증 토큰}
ELICE_INVALID_TOKEN={만료된 토큰}
STUDENT_ID={각자의 student_id}
USER_ID={각자의 user_id}
INVALID_USER_ID={만료된 user_id}
OTHER_STUEDNT_ID={다른 유저의 student_id}
HYOJIN_VALID_TOKEN={학습 과목 도메인 용 인증 토큰}
HYOJIN_ID={학습 과목 도메인 용 user_id}
INVALID_HYOJIN_ID={학습 과목 도메인 용 user_id}
```

---

## 🪵 로깅(Logging) 전략

효율적인 디버깅과 테스트 결과 분석을 위해 아래와 같은 로깅 원칙을 준수합니다.

### 1. 로그 레벨(Log Level) 사용 기준

- **INFO**: 테스트 시작/종료, 주요 스텝 전환, 성공적인 API 응답 상태 등 일반적인 정보
- **DEBUG**: API 요청 파라미터(Payload), 상세 응답 바디(Response Body) 등 디버깅용 데이터
- **WARNING**: 기대한 결과는 아니지만 테스트 중단 사유는 아닌 경우 (예: 권장되지 않는 API 호출)
- **ERROR**: Assertion 실패, 네트워크 오류, 예상치 못한 런타임 예외 발생 시

### 2. 로그 메시지 표준 포맷

로그는 시간, 레벨, 도메인, 메시지를 포함하여 가독성을 높입니다.

> `2026-02-06 11:29:23 [INFO] API 요청 시작: classroom/{classroom_id}/course`

### 3. Pytest 기반 로깅 설정

- 콘솔 출력은 핵심적인 **INFO** 레벨 위주로, 파일 기록은 상세한 **DEBUG** 레벨까지 기록합니다.

---

## 💻 CI 파이프라인 구축 (Jenkins)

Jenkins를 사용하여 GitLab 저장소의 코드를 기반으로 API 자동화 테스트를 실행하고 Allure 리포트를 생성하는 CI 환경을 구성합니다.

### 1. Jenkins Credentials를 이용한 보안 환경변수 주입

`Jenkinsfile`에는 보안을 위해 특정 ID를 참조하도록 되어 있습니다. <br>
따라서 파이프라인 실행을 위해 다음 Credentials ID가 필요합니다.

- **GitLab 연결용 ID**: `LXP_GitLab_Repo_Key`
- **API 토큰용 ID**: `LXP_TOKENS`
- **내 정보용 ID**: `LXP_MY_INFO`
- **타인 정보용 ID**: `LXP_OTHER_INFO`

※ 주의: ID(이름)는 똑같아야 하지만, 그 안에 들어가는 실제 값(토큰이나 ID)은 본인의 계정 정보나 토큰 값을 넣어야 합니다.

### 2. 테스트 결과 시각화

Jenkins Pipeline에서 저장소의 Jenkinsfile을 사용하여 빌드를 실행합니다. <br>
실행 후 Jenkins UI에서 다음 결과를 확인할 수 있습니다.

- Jenkins 기본 Test Result 리포트
- Allure 플러그인을 통한 상세 테스트 리포트

---

## 🌟 part2_load_test 설정

### 1. 테스트 환경 (Test Environment)

- **Infrastructure**: Local
- **JMeter Version**: `5.6.3`

### 2. 테스트 시나리오 (Test Scenario)

- **목표**
  1.  테스트용 Dummy 계정 100개를 이용해 실제 여러 유저가 `입장 → 응시 → 제출 → 재응시`하는 과정을 테스트
  2.  유저 증가에 따른 TPS와 Latency의 상관관계를 분석하고, 임계 지점 및 변곡점 도출
- **테스트 목적**: 100명의 유저가 에러 없이 시험을 제출하고 다시 들어오는 사이클이 원활하게 도는지 검증
- **테스트 성공 기준**
  1.  **Error Rate**: 1% 미만 유지
  2.  **평균 Latency(응답속도)**: 5,000ms 이내

### 3. 테스트 요구사항 (Requirements)

| 설정 항목             | 제한 값                        | 비고                                                |
| :-------------------- | :----------------------------- | :-------------------------------------------------- |
| **Number of Threads** | `10 → 30 → 50 → 70 → 100(Max)` | 단계별 증설 필수, 한 번에 100명 실행 금지           |
| **Ramp-up Period**    | `60s`                          | 짧게 설정 시 공격으로 간주됨                        |
| **Loop Count**        | `5회`                          | Infinite 절대 금지. 유저당 최대 5번의 사이클만 허용 |

### 4. API 선별

| Step | 역할      | Method | Endpoint (Target)                                     |
| :--- | :-------- | :----- | :---------------------------------------------------- |
| 1    | 과목 정보 | `GET`  | ${COURSE_URL}/lecture_page                            |
| 2    | 시험 입장 | `POST` | ${REST_URL}/org/qaproject/user/lecture/test/enter/    |
| 3    | 시험 시작 | `POST` | ${REST_URL}/org/qaproject/user/lecture/test/start/    |
| 3    | 시험 제출 | `POST` | ${REST_URL}/org/qaproject/user/lecture/test/stop/     |
| 4    | 재응시    | `POST` | ${REST_URL}/org/qaproject/lecture/test/reset/by_self/ |

### 5. 📂 Test Plan Structure

```bash
Test Plan (테스트 계획)
┗━ Thread Group (사용자 그룹 설정)
   ┣━ Config Elements (설정)
   ┃  ┣━ CSV Data Set Config (테스트 데이터 로드)
   ┃  ┣━ HTTP Header Manager (공통 헤더)
   ┃  ┗━ HTTP Request Defaults (서버 접속 정보)
   ┣━ Once Only Controller (최초 1회 실행)
   ┃  ┗━ Login / Init Setup
   ┣━ Pause (초기 대기 시간)
   ┣━ Loop Controller (테스트 반복 구간)
   ┃  ┣━ Step 1. 과목 정보 (GET)
   ┃  ┃  ┗━ Uniform Random Timer (3s~5s)
   ┃  ┣━ Step 2. 시험 입장 (POST)
   ┃  ┃  ┗━ Uniform Random Timer (3s~5s)
   ┃  ┣━ Step 3. 시험 시작 (POST)
   ┃  ┃  ┗━ Uniform Random Timer (3s~5s)
   ┃  ┣━ Step 4. 시험 제출 (POST)
   ┃  ┃  ┗━ Uniform Random Timer (3s~5s)
   ┃  ┗━ Step 5. 재응시 (POST)
   ┗━ Listeners (결과 확인)
      ┣━ View Results Tree
      ┗━ Summary Report
```

### 6. 부하 테스트 결과 (Test Results)

### 7. 모니터링 및 병목 현상 분석 (Analysis)


---

## 🐛Bug Report Summary
⚠️**인가 검증 누락**으로 인한 **타 사용자 데이터에 대한 조회 및 삭제가 가능**한 보안 취약점 발견

| 결함 ID | 구분 | 이슈 설명 |
|---------|------|-----------|
| BUG_BOARD_01 | 보안/권한 (IDOR) | 타인 소유 게시글 삭제가 권한 검증 없이 수행됨 |
| BUG_BOARD_02 | 보안/권한 (IDOR) | 타인의 비밀글(is_secret=true) 상세 내용 조회가 권한 검증 없이 가능함 |
| BUG_CHM_01 | 개인정보 노출 | 감정 조회 API 호출 시 타인의 이메일 정보가 노출됨 |
| BUG_CHM_02 | 보안/권한 (IDOR) | 타인의 성적 및 학습 진행률이 권한 검증 없이 조회됨 |