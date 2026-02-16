import requests

URL = "http://localhost:10000/analyze-report/"
API_KEY = "secret"

# Create a dummy PDF content
dummy_pdf = b"%PDF-1.5 dummy content"

test_files = [
    ("test.pdf", dummy_pdf),
    ("test.PDF", dummy_pdf),  # Test case sensitivity
    ("test.txt", dummy_pdf),  # Supported type
    ("test.webp", dummy_pdf), # Supported type
]

print(f"Testing upload at {URL}...")

for filename, content in test_files:
    print(f"\nUploading {filename}...")
    files = {'file': (filename, content, 'application/pdf')}
    headers = {'x-api-key': API_KEY}
    
    try:
        response = requests.post(URL, files=files, headers=headers)
        if response.status_code == 200:
            print(f"SUCCESS: {filename}")
        else:
            print(f"FAILED: {filename} -> {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error: {e}")
