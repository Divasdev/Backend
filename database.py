from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Database URL: we are using SQLite and storing the database in a local file called blog.db.
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"


# Create the SQLAlchemy engine. It is responsible for connecting our application to the database.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Create a session factory. We use sessions to interact with the database.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# Base class for all our database models.
# Our model classes will inherit from Base.
class Base(DeclarativeBase):
    pass


# Dependency that gives a FastAPI route a database session
# and closes the session after the request.
def get_db():
    # Open a new database session.
    with SessionLocal() as db:
        # Give the database session to the FastAPI route.
        yield db