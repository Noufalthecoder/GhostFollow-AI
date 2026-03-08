"""
Run once to save Gmail session into storage_state.json for Playwright automation.

Usage:
  python automation/save_gmail_session.py
"""

from playwright.sync_api import sync_playwright


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://mail.google.com", wait_until="domcontentloaded")
        input("Log into Gmail in the opened browser, then press Enter to save session...")
        context.storage_state(path="storage_state.json")
        context.close()
        browser.close()
        print("Saved Gmail session to storage_state.json")
