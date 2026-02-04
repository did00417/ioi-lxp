import pytest
import os
from dotenv import load_dotenv

from utils.file_manager import FileManager
from utils.config_loader import get_dashboard_url, get_classroom_url, get_rest_url
from api.api_client import APIClient

load_dotenv()

# url 받기
@pytest.fixture(scope="session")
def dashboard_url():
    return get_dashboard_url()

@pytest.fixture(scope="session")
def classroom_url():
    return get_classroom_url()

@pytest.fixture(scope="session")
def rest_url():
    return get_rest_url()

# 각 url마다 api client 생성 -> GET/POST/DELETE 등 편하게 사용 가능
@pytest.fixture(scope="session")
def dashboard_client(dashboard_url):
    return APIClient(dashboard_url)

@pytest.fixture(scope="session")
def classroom_client(classroom_url):
    return APIClient(classroom_url)

@pytest.fixture(scope="session")
def rest_client(rest_url):
    return APIClient(rest_url)

# 헤더, 쿼리 파라미터 env에서 가져오기
@pytest.fixture(scope="session")
def test_data():
    fm = FileManager()
    data = fm.read_json("test_data.json")
    
    # 토큰, 학생 아이디, org-name 플레이스홀더 교체
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
def valid_headers(test_data):
    return test_data["headers"]

@pytest.fixture(scope="session") # 만료된 토큰 사용한 헤더 -> 비정상 테스트용
def invalid_headers(test_data):
    return test_data["invalid_headers"]

@pytest.fixture(scope="session")
def params(test_data):
    return test_data["params"]