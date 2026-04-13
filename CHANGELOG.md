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