import pandas as pd

def extract_data_from_csv(file):
    # Read CSV
    df = pd.read_csv(file.file)

    # Normalize headers
    df.columns = [c.strip().lower() for c in df.columns]

    # Drop empty rows
    df = df.dropna(how="all")

    # Convert numeric values safely
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    return df
