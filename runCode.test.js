const { runCode } = require('./runCode');

describe('OnPyRunner Execution Baseline', () => {
    
    test('정상적인 출력값을 반환하는가?', () => {
        const code = 'print("Hello World")';
        const result = runCode({ code });

        expect(result.exitCode).toBe(0);
        expect(result.stdout.trim()).toBe('Hello World');
    });

    test('표준 입력(stdin)을 정상적으로 처리하는가?', () => {
        const code = 'name = input(); print(f"Hi, {name}")';
        const input = 'leejw';
        const result = runCode({ code, input });

        expect(result.stdout.trim()).toBe('Hi, leejw');
    });

    test('런타임 에러 발생 시 stderr를 포착하는가?', () => {
        const code = 'print(1 / 0)';
        const result = runCode({ code });

        expect(result.exitCode).not.toBe(0);
        expect(result.stderr).toContain('ZeroDivisionError');
    });
});