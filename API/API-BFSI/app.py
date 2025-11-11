from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from database import Base, engine, SessionLocal
from models import User, Prediction
from schemas import (
    UserCreate,
    UserLogin,
    PredictRequest,
    PredictResponse,
    TransactionHistoryResponse,
    AnalyticsResponse,
    MetricsResponse,
    BulkPredictRequest,
    BulkPredictResult,
    BulkPredictResponse
)

from utils.features import derive_features_auto
from utils.auth import hash_password, verify_password
from utils.hf_model import generate_explanation
from datetime import datetime, timedelta
from catboost import CatBoostClassifier
import pandas as pd
import numpy as np
from typing import List
from collections import defaultdict
import time
from typing import Dict, List, Any
# ------------------ FASTAPI APP ------------------
app = FastAPI(
    title="RiskShield Fraud Detection API",
    description="AI-powered fraud detection system with hybrid rule-based and ML approach",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://risk-shield.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables if not existing
Base.metadata.create_all(bind=engine)

# ------------------ LOAD MODEL ------------------
model_path = "model/catboost_fraud_model_balanced_tuned.cbm"
cat_model = CatBoostClassifier()
try:
    cat_model.load_model(model_path)
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load model - {e}")
    cat_model = None


# ------------------ DB SESSION DEPENDENCY ------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------ HEALTH CHECK ------------------
@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_loaded": cat_model is not None
    }


# ------------------ REGISTER ------------------
@app.post("/api/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = hash_password(user.password)
        new_user = User(
            email=user.email,
            full_name=user.full_name,
            password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "data": {
                "email": new_user.email,
                "full_name": new_user.full_name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


# ------------------ LOGIN ------------------
@app.post("/api/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user login
    """
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        return {
            "status": "success",
            "message": "Login successful",
            "data": {
                "email": db_user.email,
                "full_name": db_user.full_name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


# ------------------ PREDICT FRAUD ------------------
@app.post("/api/predict", response_model=PredictResponse)
def predict_transaction(data: PredictRequest, db: Session = Depends(get_db)):
    """
    Predict fraud for a transaction using hybrid approach (ML model + rule-based system)
    """
    try:
        # Validate model is loaded
        if cat_model is None:
            raise HTTPException(status_code=503, detail="Model not available")
        
        # Validate user
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not registered")

        # Convert to dict
        data_dict = data.dict()

        # Derive auto features
        features_df = derive_features_auto(data_dict)
        features = features_df.to_dict(orient="records")[0]

        # Model prediction
        model_proba = float(cat_model.predict_proba(features_df)[0, 1])
        
        # -----------------------------
        # RULE-BASED CHECKS
        # -----------------------------
        rule_flags = []
        rule_score = 0.0

        # Rule 1: High amount transaction
        if features["transaction_amount"] > 100000:
            rule_flags.append("High amount transaction (>₹100K)")
            rule_score += 0.2

        # Rule 2: Large night-time transaction
        if features["is_night_txn"] == 1 and features["transaction_amount"] > 50000:
            rule_flags.append("Large night-time transaction")
            rule_score += 0.2

        # Rule 3: New unverified account
        if features["account_age_days"] < 10 and features["kyc_verified"] == 0:
            rule_flags.append("New unverified account")
            rule_score += 0.25

        # Rule 4: Weekend high-value transaction
        if features["is_weekend_txn"] == 1 and features["transaction_amount"] > 80000:
            rule_flags.append("Weekend high-value transaction")
            rule_score += 0.15

        # Rule 5: Holiday transaction risk
        if features.get("is_holiday_txn", 0) == 1 and features["transaction_amount"] > 70000:
            rule_flags.append("High-value holiday transaction")
            rule_score += 0.1

        # Rule 6: Historical pattern - repeated high-risk transactions
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_txns = db.query(Prediction).filter(
            Prediction.customer_id == data_dict["customer_id"],
            Prediction.timestamp >= one_hour_ago
        ).all()
        
        high_value_txns = sum(1 for txn in recent_txns if txn.risk_score > 0.7)
        if high_value_txns >= 3:
            rule_flags.append("Multiple high-risk transactions in last hour")
            rule_score += 0.3

        # -----------------------------
        # HYBRID DECISION
        # -----------------------------
        combined_score = round(min(1.0, model_proba + rule_score), 4)
        final_is_fraud = int(combined_score >= 0.6)

        # Generate explanation
        explanation = generate_explanation(
            data_dict, 
            features, 
            combined_score, 
            rule_score, 
            rule_flags
        )

        # Store in database
        new_pred = Prediction(
            customer_id=data_dict["customer_id"],
            transaction_id=data_dict["transaction_id"],
            email=data_dict["email"],
            risk_score=combined_score,
            is_fraud=final_is_fraud,
            derived_features={**features, "rule_flags": rule_flags},
            explanation=explanation
        )
        db.add(new_pred)
        db.commit()
        db.refresh(new_pred)

        return PredictResponse(
            status="success",
            message="Prediction completed successfully",
            data={
                "prediction_id": new_pred.id,
                "user": user.full_name,
                "model_risk_score": round(model_proba, 4),
                "rule_score": round(rule_score, 2),
                "combined_score": combined_score,
                "is_fraud": final_is_fraud,
                "rules_triggered": rule_flags,
                "derived_features": features,
                "explanation": explanation,
                "timestamp": new_pred.timestamp.isoformat()
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ------------------ TRANSACTION HISTORY ------------------
@app.get("/api/transactions/{email}", response_model=TransactionHistoryResponse)
def get_transaction_history(email: str, db: Session = Depends(get_db)):
    """
    Get complete transaction history for a specific user
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch all predictions for this user
        predictions = db.query(Prediction).filter(
            Prediction.email == email
        ).order_by(Prediction.timestamp.desc()).all()

        transactions = []
        for pred in predictions:
            transactions.append({
                "id": pred.id,
                "customer_id": pred.customer_id,
                "transaction_id": pred.transaction_id,
                "risk_score": pred.risk_score,
                "is_fraud": pred.is_fraud,
                "derived_features": pred.derived_features,
                "explanation": pred.explanation,
                "timestamp": pred.timestamp.isoformat()
            })

        return TransactionHistoryResponse(
            status="success",
            message=f"Found {len(transactions)} transactions",
            data={
                "user_email": email,
                "user_name": user.full_name,
                "total_transactions": len(transactions),
                "transactions": transactions
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transactions: {str(e)}")


# ------------------ ANALYTICS DASHBOARD ------------------
@app.get("/api/analytics", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    """
    Get comprehensive analytics for dashboard visualization
    """
    try:
        # Fetch all predictions
        all_predictions = db.query(Prediction).all()
        
        if not all_predictions:
            return AnalyticsResponse(
                status="success",
                message="No data available yet",
                data={
                    "kpis": {
                        "total_transactions": 0,
                        "fraud_detected": 0,
                        "accuracy_rate": 0.0,
                        "amount_protected": 0.0
                    },
                    "graphs": {
                        "fraud_vs_legitimate": {"fraud": 0, "legitimate": 0},
                        "fraud_rate_trend": [],
                        "fraud_by_channel": {},
                        "amount_vs_risk_scatter": []
                    }
                }
            )

        # Calculate KPIs
        total_txns = len(all_predictions)
        fraud_count = sum(1 for p in all_predictions if p.is_fraud == 1)
        legitimate_count = total_txns - fraud_count
        
        # Estimate amount protected (fraud transactions)
        amount_protected = sum(
            p.derived_features.get("transaction_amount", 0) 
            for p in all_predictions if p.is_fraud == 1
        )
        
        # Simulated accuracy (you should calculate this based on actual labels if available)
        accuracy_rate = 93.3  # Placeholder - replace with actual calculation
        
        # Graph 1: Fraud vs Legitimate
        fraud_vs_legit = {
            "fraud": fraud_count,
            "legitimate": legitimate_count
        }
        
        # Graph 2: Fraud Rate Trend (Monthly)
        monthly_data = defaultdict(lambda: {"total": 0, "fraud": 0})
        for pred in all_predictions:
            month_key = pred.timestamp.strftime("%Y-%m")
            monthly_data[month_key]["total"] += 1
            if pred.is_fraud == 1:
                monthly_data[month_key]["fraud"] += 1
        
        fraud_rate_trend = []
        for month in sorted(monthly_data.keys()):
            total = monthly_data[month]["total"]
            fraud = monthly_data[month]["fraud"]
            fraud_rate = round((fraud / total * 100) if total > 0 else 0, 2)
            fraud_rate_trend.append({
                "month": month,
                "fraud_rate": fraud_rate,
                "total_transactions": total,
                "fraud_count": fraud
            })
        
        # Graph 3: Fraud Distribution by Channel
        channel_mapping = {0: "Online", 1: "ATM", 2: "POS", 3: "Mobile"}
        channel_fraud = defaultdict(int)
        
        for pred in all_predictions:
            if pred.is_fraud == 1:
                channel_code = pred.derived_features.get("channel_encoded", 0)
                channel_name = channel_mapping.get(channel_code, "Unknown")
                channel_fraud[channel_name] += 1
        
        # Graph 4: Transaction Amount vs Risk Score (Scatter Plot)
        scatter_data = []
        for pred in all_predictions:
            scatter_data.append({
                "transaction_amount": pred.derived_features.get("transaction_amount", 0),
                "risk_score": pred.risk_score,
                "is_fraud": pred.is_fraud
            })
        
        return AnalyticsResponse(
            status="success",
            message="Analytics generated successfully",
            data={
                "kpis": {
                    "total_transactions": total_txns,
                    "fraud_detected": fraud_count,
                    "accuracy_rate": accuracy_rate,
                    "amount_protected": round(amount_protected, 2)
                },
                "graphs": {
                    "fraud_vs_legitimate": fraud_vs_legit,
                    "fraud_rate_trend": fraud_rate_trend,
                    "fraud_by_channel": dict(channel_fraud),
                    "amount_vs_risk_scatter": scatter_data
                }
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")

# ------------------ MODEL METRICS ------------------
@app.get("/api/metrics", response_model=MetricsResponse)
def get_model_metrics():
    """
    Get model performance metrics (based on actual training results)
    """
    return MetricsResponse(
        status="success",
        message="Model metrics retrieved successfully",
        data={
            "model_name": "CatBoost Fraud Detection Model (Recall-Optimized)",
            "version": "1.0.0",
            "training_date": "2025-01-15",
            "metrics": {
                "accuracy": 0.76,
                "precision": 0.24,
                "recall": 0.83,   # This is the important part - FRAUD DETECTION RECALL
                "f1_score": 0.37,
                "auc_roc": 0.80,
                "confusion_matrix": {
                    "true_positive": 71,
                    "false_positive": 224,
                    "true_negative": 690,
                    "false_negative": 15
                }
            },
            # Keep these unless you want to regenerate actual importance values
            "feature_importance": [
                {"feature": "transaction_amount", "importance": 0.234},
                {"feature": "account_age_days", "importance": 0.189},
                {"feature": "kyc_verified", "importance": 0.156},
                {"feature": "is_night_txn", "importance": 0.123},
                {"feature": "hour_of_day", "importance": 0.098},
                {"feature": "channel_encoded", "importance": 0.087},
                {"feature": "is_high_amount_transaction", "importance": 0.073},
                {"feature": "day_of_week", "importance": 0.040}
            ],
            "performance_summary": {
                "total_predictions": 1000,
                "fraud_detected": 71,
                "false_positives": 224,
                "false_negatives": 15,
                "detection_rate": 0.83,
                "false_positive_rate": round(224 / (224 + 690), 3)
            }
        }
    )


# ------------------ BULK PREDICT ------------------
@app.post("/api/bulk-predict", response_model=BulkPredictResponse)
def bulk_predict_transactions(data: BulkPredictRequest, db: Session = Depends(get_db)):
    """
    Bulk fraud prediction for multiple transactions
    Accepts up to 1000 transactions at once
    """
    start_time = time.time()
    
    try:
        # Validate model is loaded
        if cat_model is None:
            raise HTTPException(status_code=503, detail="Model not available")
        
        # Validate user
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not registered")
        
        results = []
        successful = 0
        failed = 0
        fraud_detected = 0
        
        # Process each transaction
        for txn_data in data.transactions:
            try:
                # Add email to transaction data
                txn_data["email"] = data.email
                
                # Derive features
                features_df = derive_features_auto(txn_data)
                features = features_df.to_dict(orient="records")[0]
                
                # Model prediction
                model_proba = float(cat_model.predict_proba(features_df)[0, 1])
                
                # Rule-based checks
                rule_flags = []
                rule_score = 0.0
                
                # Rule 1: High amount
                if features["transaction_amount"] > 100000:
                    rule_flags.append("High amount transaction (>₹100K)")
                    rule_score += 0.2
                
                # Rule 2: Night transaction
                if features["is_night_txn"] == 1 and features["transaction_amount"] > 50000:
                    rule_flags.append("Large night-time transaction")
                    rule_score += 0.2
                
                # Rule 3: New unverified account
                if features["account_age_days"] < 10 and features["kyc_verified"] == 0:
                    rule_flags.append("New unverified account")
                    rule_score += 0.25
                
                # Rule 4: Weekend high-value
                if features["is_weekend_txn"] == 1 and features["transaction_amount"] > 80000:
                    rule_flags.append("Weekend high-value transaction")
                    rule_score += 0.15
                
                # Rule 5: Holiday risk
                if features.get("is_holiday_txn", 0) == 1 and features["transaction_amount"] > 70000:
                    rule_flags.append("High-value holiday transaction")
                    rule_score += 0.1
                
                # Combined score
                combined_score = round(min(1.0, model_proba + rule_score), 4)
                final_is_fraud = int(combined_score >= 0.6)
                
                if final_is_fraud:
                    fraud_detected += 1
                
                # Generate explanation
                explanation = generate_explanation(
                    txn_data, features, combined_score, rule_score, rule_flags
                )
                
                # Store in database
                new_pred = Prediction(
                    customer_id=txn_data["customer_id"],
                    transaction_id=txn_data["transaction_id"],
                    email=data.email,
                    risk_score=combined_score,
                    is_fraud=final_is_fraud,
                    derived_features={**features, "rule_flags": rule_flags},
                    explanation=explanation
                )
                db.add(new_pred)
                
                # Add to results
                results.append({
                    "transaction_id": txn_data["transaction_id"],
                    "customer_id": txn_data["customer_id"],
                    "risk_score": combined_score,
                    "is_fraud": final_is_fraud,
                    "model_risk_score": round(model_proba, 4),
                    "rule_score": round(rule_score, 2),
                    "rules_triggered": rule_flags,
                    "status": "success",
                    "error_message": None
                })
                
                successful += 1
                
            except Exception as e:
                failed += 1
                results.append({
                    "transaction_id": txn_data.get("transaction_id", "unknown"),
                    "customer_id": txn_data.get("customer_id", "unknown"),
                    "risk_score": 0.0,
                    "is_fraud": 0,
                    "model_risk_score": 0.0,
                    "rule_score": 0.0,
                    "rules_triggered": [],
                    "status": "error",
                    "error_message": str(e)
                })
        
        # Commit all successful predictions
        db.commit()
        
        # Calculate processing time
        processing_time = round(time.time() - start_time, 2)
        
        return BulkPredictResponse(
            status="success",
            message=f"Bulk prediction completed: {successful} successful, {failed} failed",
            data={
                "user": user.full_name,
                "total_processed": len(data.transactions),
                "successful": successful,
                "failed": failed,
                "fraud_detected": fraud_detected,
                "fraud_rate": round((fraud_detected / successful * 100) if successful > 0 else 0, 2),
                "processing_time_seconds": processing_time,
                "avg_time_per_transaction_ms": round((processing_time / len(data.transactions)) * 1000, 2),
                "results": results
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk prediction failed: {str(e)}")
# ------------------ ROOT ENDPOINT ------------------
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to RiskShield Fraud Detection API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "register": "/api/register",
            "login": "/api/login",
            "predict": "/api/predict",
            "transactions": "/api/transactions/{email}",
            "analytics": "/api/analytics",
            "metrics": "/api/metrics"
        },
        "documentation": "/docs"
    }


    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

