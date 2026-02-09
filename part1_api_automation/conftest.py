import pytest

from utils.config_loader import get_service_url, get_header, load_test_data
from api.api_client import APIClient
import logging

logger = logging.getLogger(__name__)

#--------------- 각 url 받아서 클라이언트 생성하기 ----------------

@pytest.fixture(scope="session")
def dashboard_client():
    return APIClient(get_service_url("dashboard"))

@pytest.fixture(scope="session")
def classroom_client():
    return APIClient(get_service_url("classroom"))

@pytest.fixture(scope="session")
def rest_client():
    return APIClient(get_service_url("rest"))

#------------------ <공용> 헤더 받아서 사용 --------------------------

@pytest.fixture(scope="session")
def header_data():
    return get_header()

@pytest.fixture
def valid_headers(header_data):
    return header_data["headers"]

@pytest.fixture
def invalid_headers(header_data):
    return header_data["invalid_headers"]

#------------------ <공용> logger 설정 --------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_api_client():
    logger.info("=== 전체 API 테스트 세션 시작 ===")
    yield
    logger.info("=== 전체 API 테스트 세션 종료 ===")

#--------------------- 각자 사용할 테스트 데이터 받기 ------------------------

@pytest.fixture(scope="session")
def test_board_data():
    return load_test_data("board")

@pytest.fixture(scope="session")
def test_dash_data():
    return load_test_data("dash")

@pytest.fixture(scope="session")
def test_classhome_data():
    return load_test_data("classhome")

@pytest.fixture(scope="session")
def test_subject_data():
    return load_test_data("subject")

#-------------- <수진> 간편하게 사용할 학습 대시보드 메뉴 데이터 -----------------------

@pytest.fixture(scope="session")
def dash_params(test_dash_data):
    return test_dash_data["params"]

@pytest.fixture(scope="session")
def dash_page(test_dash_data):
    return test_dash_data["page"]

#-------------------- <유진> 게시판 메뉴 데이터 ------------------------------

@pytest.fixture(scope="session")
def board_id(test_board_data):
    return test_board_data["params"]["board_id"]

@pytest.fixture(scope="session")
def classroom_id(test_board_data):
    return test_board_data["params"]["classroom_id"]

@pytest.fixture(scope="session")
def create_article_data(test_board_data):
    return test_board_data["articles"]["create_article"]

#-------------- <정은> 클래스 홈 사용 데이터 -----------------------
@pytest.fixture
def classhome_params(test_classhome_data):
    return test_classhome_data["params"]

@pytest.fixture(scope="session")
def schedule_common(test_classhome_data):
    return test_classhome_data["schedule_common_data"]

@pytest.fixture(scope="session")
def schedule_cases(test_classhome_data):
    return test_classhome_data["schedule_cases_data"]
#-------------------- <효진> 학습 과목 데이터 ------------------------------

@pytest.fixture(scope="session")
def subject_params(test_subject_data):
    return test_subject_data["params"]

#-------------------- <동빈> 학습 과목 데이터 ------------------------------
@pytest.fixture(scope="session")
def test_schedule_data():
    return load_test_data("schedule")
@pytest.fixture(scope="session")
def schedule_params(test_schedule_data):
    return test_schedule_data["params"]

@pytest.fixture(scope="session")
def weekly_case(test_schedule_data):
    return test_schedule_data["cases"]["weekly"]