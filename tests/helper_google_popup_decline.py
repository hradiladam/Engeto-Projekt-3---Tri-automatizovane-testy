def dismiss_google_popup_if_present(page):
    try:
        iframe = page.frame_locator("iframe[title='Dialogové okno přihlášení přes Google']")
        close_btn = iframe.get_by_role("button", name="Zavřít")

        if close_btn.is_visible(timeout=3000):
            print("DEBUG: Google sign-in iframe IS visible")
            close_btn.click()
            # Wait for iframe to be detached or hidden after click
            page.wait_for_selector("iframe[title='Dialogové okno přihlášení přes Google']", state="detached", timeout=5000)
            print("DEBUG: Closed Google sign-in dialog and iframe detached")
        else:
            print("DEBUG: Google sign-in iframe not visible")
    except Exception as e:
        print(f"DEBUG: Google popup dismissal failed or not needed: {e}")
