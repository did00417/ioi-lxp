import json
import os

class JsonReader:
    def __init__(self):
        # 현재 utils 폴더 경로
        current_dir = os.path.dirname(__file__)  # part1/utils
        
        # part1 폴더 경로
        self.part_dir = os.path.abspath(os.path.join(current_dir, ".."))  # part1 폴더 기준
        
        # config 폴더
        self.testdata_dir = os.path.join(self.part_dir, "config")
        
    def read_json(self, file_name: str):
        file_path = os.path.join(self.testdata_dir, file_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"[CONFIG ERROR] 파일을 찾을 수 없습니다: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except json.JSONDecodeError as e:
            raise ValueError(
                f"[CONFIG ERROR] JSON 형식이 올바르지 않습니다: {file_path}"
            ) from e