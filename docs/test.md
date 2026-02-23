## 로컬에서 테스트해보는 법
```bash
docker compose -f docker-compose.dev.yml up -d --build
docker comopose -f docker-compose.dev.yml watch

pytest -vv
```

## worker N개
```bash
docker compose up -d --scale worker=N
```