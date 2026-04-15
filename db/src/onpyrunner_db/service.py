# onpyrunner_db/service.py

from sqlalchemy import inspect, select

from onpyrunner_db.database import AsyncSessionLocal
from onpyrunner_db.models import Execution

valid_columns = {attr.key for attr in inspect(Execution).mapper.column_attrs}
protected_columns = {"id"}


async def create_execution(
    job_id: str,
    language: str,
    source_code: str,
    stdin: str = "",
) -> None:
    async with AsyncSessionLocal() as db:
        execution = Execution(
            job_id=job_id,
            language=language,
            source_code=source_code,
            stdin=stdin,
            status="PENDING",
        )
        db.add(execution)
        await db.commit()


async def update_execution(job_id: str, **kwargs) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Execution).where(Execution.job_id == job_id))
        execution = result.scalar_one_or_none()
        if execution is None:
            raise ValueError(f"Execution not found for job_id={job_id}")

        for key, value in kwargs.items():
            if key not in valid_columns:
                raise ValueError(f"Invalid column name: '{key}'")
            if key in protected_columns:
                raise ValueError(f"Column '{key}' is protected and cannot be updated.")

            setattr(execution, key, value)

        await db.commit()
