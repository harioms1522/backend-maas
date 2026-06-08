from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import DATABASE_URL

# Create a base class for the models
Base = declarative_base()

# Create the SQLAlchemy engine
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

# Create a configured "Session" class
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
async_session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
async def get_db():
    async with async_session_local() as session:
        yield session