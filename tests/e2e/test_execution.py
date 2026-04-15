import os
import time
from textwrap import dedent

import pytest
import requests
from dotenv import load_dotenv
from onpyrunner_db.models import Execution
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker


class E2ETestHelper:
    def __init__(self, base_url, db_url):
        self.base_url = base_url
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        self.test_session = sessionmaker(bind=self.engine)

    def post_execute(self, json):
        response = requests.post(f"{self.base_url}/execute", json=json)
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        return job_id

    def get_job_result(self, job_id, max_wait=5):
        for _ in range(max_wait * 10):
            response = requests.get(f"{self.base_url}/jobs/{job_id}")
            result = response.json()
            if result["status"] in ["COMPLETED", "FAILED"]:
                return result
            time.sleep(0.1)
        raise TimeoutError(f"Job {job_id} did not complete in time")

    def get_execution_from_db(self, job_id) -> Execution | None:
        with self.test_session() as db:
            result = db.execute(select(Execution).where(Execution.job_id == job_id))
            return result.scalar_one_or_none()

    # 모든 테스트의 공통 전제조건 검증
    def assert_base_conditions(self, json):
        job_id = self.post_execute(json)
        result = self.get_job_result(job_id)
        assert result["status"] == "COMPLETED"
        return result

    # 성공 검증
    def assert_success(self, json):
        result = self.assert_base_conditions(json)
        print(result)
        assert result["result"]["outcome"] == "SUCCESS"
        assert result["result"]["exit_code"] == 0

    # 런타임 에러 검증
    def assert_runtime_error(self, json):
        result = self.assert_base_conditions(json)
        print(result)
        assert result["result"]["outcome"] == "RUNTIME_ERROR"
        assert result["result"]["exit_code"] != 0

    # 시간 초과 검증
    def assert_time_limit_exceeded(self, json):
        result = self.assert_base_conditions(json)
        print(result)
        assert result["result"]["outcome"] == "TIME_LIMIT_EXCEEDED"
        assert result["result"]["exit_code"] != 0

    # 메모리 초과 검증
    def assert_memory_limit_exceeded(self, json):
        result = self.assert_base_conditions(json)
        print(result)
        assert result["result"]["outcome"] == "MEMORY_LIMIT_EXCEEDED"
        assert result["result"]["exit_code"] != 0

    # 표준 출력 초과 검증
    def assert_stdout_limit_exceeded(self, json):
        result = self.assert_base_conditions(json)
        print(result)
        assert result["result"]["outcome"] == "STDOUT_LIMIT_EXCEEDED"
        assert result["result"]["exit_code"] != 0

    # 표준 에러 초과 검증
    def assert_stderr_limit_exceeded(self, json):
        result = self.assert_base_conditions(json)
        print(result)
        assert result["result"]["outcome"] == "STDERR_LIMIT_EXCEEDED"
        assert result["result"]["exit_code"] != 0


BASE_URL = "http://localhost:8000"

load_dotenv()

DB_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@localhost:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB_NAME')}"
)
helper = E2ETestHelper(BASE_URL, DB_URL)


def test_addition():
    # a + b 검증
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


@pytest.mark.slow
def test_timeout_cpu_time():
    # CPU 사용 시간 초과 검증
    # nsjail time limit: 3초 (wall_time / cpu_time)
    helper.assert_time_limit_exceeded(
        json={
            "language": "python",
            "source_code": "while True: pass",
        }
    )


@pytest.mark.slow
def test_timeout_wall_time():
    # 전체 실행 시간 초과 검증
    # nsjail time limit: 3초 (wall_time / cpu_time)
    helper.assert_time_limit_exceeded(
        json={
            "language": "python",
            "source_code": dedent("""
            import time
            time.sleep(10)
            """),
        }
    )


def test_memory_limit_exceeded():
    # 메모리 초과 검증
    helper.assert_memory_limit_exceeded(
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
            while 1: os.fork()
            """),
        }
    )


def test_block_thread():
    helper.assert_runtime_error(
        json={
            "language": "python",
            "source_code": dedent("""
            import threading
            def worker():
                while True:
                    pass
            t = threading.Thread(target=worker)
            t.start()
            """),
        }
    )


def test_stdout_limit_exceeded():
    # 표준 출력 제한 검증
    helper.assert_stdout_limit_exceeded(
        json={
            "language": "python",
            "source_code": dedent("""
            while True:
                print("A" * 1000)
            """),
        }
    )


def test_stderr_limit_exceeded():
    # 표준 에러 제한 검증
    helper.assert_stderr_limit_exceeded(
        json={
            "language": "python",
            "source_code": dedent("""
            import sys
            while True:
                print("A" * 1000, file=sys.stderr)
            """),
        }
    )


"""
DB 연동 검증 test case
"""


def test_execution_row_created():
    """POST /execute 후 DB에 execution row가 생기는지"""
    job_id = helper.post_execute(
        {
            "language": "python",
            "source_code": "a, b = map(int, input().split()); print(a + b)",
            "stdin": "1 2",
        }
    )

    helper.get_job_result(job_id)
    execution = helper.get_execution_from_db(job_id)

    assert execution is not None
    assert execution.status in ["PENDING", "COMPLETED"]
    assert execution.source_code == "a, b = map(int, input().split()); print(a + b)"
    assert execution.language == "python"
    assert execution.stdin == "1 2"


def test_completed_row_updated():
    """Worker 처리 후 DB에 결과와 타임스탬프가 채워지는지"""
    job_id = helper.post_execute(
        {
            "language": "python",
            "source_code": "a, b = map(int, input().split()); print(a + b)",
            "stdin": "1 2",
        }
    )
    helper.get_job_result(job_id)

    execution = helper.get_execution_from_db(job_id)

    assert execution is not None
    assert execution.status == "COMPLETED"

    # 6개 타임스탬프 전부 채워졌는지
    assert execution.api_received_at is not None
    assert execution.queue_entered_at is not None
    assert execution.worker_picked_at is not None
    assert execution.execution_started_at is not None
    assert execution.execution_finished_at is not None
    assert execution.result_stored_at is not None

    # 타임스탬프 순서가 맞는지
    assert execution.api_received_at <= execution.queue_entered_at
    assert execution.queue_entered_at <= execution.worker_picked_at
    assert execution.worker_picked_at <= execution.execution_started_at
    assert execution.execution_started_at <= execution.execution_finished_at
    assert execution.execution_finished_at <= execution.result_stored_at

    # 실행 결과
    assert execution.stdout is not None and execution.stdout.strip() == "3"
    assert execution.exit_code == 0


@pytest.mark.skip(reason="시스템 실패 시나리오 구현 필요")
def test_failed_row_updated():
    """시스템 에러 시 FAILED 상태와 사유가 기록되는지"""
    # 이건 시스템 에러를 유발해야 하는데,
    # 현재 구조에서는 시스템 자체가 실패해야 FAILED가 되니까
    # 필요하면 나중에 추가
    pass


def test_timestamp_order_on_slow_execution():
    """실행 시간이 긴 job에서 구간별 타임스탬프 차이가 유의미한지"""
    job_id = helper.post_execute(
        {
            "language": "python",
            "source_code": "import time; time.sleep(2); print('done')",
        }
    )
    helper.get_job_result(job_id, max_wait=10)

    execution = helper.get_execution_from_db(job_id)

    assert execution is not None
    assert execution.execution_started_at is not None
    assert execution.execution_finished_at is not None

    # 실행 구간이 최소 1초 이상
    diff = (
        execution.execution_finished_at - execution.execution_started_at
    ).total_seconds()
    assert diff >= 1.0
