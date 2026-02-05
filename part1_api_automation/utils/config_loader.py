from .file_manager import FileManager
import os
import copy
from dotenv import load_dotenv

fm = FileManager()
load_dotenv()

# config 폴더의 url 불러오는 함수
def get_service_url(service: str):
    env = os.getenv("TEST_ENV", "base_url")
    config = fm.read_json("url.json")
    return config[service][env]

# 헤더 불러오는 함수
def get_header():
    raw = fm.read_json("header_data.json")
    data = copy.deepcopy(raw)
    
    # 토큰 플레이스홀더 교체
    data["headers"]["Authorization"] = data["headers"]["Authorization"].format(
        ELICE_VALID_TOKEN=os.getenv("ELICE_VALID_TOKEN")
    )
    data["invalid_headers"]["Authorization"] = data["invalid_headers"]["Authorization"].format(
        ELICE_INVALID_TOKEN=os.getenv("ELICE_INVALID_TOKEN")
    )
    
    return data

# 각자 파라미터 불러오는 함수
def load_test_data(domain: str):
    """
    domain 예:
    - "board" → test_board_data.json
    - "dash"  → test_dash_data.json
    """
    file_name = f"test_{domain}_data.json"
    raw = fm.read_json(file_name)

    if raw is None:
        raise FileNotFoundError(f"{file_name} 파일을 찾을 수 없습니다")

    data = copy.deepcopy(raw)

    # 플레이스홀더 치환
    if "params" in data:
        for key, value in data["params"].items():
            if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                env_key = value.strip("{}")
                env_value = os.getenv(env_key)
                if not env_value:
                    raise RuntimeError(f"환경변수 {env_key} 가 설정되지 않았습니다")
                data["params"][key] = env_value

    return data