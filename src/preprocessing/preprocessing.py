import pandas as pd
import numpy as np

def clean_transaction_data(input_path: str, output_path: str = "transactions_cleaned.csv") -> pd.DataFrame:
    """
    Cleans BFSI transaction dataset by fixing data types, handling nulls, 
    and correcting logical inconsistencies without removing valid records.
    
    Parameters:
        input_path (str): Path to the raw CSV dataset.
        output_path (str): Path where cleaned dataset will be saved (default: transactions_cleaned.csv)
    
    Returns:
        pd.DataFrame: Cleaned DataFrame ready for analysis or modeling.
    """
    # --- Load dataset ---
    df = pd.read_csv(input_path)

    # --- Data Type Fixes ---
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['account_age_days'] = pd.to_numeric(df['account_age_days'], errors='coerce')
    df['transaction_amount'] = pd.to_numeric(df['transaction_amount'], errors='coerce')
    df['avg_transaction_amount'] = pd.to_numeric(df['avg_transaction_amount'], errors='coerce')
    df['failed_login_attempts'] = pd.to_numeric(df['failed_login_attempts'], errors='coerce')
    df['velocity_check'] = pd.to_numeric(df['velocity_check'], errors='coerce')

    # --- Handle categorical text issues ---
    if 'kyc_verified' in df.columns:
        df['kyc_verified'] = df['kyc_verified'].astype(str).str.strip().str.title().replace({'Yes': 1, 'No': 0})
    df['multi_device_login'] = pd.to_numeric(df['multi_device_login'], errors='coerce')

    # --- Fill missing values logically ---
    df['kyc_verified'] = df['kyc_verified'].fillna(0)
    df['channel'] = df['channel'].fillna('Unknown')
    df['location'] = df['location'].fillna('Unknown')
    df['currency'] = df['currency'].fillna('USD')
    df['transaction_type'] = df['transaction_type'].fillna('Transfer')

    # For numeric fields, fill missing with median
    numeric_cols = ['account_age_days', 'transaction_amount', 'avg_transaction_amount', 'failed_login_attempts', 'velocity_check']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # --- Logical fixes ---
    df.loc[df['account_age_days'] < 0, 'account_age_days'] = 0
    df.loc[df['transaction_amount'] < 0, 'transaction_amount'] = abs(df['transaction_amount'])
    df['is_fraud'] = df['is_fraud'].astype(int)

    # --- Drop duplicates ---
    df = df.drop_duplicates(subset=['transaction_id'])

    # --- Save cleaned dataset ---
    df.to_csv(output_path, index=False)
    print(f"✅ Cleaning completed. Cleaned file saved as '{output_path}'")

    return df
