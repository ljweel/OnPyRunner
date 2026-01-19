# Docker Command Reference

OnPyRunner 개발 및 테스트 과정에서 자주 사용하는 Docker 명령어를 정리한 문서입니다.

Docker 핵심 파일 트리
```
/
├── usr/
│   ├── bin/
│   │   └── python3           # 실제 Python 런타임
│   └── lib/
│       └── python3/          # Python 표준 라이브러리 (stdlib)
│
├── usr/local/bin/
│   └── nsjail                # sandbox 진입점 (모든 실행은 여기서 시작)
│
├── sandbox/
│   ├── input.py              # (선택) 실행할 사용자 코드
│   └── input.txt             # (선택) stdin / 파일 입력
│
├── nsjail.cfg                # nsjail 실행 정책 (mount / uid / seccomp 등)
│
└── dev/random                # random만 mount
```

---

## Build
```bash
docker build -f Dockerfile.dev -t onpyrunner:dev .
```


## Enter inside Docker

컨테이너 내부의 파일 구조, nsjail 설정, Python 실행 환경을 직접 확인할 때 사용합니다.
``` bash
docker run --rm -it \
  --privileged \
  --network none \
  onpyrunner:dev \
  /bin/bash
```
옵션 설명

- --rm : 컨테이너 종료 시 자동 삭제
- -it : 인터랙티브 터미널
- --privileged : nsjail 실행에 필요한 커널 권한
- --network none : 네트워크 완전 차단


## Run Bash in nsjail in Docker
```bash
docker run --rm -it \
  --privileged \
  --network none \
  onpyrunner:dev \
  /usr/bin/bash
```

## Run Python in nsjail in Docker
```bash
docker run --rm -i \
  --privileged \
  --network none \
  onpyrunner:dev \
  nsjail --config /nsjail.cfg -- \
  /usr/bin/python3 -c "print('Hello World')"
```



## 억지로 nsjail 내부 보는 법 (배포할 때는 절대 금지)
```
mount {
    src: "/bin"
    dst: "/bin"
    is_bind: true
    rw: false
}
```
하고 다시 빌드하고
```bash
docker run --rm -it \
  --privileged \
  --network none \
  onpyrunner:dev \
  /usr/bin/bash
```
하고
```bash
nsjail --config /nsjail.cfg -- usr/bin/python3 -c "import os; os.system('ls -al')"
```

### 주의사항


## Test

API 서버에서 Docker 컨테이너를 호출하는 로직이 정상 동작하는지 확인합니다.

```bash
npm test
```
