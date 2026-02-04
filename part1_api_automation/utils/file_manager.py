import json
import os

class FileManager:
    def __init__(self):
        # 현재 utils 폴더 경로
        current_dir = os.path.dirname(__file__)  # part1/utils
        
        # part1 폴더 경로
        self.part_dir = os.path.abspath(os.path.join(current_dir, ".."))  # part1 폴더 기준
        
        self.testdata_dir = os.path.join(self.part_dir, "config")
        
    def read_json(self, file_name:str):
        file_path = os.path.join(self.testdata_dir, file_name)
        try: 
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"{file_path} 파일을 찾을 수 없음")
            return None
        except json.JSONDecodeError:
            print(f"{file_path} 파일이 올바른 JSON 형식이 아님")
            return None