"""
Configuration Management for RiskShield
Handles environment variables and application settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    """
    Application settings with validation
    """
    
    # Application Info
    APP_NAME: str = "RiskShield Fraud Detection API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered fraud detection system"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    DEBUG: bool = False
    
    # Database Configuration
    DB_USER=<your_database_username>
    DB_PASSWORD=<your_database_password>
    DB_HOST=<your_database_host_url_or_ip>
    DB_PORT=5432
    DB_NAME=<your_database_name>
    DB_SSLMODE=require
    


    # Database Connection Pool
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # Model Configuration
    MODEL_PATH: str = "model/catboost_fraud_model_balanced_tuned.cbm"
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_SECRET: str = "change-this-jwt-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Password Requirements
    MIN_PASSWORD_LENGTH: int = 6
    MAX_PASSWORD_LENGTH: int = 100
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:3000"
    ]
    
    # Fraud Detection Thresholds
    FRAUD_THRESHOLD: float = 0.6
    HIGH_RISK_THRESHOLD: float = 0.8
    HIGH_AMOUNT_THRESHOLD: float = 100000
    
    # Rule-Based Detection
    NIGHT_HOURS_START: int = 22
    NIGHT_HOURS_END: int = 6
    HIGH_AMOUNT_NIGHT_THRESHOLD: float = 50000
    WEEKEND_HIGH_THRESHOLD: float = 80000
    HOLIDAY_HIGH_THRESHOLD: float = 70000
    NEW_ACCOUNT_DAYS: int = 10
    VELOCITY_CHECK_HOURS: int = 1
    VELOCITY_CHECK_THRESHOLD: int = 3
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/riskshield.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Feature Flags
    ENABLE_ML_MODEL: bool = True
    ENABLE_RULE_ENGINE: bool = True
    ENABLE_HF_EXPLANATIONS: bool = False
    ENABLE_METRICS: bool = True
    
    # Performance
    ENABLE_CACHING: bool = False
    CACHE_TTL: int = 3600
    
    # Monitoring
    METRICS_PORT: int = 9090
    
    # Email Configuration (for alerts - optional)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ALERT_EMAIL: str = ""
    ENABLE_EMAIL_ALERTS: bool = False
    
    # Redis Configuration (optional)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_ENABLED: bool = False
    
    @property
    def database_url(self) -> str:
        """Generate database URL (Neon + local compatible)"""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSLMODE}"
        )

    @property
    def async_database_url(self) -> str:
        """Generate async database URL (Neon + asyncpg)"""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSLMODE}"
        )

    def is_production(self) -> bool:
        """Check if running in production"""
        return not self.DEBUG
    
    def validate_model_path(self) -> bool:
        """Validate model file exists"""
        return Path(self.MODEL_PATH).exists()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Logging Configuration
def setup_logging():
    """Setup application logging"""
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Create logs directory if not exists
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=settings.LOG_FORMAT,
        handlers=[
            RotatingFileHandler(
                settings.LOG_FILE,
                maxBytes=settings.LOG_MAX_BYTES,
                backupCount=settings.LOG_BACKUP_COUNT
            ),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: {settings.LOG_LEVEL}")
    return logger


# Configuration Display
def display_config():
    """Display current configuration (for debugging)"""
    print("=" * 60)
    print("🛡️  RiskShield Configuration")
    print("=" * 60)
    print(f"App Name: {settings.APP_NAME}")
    print(f"Version: {settings.APP_VERSION}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"API Host: {settings.API_HOST}")
    print(f"API Port: {settings.API_PORT}")
    print(f"Database: {settings.DB_NAME} @ {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"Model Path: {settings.MODEL_PATH}")
    print(f"Model Exists: {settings.validate_model_path()}")
    print(f"Fraud Threshold: {settings.FRAUD_THRESHOLD}")
    print(f"ML Model Enabled: {settings.ENABLE_ML_MODEL}")
    print(f"Rule Engine Enabled: {settings.ENABLE_RULE_ENGINE}")
    print(f"Rate Limiting: {settings.RATE_LIMIT_ENABLED}")
    print(f"CORS Origins: {len(settings.CORS_ORIGINS)} configured")
    print("=" * 60)


# Validation Functions
def validate_configuration() -> List[str]:
    """
    Validate configuration and return list of warnings/errors
    """
    issues = []
    
    # Check database configuration
    if settings.DB_PASSWORD == "admin123":
        issues.append("⚠️  WARNING: Using default database password")
    
    # Check secret keys
    if "change-this" in settings.SECRET_KEY.lower():
        issues.append("⚠️  WARNING: Using default SECRET_KEY")
    
    if "change-this" in settings.JWT_SECRET.lower():
        issues.append("⚠️  WARNING: Using default JWT_SECRET")
    
    # Check model file
    if not settings.validate_model_path():
        issues.append(f"⚠️  WARNING: Model file not found at {settings.MODEL_PATH}")
    
    # Check production settings
    if settings.is_production():
        if settings.DEBUG:
            issues.append("⚠️  WARNING: Debug mode enabled in production")
        
        if not settings.RATE_LIMIT_ENABLED:
            issues.append("⚠️  WARNING: Rate limiting disabled in production")
    
    # Check thresholds
    if settings.FRAUD_THRESHOLD < 0 or settings.FRAUD_THRESHOLD > 1:
        issues.append("❌ ERROR: Invalid fraud threshold (must be 0-1)")
    
    return issues


# Environment Detection
def get_environment() -> str:
    """Detect current environment"""
    if settings.DEBUG:
        return "development"
    elif os.getenv("STAGING"):
        return "staging"
    else:
        return "production"


# Export commonly used settings
__all__ = [
    'settings',
    'setup_logging',
    'display_config',
    'validate_configuration',
    'get_environment'
]


if __name__ == "__main__":
    # Display configuration when run directly
    display_config()
    
    # Validate configuration
    issues = validate_configuration()
    if issues:
        print("\n⚠️  Configuration Issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ Configuration validated successfully")