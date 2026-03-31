FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# shared 패키지 설치
COPY shared/ /app/shared/
RUN uv pip install --system /app/shared/

# API 패키지 설치
COPY api/ /app/api/
RUN uv pip install --system /app/api/

EXPOSE 8000

CMD ["uvicorn", "onpyrunner_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
