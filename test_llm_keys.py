import os

keys_to_check = ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'CLAUDE_API_KEY']

for key in keys_to_check:
    value = os.getenv(key)
    if value:
        print(f"{key}: Set (length: {len(value)})")
    else:
        print(f"{key}: Not set")
