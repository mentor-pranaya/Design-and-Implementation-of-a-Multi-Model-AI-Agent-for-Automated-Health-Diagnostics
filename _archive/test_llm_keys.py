import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

keys_to_check = ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'CLAUDE_API_KEY']

print("=" * 50)
print("LLM API Key Status")
print("=" * 50)

for key in keys_to_check:
    value = os.getenv(key)
    if value:
        # Mask most of the key for security
        masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
        print(f"✓ {key}: Set ({masked})")
    else:
        print(f"✗ {key}: Not set")

print("=" * 50)
print("Note: Keys are loaded from .env file")
print("=" * 50)
