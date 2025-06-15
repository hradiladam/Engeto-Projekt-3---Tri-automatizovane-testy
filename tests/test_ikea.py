import pytest
from playwright.sync_api import expect


@pytest.fixture(autouse=True, scope="function")
def page(playwright, browser_name):
    browser = getattr(playwright, browser_name).launch(headless=False, slow_mo=200)
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
    browser.close()


@pytest.fixture(autouse=True, scope="function")
def accept_cookies(page):
    page.goto("https://www.ikea.com/cz/cs/")
    accept_btn = page.get_by_role("button", name="Přijmout vše")

    try:
        if accept_btn.is_visible(timeout=5000):
            accept_btn.click()
            print("\nDEBUG: Cookie button clicked")
    except:
        print("\nDEBUG: Cookie button not found or failed to click")


# Test that switches the site to English and verifies that the nearest store is correctly selected based on a user-provided postal code
# Checks all 4 options in Czechia
@pytest.mark.parametrize("postal_code, expected_id, expected_text", [
    ("25262", "choice-178", "Praha – Zličín"),
    ("61400", "choice-278", "Brno"),
    ("19800", "choice-408", "Praha – Černý Most"),
    ("75131", "choice-309", "Ostrava"),
])
def test_ikea_find_nearest_store_eng(page, postal_code, expected_id, expected_text):
    # --- Change language to English ---
    language_button = page.get_by_role("button", name="Změna jazyka nebo země, aktuá")
    language_button.click()
    print("DEBUG: Clicked language button")

    # Wait for the language panel to show
    page.locator("div.hnf-sheets__content-wrapper").wait_for(state="visible")
    print("DEBUG: Language panel visible")

    # Click on English
    english_button = page.get_by_role("button", name="English")
    english_button.click()
    print("DEBUG: Selected English language")

    # Wait for the English site to load
    page.wait_for_load_state("load")
    expect(page).to_have_url("https://www.ikea.com/cz/en/")
    print("DEBUG: English site loaded with correct URL")

    # --- Choose store by postal code ---
    select_store_button = page.get_by_role("button", name="Select store")
    select_store_button.click()
    print("DEBUG: Clicked 'Select store' button")

    # Type the postal code
    search_input = page.get_by_role("searchbox", name="Search by location")
    search_input.fill(postal_code)
    search_input.press("Enter")
    print(f"DEBUG: Entered postal code '{postal_code}' and pressed Enter")

    # Wait for and verify the first (nearest) store has the expected ID attribute
    first_store_div = page.locator("div.hnf-store-picker__storelist > ul > li > div").first
    expect(first_store_div).to_have_attribute("id", expected_id, timeout=10000)
    actual_id = first_store_div.get_attribute("id")
    print(f"DEBUG: Verified store has id '{actual_id}' (expected '{expected_id}')")

    # Verify the store name text inside
    store_name = first_store_div.locator("button > span > span > span.hnf-choice-item__title")
    expect(store_name).to_have_text(expected_text, timeout=5000)
    print(f"DEBUG: Verified store name text is '{expected_text}'")
    
    # Click on the first store
    button = first_store_div.get_by_role("button")  # Button inside the div with store id
    button.click()
    print("DEBUG: Clicked the first store button")

    # Check that the selected store name appears in the header
    selected_store = page.locator("#hnf-header-storepicker > a > span.hnf-utilities__value")
    selected_store.wait_for(state="visible", timeout=10000)
    expect(selected_store).to_have_text(expected_text, timeout=10000)
    print(f"DEBUG: Verified selected store name in header: '{expected_text}'")

# pytest tests/test_ikea.py -s
# pytest tests/test_ikea.py --browser chromium -s
# pytest tests/test_ikea.py --browser firefox -s
# pytest tests/test_ikea.py --browser webkit -s
