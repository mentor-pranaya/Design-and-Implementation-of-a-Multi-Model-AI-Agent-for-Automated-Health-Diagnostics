import requests

# Test CSV upload
url = "http://localhost:8000/api/upload"
files = {'file': open('test_samples/anemic_high_cholesterol.csv', 'rb')}
response = requests.post(url, files=files)

print("Status Code:", response.status_code)
print("Response:", response.json() if response.headers.get('content-type') == 'application/json' else response.text)
