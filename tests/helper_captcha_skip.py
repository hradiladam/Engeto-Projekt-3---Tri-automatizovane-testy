def is_human_interaction_required(page):
    # Detect Cloudflare / CAPTCHA / other human-check elements
    if page.get_by_text("Prosím, potvrďte, že jste z masa a kostí", exact=False).is_visible(timeout=3000):
        return True
    return False