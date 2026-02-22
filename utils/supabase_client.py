from supabase import create_client
import os

SUPABASE_URL = "https://fcjkzajvblufrgvwexep.supabase.co"
SUPABASE_KEY = "sb_publishable_0Q3jJXrBsDozfwmaHYqIdQ_Ym7j9hdQ"

supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
