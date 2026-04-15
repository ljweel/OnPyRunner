FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# shared 패키지 설치
COPY shared/ /app/shared/
RUN uv pip install --system /app/shared/

# DB 패키지 설치
COPY db/ /app/db/
RUN uv pip install --system /app/db/

# API 패키지 설치
COPY api/ /app/api/
RUN uv pip install --system /app/api/

# entrypoint
COPY api/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["uvicorn", "onpyrunner_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
