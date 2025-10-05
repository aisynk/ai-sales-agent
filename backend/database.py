# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from .env file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_sales_agent.db")

# Create database engine
# SQLite needs special config for threading
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Print SQL queries (helpful for learning/debugging)
    connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI
)

# Create session factory
# Sessions are how we interact with the database
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all database models
# All our table definitions will inherit from this
Base = declarative_base()

# Dependency function for FastAPI endpoints
def get_db():
    """
    Provides database session to API endpoints
    Automatically closes session when done
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()