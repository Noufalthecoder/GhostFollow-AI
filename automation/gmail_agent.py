import os
from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def send_gmail_followup(
    recipient_email: str | None,
    subject_hint: str,
    followup_message: str,
    thread_query: str,
) -> dict[str, Any]:
    """
    Automates Gmail Web to send a follow-up by interacting with visible UI elements.

    Setup requirements for real runs:
    1) playwright install
    2) Valid Gmail session saved in storage_state.json
    """
    if not followup_message:
        return {"status": "failed", "detail": "Follow-up message is empty."}

    storage_state = os.getenv("GMAIL_STORAGE_STATE", "storage_state.json")
    headless = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower() == "true"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless, slow_mo=180)
            context = (
                browser.new_context(storage_state=storage_state)
                if os.path.exists(storage_state)
                else browser.new_context()
            )
            page = context.new_page()
            page.goto("https://mail.google.com/mail/u/0/#inbox", wait_until="domcontentloaded")

            page.wait_for_timeout(2000)
            search_box = page.locator('input[aria-label="Search mail"]')
            if search_box.count() > 0:
                search_term = thread_query or recipient_email or subject_hint
                search_box.fill(search_term)
                search_box.press("Enter")
                page.wait_for_timeout(1800)

            # Open the first matching thread row.
            thread_row = page.locator('tr.zA').first
            thread_row.click(timeout=6000)
            page.wait_for_timeout(1200)

            reply_button = page.locator('div[role="button"][aria-label*="Reply"]').first
            reply_button.click(timeout=5000)

            editor = page.locator('div[aria-label="Message Body"]').last
            editor.click(timeout=5000)
            editor.fill(followup_message)

            send_button = page.locator('div[role="button"][aria-label*="Send"]').last
            send_button.click(timeout=5000)

            page.wait_for_timeout(1200)
            context.close()
            browser.close()

            return {"status": "sent", "detail": "Follow-up sent via Gmail automation."}

    except PlaywrightTimeoutError as exc:
        return {"status": "failed", "detail": f"Timeout in Gmail workflow: {exc}"}
    except Exception as exc:
        return {"status": "failed", "detail": f"Gmail automation failed: {exc}"}


if __name__ == "__main__":
    sample = send_gmail_followup(
        recipient_email="customer@example.com",
        subject_hint="Pricing question",
        followup_message="Hi! Quick follow-up in case this got buried in your inbox.",
        thread_query="Pricing",
    )
    print(sample)
