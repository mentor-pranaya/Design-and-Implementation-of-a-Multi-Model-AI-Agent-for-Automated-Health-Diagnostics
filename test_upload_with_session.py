#!/usr/bin/env python3
"""Test file upload with session token."""

import requests

# Login to get a session token
login_data = {'username': 'test', 'password': 'secret', 'role': 'patient'}
r = requests.post('http://localhost:10000/api/login/', json=login_data)
print('Login:', r.status_code)

if r.status_code == 200:
    token = r.json().get('access_token')
    print('Token:', token)
    
    # Upload a file using the session token
    files = {'file': open('data/test_report.png', 'rb')}
    headers = {'x-api-key': token}
    r2 = requests.post('http://localhost:10000/analyze-report/', files=files, headers=headers)
    print('Upload:', r2.status_code)
    
    if r2.status_code == 200:
        result = r2.json()
        print('Success:', result.get('status'))
        print('Synthesis present:', bool(result.get('synthesis')))
    else:
        print('Error:', r2.text)
else:
    print('Login failed:', r.text)
