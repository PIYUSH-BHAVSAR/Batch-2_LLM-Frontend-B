"""
Fraud explanation generator using rule-based templates
Falls back to simple explanations if HuggingFace models are not available
"""

def generate_explanation(transaction_data: dict, derived_features: dict, 
                        risk_score: float, rule_score: float, 
                        rules_triggered: list) -> str:
    """
    Generate a clear, professional explanation for the fraud prediction.
    Uses template-based approach for reliability and speed.
    """
    
    # Determine fraud status
    is_fraud = risk_score >= 0.6
    fraud_status = "FRAUDULENT" if is_fraud else "LEGITIMATE"
    
    # Build explanation parts
    explanation_parts = []
    
    # 1. Overall assessment
    if is_fraud:
        explanation_parts.append(
            f"⚠️ This transaction has been flagged as {fraud_status} with a combined risk score of {risk_score:.2%}."
        )
    else:
        explanation_parts.append(
            f"✓ This transaction appears {fraud_status} with a combined risk score of {risk_score:.2%}."
        )
    
    # 2. Model contribution
    model_risk = risk_score - rule_score
    if model_risk > 0.5:
        explanation_parts.append(
            f"The ML model detected a high fraud probability ({model_risk:.2%})."
        )
    elif model_risk > 0.3:
        explanation_parts.append(
            f"The ML model indicated moderate risk ({model_risk:.2%})."
        )
    else:
        explanation_parts.append(
            f"The ML model indicated low risk ({model_risk:.2%})."
        )
    
    # 3. Rule-based contribution
    if rules_triggered:
        explanation_parts.append(
            f"Additionally, {len(rules_triggered)} risk rule(s) were triggered:"
        )
        for rule in rules_triggered:
            explanation_parts.append(f"  • {rule}")
    else:
        explanation_parts.append("No specific risk rules were triggered.")
    
    # 4. Key risk factors
    risk_factors = []
    
    amount = derived_features.get("transaction_amount", 0)
    if amount > 100000:
        risk_factors.append(f"Very high transaction amount (₹{amount:,.2f})")
    elif amount > 50000:
        risk_factors.append(f"High transaction amount (₹{amount:,.2f})")
    
    if derived_features.get("kyc_verified", 1) == 0:
        risk_factors.append("Account not KYC verified")
    
    account_age = derived_features.get("account_age_days", 999)
    if account_age < 10:
        risk_factors.append(f"Very new account ({account_age} days old)")
    elif account_age < 30:
        risk_factors.append(f"New account ({account_age} days old)")
    
    if derived_features.get("is_night_txn", 0) == 1:
        risk_factors.append("Transaction during night hours (10 PM - 6 AM)")
    
    if derived_features.get("is_weekend_txn", 0) == 1:
        risk_factors.append("Weekend transaction")
    
    if derived_features.get("is_holiday_txn", 0) == 1:
        risk_factors.append("Transaction on a public holiday")
    
    if risk_factors:
        explanation_parts.append("\nKey risk factors identified:")
        for factor in risk_factors[:5]:  # Limit to top 5
            explanation_parts.append(f"  • {factor}")
    
    # 5. Recommendation
    if is_fraud:
        if risk_score > 0.8:
            explanation_parts.append(
                "\n🚨 RECOMMENDATION: Block this transaction and contact the customer immediately."
            )
        elif risk_score > 0.6:
            explanation_parts.append(
                "\n⚠️ RECOMMENDATION: Review this transaction and consider additional verification."
            )
    else:
        explanation_parts.append(
            "\n✓ RECOMMENDATION: Transaction can proceed with standard monitoring."
        )
    
    return "\n".join(explanation_parts)


def generate_explanation_simple(risk_score: float, is_fraud: int, 
                               rules_triggered: list) -> str:
    """
    Simple fallback explanation generator
    """
    status = "fraudulent" if is_fraud else "legitimate"
    
    explanation = f"This transaction is classified as {status} with a risk score of {risk_score:.2%}."
    
    if rules_triggered:
        explanation += f" The following risk indicators were detected: {', '.join(rules_triggered)}."
    else:
        explanation += " No specific risk indicators were detected."
    
    return explanation


# Optional: Advanced HuggingFace model integration
# Uncomment and modify if you want to use actual LLM generation

"""
from transformers import pipeline
import logging

try:
    # Load a small generative model
    generator = pipeline(
        "text-generation",
        model="distilgpt2",
        max_new_tokens=150,
        temperature=0.7
    )
    HF_MODEL_AVAILABLE = True
    logging.info("✅ HuggingFace model loaded successfully")
except Exception as e:
    HF_MODEL_AVAILABLE = False
    logging.warning(f"⚠️ HuggingFace model not available: {e}")
    generator = None


def generate_explanation_with_llm(transaction_data: dict, derived_features: dict,
                                  risk_score: float, rule_score: float,
                                  rules_triggered: list) -> str:
    '''
    Generate explanation using LLM (if available)
    '''
    if not HF_MODEL_AVAILABLE or generator is None:
        return generate_explanation(transaction_data, derived_features, 
                                   risk_score, rule_score, rules_triggered)
    
    try:
        prompt = f'''
        Fraud Detection Analysis:
        - Risk Score: {risk_score:.2%}
        - Amount: ₹{derived_features.get("transaction_amount", 0):,.2f}
        - KYC Verified: {"Yes" if derived_features.get("kyc_verified") == 1 else "No"}
        - Account Age: {derived_features.get("account_age_days", 0)} days
        - Rules Triggered: {", ".join(rules_triggered) if rules_triggered else "None"}
        
        Explain why this transaction is {"fraudulent" if risk_score >= 0.6 else "legitimate"}:
        '''
        
        result = generator(prompt, max_new_tokens=150, do_sample=True)[0]["generated_text"]
        
        # Extract only the generated part (after the prompt)
        if prompt in result:
            explanation = result.split(prompt)[-1].strip()
        else:
            explanation = result.strip()
        
        return explanation
        
    except Exception as e:
        logging.error(f"LLM generation failed: {e}")
        return generate_explanation(transaction_data, derived_features,
                                   risk_score, rule_score, rules_triggered)
"""