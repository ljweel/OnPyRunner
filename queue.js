import { Queue } from 'bullmq';
import IORedis from 'ioredis';

const jobQueue = new Queue('jobQueue');

async function addJobs(code, input) {
    return jobQueue.add('run-code', {'code': code, 'input': input});
}

const connection = new IORedis({ maxRetriesPerRequest: null });

export {jobQueue, addJobs, connection};