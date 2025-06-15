# NOTE:
# This test includes handling for CAPTCHA detection taht occurs on webkit excusivelly. It is designed to skip this specific Captcha. I am not sure if the way it is implemented is proper.
# This test includes handling for Google sign-in popups that occur on firefox and webkit. I am again not sure if it is implemented properly.


import pytest
from playwright.sync_api import expect, TimeoutError
from tests.helper_captcha_skip import is_human_interaction_required
from tests.helper_google_popup_decline import dismiss_google_popup_if_present


@pytest.fixture(autouse=True, scope="function")
def page(playwright, browser_name):
    browser = getattr(playwright, browser_name).launch(headless=False, slow_mo=200)
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
    browser.close()


@pytest.fixture(autouse=True)
def accept_cookies(page):
    page.goto("https://www.alza.cz/")
    
    if is_human_interaction_required(page):
        pytest.skip("Human verification required (e.g. CAPTCHA or Cloudflare)")

    accept_btn = page.get_by_role("link", name="Rozumím")
    
    try:
        if accept_btn.is_visible(timeout=5000):
            accept_btn.click()
            print("\nDEBUG: Cookie button clicked")
    except:
        print("\nDEBUG: Cookie button not found or failed to click")


# Test that checks that user is offered AlzaPlus subscribtion when in cart going through Payment and Delivery options
@pytest.mark.parametrize("item", [
    "Dell Alienware AW3423DW",
    "Marshall Monitor III",
    "BOSCH MUMS2EW40"
])
def test_alza_plus_offered_in_cart_eng(page, item):
    # ---Switch to Eng---
    lang_btn = page.get_by_test_id("headerLanguageSwitcher").get_by_role("img", name="CZ")
    lang_btn.wait_for(state="visible", timeout=10000)
    lang_btn.click()
    print("DEBUG: Clicked language button")

    lang_tab = page.get_by_text("Alza.cz - Jazyk / LanguageČeš")
    lang_tab.wait_for(state="visible")
    print("DEBUG: Language panel visible")

    page.get_by_role("button", name="English English").click()
    page.get_by_role("button", name="Potvrdit / Confirm").click()
    print("DEBUG: Selected English language")
    
    page.wait_for_load_state("load")
    expect(page).to_have_url("https://www.alza.cz/EN/?setlang=en-GB")
    print("DEBUG: English site loaded with correct URL")

    # --- Search for item and add it to cart---

    dismiss_google_popup_if_present(page) # Remove google account sign-in popup

    searchbox = page.get_by_role("combobox", name="What are you looking for? E.g")
    searchbox_btn = page.get_by_test_id("button-search")

    searchbox.wait_for(state="visible", timeout=5000)
    searchbox.click()
    searchbox.fill(item)

    searchbox_btn.click()
    
    buy_btn = page.locator("a.btnk1").first
    buy_btn.click()
    print("DEBUG: Items added to the cart")

    dismiss_google_popup_if_present(page)  # Remove google account sign-in popup

    # Check that item was added to cart, go to the cart and check that order page opens
    
    basket_btn = page.get_by_title("Go to Shopping Cart")
    expect(basket_btn).to_contain_text("1")

    dismiss_google_popup_if_present(page)  # Remove google account sign-in popup

    basket_btn.click()
    expect(page).to_have_url("https://www.alza.cz/Order1.htm")

    dismiss_google_popup_if_present(page) # Remove google account sign-in popup

    # Progress to payment and delviery page
    continue_btn = page.get_by_role("link", name="Continue", exact=True)
    continue_btn.wait_for(state="visible")  # Wait until visible
    continue_btn.click()

    dismiss_google_popup_if_present(page) # Remove google account sign-in popup

    try:
        offer_tab = page.get_by_text("Do not forget these important things May come in handy This issue can be solved")
        offer_tab.wait_for(state="visible", timeout=5000)  # wait max 5 seconds
        print("DEBUG: Add items panel visible")

        decline_btn = page.get_by_text("Do not add anything")
        decline_btn.click()
        print("DEBUG: Declined additional items offer")

    except TimeoutError:
        print("DEBUG: Add items panel did not appear, continuing without declining")

    dismiss_google_popup_if_present(page) # Remove google account sign-in popup

    # Check that Alza Plus offer is visible on payment and delviery page and includes both 1-year-membership and monthly subsciption
    alza_plus_banner = page.get_by_text("FREE shipping on everything with AlzaPlus+Activate AlzaPlus+ and get FREE")
    expect(alza_plus_banner).to_be_visible()
    print("DEBUG: Alza Plus banner is visible")

    one_year_membership = page.get_by_test_id("apSubsType1")
    expect(one_year_membership).to_be_visible()
    print("DEBUG: 1-year memebrship option is available")

    monthly_subscription = page.get_by_test_id("apSubsType2")
    expect(monthly_subscription).to_be_visible()
    print("DEBUG: Monthly subtsciption is available")

    # Cleanup of the cart
    back_btn = page.get_by_role("link", name="Back")
    back_btn.click()
    
    empty_cart_label = page.get_by_text("Empty cart")
    empty_cart_label.wait_for(state="visible", timeout=5000)
    empty_cart_label.click()

    flush_button = page.get_by_test_id("basketItems_flushButton")
    flush_button.wait_for(state="visible", timeout=5000)
    flush_button.click()

    confirm_button = page.get_by_role("button", name="Empty cart")
    confirm_button.wait_for(state="visible", timeout=5000)
    confirm_button.click()

# pytest tests/test_alza.py -s
# pytest tests/test_alza.py --browser chromium -s
# pytest tests/test_alza.py --browser firefox -s
# pytest tests/test_alza.py --browser webkit -s

    

    

