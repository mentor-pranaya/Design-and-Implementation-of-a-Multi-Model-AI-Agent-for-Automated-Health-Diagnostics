import pandas as pd
import io

def extract_parameters_from_csv(content: bytes) -> dict:
    try:
        df = pd.read_csv(io.BytesIO(content))
        params = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                params[col.lower()] = df[col].iloc[0] if not df[col].empty else 0
        return params
    except Exception:
        return {}
