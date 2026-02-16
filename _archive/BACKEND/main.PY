from fastapi import FastAPI, UploadFile
import pandas as pd

app = FastAPI(title="Health Diagnostics API")

@app.get("/")
def home():
    return {"message": "Backend is running successfully"}

@app.post("/analyze")
async def analyze(file: UploadFile):
    df = pd.read_csv(file.file)
    return {
        "rows": len(df),
        "columns": df.columns.tolist()
    }

