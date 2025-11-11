from datetime import datetime
import pandas as pd
import holidays  # 🇮🇳 Indian holidays library

def derive_features_auto(input_data: dict) -> pd.DataFrame:
    """
    Automatically derives all 13 model features from minimal input.
    Detects Indian national holidays automatically.
    """
    txn_dt = datetime.strptime(input_data['transaction_datetime'], "%Y-%m-%d %H:%M:%S")

    hour_of_day = txn_dt.hour
    day_of_week = txn_dt.weekday()
    is_night_txn = 1 if hour_of_day >= 22 or hour_of_day < 6 else 0
    is_weekend_txn = 1 if day_of_week >= 5 else 0

    # High amount and combined conditions
    is_high_amount_transaction = 1 if input_data['transaction_amount'] > 50000 else 0
    high_amount_night_txn = 1 if is_high_amount_transaction and is_night_txn else 0

    # Low KYC + low age risky transactions
    kyc_low_age_txn = 1 if (input_data['kyc_verified'] == 0 and input_data['account_age_days'] < 30) else 0

    # 🇮🇳 Detect if date is an Indian holiday
    india_holidays = holidays.India(years=txn_dt.year)
    is_holiday_txn = 1 if txn_dt.date() in india_holidays else 0

    features = {
        'kyc_verified': input_data['kyc_verified'],
        'account_age_days': input_data['account_age_days'],
        'transaction_amount': input_data['transaction_amount'],
        'channel_encoded': input_data['channel_encoded'],
        'hour_of_day': hour_of_day,
        'day_of_week': day_of_week,
        'is_night_txn': is_night_txn,
        'is_high_amount_transaction': is_high_amount_transaction,
        'high_amount_night_txn': high_amount_night_txn,
        'kyc_low_age_txn': kyc_low_age_txn,
        'is_weekend_txn': is_weekend_txn,
        'is_holiday_txn': is_holiday_txn
    }

    return pd.DataFrame([features])
