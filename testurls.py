#!/usr/bin/env python3
# Usage : python3 testurls.py 

import requests

url = "https://raw.githubusercontent.com/aluusre/CRLproject/main/CRLURLs.json"
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



"""
Requirement:
brew install python3
python3 -m pip install requests
python3 -m pip show requests

DC-C02G10ZDMD6T CRLproject % python3 testurls.py 
/Users/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(
HTTP Status: 200
JSON Data: {'eventType': 'CDNCheck', 'type': 'crl', 'urls': ['http://crl.digicert.cn/DigiCertAssuredIDRootCA.crl', 'http://crl3.digicert.com/DigiCertGlobalRootCA.crl']}
"""
