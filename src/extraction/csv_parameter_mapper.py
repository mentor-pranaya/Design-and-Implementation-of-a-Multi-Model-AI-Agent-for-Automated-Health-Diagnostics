import pandas as pd
import io

def extract_parameters_from_csv(content: bytes) -> dict:
    try:
        df = pd.read_csv(io.BytesIO(content))
        params = {}
        
        # Check if we have 'Parameter' and 'Value' columns
        cols = [c.lower() for c in df.columns]
        if 'parameter' in cols and 'value' in cols:
            p_idx = cols.index('parameter')
            v_idx = cols.index('value')
            for _, row in df.iterrows():
                try:
                    p_name = str(row.iloc[p_idx]).lower()
                    p_val = float(row.iloc[v_idx])
                    params[p_name] = p_val
                except (ValueError, TypeError):
                    continue
        else:
            # Fallback: take numeric columns from the first row
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    params[col.lower()] = df[col].iloc[0] if not df[col].empty else 0
        return params
    except Exception:
        return {}
