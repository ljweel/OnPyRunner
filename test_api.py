import requests
import time

class APITestHelper:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def post_execute(self, json):
        response = requests.post(f"{self.base_url}/execute", json=json)
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        return job_id
    
    def get_job_result(self, job_id, max_wait=5):
        for _ in range(max_wait):
            response = requests.get(f"{self.base_url}/jobs/{job_id}")
            result = response.json()
            if result["status"] in ["COMPLETED", "FAILED"]:
                return result
            time.sleep(1)
        raise TimeoutError(f"Job {job_id} did not complete in time")

    # 모든 테스트의 공통 전제조건 검증증
    def assert_base_conditions(self, json):
        job_id = self.post_execute(json)
        result = self.get_job_result(job_id)
        assert result["status"] == "COMPLETED"
        assert "[E]" not in result["result"]["stderr"]
        return result

    # 성공 검증증
    def assert_success(self, json):
        result = self.assert_base_conditions(json)
        assert result["result"]["outcome"] == "SUCCESS"
        assert result["result"]["exit_code"] == 0
    
    # 런타임 에러 검증증
    def assert_runtime_error(self, json):
        result = self.assert_base_conditions(json)
        assert result["result"]["outcome"] == "RUNTIME_ERROR"
        assert result["result"]["exit_code"] != 0
    
    # 시간 초과 검증증
    def assert_timeout(self, json):
        result = self.assert_base_conditions(json)
        assert result["result"]["outcome"] == "TIMEOUT"
        assert result["result"]["exit_code"] != 0
    
    # 메모리 초과 검증
    def assert_memory_limit_exceeded(self, json):
        result = self.assert_base_conditions(json)
        assert result["result"]["outcome"] == "MEMORY_LIMIT_EXCEEDED"
        assert result["result"]["exit_code"] != 0
    
    # 파일 초과 검증
    def assert_file_limit_exceeded(self, json):
        result = self.assert_base_conditions(json)
        assert result["result"]["outcome"] == "FILE_LIMIT_EXCEEDED"
        assert result["result"]["exit_code"] != 0


BASE_URL = "http://localhost:8000"
helper = APITestHelper(BASE_URL)

def test_addition():
    """Hello World 출력"""
    helper.assert_success(
        json={
            "language": "python",
            "source_code": "a, b = map(int, input().split()); print(a + b)",
            "stdin": "1 2",
        }
    )

def test_division_by_zero():
    """0으로 나누기 에러"""
    helper.assert_runtime_error(
        json={
            "language": "python",
            "source_code": "print(1/0)",
        }
    )

def test_timeout():
    """타임아웃"""
    helper.assert_timeout(
        json={
            "language": "python",
            "source_code": "import time; time.sleep(10)",
        }
    )