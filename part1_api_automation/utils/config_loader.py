from .file_manager import FileManager
import os

fm = FileManager()

# config 폴더의 url 불러오는 함수
def get_service_url(service: str):
    env = os.getenv("TEST_ENV", "base_url")
    config = fm.read_json("url.json")
    return config[service][env]