"""
RiskShield API Testing Client
Comprehensive testing utility for all endpoints
"""

import requests
import json
from datetime import datetime, timedelta
import random
from typing import List,Dict, Any

BASE_URL = "http://localhost:8000"

class RiskShieldClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/api/health")
        return response.json()
    
    def register_user(self, full_name: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        payload = {
            "full_name": full_name,
            "email": email,
            "password": password
        }
        response = self.session.post(f"{self.base_url}/api/register", json=payload)
        return response.json()
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user"""
        payload = {
            "email": email,
            "password": password
        }
        response = self.session.post(f"{self.base_url}/api/login", json=payload)
        return response.json()
    
    def predict_transaction(self, 
                          email: str,
                          customer_id: str,
                          transaction_id: str,
                          transaction_datetime: str,
                          transaction_amount: float,
                          kyc_verified: int,
                          account_age_days: int,
                          channel_encoded: int) -> Dict[str, Any]:
        """Predict fraud for a transaction"""
        payload = {
            "email": email,
            "customer_id": customer_id,
            "transaction_id": transaction_id,
            "transaction_datetime": transaction_datetime,
            "transaction_amount": transaction_amount,
            "kyc_verified": kyc_verified,
            "account_age_days": account_age_days,
            "channel_encoded": channel_encoded
        }
        response = self.session.post(f"{self.base_url}/api/predict", json=payload)
        return response.json()
    
    def get_transactions(self, email: str) -> Dict[str, Any]:
        """Get transaction history for a user"""
        response = self.session.get(f"{self.base_url}/api/transactions/{email}")
        return response.json()
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics dashboard data"""
        response = self.session.get(f"{self.base_url}/api/analytics")
        return response.json()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get model metrics"""
        response = self.session.get(f"{self.base_url}/api/metrics")
        return response.json()

    def bulk_predict(self, email: str, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk predict multiple transactions"""
        payload = {
            "email": email,
            "transactions": transactions
        }
        response = self.session.post(f"{self.base_url}/api/bulk-predict", json=payload)
        return response.json()

def generate_test_transaction(email: str, customer_id: str, 
                              scenario: str = "normal") -> Dict[str, Any]:
    """Generate test transaction data based on scenario"""
    
    transaction_id = f"TXN{random.randint(10000, 99999)}"
    now = datetime.now()
    
    scenarios = {
        "normal": {
            "transaction_amount": random.uniform(500, 5000),
            "kyc_verified": 1,
            "account_age_days": random.randint(100, 500),
            "channel_encoded": random.randint(0, 3),
            "hour": random.randint(9, 18)
        },
        "high_risk": {
            "transaction_amount": random.uniform(100000, 200000),
            "kyc_verified": 0,
            "account_age_days": random.randint(1, 10),
            "channel_encoded": 0,
            "hour": random.randint(22, 23)
        },
        "night_transaction": {
            "transaction_amount": random.uniform(60000, 90000),
            "kyc_verified": 1,
            "account_age_days": random.randint(50, 200),
            "channel_encoded": 1,
            "hour": random.randint(0, 5)
        },
        "weekend_high": {
            "transaction_amount": random.uniform(85000, 120000),
            "kyc_verified": 1,
            "account_age_days": random.randint(30, 100),
            "channel_encoded": 2,
            "hour": random.randint(10, 16)
        }
    }
    
    config = scenarios.get(scenario, scenarios["normal"])
    
    # Adjust datetime for scenario
    txn_time = now.replace(hour=config["hour"], minute=random.randint(0, 59))
    
    # For weekend scenario, adjust to Saturday or Sunday
    if scenario == "weekend_high":
        days_to_add = (5 - txn_time.weekday()) % 7
        txn_time = txn_time + timedelta(days=days_to_add)
    
    return {
        "email": email,
        "customer_id": customer_id,
        "transaction_id": transaction_id,
        "transaction_datetime": txn_time.strftime("%Y-%m-%d %H:%M:%S"),
        "transaction_amount": config["transaction_amount"],
        "kyc_verified": config["kyc_verified"],
        "account_age_days": config["account_age_days"],
        "channel_encoded": config["channel_encoded"]
    }


def run_comprehensive_test():
    """Run comprehensive API tests"""
    
    client = RiskShieldClient()
    
    print("=" * 60)
    print("🛡️  RiskShield API Comprehensive Test")
    print("=" * 60)
    
    # 1. Health Check
    print("\n1️⃣  Health Check")
    print("-" * 60)
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    # 2. Register User
    print("\n2️⃣  User Registration")
    print("-" * 60)
    test_email = f"test_{random.randint(1000, 9999)}@example.com"
    test_password = "TestPass123"
    
    register_response = client.register_user(
        full_name="Test User",
        email=test_email,
        password=test_password
    )
    print(json.dumps(register_response, indent=2))
    
    # 3. Login
    print("\n3️⃣  User Login")
    print("-" * 60)
    login_response = client.login_user(test_email, test_password)
    print(json.dumps(login_response, indent=2))
    
    # 4. Test Different Transaction Scenarios
    print("\n4️⃣  Transaction Predictions")
    print("-" * 60)
    
    scenarios = ["normal", "high_risk", "night_transaction", "weekend_high"]
    customer_id = f"CUST{random.randint(1000, 9999)}"
    
    for scenario in scenarios:
        print(f"\n   📊 Testing: {scenario.upper().replace('_', ' ')}")
        print("   " + "-" * 56)
        
        txn_data = generate_test_transaction(test_email, customer_id, scenario)
        prediction = client.predict_transaction(**txn_data)
        
        if prediction.get("status") == "success":
            data = prediction["data"]
            print(f"   ✓ Transaction ID: {txn_data['transaction_id']}")
            print(f"   ✓ Amount: ₹{txn_data['transaction_amount']:,.2f}")
            print(f"   ✓ Combined Score: {data['combined_score']}")
            print(f"   ✓ Is Fraud: {'Yes' if data['is_fraud'] else 'No'}")
            print(f"   ✓ Rules Triggered: {len(data['rules_triggered'])}")
            if data['rules_triggered']:
                for rule in data['rules_triggered']:
                    print(f"      • {rule}")
        else:
            print(f"   ✗ Error: {prediction.get('detail', 'Unknown error')}")
    
    # 5. Get Transaction History
    print("\n5️⃣  Transaction History")
    print("-" * 60)
    history = client.get_transactions(test_email)
    if history.get("status") == "success":
        data = history["data"]
        print(f"Total Transactions: {data['total_transactions']}")
        print(f"User: {data['user_name']}")
    print(json.dumps(history, indent=2)[:500] + "...")
    
    # 6. Get Analytics
    print("\n6️⃣  Analytics Dashboard")
    print("-" * 60)
    analytics = client.get_analytics()
    if analytics.get("status") == "success":
        kpis = analytics["data"]["kpis"]
        print(f"Total Transactions: {kpis['total_transactions']}")
        print(f"Fraud Detected: {kpis['fraud_detected']}")
        print(f"Accuracy Rate: {kpis['accuracy_rate']}%")
        print(f"Amount Protected: ₹{kpis['amount_protected']:,.2f}")
    
    # 7. Get Model Metrics
    print("\n7️⃣  Model Metrics")
    print("-" * 60)
    metrics = client.get_metrics()
    if metrics.get("status") == "success":
        model_metrics = metrics["data"]["metrics"]
        print(f"Accuracy: {model_metrics['accuracy']:.3f}")
        print(f"Precision: {model_metrics['precision']:.3f}")
        print(f"Recall: {model_metrics['recall']:.3f}")
        print(f"F1 Score: {model_metrics['f1_score']:.3f}")
        print(f"AUC-ROC: {model_metrics['auc_roc']:.3f}")
    
    print("\n" + "=" * 60)
    print("✅ Comprehensive Test Completed!")
    print("=" * 60)


def quick_fraud_test():
    """Quick test for high-risk fraud scenarios"""
    
    client = RiskShieldClient()
    
    print("\n🚨 Quick Fraud Detection Test")
    print("=" * 60)
    
    # Use existing user or create new one
    test_email = "quicktest@example.com"
    test_password = "QuickTest123"
    
    try:
        client.register_user("Quick Test", test_email, test_password)
    except:
        pass  # User might already exist
    
    # Test high-risk transaction
    txn_data = generate_test_transaction(test_email, "CUST9999", "high_risk")
    
    print(f"\n📋 Transaction Details:")
    print(f"   Amount: ₹{txn_data['transaction_amount']:,.2f}")
    print(f"   Time: {txn_data['transaction_datetime']}")
    print(f"   KYC: {'Verified' if txn_data['kyc_verified'] else 'Not Verified'}")
    print(f"   Account Age: {txn_data['account_age_days']} days")
    
    result = client.predict_transaction(**txn_data)
    
    if result.get("status") == "success":
        data = result["data"]
        print(f"\n🎯 Prediction Results:")
        print(f"   Risk Score: {data['combined_score']:.2%}")
        print(f"   Fraud Status: {'FRAUDULENT' if data['is_fraud'] else 'LEGITIMATE'}")
        print(f"   Model Score: {data['model_risk_score']:.2%}")
        print(f"   Rule Score: {data['rule_score']:.2%}")
        
        if data['rules_triggered']:
            print(f"\n⚠️  Rules Triggered:")
            for rule in data['rules_triggered']:
                print(f"   • {rule}")
        
        print(f"\n💡 Explanation:")
        print(f"   {data['explanation'][:200]}...")
    
    print("\n" + "=" * 60)

def test_bulk_predict():
    """Test bulk prediction functionality"""
    
    client = RiskShieldClient()
    
    print("\n" + "=" * 60)
    print("📦 Bulk Prediction Test")
    print("=" * 60)
    
    # Register test user
    test_email = f"bulk_test_{random.randint(1000, 9999)}@example.com"
    test_password = "BulkTest123"
    
    try:
        client.register_user("Bulk Test User", test_email, test_password)
    except:
        pass
    
    # Generate 50 test transactions
    transactions = []
    customer_id = f"CUST{random.randint(1000, 9999)}"
    
    for i in range(50):
        scenario = random.choice(["normal", "high_risk", "night_transaction", "weekend_high"])
        txn = generate_test_transaction(test_email, customer_id, scenario)
        # Remove email field as it's sent separately
        txn.pop("email", None)
        transactions.append(txn)
    
    print(f"\n📊 Testing bulk prediction with {len(transactions)} transactions...")
    
    # Make bulk prediction
    result = client.bulk_predict(test_email, transactions)
    
    if result.get("status") == "success":
        data = result["data"]
        print(f"\n✅ Bulk Prediction Results:")
        print(f"   Total Processed: {data['total_processed']}")
        print(f"   Successful: {data['successful']}")
        print(f"   Failed: {data['failed']}")
        print(f"   Fraud Detected: {data['fraud_detected']}")
        print(f"   Fraud Rate: {data['fraud_rate']}%")
        print(f"   Processing Time: {data['processing_time_seconds']}s")
        print(f"   Avg Time/Transaction: {data['avg_time_per_transaction_ms']}ms")
        
        # Show sample results
        print(f"\n📋 Sample Results (first 5):")
        for result in data['results'][:5]:
            status_icon = "✓" if result['status'] == "success" else "✗"
            fraud_icon = "🚨" if result['is_fraud'] else "✅"
            print(f"   {status_icon} {result['transaction_id']}: {fraud_icon} Risk={result['risk_score']:.2%}")
    else:
        print(f"\n❌ Error: {result.get('detail', 'Unknown error')}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            quick_fraud_test()
        elif sys.argv[1] == "bulk":
            test_bulk_predict()
    else:
        run_comprehensive_test()