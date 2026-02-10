import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from automation_framework.config.driver_manager import DriverManager
from automation_framework.platforms.web.selenium_helper import SeleniumHelper

@pytest.fixture(scope="module")
def driver():
    """Provide a WebDriver instance using DriverManager."""
    driver_manager = DriverManager()
    web_driver = driver_manager.get_driver()
    yield web_driver
    # Teardown: Quit the driver after all tests in the module run
    web_driver.quit()

@pytest.fixture
def helper(driver):
    """Provide a SeleniumHelper instance."""
    return SeleniumHelper(driver)

class TestSeleniumHelperWaits:
    """
    Simple functional tests for SeleniumHelper wait methods.
    These tests assume a local HTML file or a test server is available.
    """
    # Replace this with your actual test page URL.
    TEST_PAGE_URL = "file:///path/to/your/test_page.html" # Or e.g., "http://localhost:8000/test.html"

    def test_wait_for_element_present_success(self, helper):
        """
        Tests that wait_for_element_present returns True when the element exists in the DOM.
        Assumes the test page has an element with id 'existing-div'.
        """
        helper.driver.get(self.TEST_PAGE_URL)
        xpath = "//div[@id='existing-div']"

        result = helper.wait_for_element_present(xpath)
        assert result is True

    def test_wait_for_element_present_timeout(self, helper):
        """
        Tests that wait_for_element_present returns False when the element does not appear within the timeout.
        Uses a short timeout and an element that does not exist on the page.
        """
        helper.driver.get(self.TEST_PAGE_URL)
        xpath = "//div[@id='non-existent-div']"

        result = helper.wait_for_element_present(xpath, timeout=2)
        assert result is False

    def test_wait_for_element_visible_success(self, helper):
        """
        Tests that wait_for_element_visible returns True when the element exists and is visible.
        Assumes the test page has a visible element with class 'visible-text'.
        """
        helper.driver.get(self.TEST_PAGE_URL)
        xpath = "//p[@class='visible-text']"

        result = helper.wait_for_element_visible(xpath)
        assert result is True

    def test_wait_for_element_visible_timeout(self, helper):
        """
        Tests that wait_for_element_visible returns False when the element remains hidden or does not appear within the timeout.
        Assumes the test page has an element with id 'hidden-span' that is styled as hidden.
        """
        helper.driver.get(self.TEST_PAGE_URL)
        xpath = "//span[@id='hidden-span']"

        result = helper.wait_for_element_visible(xpath, timeout=2)
        assert result is False

    def test_wait_for_element_clickable_success(self, helper):
        """
        Tests that wait_for_element_clickable returns the WebElement when the element is present, visible, and enabled.
        Assumes the test page has a clickable button with id 'clickable-btn'.
        """
        helper.driver.get(self.TEST_PAGE_URL)
        xpath = "//button[@id='clickable-btn']"

        element = helper.wait_for_element_clickable(xpath)
        assert hasattr(element, 'click')

    def test_wait_for_element_clickable_timeout(self, helper):
        """
        Tests that wait_for_element_clickable raises TimeoutException when the element is not clickable within the timeout.
        Assumes the test page has a disabled button with id 'disabled-btn'.
        """
        helper.driver.get(self.TEST_PAGE_URL)
        xpath = "//button[@id='disabled-btn']"

        with pytest.raises(TimeoutException):
             helper.wait_for_element_clickable(xpath, timeout=2)

    def test_wait_for_text_present_in_element_success(self, helper):
        """
        Tests that wait_for_text_present_in_element returns True when the specified text appears within the element.
        Assumes the test page has an element with id 'text-container' containing the text 'Expected Content'.
        """
        helper.driver.get(self.TEST_PAGE_URL)
        xpath = "//div[@id='text-container']"
        text = "Expected Content"

        result = helper.wait_for_text_present_in_element(xpath, text)
        assert result is True

    def test_wait_for_text_present_in_element_timeout(self, helper):
        """
        Tests that wait_for_text_present_in_element returns False when the specified text does not appear within the timeout.
        Assumes the test page has an element with id 'text-container' that does not contain 'Absent Text'.
        """
        helper.driver.get(self.TEST_PAGE_URL)
        xpath = "//div[@id='text-container']"
        text = "Absent Text"

        result = helper.wait_for_text_present_in_element(xpath, text, timeout=2)
        assert result is False

    def test_wait_for_url_contains_success(self, helper):
        """
        Tests that wait_for_url_contains returns True when the current URL contains the specified substring.
        Navigates to a URL that definitely includes the substring '#section-test'.
        """
        url_with_substring = f"{self.TEST_PAGE_URL}#section-test"
        helper.driver.get(url_with_substring)
        substring = "#section-test"

        result = helper.wait_for_url_contains(substring)
        assert result is True

    def test_wait_for_url_contains_timeout(self, helper):
        """
        Tests that wait_for_url_contains returns False when the current URL does not contain the specified substring within the timeout.
        Navigates to the base URL and checks for an absent substring.
        """
        helper.driver.get(self.TEST_PAGE_URL)
        substring = "absent-substring-in-url"

        result = helper.wait_for_url_contains(substring, timeout=2)
        assert result is False

    def test_wait_for_element_not_present_success(self, helper):
        """
        Tests that wait_for_element_not_present returns True when the element is confirmed to be absent from the DOM.
        Navigates to a page that definitely does not contain the element with id 'never-existed'.
        """
        helper.driver.get(self.TEST_PAGE_URL) # Navigate to a page without the element
        xpath_definitely_absent = "//div[@id='never-existed']"
        result = helper.wait_for_element_not_present(xpath_definitely_absent)
        assert result is True

    def test_wait_for_element_not_present_timeout(self, helper):
        """
        Tests that wait_for_element_not_present returns False when the element remains present within the timeout.
        Assumes the test page has an element with id 'always-present-div' that stays on the page.
        """
        helper.driver.get(self.TEST_PAGE_URL)
        xpath = "//div[@id='always-present-div']"

        result = helper.wait_for_element_not_present(xpath, timeout=2)
        assert result is False

    def test_wait_for_element_not_visible_success(self, helper):
        """
        Tests that wait_for_element_not_visible returns True when the element becomes hidden or is not present.
        Navigates to a page where an element with id 'target-element' is hidden by JavaScript after loading.
        """
        url_with_hide_js = f"{self.TEST_PAGE_URL}#hide-element" # Assume JS hides #target-element on hash
        helper.driver.get(url_with_hide_js)
        xpath = "//div[@id='target-element']"

        result = helper.wait_for_element_not_visible(xpath, timeout=5) # Allow time for JS
        assert result is True

    def test_wait_for_element_not_visible_timeout(self, helper):
        """
        Tests that wait_for_element_not_visible returns False when the element remains visible within the timeout.
        Assumes the test page has an element with class 'always-visible' that stays visible.
        """
        helper.driver.get(self.TEST_PAGE_URL)
        xpath = "//p[@class='always-visible']"

        result = helper.wait_for_element_not_visible(xpath, timeout=2)
        assert result is False
