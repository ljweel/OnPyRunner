import requests
import time
from textwrap import dedent


class APIValidationHelper:
    def __init__(self, base_url):
        self.base_url = base_url

    def post(self, json):
        return requests.post(f"{self.base_url}/execute", json=json)
    

BASE_URL = "http://localhost:8000"
helper = APIValidationHelper(BASE_URL)

MAX_LENGTH = 100000 + 1  # 10KB + 1 byte

def test_source_code_size_limit():
    # 10KB 초과 소스 코드 검증
    source_code = f"print('{ 'A' * MAX_LENGTH}')"  # 10KB 이상의 소스 코드
    response = helper.post({
        "language": "python",
        "source_code": source_code,
        "stdin": ""
    })
    assert response.status_code == 422
    assert "source code exceeds 10KB." in response.text

def test_stdin_size_limit():
    # 10KB 초과 stdin 검증
    stdin = "A" * MAX_LENGTH  # 10KB 이상의 stdin
    response = helper.post({
        "language": "python",
        "source_code": "print(input())",
        "stdin": stdin,
    })
    assert response.status_code == 422
    assert "stdin exceeds 10KB." in response.text

def test_valid_request():
    # 유효한 요청 검증
    response = helper.post({
        "language": "python",
        "source_code": "print('Hello, World!')",
        "stdin": ""
    })
    assert response.status_code == 200
    assert "job_id" in response.json()

