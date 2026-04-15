from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # 타임스탬프 (구간 측정용)
    api_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    queue_entered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    worker_picked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    execution_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    execution_finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    result_stored_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # 요청 정보
    language: Mapped[str] = mapped_column(String, nullable=False)
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    stdin: Mapped[str] = mapped_column(Text, default="")

    # 실행 결과
    status: Mapped[str] = mapped_column(String, nullable=False)
    outcome: Mapped[str | None] = mapped_column(String)
    stdout: Mapped[str | None] = mapped_column(Text)
    stderr: Mapped[str | None] = mapped_column(Text)
    exit_code: Mapped[int | None] = mapped_column(Integer)
    cpu_time_ms: Mapped[int | None] = mapped_column(Integer)
    wall_time_ms: Mapped[int | None] = mapped_column(Integer)

    # 실패 시
    fail_reason: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
