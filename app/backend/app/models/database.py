from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Database connection (existing SQLite file)
DATABASE_URL = "sqlite+aiosqlite:///../../../data/vaccination_db.sqlite"

engine = create_async_engine(DATABASE_URL, echo=False)

# Session creation
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncSession:  # type: ignore
    async with AsyncSessionLocal() as db:
        async with db.begin():
            yield db
