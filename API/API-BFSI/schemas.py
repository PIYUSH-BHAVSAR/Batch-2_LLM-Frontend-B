from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# ==================== USER SCHEMAS ====================

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "password": "securepass123"
            }
        }


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "securepass123"
            }
        }


# ==================== PREDICTION SCHEMAS ====================

class PredictRequest(BaseModel):
    email: EmailStr
    customer_id: str = Field(..., min_length=1, max_length=50)
    transaction_id: str = Field(..., min_length=1, max_length=50)
    transaction_datetime: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
    transaction_amount: float = Field(..., gt=0)
    kyc_verified: int = Field(..., ge=0, le=1)
    account_age_days: int = Field(..., ge=0)
    channel_encoded: int = Field(..., ge=0, le=3)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "customer_id": "CUST12345",
                "transaction_id": "TXN98765",
                "transaction_datetime": "2025-01-15 14:30:00",
                "transaction_amount": 75000.50,
                "kyc_verified": 1,
                "account_age_days": 180,
                "channel_encoded": 0
            }
        }


class PredictResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Prediction completed successfully",
                "data": {
                    "prediction_id": 123,
                    "user": "John Doe",
                    "model_risk_score": 0.7234,
                    "rule_score": 0.15,
                    "combined_score": 0.8734,
                    "is_fraud": 1,
                    "rules_triggered": ["High amount transaction (>₹100K)"],
                    "derived_features": {},
                    "explanation": "This transaction was flagged...",
                    "timestamp": "2025-01-15T14:30:00"
                }
            }
        }


# ==================== TRANSACTION HISTORY SCHEMAS ====================

class Transaction(BaseModel):
    id: int
    customer_id: str
    transaction_id: str
    risk_score: float
    is_fraud: int
    derived_features: Dict[str, Any]
    explanation: str
    timestamp: str


class TransactionHistoryResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Found 15 transactions",
                "data": {
                    "user_email": "john.doe@example.com",
                    "user_name": "John Doe",
                    "total_transactions": 15,
                    "transactions": []
                }
            }
        }


# ==================== ANALYTICS SCHEMAS ====================

class KPIs(BaseModel):
    total_transactions: int
    fraud_detected: int
    accuracy_rate: float
    amount_protected: float


class FraudVsLegitimate(BaseModel):
    fraud: int
    legitimate: int


class FraudRateTrend(BaseModel):
    month: str
    fraud_rate: float
    total_transactions: int
    fraud_count: int


class AmountVsRiskScatter(BaseModel):
    transaction_amount: float
    risk_score: float
    is_fraud: int


class GraphData(BaseModel):
    fraud_vs_legitimate: Dict[str, int]
    fraud_rate_trend: List[Dict[str, Any]]
    fraud_by_channel: Dict[str, int]
    amount_vs_risk_scatter: List[Dict[str, Any]]


class AnalyticsResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Analytics generated successfully",
                "data": {
                    "kpis": {
                        "total_transactions": 1323,
                        "fraud_detected": 89,
                        "accuracy_rate": 93.3,
                        "amount_protected": 2400000.00
                    },
                    "graphs": {
                        "fraud_vs_legitimate": {"fraud": 89, "legitimate": 1234},
                        "fraud_rate_trend": [],
                        "fraud_by_channel": {},
                        "amount_vs_risk_scatter": []
                    }
                }
            }
        }


# ==================== METRICS SCHEMAS ====================

class ConfusionMatrix(BaseModel):
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int


class FeatureImportance(BaseModel):
    feature: str
    importance: float


class PerformanceSummary(BaseModel):
    total_predictions: int
    fraud_detected: int
    false_positives: int
    false_negatives: int
    detection_rate: float
    false_positive_rate: float


class ModelMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    confusion_matrix: Dict[str, int]


class MetricsResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Model metrics retrieved successfully",
                "data": {
                    "model_name": "CatBoost Fraud Detection Model",
                    "version": "1.0.0",
                    "training_date": "2024-01-15",
                    "metrics": {
                        "accuracy": 0.933,
                        "precision": 0.912,
                        "recall": 0.887,
                        "f1_score": 0.899,
                        "auc_roc": 0.956
                    }
                }
            }
        }


# ==================== BULK PREDICTION SCHEMAS ====================

class BulkPredictRequest(BaseModel):
    email: EmailStr
    transactions: List[Dict[str, Any]] = Field(..., min_items=1, max_items=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "transactions": [
                    {
                        "customer_id": "CUST001",
                        "transaction_id": "TXN001",
                        "transaction_datetime": "2025-01-15 14:30:00",
                        "transaction_amount": 50000,
                        "kyc_verified": 1,
                        "account_age_days": 180,
                        "channel_encoded": 0
                    }
                ]
            }
        }


class BulkPredictResult(BaseModel):
    transaction_id: str
    customer_id: str
    risk_score: float
    is_fraud: int
    rules_triggered: List[str]
    status: str  # "success" or "error"
    error_message: Optional[str] = None


class BulkPredictResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Bulk prediction completed",
                "data": {
                    "total_processed": 100,
                    "successful": 98,
                    "failed": 2,
                    "fraud_detected": 15,
                    "processing_time_seconds": 2.5,
                    "results": []
                }
            }
        }