# Setup Guide

다른 환경에서 처음부터 실행하기 위한 가이드.

## 사전 요구사항

- Docker, Docker Compose
- (로컬 개발 시) Python 3.13, pip

## 프로젝트 구조

```
OnPyRunner/
├── shared/          # 공유 도메인 패키지 (models, logger)
├── api/             # FastAPI 서비스
├── worker/          # Worker 서비스 (nsjail 샌드박스)
├── tests/           # 테스트
├── docker-compose.yml
├── docker-compose.dev.yml
└── entrypoint.sh
```

## Docker 네트워크 생성 (최초 1회)

```bash
docker network create ljweel-dev-network
```

## 프로덕션 실행

```bash
docker compose up -d --build
```

## 개발 환경 실행

```bash
# 빌드 & 실행
docker compose -f docker-compose.dev.yml up -d --build

# 파일 변경 감지 (코드 수정 시 자동 재빌드)
docker compose -f docker-compose.dev.yml watch
```

## Worker 스케일링

```bash
docker compose up -d --scale worker=N
```

## 로컬 개발 (venv)

Docker 없이 로컬에서 패키지를 설치하고 싶을 때:

```bash
python3.13 -m venv .venv313
source .venv313/bin/activate

pip install -e shared/
pip install -e api/
pip install -e worker/
```

## 테스트

Docker 환경이 실행 중인 상태에서:

```bash
# 빠른 테스트 (TLE 검증 제외)
pytest tests/ -m "not slow"

# 전체 테스트
pytest tests/
```

## import 확인 (설치 검증)

```bash
python -c "from onpyrunner_shared.models import ExecuteRequest; print('shared OK')"
python -c "from onpyrunner_api.app import app; print('api OK')"
python -c "from onpyrunner_worker.analyzer import ResultAnalyzer; print('worker OK')"
```
