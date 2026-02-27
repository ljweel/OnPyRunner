# 파이썬 격리 실행 api
온라인 파이썬 실행을 위한 파이썬 격리 실행 api 설계 프로젝트입니다.
[다음 링크](https://run.ljweel.dev)에서 파이썬을 온라인으로 실행해볼 수 있습니다.

## 목표
이 프로그램의 목표는 단순한 온라인 파이썬 실행기가 아니라, 격리 공간에서 안전하게 코드가 실행되는 시스템 설계를 목표로 합니다.

## 로컬 실행 방법
```bash
docker compose -f docker-compose.dev.yml up -d --build

http://localhost:8000/execute
http://localhost:8000/jobs/{jobId}
로 테스트 가능

```

## 현재 기능
- Python 코드 격리 실행 및 실행 시간 제한
- nginx Reverse Proxy 기반 API 노출

## 추가될 기능
- 실행 타임라인 분석 (E2E latency 분해)
- 실행 로그 시각화
- 다른 언어 지원
- 실행 결과 캐싱 전략
- 실행 서버 및 worker 구조 