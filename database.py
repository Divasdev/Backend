from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Database URL: we are using SQLite and storing the database in a local file called blog.db.
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"


# Create the SQLAlchemy engine. It is responsible for connecting our application to the database.
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)



AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Base class for all our database models.
# Our model classes will inherit from Base.
class Base(DeclarativeBase):
    pass


# Dependency that gives a FastAPI route a database session
# and closes the session after the request.
async def get_db():
    # Open a new database session.
   async with AsyncSessionLocal() as session:
        # Give the database session to the FastAPI route.
        yield session