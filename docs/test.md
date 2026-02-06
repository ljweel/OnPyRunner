## 테스트해보는 법
```bash
docker compose up -d --build
docker comopose watch

pytest test_api.py -vv
or
pytest -vv
```