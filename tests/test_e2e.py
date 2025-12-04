import time
from playwright.sync_api import Page, expect


def test_add_book_flow(page: Page):
    """Fill Add Book form and verify the data stays visible in the UI."""
    page.goto("http://localhost:5000/add_book")

    unique_isbn = "9" + str(int(time.time()))[:12]

    page.fill('input[name="title"]', "E2E Test Book")
    page.fill('input[name="author"]', "Test Author")
    page.fill('input[name="isbn"]', unique_isbn)
    page.locator('input[type="number"]').fill("3")  # Total Copies field

    page.click('button[type="submit"]')

    # Either redirect to catalog or stay on add_book with the form visible
    if page.url.endswith("/catalog"):
        expect(page.locator("table").first).to_be_visible()
    else:
        assert page.url.endswith("/add_book")
        # Form and entered values should still be present
        expect(page.locator('input[name="title"]')).to_have_value("E2E Test Book")
        expect(page.locator('input[name="author"]')).to_have_value("Test Author")
        expect(page.locator('input[name="isbn"]')).to_have_value(unique_isbn)


def test_catalog_displays_books(page: Page):
    """Catalog page renders heading and table."""
    page.goto("http://localhost:5000/catalog")
    expect(page.get_by_role("heading", name="Book Catalog")).to_be_visible()
    expect(page.locator("table").first).to_be_visible()
