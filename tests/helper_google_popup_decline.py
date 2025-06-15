def dismiss_google_popup_if_present(page):
    try:
        iframe_locator = page.locator('iframe[title*="přihlášení přes Google"], iframe[title*="Google sign-in dialog"]')
        if iframe_locator.is_visible(timeout=3000):
            print("DEBUG: Google sign-in iframe IS visible")

            # Try to interact with the iframe's close button
            iframe = page.frame_locator('iframe[title*="přihlášení přes Google"], iframe[title*="Google sign-in dialog"]')
            close_btn = iframe.locator('div[aria-label="Zavřít"], div[aria-label="Close"]')

            if close_btn.is_visible(timeout=3000):
                close_btn.click()
                print("DEBUG: Closed Google sign-in dialog")

            # Wait for iframe to be removed from DOM entirely
            page.wait_for_selector('iframe[title*="přihlášení přes Google"], iframe[title*="Google sign-in dialog"]', state="detached", timeout=10000)
            print("DEBUG: Google sign-in iframe detached")

        else:
            print("DEBUG: Google sign-in iframe not visible")

    except Exception as e:
        print(f"DEBUG: Error while dismissing Google popup: {e}")
