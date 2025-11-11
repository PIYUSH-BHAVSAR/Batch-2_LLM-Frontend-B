"""
Database Configuration and Connection Management
Uses centralized configuration from config.py
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import logging

logger = logging.getLogger(__name__)

# Database URL from settings
SQLALCHEMY_DATABASE_URL = settings.database_url

# Create engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Database session dependency for FastAPI
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Creates all tables if they don't exist
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


def check_db_connection():
    """
    Check if database connection is working
    Returns True if connection successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def get_db_info():
    """
    Get database information for monitoring
    """
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT version()")
            version = result.fetchone()[0]
            
            return {
                "status": "connected",
                "database": settings.DB_NAME,
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "version": version,
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    # Test database connection when run directly
    print("Testing database connection...")
    if check_db_connection():
        print("✅ Database connection successful")
        info = get_db_info()
        print(f"Database: {info.get('database')}")
        print(f"Host: {info.get('host')}:{info.get('port')}")
        print(f"Version: {info.get('version')}")
    else:
        print("❌ Database connection failed")