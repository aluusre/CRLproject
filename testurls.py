#!/usr/bin/env python3
# Usage : python3 testurls.py 

import requests

url = "https://raw.githubusercontent.com/aluusre/CRLproject/main/CRLurls2.json"
response = requests.get(url)

print("HTTP Status:", response.status_code)

if response.status_code == 200:
    try:
        data = response.json()
        print("JSON Data:", data)
    except ValueError:
        print("Response is not valid JSON. Raw text:\n", response.text)
else:
    print("Failed to fetch JSON. Raw response:\n", response.text)
