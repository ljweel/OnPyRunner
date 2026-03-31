## 로컬에서 테스트해보는 법
```bash
docker compose -f docker-compose.dev.yml up -d --build
docker compose -f docker-compose.dev.yml watch

pytest tests/ -m "not slow"  # slow test(TLE 검증 test) 제외
pytest tests/                 # 전부 실행
```

## Worker N개
```bash
docker compose up -d --scale worker=N
```
