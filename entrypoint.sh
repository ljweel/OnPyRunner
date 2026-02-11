#!/bin/bash
set -e

echo "[INFO] Starting cgroup v2 initialization..."

# 1. cgroup v2 마운트 확인 및 권한 확보
# 컨테이너 내부의 cgroup이 read-only인 경우를 대비해 rw로 리마운트 시도
mount -o remount,rw /sys/fs/cgroup 2>/dev/null || true

# 2. 프로세스들이 이동할 'init' 그룹 생성
mkdir -p /sys/fs/cgroup/init

# 3. 루트 cgroup에 있는 모든 프로세스를 'init' 그룹으로 이동
# 현재 쉘($$)을 포함하여 루트에 있는 모든 PID를 옮겨야 루트의 subtree_control 수정 가능
# 'Device or resource busy' 에러를 방지하는 핵심 단계입니다.
for pid in $(cat /sys/fs/cgroup/cgroup.procs); do
    # 이동 시도 (종료된 프로세스나 커널 스레드는 실패할 수 있으므로 에러 무시)
    echo "$pid" > /sys/fs/cgroup/init/cgroup.procs 2>/dev/null || true
done

echo "[INFO] All processes moved to /sys/fs/cgroup/init"

# 4. 루트 cgroup에서 사용 가능한 모든 컨트롤러를 하위로 개방
# nsjail이 하위에서 memory, cpu, pids 제한을 걸 수 있게 허용합니다.
if [ -f /sys/fs/cgroup/cgroup.controllers ]; then
    for controller in $(cat /sys/fs/cgroup/cgroup.controllers); do
        echo "+$controller" > /sys/fs/cgroup/cgroup.subtree_control 2>/dev/null \
            && echo "[INFO] Enabled controller: $controller" \
            || echo "[WARN] Failed to enable controller: $controller"
    done
fi


mkdir -p /sys/fs/cgroup/nsjail
echo "+memory +cpu +pids" > /sys/fs/cgroup/nsjail/cgroup.subtree_control

echo "[INFO] cgroup v2 setup complete. Starting Worker..."
# 5. 원래 실행하려던 명령어 실행 (예: python worker.py)
# exec를 사용하여 PID 1번을 교체합니다.
exec "$@"


