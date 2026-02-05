import pytest
import os
from dotenv import load_dotenv

from utils.file_manager import FileManager
from utils.config_loader import get_service_url, get_header, load_test_data
from api.api_client import APIClient


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

#--------------------- 각자 사용할 테스트 데이터 받기 ------------------------

@pytest.fixture(scope="session")
def test_board_data():
    return load_test_data("board")

@pytest.fixture(scope="session")
def test_dash_data():
    return load_test_data("dash")

@pytest.fixture(scope="session")
def test_subject_data():
    return load_test_data("subject")

#-------------- <수진> 간편하게 사용할 학습 대시보드 메뉴 데이터 -----------------------

@pytest.fixture
def dash_params(test_dash_data):
    return test_dash_data["params"]

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

#-------------------- <효진> 학습 과목 데이터 ------------------------------

@pytest.fixture(scope="session")
def subject_params(test_subject_data):
    return test_subject_data["params"]