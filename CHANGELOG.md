# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-02-22

### Added

- FastAPI 기반 REST API (POST /execute, GET /jobs/{job_id})
- Redis 기반 job queue (lpush/brpop) 및 result 캐시 (TTL)
- nsjail 샌드박스를 통한 Python 코드 실행
- Docker + Docker Compose 기반 컨테이너화
- Nginx 리버스 프록시
- GitHub Actions CI/CD 파이프라인
- nsjail + Docker 이중 샌드박싱 (cgroup 위임 방식)
- subprocess.Popen + ThreadPoolExecutor를 이용한 stdout/stderr 동시 스트림 읽기
- stdout/stderr 출력 크기 제한 (OUTPUT_LIMIT_EXCEEDED)
- rlimit_fsize 대신 Popen 스트림 drain 방식의 출력 제한
- JobOutcome 기반 실행 결과 분류 (SUCCESS, TIMEOUT, MLE, OLE 등)
- Makefile 기반 빌드/실행 명령어
- docker compose watch 개발 환경 (API: sync, Worker: restart)

## [1.1.0] - 2026-04-15

### Added

- docker-compose (dev/prod)에 postgres:16-alpine 서비스 추가
- API Dockerfile에 onpyrunner-db 패키지 설치 추가
- 컨테이너 시작 시 Alembic 마이그레이션 실행하는 entrypoint.sh 추가
- api, worker 서비스에 PostgreSQL 환경변수 전달
- Execution 모델 및 Alembic 마이그레이션 추가
- create_execution / update_execution 서비스 함수 구현
- API/Worker에서 각 실행 단계별 타임스탬프 및 결과 DB 기록
- DB 연동을 위해 Worker를 asyncio 기반으로 전환
- Worker Dockerfile에 db 패키지 설치 추가
- DB 통합 테스트 추가
- docker compose의 healthcheck로 db/redis 준비 완료 후 api/worker 시작 보장
- DB 연결 환경 변수를 단일 URL로 통합
