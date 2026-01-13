import express from 'express';

const app = express();
app.use(express.json());
app.listen(3000);

app.post('/api/run', async (req, res) => {
    const { code, input } = req.body;
    
    // TODO: Python 코드 실행 로직 구현
    // 1. Sandbox 생성
    // 2. 코드 실행
    // 3. 결과 반환
    
    res.json({
        stdout: '',
        stderr: '',
        exitCode: 0,
    });
});


