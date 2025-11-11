from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# ==================== USERS TABLE ====================
class User(Base):
    """
    User table for authentication and user management
    """
    __tablename__ = "users"

    email = Column(String(100), primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    password = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to predictions
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(email={self.email}, full_name={self.full_name})>"


# ==================== PREDICTIONS TABLE ====================
class Prediction(Base):
    """
    Predictions table for storing fraud detection results
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    transaction_id = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), ForeignKey("users.email", ondelete="CASCADE"), nullable=False)
    risk_score = Column(Float, nullable=False)
    is_fraud = Column(Integer, nullable=False)
    derived_features = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship
    user = relationship("User", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction(id={self.id}, transaction_id={self.transaction_id}, is_fraud={self.is_fraud})>"