from .json_reader import JsonReader
import os
import copy
from dotenv import load_dotenv

# config 폴더의 url 불러오는 함수
def get_service_url(service: str):
    load_dotenv()
    jr = JsonReader()
    
    env = os.getenv("TEST_ENV", "base_url")
    config = jr.read_json("url.json")

    try:
        return config[service][env]
    except KeyError as e:
        raise KeyError(
            f"[CONFIG ERROR] url.json에 service='{service}', env='{env}' 설정이 없습니다"
        ) from e

# 헤더 불러오는 함수
def get_header():
    load_dotenv()
    jr = JsonReader()
    
    raw = jr.read_json("header_data.json")
    data = copy.deepcopy(raw)
    
    valid_token = os.getenv("ELICE_VALID_TOKEN")
    invalid_token = os.getenv("ELICE_INVALID_TOKEN")
    hyojin_token = os.getenv("HYOJIN_VALID_TOKEN")

    if not valid_token or not invalid_token:
        raise RuntimeError("[CONFIG ERROR] ELICE 토큰 환경변수가 설정되지 않았습니다")

    # 피드백 반영: ${...} 패턴에 맞추기 위해 .format() 대신 .replace() 사용
    data["headers"]["Authorization"] = data["headers"]["Authorization"].replace(
        "${ELICE_VALID_TOKEN}", valid_token
    )
    data["invalid_headers"]["Authorization"] = data["invalid_headers"]["Authorization"].replace(
        "${ELICE_INVALID_TOKEN}", invalid_token
    )
    data["hyojin_headers"]["Authorization"] = data["hyojin_headers"]["Authorization"].replace(
        "${HYOJIN_VALID_TOKEN}", hyojin_token
    )

    return data

# 각자 파라미터 불러오는 함수
def load_test_data(domain: str):
    """
    domain 예:
    - "board" → test_board_data.json
    - "dash"  → test_dash_data.json
    """
    load_dotenv()
    jr = JsonReader()
    
    file_name = f"test_{domain}_data.json"
    raw = jr.read_json(file_name)
    data = copy.deepcopy(raw)

    # 플레이스홀더 치환 - 피드백 반영: {env_key} 대신 ${env_key} 형식으로 변경
    if "params" in data:
        for key, value in data["params"].items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_key = value[2:-1]  # '${' 와 '}' 를 잘라내고 순수 키값만 추출
                env_value = os.getenv(env_key)
                if not env_value:
                    raise RuntimeError(f"환경변수 {env_key} 가 설정되지 않았습니다")
                data["params"][key] = env_value

    return data
