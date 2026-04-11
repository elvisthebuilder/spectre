"""
SPECTRE Component Test: Perplexity Account Creator
Run: .venv/bin/python test_perplexity.py
"""
import sys
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
logger = logging.getLogger("SPECTRE-TEST")

# Step 1: Check for emailnator cookies
cookies_path = os.path.join(os.path.dirname(__file__), "emailnator_cookies.json")
if not os.path.exists(cookies_path):
    print(f"\n✗ FAIL: emailnator_cookies.json not found at {cookies_path}")
    sys.exit(1)

with open(cookies_path) as f:
    emailnator_cookies = json.load(f)
print(f"✓ Emailnator cookies loaded: {list(emailnator_cookies.keys())}")

# Step 2: Test CSRF endpoint
from perplexity.client import Client
print("\n--- Testing CSRF Token Fetch ---")
client = Client()
print(f"✓ Client initialized. Copilot quota: {client.copilot}")

try:
    resp = client.session.get("https://www.perplexity.ai/api/auth/csrf", timeout=10)
    print(f"✓ CSRF response status: {resp.status_code}")
    data = resp.json()
    print(f"✓ CSRF response body: {data}")
    csrf = data.get("csrfToken")
    if csrf:
        print(f"✓ CSRF token: {csrf[:12]}...")
    else:
        print(f"✗ No csrfToken in response. Full body: {resp.text[:300]}")
except Exception as e:
    print(f"✗ CSRF fetch failed: {e}")
    sys.exit(1)

# Step 3: Test Emailnator
print("\n--- Testing Emailnator ---")
from perplexity.emailnator import Emailnator
try:
    enator = Emailnator(emailnator_cookies)
    print(f"✓ Generated disposable email: {enator.email}")
except Exception as e:
    print(f"✗ Emailnator failed: {e}")
    sys.exit(1)

# Step 4: Send sign-in request
print("\n--- Sending Sign-In Request to Perplexity ---")
from perplexity.config import ENDPOINT_AUTH_SIGNIN
try:
    resp = client.session.post(
        ENDPOINT_AUTH_SIGNIN,
        json={
            "email": enator.email,
            "csrfToken": csrf,
            "callbackUrl": "https://www.perplexity.ai/",
            "json": "true",
        },
        timeout=10,
    )
    print(f"✓ Sign-in response status: {resp.status_code}")
    print(f"✓ Sign-in response body: {resp.text[:300]}")
except Exception as e:
    print(f"✗ Sign-in request failed: {e}")
    sys.exit(1)

# Step 5: Wait for email
if resp.ok:
    print("\n--- Waiting for sign-in email (20s timeout) ---")
    new_msgs = enator.reload(
        wait_for=lambda x: x["subject"] == "Sign in to Perplexity",
        timeout=20,
    )
    if new_msgs:
        print(f"✓ Email received: {new_msgs}")
    else:
        print("✗ No email received within 20 seconds.")
        print("  (Possible causes: Perplexity blocked the sign-in, or Emailnator cookies are stale)")
else:
    print(f"✗ Sign-in was rejected by Perplexity. Status: {resp.status_code}")

print("\n=== Test Complete ===")
print("\n--- Test fetching email body ---")
msg = new_msgs[0]
print(f"Opening msg: {msg['messageID']}")
body = enator.open(msg["messageID"])
print(body)
import re
match = re.search(r"https://www\.perplexity\.ai/api/auth/callback/email\?[^\s\"'<]+", body)
if match:
    print(f"Matched signin URL: {match.group(0)}")
else:
    print("NO MATCH! Links in body:")
    for link in re.findall(r"href=[\"'](http[^\"]+)[\"']", body):
        print(" -", link)
