import os
import hashlib
import secrets
import pandas as pd

SALT_FILE = "salt.txt"
ANON_FILE = "anonymized_call_logs.csv"

# Generating a cryptographically secure random salt
def generate_salt(length: int = 32) -> str:
    return secrets.token_hex(length)

# Return a sanitized dataframe using a given salt.
def sanitize(df: pd.DataFrame, salt: str) -> pd.DataFrame:

    # A vectorized hasher for the purposes of perfomance over apply()
    hasher = lambda value: hashlib.sha256(f"{value}{salt}".encode()).hexdigest()[:10]

    # Appending a hash column
    df["user_hash"] = df["number"].map(hasher)

    # A list of safe columns
    safe_columns = ["user_hash", "duration", "date", "type"]

    # Buiding the final anonymized df.
    safe_df = df[safe_columns].copy()
    return safe_df

def anonymize(filepath: str) -> pd.DataFrame:
    parent_dir = os.path.dirname(filepath)
    salt_path = os.path.join(parent_dir, SALT_FILE)
    anon_path = os.path.join(parent_dir, ANON_FILE)
    
    # If an anonymized dataset already exists, load and return
    if os.path.exists(anon_path) and os.path.exists(salt_path):
        return pd.read_csv(anon_path)

    # If there isn't an anonymized file, create one
    df = pd.read_xml(filepath)

    # Load existing salt or create new one
    if os.path.exists(salt_path):
        with open(salt_path, "r") as f:
            salt = f.read().strip()
    else:
        salt = generate_salt()
        with open(salt_path, "w") as f:
            f.write(salt)

    # Build sanitized DF
    df_safe = sanitize(df, salt)

    # Save anonymized version
    df_safe.to_csv(anon_path, index=False)

    return df_safe 

