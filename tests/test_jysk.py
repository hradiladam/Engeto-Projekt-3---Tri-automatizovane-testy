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
    page.goto("https://jysk.cz/")
    accept_necessary_btn = page.get_by_role("button", name="Nezbytně nutné")

    try:
        if accept_necessary_btn.is_visible(timeout=5000):
            accept_necessary_btn.click()
            print("\nDEBUG: Cookie button clicked")
    except:
        print("\nDEBUG: Cookie button not found or failed to click")


# Test that checks that filtering by quality works and displayed items are items of selected quality
#  - tested with mattresses
@pytest.mark.parametrize("quality", [
    "BASIC",
    "PLUS",
    "GOLD",
])
def test_size_and_firmness_filter(page, quality):

    # Selecting category of mattrasses
    menu_btn = page.get_by_role("link", name="Menu")
    menu_btn.click()

    menu_bar = page.locator("#mega-menu-content > div > div.off-canvas-container.lowerModal-container")
    menu_bar.wait_for(state="visible", timeout=10000)
    expect(menu_bar).to_be_visible(timeout=10000)
    print("DEBUG: Menu displayed")

    page.get_by_role("link", name="Postele a matrace").click()
    page.get_by_role("link", name="Zobrazit vše").click()
    expect(page).to_have_url("https://jysk.cz/loznice/matrace")
    print("DEBUG: Page with mattrasses has been loaded")

    # Choosing quality
    all_filters_btn = page.get_by_role("button", name="Všechny filtry")
    all_filters_btn.wait_for(state="visible")
    all_filters_btn.click()

    filters_bar = page.locator("div.off-canvas-content.off-canvas-content--sticky").filter(has_text="Filtry")
    filters_bar.wait_for(state="visible", timeout=25000)
    expect(filters_bar).to_be_visible(timeout=25000)
    print("DEBUG: Menu with filters for mattresses is diplayed")

    # Choose quality
    page.get_by_role("button", name="Kvalita", exact=True).click()
    page.get_by_role("checkbox", name=quality).check()
    print("DEBUG: Quality selected")

    # Display results
    page.get_by_role("button", name="Zobrazit výsledky vyhledávání:").click()
    print("DEBUG: Results selected")

    # Check that filters are registered
    selected_filters = page.locator("div.w3-pills-container").nth(0)
    expect(selected_filters).to_contain_text(quality)
    print("DEBUG: Selected filters have been registered correctly")

    # Scroll to the bottom to ensure all products are loaded (lazy loading)
    page.mouse.wheel(0, 15000)
    page.wait_for_timeout(10000)  # Give time for lazy content to load/render

    # Count visible mattresses displayed on page after using "quality" in the filter
    product_locator = page.locator("div.product-teaser-body")
    total_products = product_locator.count()

    # Count how many are visible
    visible_count = sum(product_locator.nth(i).is_visible() for i in range(total_products))
    print(f"DEBUG: There are {visible_count} displayed mattresses after applying the quality filter: {quality}")

    # Now individually check each visible product's sticker text matches quality (case-insensitive)
    for i in range(total_products):
        product = product_locator.nth(i)
        if product.is_visible():
            sticker = product.locator("span.sticker-text")
            sticker_text = sticker.text_content()
            # Only check if sticker text is not empty
            if sticker_text:
                expect(sticker).to_have_text(quality, ignore_case=True)
    print(f"DEBUG: All displayed products' quality stickers match selected quality of: {quality}")




# pytest tests/test_jysk.py -s
# pytest tests/test_jysk.py --browser chromium -s
# pytest tests/test_jysk.py --browser firefox -s
# pytest tests/test_jysk.py --browser webkit -s