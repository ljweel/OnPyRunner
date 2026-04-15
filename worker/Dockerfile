# Stage 1: Build nsjail
FROM debian:bookworm AS builder

RUN apt-get update && apt-get install -y \
    flex \
    bison \
    g++ \
    gcc \
    git \
    libnl-route-3-dev \
    libprotobuf-dev \
    make \
    pkg-config \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/google/nsjail.git /nsjail && \
    cd /nsjail && \
    make

# Stage 2: Final Image
FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# nsjail 실행에 필요한 최소 런타임 라이브러리 설치
RUN apt-get update && apt-get install -y \
    libprotobuf32 \
    libnl-route-3-200 \
    && rm -rf /var/lib/apt/lists/*

# 빌드된 nsjail 바이너리 복사
COPY --from=builder /nsjail/nsjail /usr/bin/nsjail

# shared 패키지 설치
COPY shared/ /app/shared/
RUN uv pip install --system /app/shared/

# DB 패키지 설치 (추가)
COPY db/ /app/db/
RUN uv pip install --system /app/db/

# Worker 패키지 설치
COPY worker/ /app/worker/
RUN uv pip install --system /app/worker/

# cgroup 설정용 entrypoint
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["python", "-m", "onpyrunner_worker.main"]