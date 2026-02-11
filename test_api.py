import requests
import time
from textwrap import dedent

DEBUG = False

class APITestHelper:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def post_execute(self, json):
        response = requests.post(f"{self.base_url}/execute", json=json)
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        return job_id
    
    def get_job_result(self, job_id, max_wait=5):

        for _ in range(max_wait*10):
            response = requests.get(f"{self.base_url}/jobs/{job_id}")
            result = response.json()
            if result["status"] in ["COMPLETED", "FAILED"]:
                return result
            time.sleep(0.1)
        raise TimeoutError(f"Job {job_id} did not complete in time")

    # 모든 테스트의 공통 전제조건 검증증
    def assert_base_conditions(self, json):
        job_id = self.post_execute(json)
        result = self.get_job_result(job_id)
        assert result["status"] == "COMPLETED"
        return result

    # 성공 검증증
    def assert_success(self, json):
        result = self.assert_base_conditions(json)
        print(result)
        assert result["result"]["outcome"] == "SUCCESS"
        assert result["result"]["exit_code"] == 0
    
    # 런타임 에러 검증증
    def assert_runtime_error(self, json):
        result = self.assert_base_conditions(json)
        print(result)
        assert result["result"]["outcome"] == "RUNTIME_ERROR"
        assert result["result"]["exit_code"] != 0
    
    # 시간 초과 검증증
    def assert_timeout(self, json):
        result = self.assert_base_conditions(json)
        print(result)
        assert result["result"]["outcome"] == "TIME_LIMIT_EXCEEDED"
        assert result["result"]["exit_code"] != 0
    


BASE_URL = "http://localhost:8000"
helper = APITestHelper(BASE_URL)

def test_addition():
    # Hello World 출력 검증
    helper.assert_success(
        json={
            "language": "python",
            "source_code": "a, b = map(int, input().split()); print(a + b)",
            "stdin": "1 2",
        }
    )

def test_division_by_zero():
    # 0으로 나누기 에러 검증
    helper.assert_runtime_error(
        json={
            "language": "python",
            "source_code": "print(1/0)",
        }
    )

def test_network_isolated():
    # 네트워크 격리 검증
    helper.assert_runtime_error(
        json={
            "language": "python",
            "source_code": dedent("""
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("8.8.8.8", 53))
            """),
        }
    )




# def test_timeout_cpu_time():
#     # CPU 사용 시간 초과 검증
#     helper.assert_timeout(
#         json={
#             "language": "python",
#             "source_code": "while True: pass",
#         }
#     )



def test_memory_limit_exceeded():
    # 메모리 초과 검증
    helper.assert_runtime_error(
        json={
            "language": "python",
            "source_code": "a = [1] * 1000000000; print(a)",
        }
    )

def test_file_system_isolated():
    # 파일 시스템 격리 검증
    helper.assert_runtime_error(
        json={
            "language": "python",
            "source_code": "open('test.txt', 'w').write('test')",
        }
    )

def test_block_proc():
    # 프로세스 생성 제한 검증
    helper.assert_runtime_error(
        json={
            "language": "python",
            "source_code": dedent("""
            import os
            while 1: os.fork()"""),
        }
    )

def test_tmp():
    1
