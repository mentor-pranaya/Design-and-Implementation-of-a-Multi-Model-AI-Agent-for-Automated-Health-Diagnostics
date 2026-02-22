import os
from typing import Dict, Optional

try:
    from supabase import create_client  # supabase-py
except Exception:  # pragma: no cover - optional runtime
    create_client = None


def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set in environment to use Supabase features.")
    if create_client is None:
        raise ImportError("supabase package not installed. Install with `pip install supabase`")
    return create_client(url, key)


def save_report(report_path: str, metadata: Optional[Dict] = None) -> Dict:
    """Upload a report PDF to Supabase storage and insert metadata into `reports` table.

    This function requires `SUPABASE_URL` and `SUPABASE_KEY` environment variables.
    It also expects a `reports` bucket and `reports` table to exist in Supabase project.
    """
    client = get_supabase_client()

    bucket = "reports"
    file_name = os.path.basename(report_path)

    # Upload file
    with open(report_path, "rb") as fh:
        data = fh.read()

    storage = client.storage()
    res = storage.from_(bucket).upload(file_name, data)
    if res.get("error"):
        raise RuntimeError(f"Supabase storage upload failed: {res['error']}")

    public_url = storage.from_(bucket).get_public_url(file_name).get("publicURL")

    # Insert metadata
    meta = metadata or {}
    meta_record = {"file_name": file_name, "url": public_url, **meta}
    db = client.table("reports")
    insert_res = db.insert(meta_record).execute()
    return {"storage": res, "metadata_insert": insert_res}


def list_reports(limit: int = 50):
    client = get_supabase_client()
    db = client.table("reports")
    return db.select("*").limit(limit).execute()
