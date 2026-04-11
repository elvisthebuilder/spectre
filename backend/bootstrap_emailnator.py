"""
SPECTRE: Emailnator Cookie Bootstrapper
Visits Emailnator via Playwright, waits for valid cookies, saves them.
Run: .venv/bin/python bootstrap_emailnator.py
"""
import json
import os
import time

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "emailnator_cookies.json")

def bootstrap():
    print("=== SPECTRE Emailnator Cookie Bootstrapper ===")
    print("Launching browser to capture fresh Emailnator session...")
    
    try:
        from patchright.sync_api import sync_playwright as sync_patchright
        print("Using patchright (undetected mode)")
        use_patchright = True
    except ImportError:
        from playwright.sync_api import sync_playwright
        use_patchright = False
        print("Using standard playwright")

    with (sync_patchright() if use_patchright else sync_playwright()) as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context()
        page = context.new_page()
        
        print("Navigating to https://www.emailnator.com/ ...")
        page.goto("https://www.emailnator.com/", wait_until="domcontentloaded", timeout=60000)
        
        print("Waiting 5 seconds for critical scripts and cookies to settle...")
        time.sleep(5)
        
        # Trigger a fresh email generation to ensure session is active
        try:
            generate_btn = page.locator("button:has-text('Generate'), button:has-text('New'), [id*='generate'], [class*='generate']").first
            if generate_btn.count() > 0:
                generate_btn.click()
                time.sleep(2)
        except:
            pass
        
        # Extract all cookies for the domain
        cookies = context.cookies("https://www.emailnator.com")
        
        if not cookies:
            print("✗ No cookies found! The site may have changed structure.")
            browser.close()
            return

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]
        
        print(f"✓ Captured {len(cookies)} cookies: {list(cookie_dict.keys())}")
        
        # Check that XSRF-TOKEN is present
        if "XSRF-TOKEN" not in cookie_dict:
            print("✗ WARNING: XSRF-TOKEN not found in cookies!")
            print(f"  Available: {list(cookie_dict.keys())}")
        else:
            print(f"✓ XSRF-TOKEN captured: {cookie_dict['XSRF-TOKEN'][:20]}...")
        
        # Save cookies
        with open(OUTPUT_PATH, "w") as f:
            json.dump(cookie_dict, f, indent=2)
        
        print(f"\n✓ Fresh cookies saved to: {OUTPUT_PATH}")
        print("=== Bootstrap Complete ===")
        browser.close()

if __name__ == "__main__":
    bootstrap()
