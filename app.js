import express from 'express';
import { addJobs } from './queue.js';

const app = express();
app.use(express.json());
app.listen(3000);


app.post('/api/jobs', async (req, res) => { // 1. 요청
    const { code, input } = req.body;
    const job = await addJobs(code, input); // 2. job 생성 및 MQ에 job push

    console.log(code, input);

    res.status(202).json({ // 3. job.id 반환
        jobId: job.id,
        status: 'queued',
    });

});

// 8. jobId로 Redis 조회
// 9. 상태/결과 반환


