"""
SPECTRE Diagnostic: Emailnator Cookie Validator
Run: .venv/bin/python test_emailnator_raw.py
"""
import json
import sys
import os
from curl_cffi import requests

cookies_path = os.path.join(os.path.dirname(__file__), "emailnator_cookies.json")
with open(cookies_path) as f:
    cookies = json.load(f)

from urllib.parse import unquote
xsrf = unquote(cookies.get("XSRF-TOKEN", ""))

headers = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "x-xsrf-token": xsrf,
    "origin": "https://www.emailnator.com",
    "referer": "https://www.emailnator.com/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

s = requests.Session(headers=headers, cookies=cookies, impersonate="chrome")

print("=== RAW Emailnator Generate Probe ===")
try:
    resp = s.post(
        "https://www.emailnator.com/generate-email",
        json={"email": ["googleMail"]},
        timeout=10
    )
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text[:500]}")
except Exception as e:
    print(f"Request failed: {e}")
