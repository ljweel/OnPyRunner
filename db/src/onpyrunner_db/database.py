import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


def get_database_url() -> str:
    load_dotenv()
    url = os.getenv("POSTGRES_URL")
    if url is None:
        raise ValueError("POSTGRES_URL 환경 변수가 설정되지 않았습니다.")
    return url


DATABASE_URL = get_database_url()

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
