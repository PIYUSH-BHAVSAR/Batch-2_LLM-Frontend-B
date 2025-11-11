# 🔌 RiskShield API - Complete Examples

## Base URL
```
http://localhost:8000
```

---

## 🏥 Health Check

### Request
```http
GET /api/health
```

### Response
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T14:30:00.000000",
  "model_loaded": true
}
```

---

## 👤 Authentication

### 1. Register User

#### Request
```http
POST /api/register
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123"
}
```

#### Response (Success - 200)
```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "email": "john.doe@example.com",
    "full_name": "John Doe"
  }
}
```

#### Response (Error - 400)
```json
{
  "detail": "Email already registered"
}
```

### 2. Login User

#### Request
```http
POST /api/login
Content-Type: application/json

{
  "email": "john.doe@example.com",
  "password": "SecurePass123"
}
```

#### Response (Success - 200)
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "email": "john.doe@example.com",
    "full_name": "John Doe"
  }
}
```

#### Response (Error - 401)
```json
{
  "detail": "Invalid email or password"
}
```

---

## 🎯 Fraud Prediction

### Predict Transaction

#### Request
```http
POST /api/predict
Content-Type: application/json

{
  "email": "john.doe@example.com",
  "customer_id": "CUST12345",
  "transaction_id": "TXN98765",
  "transaction_datetime": "2025-01-15 14:30:00",
  "transaction_amount": 75000.50,
  "kyc_verified": 1,
  "account_age_days": 180,
  "channel_encoded": 0
}
```

#### Field Descriptions
| Field | Type | Description | Valid Values |
|-------|------|-------------|--------------|
| email | string | User email (must be registered) | Valid email |
| customer_id | string | Unique customer identifier | Max 50 chars |
| transaction_id | string | Unique transaction identifier | Max 50 chars |
| transaction_datetime | string | Transaction timestamp | "YYYY-MM-DD HH:MM:SS" |
| transaction_amount | float | Transaction amount in ₹ | > 0 |
| kyc_verified | int | KYC verification status | 0 or 1 |
| account_age_days | int | Account age in days | ≥ 0 |
| channel_encoded | int | Transaction channel | 0=Online, 1=ATM, 2=POS, 3=Mobile |

#### Response (Low Risk - 200)
```json
{
  "status": "success",
  "message": "Prediction completed successfully",
  "data": {
    "prediction_id": 123,
    "user": "John Doe",
    "model_risk_score": 0.2534,
    "rule_score": 0.0,
    "combined_score": 0.2534,
    "is_fraud": 0,
    "rules_triggered": [],
    "derived_features": {
      "kyc_verified": 1,
      "account_age_days": 180,
      "transaction_amount": 75000.50,
      "channel_encoded": 0,
      "hour_of_day": 14,
      "day_of_week": 0,
      "is_night_txn": 0,
      "is_high_amount_transaction": 1,
      "high_amount_night_txn": 0,
      "kyc_low_age_txn": 0,
      "is_weekend_txn": 0,
      "is_holiday_txn": 0,
      "rule_flags": []
    },
    "explanation": "✓ This transaction appears LEGITIMATE with a combined risk score of 25.34%...",
    "timestamp": "2025-01-15T14:30:00"
  }
}
```

#### Response (High Risk - 200)
```json
{
  "status": "success",
  "message": "Prediction completed successfully",
  "data": {
    "prediction_id": 124,
    "user": "John Doe",
    "model_risk_score": 0.6234,
    "rule_score": 0.25,
    "combined_score": 0.8734,
    "is_fraud": 1,
    "rules_triggered": [
      "High amount transaction (>₹100K)",
      "New unverified account"
    ],
    "derived_features": {
      "kyc_verified": 0,
      "account_age_days": 5,
      "transaction_amount": 125000.00,
      "channel_encoded": 0,
      "hour_of_day": 23,
      "day_of_week": 5,
      "is_night_txn": 1,
      "is_high_amount_transaction": 1,
      "high_amount_night_txn": 1,
      "kyc_low_age_txn": 1,
      "is_weekend_txn": 1,
      "is_holiday_txn": 0,
      "rule_flags": [
        "High amount transaction (>₹100K)",
        "New unverified account"
      ]
    },
    "explanation": "⚠️ This transaction has been flagged as FRAUDULENT with a combined risk score of 87.34%. The ML model detected a high fraud probability (62.34%). Additionally, 2 risk rule(s) were triggered: • High amount transaction (>₹100K) • New unverified account. Key risk factors identified: • Very high transaction amount (₹125,000.00) • Account not KYC verified • Very new account (5 days old) • Transaction during night hours (10 PM - 6 AM) • Weekend transaction. 🚨 RECOMMENDATION: Block this transaction and contact the customer immediately.",
    "timestamp": "2025-01-15T23:15:00"
  }
}
```

#### Response (Error - 401)
```json
{
  "detail": "User not registered"
}
```

---

## 📜 Transaction History

### Get User Transactions

#### Request
```http
GET /api/transactions/john.doe@example.com
```

#### Response (200)
```json
{
  "status": "success",
  "message": "Found 15 transactions",
  "data": {
    "user_email": "john.doe@example.com",
    "user_name": "John Doe",
    "total_transactions": 15,
    "transactions": [
      {
        "id": 124,
        "customer_id": "CUST12345",
        "transaction_id": "TXN98766",
        "risk_score": 0.8734,
        "is_fraud": 1,
        "derived_features": {
          "transaction_amount": 125000.00,
          "kyc_verified": 0,
          "account_age_days": 5,
          "is_night_txn": 1,
          "rule_flags": ["High amount transaction (>₹100K)"]
        },
        "explanation": "⚠️ This transaction has been flagged as FRAUDULENT...",
        "timestamp": "2025-01-15T23:15:00"
      },
      {
        "id": 123,
        "customer_id": "CUST12345",
        "transaction_id": "TXN98765",
        "risk_score": 0.2534,
        "is_fraud": 0,
        "derived_features": {
          "transaction_amount": 75000.50,
          "kyc_verified": 1,
          "account_age_days": 180,
          "is_night_txn": 0,
          "rule_flags": []
        },
        "explanation": "✓ This transaction appears LEGITIMATE...",
        "timestamp": "2025-01-15T14:30:00"
      }
    ]
  }
}
```

#### Response (Error - 404)
```json
{
  "detail": "User not found"
}
```

---

## 📊 Analytics Dashboard

### Get Analytics

#### Request
```http
GET /api/analytics
```

#### Response (200)
```json
{
  "status": "success",
  "message": "Analytics generated successfully",
  "data": {
    "kpis": {
      "total_transactions": 1323,
      "fraud_detected": 89,
      "accuracy_rate": 93.3,
      "amount_protected": 2456789.50
    },
    "graphs": {
      "fraud_vs_legitimate": {
        "fraud": 89,
        "legitimate": 1234
      },
      "fraud_rate_trend": [
        {
          "month": "2024-10",
          "fraud_rate": 6.2,
          "total_transactions": 450,
          "fraud_count": 28
        },
        {
          "month": "2024-11",
          "fraud_rate": 7.1,
          "total_transactions": 520,
          "fraud_count": 37
        },
        {
          "month": "2024-12",
          "fraud_rate": 6.8,
          "total_transactions": 353,
          "fraud_count": 24
        }
      ],
      "fraud_by_channel": {
        "Online": 45,
        "ATM": 18,
        "POS": 15,
        "Mobile": 11
      },
      "amount_vs_risk_scatter": [
        {
          "transaction_amount": 125000.00,
          "risk_score": 0.8734,
          "is_fraud": 1
        },
        {
          "transaction_amount": 75000.50,
          "risk_score": 0.2534,
          "is_fraud": 0
        },
        {
          "transaction_amount": 95000.00,
          "risk_score": 0.6823,
          "is_fraud": 1
        }
      ]
    }
  }
}
```

#### Visualization Guide

**1. Fraud vs Legitimate Bar Chart**
```javascript
// Chart.js example
{
  labels: ['Fraud', 'Legitimate'],
  datasets: [{
    data: [89, 1234],
    backgroundColor: ['#ef4444', '#22c55e']
  }]
}
```

**2. Fraud Rate Trend Line Chart**
```javascript
// Chart.js example
{
  labels: ['2024-10', '2024-11', '2024-12'],
  datasets: [{
    label: 'Fraud Rate %',
    data: [6.2, 7.1, 6.8],
    borderColor: '#ef4444',
    fill: false
  }]
}
```

**3. Fraud by Channel Pie Chart**
```javascript
// Chart.js example
{
  labels: ['Online', 'ATM', 'POS', 'Mobile'],
  datasets: [{
    data: [45, 18, 15, 11],
    backgroundColor: ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b']
  }]
}
```

**4. Amount vs Risk Scatter Plot**
```javascript
// Chart.js example
{
  datasets: [{
    label: 'Fraud',
    data: [{x: 125000, y: 0.8734}],
    backgroundColor: '#ef4444'
  }, {
    label: 'Legitimate',
    data: [{x: 75000.50, y: 0.2534}],
    backgroundColor: '#22c55e'
  }]
}
```

---

## 📈 Model Metrics

### Get Model Performance

#### Request
```http
GET /api/metrics
```

#### Response (200)
```json
{
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
      "auc_roc": 0.956,
      "confusion_matrix": {
        "true_positive": 234,
        "false_positive": 23,
        "true_negative": 1056,
        "false_negative": 10
      }
    },
    "feature_importance": [
      {
        "feature": "transaction_amount",
        "importance": 0.234
      },
      {
        "feature": "account_age_days",
        "importance": 0.189
      },
      {
        "feature": "kyc_verified",
        "importance": 0.156
      },
      {
        "feature": "is_night_txn",
        "importance": 0.123
      },
      {
        "feature": "hour_of_day",
        "importance": 0.098
      },
      {
        "feature": "channel_encoded",
        "importance": 0.087
      },
      {
        "feature": "is_high_amount_transaction",
        "importance": 0.073
      },
      {
        "feature": "day_of_week",
        "importance": 0.040
      }
    ],
    "performance_summary": {
      "total_predictions": 1323,
      "fraud_detected": 89,
      "false_positives": 23,
      "false_negatives": 10,
      "detection_rate": 0.899,
      "false_positive_rate": 0.021
    }
  }
}
```
## 📦 Bulk Fraud Prediction

### Bulk Predict Transactions

#### Request
\`\`\`http
POST /api/bulk-predict
Content-Type: application/json

{
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
    },
    {
      "customer_id": "CUST001",
      "transaction_id": "TXN002",
      "transaction_datetime": "2025-01-15 15:00:00",
      "transaction_amount": 125000,
      "kyc_verified": 0,
      "account_age_days": 5,
      "channel_encoded": 0
    }
  ]
}
\`\`\`

#### Response (200)
\`\`\`json
{
  "status": "success",
  "message": "Bulk prediction completed: 2 successful, 0 failed",
  "data": {
    "user": "John Doe",
    "total_processed": 2,
    "successful": 2,
    "failed": 0,
    "fraud_detected": 1,
    "fraud_rate": 50.0,
    "processing_time_seconds": 0.45,
    "avg_time_per_transaction_ms": 225.0,
    "results": [
      {
        "transaction_id": "TXN001",
        "customer_id": "CUST001",
        "risk_score": 0.2534,
        "is_fraud": 0,
        "model_risk_score": 0.2534,
        "rule_score": 0.0,
        "rules_triggered": [],
        "status": "success",
        "error_message": null
      },
      {
        "transaction_id": "TXN002",
        "customer_id": "CUST001",
        "risk_score": 0.8734,
        "is_fraud": 1,
        "model_risk_score": 0.6234,
        "rule_score": 0.25,
        "rules_triggered": [
          "High amount transaction (>₹100K)",
          "New unverified account"
        ],
        "status": "success",
        "error_message": null
      }
    ]
  }
}
\`\`\`

#### Limits
- Maximum 1000 transactions per request
- Minimum 1 transaction per request
- Each transaction stored individually in database
- Failed transactions don't stop processing of others
\`\`\`
---

## 🧪 Test Scenarios

### Scenario 1: Normal Transaction (Low Risk)
```json
{
  "email": "user@example.com",
  "customer_id": "CUST001",
  "transaction_id": "TXN001",
  "transaction_datetime": "2025-01-15 14:30:00",
  "transaction_amount": 5000,
  "kyc_verified": 1,
  "account_age_days": 365,
  "channel_encoded": 0
}
```
**Expected**: `is_fraud: 0`, `combined_score: < 0.3`

### Scenario 2: High-Risk Fraud
```json
{
  "email": "user@example.com",
  "customer_id": "CUST002",
  "transaction_id": "TXN002",
  "transaction_datetime": "2025-01-15 23:45:00",
  "transaction_amount": 150000,
  "kyc_verified": 0,
  "account_age_days": 5,
  "channel_encoded": 0
}
```
**Expected**: `is_fraud: 1`, `combined_score: > 0.8`, Multiple rules triggered

### Scenario 3: Weekend High-Value
```json
{
  "email": "user@example.com",
  "customer_id": "CUST003",
  "transaction_id": "TXN003",
  "transaction_datetime": "2025-01-18 16:00:00",
  "transaction_amount": 95000,
  "kyc_verified": 1,
  "account_age_days": 120,
  "channel_encoded": 2
}
```
**Expected**: `is_fraud: 0-1`, Weekend rule triggered

### Scenario 4: Night Transaction
```json
{
  "email": "user@example.com",
  "customer_id": "CUST004",
  "transaction_id": "TXN004",
  "transaction_datetime": "2025-01-15 02:30:00",
  "transaction_amount": 65000,
  "kyc_verified": 1,
  "account_age_days": 200,
  "channel_encoded": 1
}
```
**Expected**: Night transaction rule may trigger

---

## 🚨 Error Responses

### 400 Bad Request
```json
{
  "detail": [
    {
      "loc": ["body", "transaction_amount"],
      "msg": "value is not a valid float",
      "type": "type_error.float"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "User not registered"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Prediction failed: Model not loaded"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Model not available"
}
```

---

## 📝 Notes

1. **Date Format**: All dates must be in `YYYY-MM-DD HH:MM:SS` format
2. **Unique IDs**: `transaction_id` must be unique across all transactions
3. **Email**: Must be registered before making predictions
4. **Channel Codes**:
   - 0 = Online Banking
   - 1 = ATM
   - 2 = POS Terminal
   - 3 = Mobile App
5. **Risk Scores**: Range from 0.0 to 1.0
6. **Fraud Threshold**: 0.6 (transactions ≥ 0.6 are flagged as fraud)

---

## 🔗 Interactive Documentation

Visit these URLs for interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc