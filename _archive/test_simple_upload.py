#!/usr/bin/env python3
"""Simple test for file upload."""
import requests

files = {'file': open('data/test_report.png', 'rb')}
r = requests.post('http://localhost:10000/analyze-report/', files=files)
print('Status:', r.status_code)
print('Success:', r.json().get('status'))
