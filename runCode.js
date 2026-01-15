const { spawnSync } = require('child_process');

/**
 * Python 코드를 실행하고 결과를 반환하는 함수
 * @param {string} code - Python 코드
 * @param {string} input - 입력
 * @returns {JSON} - { stdout: string, stderr: string, exitCode: number }
 */
function runCode({code, input}) {
    const sudoPath = '/usr/bin/sudo'; // which sudo 쳐서 나오는 결과
    const nsjailPath = '/usr/local/bin/nsjail'; // which nsjail 쳐서 나오는 결과
    const pythonPath = '/usr/bin/python3.14'; // which python3.14 쳐서 나오는 결과


    const nsjailArgs = [
        nsjailPath,
        '-Mo', // 1번 실행 후 종료
        '--chroot', '/',
        '--user', '65534', // nobody 계정
        '--', // 이 뒤는 실행 커맨드드
        pythonPath,
        '-c', code,
    ];
    try {
        const result = spawnSync(sudoPath, nsjailArgs, {
            input: input,
            encoding: 'utf-8',
            shell: false
        });
        
        if (result.error) {
            return { stdout: '', stderr: result.error.message, exitCode: -1 };
        }

        return {
            stdout: result.stdout || '',
            stderr: result.stderr || '',
            exitCode: result.status
        };
    } catch (e) {
        return { stdout: '', stderr: e.message, exitCode: -1 };
    }

}

module.exports = { runCode };