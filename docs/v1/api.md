
# Base URL

'''
/api/v1
'''

# Endpoint

## 공통 규칙
- response는 항상 job_id와 status를 가지고 있음. 

## POST /execute

실행 작업을 제출

Submit a new execution job

### request
```json
{
    "language": "python",
    "source_code": "print('Hello, World!')",
    "stdin": "",
    "limits": {
        "cpu_time_ms": 3000,
        "memory_mb": 128
    }
}
```

### response
항상 status:PENDING을 반환환
```json
{
    "job_id": "...",
    "status": "PENDING"
}
```


## GET /jobs/{job_id}


### Response (PENDING or RUNNING)
```json
{
    "job_id": "...",
    "status": "PENDING" | "RUNNING"
}
```

### Response (COMPLETED)

```json
{
    "job_id": "...",
    "status": "COMPLETED",
    "result": {
        "outcome": "SUCCESS",
        "stdout": "hello world\n",
        "stderr": "",
        "exit_code": 0,
        "usage_info": {
            "cpu_time_ms": 32,
            "wall_time_ms": 45,
        }
    }
}
```

### Response (FAILED)

```json 
{
    "job_id": "...",
    "status": "FAILED",
    "reason": "System Error"
}
```