from utils.supabase_client import supabase

response = supabase.table("reports").select("*").execute()
print(response)
