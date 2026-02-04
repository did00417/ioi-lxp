from .file_manager import FileManager
import os

fm = FileManager()

def get_dashboard_url(service="dashboard"):
    env = os.getenv("TEST_ENV", "base_url")
    config = fm.read_json("url.json")
    
    return config[service][env]

def get_classroom_url(service="classroom"):
    env = os.getenv("TEST_ENV", "base_url")
    config = fm.read_json("url.json")
    
    return config[service][env]

def get_rest_url(service="rest"):
    env = os.getenv("TEST_ENV", "base_url")
    config = fm.read_json("url.json")
    
    return config[service][env]