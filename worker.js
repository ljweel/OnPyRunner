import { Worker } from 'bullmq';
import { connection } from './queue.js';

const worker = new Worker(
    'jobQueue',
    async (job) => { // 4. MQ에서 job pop
        const { code, input } = job.data;

        console.log('job popped:', job.id);
        console.log('job.data:', job.data);
        // 5. Python 실행 (격리)
        // 6. stdout / stderr 반환
        // 7. 결과 Redis 저장
    },
    { connection },
);