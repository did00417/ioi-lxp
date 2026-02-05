import pytest
import os
from dotenv import load_dotenv

from utils.file_manager import FileManager
from utils.config_loader import get_service_url
from api.api_client import APIClient

load_dotenv()

# 각 url 받아서 클라이언트 생성하기
@pytest.fixture(scope="session")
def dashboard_client():
    return APIClient(get_service_url("dashboard"))

@pytest.fixture(scope="session")
def classroom_client():
    return APIClient(get_service_url("classroom"))

@pytest.fixture(scope="session")
def rest_client():
    return APIClient(get_service_url("rest"))

# 헤더, 쿼리 파라미터 env에서 가져오기
@pytest.fixture(scope="session")
def test_data():
    fm = FileManager()
    data = fm.read_json("test_data.json")
    
    # 토큰, 학생 아이디 플레이스홀더 교체
    data["headers"]["Authorization"] = data["headers"]["Authorization"].format(
        ELICE_VALID_TOKEN=os.getenv("ELICE_VALID_TOKEN")
    )
    data["invalid_headers"]["Authorization"] = data["invalid_headers"]["Authorization"].format(
        ELICE_INVALID_TOKEN=os.getenv("ELICE_INVALID_TOKEN")
    )

    data["params"]["student_id"] = data["params"]["student_id"].format(
        STUDENT_ID=os.getenv("STUDENT_ID")
    )
    
    return data
@pytest.fixture(scope="session")
def file_manager():
    return FileManager()
@pytest.fixture(scope="session")
def valid_headers(test_data):
    return test_data["headers"]

@pytest.fixture(scope="session") # 만료된 토큰 사용한 헤더 -> 비정상 테스트용
def invalid_headers(test_data):
    return test_data["invalid_headers"]

@pytest.fixture(scope="session")
def test_board_data(file_manager):
    return file_manager.read_json("test_board_data.json")

@pytest.fixture(scope="session")
def board_id(test_board_data):
    return test_board_data["params"]["board_id"]

@pytest.fixture(scope="session")
def classroom_id(test_board_data):
    return test_board_data["params"]["classroom_id"]

@pytest.fixture(scope="session")
def create_article_data(test_board_data):
    return test_board_data["articles"]["create_article"]