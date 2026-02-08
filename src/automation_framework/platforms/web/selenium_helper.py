"""
automation_framework.platforms.web.selenium_helper - Comprehensive Selenium automation helper.

This module provides SeleniumHelper, a robust wrapper around Selenium WebDriver
that simplifies common web automation tasks. It includes methods for element
detection, interaction, waiting, and JavaScript execution with built-in error
handling and logging integration.

The helper supports multiple locator strategies (XPath, CSS, data-testid, etc.)
and provides flexible waiting conditions (clickable, visible, present).
It handles common automation challenges like dynamic content loading,
element state verification, and cross-browser compatibility issues.

Key Features:
- Multiple element finding strategies with smart waiting
- Text input/output operations with file integration
- JavaScript execution support
- Scroll and navigation utilities
- Automated error handling with detailed context
- Integration with framework's logging and exception systems

Example Usage:
    >>> from automation_framework.platforms.web.selenium_helper import SeleniumHelper
    >>> helper = SeleniumHelper(driver)
    >>> element = helper.find_by_data_test_id("submit-button")
    >>> helper.click_element(element)
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException 
from typing import Union, Tuple, Optional, Callable, List

from automation_framework.utils.exceptions import ActionFailedError, ElementNotFoundError  # Line 7
from automation_framework.utils.logger import automation_logger 

class SeleniumHelper:
    """
    A comprehensive helper class for robust Selenium automation tasks.

    This class encapsulates common Selenium operations, emphasizing
    robust element location using XPath and integrating with the
    project's logging and debugging infrastructure. It provides
    utility methods for waiting, finding, clicking, and interacting
    with elements in a structured and maintainable way.

    The helper is designed to be instantiated per test session or
    component interaction, promoting better state management and
    isolation.
    """

    def __init__(self, driver, default_timeout=10):
        """
        Initializes the SeleniumHelper instance.

        Args:
            driver (selenium.webdriver.remote.webdriver.WebDriver): The active Selenium WebDriver instance.
            default_timeout (int, optional): The default timeout in seconds for wait operations. Defaults to 10.
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, default_timeout)
        self.default_timeout = default_timeout

    # --- Helper Method ---
    @staticmethod
    def _get_expected_condition_func(condition: str) -> Callable:
        """
        Retrieve the corresponding Selenium ExpectedCondition function based on a descriptive string identifier.

        This utility method acts as a translation layer between human-readable condition names
        and their corresponding Selenium ExpectedCondition functions. It provides a standardized
        way to access different types of element wait conditions without requiring direct
        knowledge of the Selenium EC module's function names. This abstraction simplifies
        the implementation of dynamic wait conditions and reduces the risk of typos or
        incorrect function references.

        The method maintains a comprehensive mapping of supported condition types and
        validates input parameters to ensure only valid conditions are processed,
        preventing runtime errors from unsupported condition requests.

        Args:
            condition (str): A string identifier representing the desired wait condition.
                            Supported values include:
                            - 'clickable': Maps to EC.element_to_be_clickable() - waits for element to be present, visible, and enabled
                            - 'visible': Maps to EC.visibility_of_element_located() - waits for element to be present and visible
                            - 'present': Maps to EC.presence_of_element_located() - waits for element to be present in DOM

        Returns:
            Callable: The corresponding Selenium ExpectedCondition function that can be
                    used with WebDriverWait.until() or WebDriverWait.until_not() methods.
                    The returned function expects a (By, locator) tuple as its argument.

        Raises:
            ValueError: When the provided condition string is not in the supported list.
                        The error message includes the invalid condition and a complete
                        list of supported condition types for easy reference.

        Example:
            >>> condition_func = SeleniumHelper._get_expected_condition_func('clickable')
            >>> # Returns EC.element_to_be_clickable function
            >>> wait.until(condition_func((By.ID, 'submit-button')))
        """
        condition_map = {
            "clickable": EC.element_to_be_clickable,
            "visible": EC.visibility_of_element_located,
            "present": EC.presence_of_element_located
        }

        if condition not in condition_map:
            msg = f"Unsupported condition: {condition}. Use one of: {list(condition_map.keys())}"
            automation_logger.error(msg)
            raise ValueError(msg)

        return condition_map[condition]

    @staticmethod
    def _get_current_url_or_default(self, default="Unknown") -> str:
        """
        Safely retrieve the current page URL from the WebDriver instance with graceful error handling.

        This protective wrapper method provides a reliable way to access the current page URL
        while handling potential issues that may arise from driver unavailability, connection
        problems, or driver state inconsistencies. Instead of allowing exceptions to propagate,
        this method catches potential errors and returns a safe default value, ensuring that
        calling code can continue execution without interruption.

        The method is particularly valuable in scenarios where URL information is beneficial
        but not critical, such as logging, debugging, or optional validation steps where
        a failed URL retrieval shouldn't halt the entire automation process.

        Args:
            default (str, optional): The fallback string to return when URL retrieval fails. Defaults to "Unknown" if not specified. This allows callers to customize the default response based on their context.

        Returns:
            str: The current page URL when successfully retrieved from the driver.
                The default string value when the driver is unavailable, lacks URL access,
                or encounters any error during URL retrieval. The return is always a string
                to maintain consistent return type expectations.

        Example:
            >>> current_url = SeleniumHelper._get_current_url_or_default(driver)
            >>> print(current_url)  # Returns actual URL or "Unknown" if retrieval failed
            "https://example.com/dashboard"
            >>> offline_driver = None
            >>> fallback_url = SeleniumHelper._get_current_url_or_default(offline_driver)
            >>> print(fallback_url)  # Returns default when driver is None
            "Unknown"
        """
        try:
            if hasattr(self.driver, 'current_url'):
                return self.driver.current_url
            else:
                automation_logger.warning("Stored driver does not have 'current_url' attribute.")
                return default
        except Exception as e:
            automation_logger.warning(f"Could not retrieve current URL from stored driver: {e}")
            return default

    # --- Wait Methods ---
    def wait_for_element_present(self, xpath: str, timeout: int = None) -> bool:
        """
        Verify that an element exists in the DOM structure within a specified timeframe.

        This method checks for the presence of an element by its XPath locator, confirming
        that the element is included in the HTML document structure regardless of its
        visibility or display state. The element may be hidden, scrolled out of view,
        or styled as invisible, but as long as it exists in the DOM, this method will
        return True.

        This is useful for verifying that dynamically loaded content has been added
        to the page, checking for the existence of elements before attempting
        interactions, or confirming that page initialization has reached a certain point.

        Args:
            xpath (str): XPath expression that uniquely identifies the target element.
                        Example: "//div[@id='dynamic-content']" or "//input[@name='email']"
            timeout (int, optional): Maximum time in seconds to wait for element presence.
                                Defaults to the class's configured default_timeout
                                if not specified. Use this to override standard wait times
                                for elements that may take longer or shorter to appear.

        Returns:
            bool: True when the element is successfully located in the DOM within the timeout period.
                False when the element is not found within the specified timeframe.

        Example:
            >>> helper = SeleniumHelper(driver)
            >>> # Wait for a dynamically loaded section to appear
            >>> success = helper.wait_for_element_present("//section[@data-loaded='true']")
            >>> print(success)  # True if element appears within timeout
            True
            >>> # Check for a missing element with custom timeout
            >>> not_found = helper.wait_for_element_present("//button[@data-testid='removed-btn']", timeout=5)
            >>> print(not_found)  # False if element doesn't appear within 5 seconds
            False
        """
        effective_timeout = timeout if timeout is not None else self.default_timeout
        wait_instance = WebDriverWait(self.driver, effective_timeout)
        try:
            wait_instance.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            automation_logger.warning(
                f"Timed out waiting for element to be present: {xpath}",
                extra={"timeout_seconds": effective_timeout}
            )
            return False

    def wait_for_element_visible(self, xpath: str, timeout: int = None) -> bool:
        """
        Confirm that an element exists in the DOM and is visually rendered on the page.

        This method extends element presence checking by verifying that the target element
        is not only present in the HTML structure but also has actual dimensions and is
        rendered in a visible state. An element is considered visible if it has a width
        and height greater than 0 and is not hidden through CSS properties like
        display:none or visibility:hidden.

        This is essential for ensuring that elements are ready for user interactions
        like clicking, typing, or reading text content. It prevents attempts to interact
        with elements that exist in the DOM but are not currently visible to users.

        Args:
            xpath (str): XPath expression targeting the element whose visibility should be checked.
                        Should uniquely identify the element that needs to be visible.
                        Example: "//div[@class='modal-content']" or "//img[@src='hero-image.jpg']"
            timeout (int, optional): Maximum time in seconds to wait for element visibility.
                                Uses default_timeout if not provided. Override when
                                dealing with slow-rendering content or animations.

        Returns:
            bool: True when the element is both present in the DOM and visibly rendered
                within the timeout period. False when the element remains hidden
                or fails to become visible within the specified timeframe.

        Example:
            >>> helper = SeleniumHelper(driver)
            >>> # Wait for a modal dialog to finish appearing
            >>> modal_visible = helper.wait_for_element_visible("//div[@class='modal-content']")
            >>> print(modal_visible)  # True once modal is fully visible
            True
            >>> # Check if a slow-loading image appears within 15 seconds
            >>> image_loaded = helper.wait_for_element_visible("//img[@src='hero-banner.jpg']", timeout=15)
            >>> print(image_loaded)  # False if image still loading after 15 seconds
            False
        """
        effective_timeout = timeout if timeout is not None else self.default_timeout
        wait_instance = WebDriverWait(self.driver, effective_timeout)
        try:
            wait_instance.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            automation_logger.warning(
                f"Timed out waiting for element to be visible: {xpath}",
                extra={"timeout_seconds": effective_timeout}
            )
            return False

    def wait_for_element_clickable(self, xpath: str, timeout: int = None):
        """
        Ensure an element is ready for user interaction by verifying it's present, visible, and enabled.

        This method performs the most comprehensive readiness check for interactive elements,
        confirming that the target element meets three critical conditions: it exists in the
        DOM, is visually rendered and visible, and is enabled for user interaction. An
        element is considered clickable when it's not disabled, not read-only (for inputs),
        and not covered by other elements that would prevent mouse events.

        This is the definitive method for preparing interactive elements like buttons,
        links, checkboxes, radio buttons, and enabled form fields for user actions.
        It guarantees that subsequent click operations will have the highest probability
        of success.

        Args:
            xpath (str): XPath expression identifying the interactive element to check.
                        Must target elements that support click interactions such as
                        buttons, links, checkboxes, or enabled form controls.
                        Example: "//button[@type='submit']" or "//a[@href='/dashboard']"
            timeout (int, optional): Maximum time in seconds to wait for element clickability.
                                   Uses default_timeout if not provided. Increase for
                                   elements that require complex rendering or animation.

        Returns:
            selenium.webdriver.remote.webelement.WebElement: The fully-ready WebElement
            instance when all conditions are met. This returned element is guaranteed
            to be safe for immediate click operations or other interactive methods.

        Raises:
            selenium.common.exceptions.TimeoutException: When the element fails to meet
            all clickability requirements within the specified timeout period. This
            exception indicates that the element may still be loading, animating,
            disabled, or otherwise not ready for interaction.

        Example:
            >>> helper = SeleniumHelper(driver)
            >>> # Wait for and retrieve the submit button when ready
            >>> submit_button = helper.wait_for_element_clickable("//button[@type='submit']")
            >>> # Button is guaranteed to be clickable when returned
            >>> submit_button.click()
        """
        effective_timeout = timeout if timeout is not None else self.default_timeout
        wait_instance = WebDriverWait(self.driver, effective_timeout)
        try:
            element = wait_instance.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            automation_logger.info(f"Element is clickable: {xpath}")
            return element
        except TimeoutException:
            error_msg = f"Timed out waiting for element to be clickable: {xpath}"
            automation_logger.error(error_msg, extra={"timeout_seconds": effective_timeout})
            # Optionally capture debug info here if needed
            # automation_logger.capture_debug_info(driver=self.driver, context="wait_for_element_clickable", save_screenshot=True)
            raise TimeoutException(error_msg)

    def wait_for_text_present_in_element(self, xpath: str, text: str, timeout: int = None) -> bool:
        """
        Verify that specific text content appears within an identified element.

        This method monitors a target element to confirm that it contains the specified
        text string within its inner text content. The check is case-sensitive and
        matches the exact text provided. The method waits until the target element
        not only exists but also contains the expected text, making it ideal for
        validating dynamic content updates, status messages, or loading indicators.

        This is particularly useful for confirming that AJAX requests have completed
        and updated content has been rendered, verifying that error messages have
        appeared, or ensuring that loading states have transitioned to final states.

        Args:
            xpath (str): XPath expression that locates the element whose text content
                        should be monitored. The element must be present in the DOM
                        for text checking to occur.
                        Example: "//div[@id='status-indicator']" or "//h1[@class='title']"
            text (str): The exact text string that must be present within the element.
                        Case-sensitive matching ensures precision in text verification.
                        Example: "Loading..." or "Success - Order placed!"
            timeout (int, optional): Maximum time in seconds to wait for the text to appear.
                        Uses default_timeout if not specified. Extend for
                        content that requires significant processing time.

        Returns:
            bool: True when the specified text is successfully found within the target
                    element within the timeout period. False when the text does not appear
                    or the element fails to contain the expected content within the timeframe.

        Example:
            >>> helper = SeleniumHelper(driver)
            >>> # Wait for a status indicator to show completion
            >>> status_complete = helper.wait_for_text_present_in_element("//div[@id='progress-status']", "Complete")
            >>> print(status_complete)  # True when status shows "Complete"
            True
            >>> # Verify welcome message appears with custom timeout
            >>> welcome_shown = helper.wait_for_text_present_in_element("//h1", "Welcome", timeout=8)
            >>> print(welcome_shown)  # False if welcome text doesn't appear within 8 seconds
            False
        """
        effective_timeout = timeout if timeout is not None else self.default_timeout
        wait_instance = WebDriverWait(self.driver, effective_timeout)
        try:
            wait_instance.until(EC.text_to_be_present_in_element((By.XPATH, xpath), text))
            return True
        except TimeoutException:
            automation_logger.warning(
                f"Timed out waiting for text '{text}' in element: {xpath}",
                extra={"timeout_seconds": effective_timeout, "expected_text": text}
            )
            return False

    def wait_for_url_contains(self, substring: str, timeout: int = None) -> bool:
        """
        Monitor the browser's current URL to verify it contains a specific substring.

        This method continuously checks the browser's current URL against the provided
        substring, confirming that the navigation has progressed to a location that
        includes the expected URL segment. The check is case-sensitive and verifies
        that the substring appears anywhere within the full URL path, query parameters,
        or fragment identifiers.

        This is essential for validating successful navigation after user actions,
        confirming that redirects have completed, or ensuring that the application
        has reached the intended destination page. It's particularly useful for
        verifying successful form submissions, login completions, or route changes.

        Args:
            substring (str): The URL segment that should be present in the current browser URL.
                        Can include path segments, query parameters, or any part of the URL.
                        Example: "/dashboard" or "?success=true" or "#section-3"
            timeout (int, optional): Maximum time in seconds to wait for URL to contain the substring.
                                Uses default_timeout if not provided. Extend for pages
                                That require significant processing or multiple redirects.

        Returns:
            bool: True when the current URL successfully contains the specified substring
                within the timeout period. False when the URL does not contain the
                expected segment or the timeout expires without match.

        Example:
            >>> helper = SeleniumHelper(driver)
            >>> # Verify successful login redirected to dashboard
            >>> dashboard_reached = helper.wait_for_url_contains("/dashboard")
            >>> print(dashboard_reached)  # True when URL contains "/dashboard"
            True
            >>> # Check if profile section loaded with custom timeout
            >>> profile_loaded = helper.wait_for_url_contains("profile", timeout=12)
            >>> print(profile_loaded)  # False if URL doesn't contain "profile" within 12 seconds
            False
        """
        effective_timeout = timeout if timeout is not None else self.default_timeout
        wait_instance = WebDriverWait(self.driver, effective_timeout)
        try:
            wait_instance.until(EC.url_contains(substring))
            return True
        except TimeoutException:
            automation_logger.warning(
                f"Timed out waiting for URL to contain '{substring}'. Current URL: {self.driver.current_url}",
                extra={"timeout_seconds": effective_timeout, "expected_substring": substring, "current_url": self.driver.current_url}
            )
            return False

    def wait_for_element_not_present(self, xpath: str, timeout: int = None) -> bool:
        """
        Confirm that an element has been completely removed from the DOM structure.

        This method actively monitors for the absence of a specified element,
        returning True only when the element no longer exists in the HTML document
        structure. It's particularly valuable for verifying that loading indicators,
        temporary notifications, modal overlays, or other transient elements have
        been successfully removed from the page.

        The method waits for the element to be completely absent from the DOM,
        distinguishing between elements that are hidden (still in DOM) versus
        elements that have been removed entirely. This is crucial for ensuring
        that cleanup operations have completed before proceeding with subsequent
        automation steps.

        Args:
            xpath (str): XPath expression targeting the element that should disappear.
                        The method confirms this element is no longer present in the DOM.
                        Example: "//div[@class='loading-spinner']" or "//span[@id='temporary-alert']"
            timeout (int, optional): Maximum time in seconds to wait for element removal.
                                Uses default_timeout if not specified. Extend for
                                complex animations or delayed cleanup operations.

        Returns:
            bool: True when the specified element is confirmed to be absent from the DOM
                within the timeout period. False when the element remains present
                or the timeout expires without removal confirmation.

        Example:
            >>> helper = SeleniumHelper(driver)
            >>> # Wait for loading spinner to be completely removed
            >>> spinner_gone = helper.wait_for_element_not_present("//div[@class='loading-spinner']")
            >>> print(spinner_gone)  # True when spinner element is completely removed
            True
            >>> # Verify temporary message disappears with custom timeout
            >>> message_removed = helper.wait_for_element_not_present("//span[@id='temp-message']", timeout=6)
            >>> print(message_removed)  # False if message element still exists after 6 seconds
            False
        """
        effective_timeout = timeout if timeout is not None else self.default_timeout
        wait_instance = WebDriverWait(self.driver, effective_timeout)
        try:
            wait_instance.until_not(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            automation_logger.warning(
                f"Timed out waiting for element to disappear: {xpath}",
                extra={"timeout_seconds": effective_timeout}
            )
            return False

    def wait_for_element_not_visible(self, xpath: str, timeout: int = None) -> bool:
        """
        Verify that an element is either not present in the DOM or is present but not visible.

        This method confirms that a target element either doesn't exist in the document
        structure or exists but is rendered in an invisible state. An element is considered
        not visible when it has CSS properties like display:none, visibility:hidden,
        opacity:0, or when it's positioned outside the visible viewport area.

        This is particularly useful for confirming that modal dialogs have closed,
        loading overlays have faded out, or error messages have disappeared from view
        while potentially remaining in the DOM structure. It's ideal for scenarios
        where elements may remain in the DOM but become visually hidden through
        CSS transitions or animations.

        Args:
            xpath (str): XPath expression targeting the element that should become invisible.
                        The method confirms this element is either removed from DOM
                        or present but visually hidden.
                        Example: "//div[@class='modal-overlay']" or "//p[@id='error-message']"
            timeout (int, optional): Maximum time in seconds to wait for element invisibility.
                                   Uses default_timeout if not specified. Extend for
                                   elements that use animated hiding effects.

        Returns:
            bool: True when the element is either absent from the DOM or present but not visible
                 within the timeout period. False when the element remains visible
                 or the timeout expires without invisibility confirmation.

        Example:
            >>> helper = SeleniumHelper(driver)
            >>> # Confirm modal overlay has disappeared visually
            >>> overlay_hidden = helper.wait_for_element_not_visible("//div[@class='modal-overlay']")
            >>> print(overlay_hidden)  # True when overlay is hidden (display:none or similar)
            True
            >>> # Verify error message is no longer visible with custom timeout
            >>> error_hidden = helper.wait_for_element_not_visible("//p[@id='error-message']", timeout=10)
            >>> print(error_hidden)  # False if error message remains visible after 10 seconds
            False
        """
        effective_timeout = timeout if timeout is not None else self.default_timeout
        wait_instance = WebDriverWait(self.driver, effective_timeout)
        try:
            wait_instance.until_not(EC.visibility_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            automation_logger.warning(
                f"Timed out waiting for element to become not visible: {xpath}",
                extra={"timeout_seconds": effective_timeout}
            )
            return False

    # --- LOCATOR BY PURPOSE METHODS ---
    def find_by_data_test_id(
        self,
        test_id: str,
        wait_time: Optional[int] = None,
        condition: str = "clickable"
    ) -> Union[str, bool]:
        """
        Locate and retrieve an element by its data-testid attribute with configurable wait conditions.

        This method represents the gold standard for element identification in modern web applications
        as it relies on data-testid attributes that are specifically designed for testing purposes.
        These attributes are intentionally stable and maintainable, making them the most reliable
        choice for automation locators that won't break during routine UI updates or refactoring.

        The method combines CSS selector efficiency with flexible wait conditions, allowing you to
        specify exactly when the element should be ready for interaction. It provides comprehensive
        error handling and automatic debugging support when elements cannot be located.

        Args:
            test_id (str): The specific value of the data-testid attribute to search for.
                            This should be the exact string value assigned to the target element's
                            data-testid attribute. Example: "login-submit-button" or "user-profile-card"
            wait_time (Optional[int], optional): Maximum time in seconds to wait for the element
                                            to meet the specified condition. If None (default),
                                            uses the class's default_timeout value set during
                                            initialization. Override for elements that require
                                            extended loading or processing time.
            condition (str, optional): The expected state condition the element must satisfy.
                                    Valid options are:
                                    - 'clickable': Element must be present, visible, and enabled
                                    - 'visible': Element must be present and visible
                                    - 'present': Element must be present in the DOM (any state)
                                    Defaults to 'clickable' for interactive elements.

        Returns:
            selenium.webdriver.remote.webelement.WebElement: The fully-qualified WebElement
            instance that meets the specified condition and can be used for subsequent operations
            like clicking, sending keys, or retrieving text content.

        Raises:
            ElementNotFoundError: When the element with the specified data-testid attribute
                               cannot be found within the timeout period under the requested
                               condition. The exception includes detailed context about
                               the search parameters and current page state.
            ValueError: When an unsupported condition string is provided. The error message
                       includes the invalid condition and a list of supported options.

        Example:
            >>> helper = SeleniumHelper(driver, default_timeout=10)
            >>> # Find and click a submit button that's ready for interaction
            >>> submit_btn = helper.find_by_data_test_id("login-submit-button")
            >>> submit_btn.click()
            >>> # Find an element with custom timeout and visibility requirement
            >>> modal = helper.find_by_data_test_id("confirmation-modal", wait_time=15, condition="visible")
            >>> print(modal.text)  # Access visible content
        """
        effective_wait_time = wait_time if wait_time is not None else self.default_timeout
        temp_wait = WebDriverWait(self.driver, effective_wait_time)

        locator = (By.CSS_SELECTOR, f"[data-testid='{test_id}']")

        condition_func = self._get_expected_condition_func(condition)

        try:
            element = temp_wait.until(
                condition_func(locator),
                message=f"Element with data-testid '{test_id}' not found or not {condition} within {effective_wait_time} seconds."
            )
            current_url = self._get_current_url_or_default()
            automation_logger.info(f"Located element by data-testid: {test_id}", extra={"locator": locator, "page_url": current_url})
            return element
        except TimeoutException as e:
            error_msg = f"Timeout finding element with data-testid '{test_id}' ({condition}) after {effective_wait_time}s."
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"find_by_data_test_id_{test_id}")
            current_url = self._get_current_url_or_default()
            raise ElementNotFoundError(
                element=test_id,
                page=current_url,
                locator=str(locator),
                timeout=effective_wait_time,
                details={"condition": condition}
            ) from e

    def find_by_aria_label(
        self,
        aria_label: str,
        wait_time: Optional[int] = None,
        condition: str = "clickable"
    ) -> Union[str, bool]:
        """
        Locate and retrieve an element by its ARIA label attribute with configurable wait conditions.

        This method leverages ARIA (Accessible Rich Internet Applications) labels, which are
        specifically designed to improve web accessibility for users with disabilities.
        Since ARIA labels describe the element's purpose and function, they provide highly
        reliable and semantically meaningful locators that are maintained as part of
        accessibility compliance efforts.

        ARIA labels are particularly valuable for finding interactive elements like buttons,
        links, form controls, and navigation items that may not have stable IDs or classes.
        The method includes comprehensive error handling and debugging support for robust
        automation workflows.

        Args:
            aria_label (str): The specific value of the aria-label attribute to search for.
                            This should be the exact string value assigned to the target
                            element's aria-label attribute. Example: "Close modal dialog"
                            or "Search button" - these are typically human-readable descriptions.
            wait_time (Optional[int], optional): Maximum time in seconds to wait for the element
                                            to meet the specified condition. If None (default),
                                            uses the class's default_timeout value set during
                                            initialization. Override for elements that require
                                            extended loading or processing time.
            condition (str, optional): The expected state condition the element must satisfy.
                                    Valid options are:
                                    - 'clickable': Element must be present, visible, and enabled
                                    - 'visible': Element must be present and visible
                                    - 'present': Element must be present in the DOM (any state)
                                    Defaults to 'clickable' for interactive elements.

        Returns:
            selenium.webdriver.remote.webelement.WebElement: The fully-qualified WebElement
            instance that meets the specified condition and can be used for subsequent operations
            like clicking, sending keys, or retrieving text content.

        Raises:
            ElementNotFoundError: When the element with the specified aria-label attribute
                            cannot be found within the timeout period under the requested
                            condition. The exception includes detailed context about
                            the search parameters and current page state.
            ValueError: When an unsupported condition string is provided. The error message
                    includes the invalid condition and a list of supported options.

        Example:
            >>> helper = SeleniumHelper(driver, default_timeout=10)
            >>> # Find and click a close button using its ARIA label
            >>> close_btn = helper.find_by_aria_label("Close modal dialog")
            >>> close_btn.click()
            >>> # Find a search input with custom timeout and visibility requirement
            >>> search_input = helper.find_by_aria_label("Search input field", wait_time=8, condition="visible")
            >>> search_input.send_keys("query text")  # Interact with visible element
        """
        effective_wait_time = wait_time if wait_time is not None else self.default_timeout
        temp_wait = WebDriverWait(self.driver, effective_wait_time)

        locator = (By.XPATH, f"//*[@aria-label='{aria_label}']")

        condition_func = self._get_expected_condition_func(condition)

        try:
            element = temp_wait.until(
                condition_func(locator),
                message=f"Element with aria-label '{aria_label}' not found or not {condition} within {effective_wait_time} seconds."
            )
            current_url = self._get_current_url_or_default()
            automation_logger.info(f"Located element by aria-label: {aria_label}", extra={"locator": locator, "page_url": current_url})
            return element
        except TimeoutException as e:
            error_msg = f"Timeout finding element with aria-label '{aria_label}' ({condition}) after {effective_wait_time}s."
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"find_by_aria_label_{aria_label}")
            current_url = self._get_current_url_or_default()
            raise ElementNotFoundError(
                element=aria_label,
                page=current_url,
                locator=str(locator),
                timeout=effective_wait_time,
                details={"condition": condition}
            ) from e

    def find_by_visible_text(
        self,
        text: str,
        tag: str = "*",
        wait_time: Optional[int] = None,
        condition: str = "clickable",
        exact_match: bool = False
    ) -> Union[str, bool]:
        """
        Locate and retrieve an element by its visible text content with flexible matching options.

        This method searches for elements based on the text that is actually visible to users,
        making it valuable for finding buttons, links, menu items, or other interactive elements
        that are identified by their displayed text. The method supports both exact and partial
        text matching, allowing for precise control over the search criteria.

        Text-based locators are particularly useful when structural attributes like IDs or
        classes are dynamically generated or unstable, but the displayed text remains consistent.
        The method includes comprehensive error handling and debugging support for robust
        automation workflows.

        Args:
            text (str): The visible text string to search for within the element.
                       For partial matching, any occurrence of this text within the element
                       content will be matched. For exact matching, only elements whose
                       direct text content equals this string will be selected.
            tag (str, optional): The HTML tag type to search within. Use "*" (default) to
                               search across all tag types, or specify a particular tag
                               like "button", "a", "h1", etc. for more targeted searches.
            wait_time (Optional[int], optional): Maximum time in seconds to wait for the element
                                               to meet the specified condition. If None (default),
                                               uses the class's default_timeout value set during
                                               initialization. Override for elements that require
                                               extended loading or processing time.
            condition (str, optional): The expected state condition the element must satisfy.
                                     Valid options are:
                                     - 'clickable': Element must be present, visible, and enabled
                                     - 'visible': Element must be present and visible
                                     - 'present': Element must be present in the DOM (any state)
                                     Defaults to 'clickable' for interactive elements.
            exact_match (bool, optional): When True, performs exact text matching using XPath's
                                        text() function, requiring the element's direct text
                                        content to equal the search text. When False (default),
                                        uses contains() for partial matching that includes
                                        text from descendant elements.

        Returns:
            selenium.webdriver.remote.webelement.WebElement: The fully-qualified WebElement
            instance that meets the specified condition and text criteria, ready for
            subsequent operations like clicking, sending keys, or retrieving text content.

        Raises:
            ElementNotFoundError: When no element containing the specified text can be found
                               within the timeout period under the requested condition.
                               The exception includes detailed context about the search
                               parameters and current page state.
            ValueError: When an unsupported condition string is provided. The error message
                       includes the invalid condition and a list of supported options.

        Example:
            >>> helper = SeleniumHelper(driver, default_timeout=10)
            >>> # Find a submit button with exact text match
            >>> submit_btn = helper.find_by_visible_text("Submit Form", exact_match=True)
            >>> submit_btn.click()
            >>> # Find any element containing "Settings" text with custom timeout
            >>> settings_link = helper.find_by_visible_text("Settings", tag="a", wait_time=8)
            >>> settings_link.click()
        """
        effective_wait_time = wait_time if wait_time is not None else self.default_timeout
        temp_wait = WebDriverWait(self.driver, effective_wait_time)

        if exact_match:
            # Use text() for direct child text only
            xpath_expression = f"//{tag}[text()='{text}']"
        else:
            # Use contains(., 'text') to include text from descendants
            xpath_expression = f"//{tag}[contains(., '{text}')]"

        locator = (By.XPATH, xpath_expression)

        condition_func = self._get_expected_condition_func(condition)

        try:
            element = temp_wait.until(
                condition_func(locator),
                message=f"Element containing text '{text}' not found or not {condition} within {effective_wait_time} seconds."
            )
            current_url = self._get_current_url_or_default()
            automation_logger.info(f"Located element by visible text: '{text}'", extra={"locator": locator, "page_url": current_url})
            return element
        except TimeoutException as e:
            error_msg = f"Timeout finding element with text '{text}' ({condition}) after {effective_wait_time}s."
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"find_by_visible_text_{text}")
            current_url = self._get_current_url_or_default()
            raise ElementNotFoundError(
                element=f"Text: {text}",
                page=current_url,
                locator=str(locator),
                timeout=effective_wait_time,
                details={"condition": condition, "exact_match": exact_match}
            ) from e

    def find_by_partial_attribute(
        self,
        attribute_name: str,
        attribute_value_part: str,
        tag: str = "*",
        wait_time: Optional[int] = None,
        condition: str = "clickable"
    ) -> Union[str, bool]:
        """
        Locate and retrieve an element by checking if an attribute contains a specific substring.

        This method is particularly valuable for finding elements with dynamically generated
        or changing attributes where only a portion of the attribute value remains consistent.
        Common use cases include elements with auto-generated class names, dynamic IDs,
        or versioned attributes where a stable prefix or suffix exists.

        The method uses CSS selector partial matching which is efficient and widely supported
        across different browsers. It provides flexible searching capabilities that can
        handle various attribute types and maintains consistency with standard CSS selector
        syntax that developers are familiar with.

        Args:
            attribute_name (str): The name of the HTML attribute to search within.
                                Examples include 'class', 'id', 'data-id', 'name', etc.
                                The attribute must exist on the target element.
            attribute_value_part (str): The substring value to look for within the specified attribute.
                                The search will match any attribute value that contains
                                this substring, regardless of position within the value.
            tag (str, optional): The HTML tag type to search within. Use "*" (default) to
                                search across all tag types, or specify a particular tag
                                like "input", "div", "button", etc. for more targeted searches.
            wait_time (Optional[int], optional): Maximum time in seconds to wait for the element
                                to meet the specified condition. If None (default),
                                uses the class's default_timeout value set during
                                initialization. Override for elements that require
                                extended loading or processing time.
            condition (str, optional): The expected state condition the element must satisfy.
                                Valid options are:
                                - 'clickable': Element must be present, visible, and enabled
                                - 'visible': Element must be present and visible
                                - 'present': Element must be present in the DOM (any state)
                                Defaults to 'clickable' for interactive elements.

        Returns:
            selenium.webdriver.remote.webelement.WebElement: The fully-qualified WebElement
            instance that meets the specified condition and attribute criteria, ready for
            subsequent operations like clicking, sending keys, or retrieving text content.

        Raises:
            ElementNotFoundError: When no element with the specified attribute containing
                                the target substring can be found within the timeout period
                                under the requested condition. The exception includes detailed
                                context about the search parameters and current page state.
            ValueError: When an unsupported condition string is provided. The error message
                                includes the invalid condition and a list of supported options.

        Example:
            >>> helper = SeleniumHelper(driver, default_timeout=10)
            >>> # Find an input with a class that contains "search-field"
            >>> search_input = helper.find_by_partial_attribute("class", "search-field", tag="input")
            >>> search_input.send_keys("search term")
            >>> # Find a button with ID containing "submit" using custom timeout
            >>> submit_btn = helper.find_by_partial_attribute("id", "submit", tag="button", wait_time=12)
            >>> submit_btn.click()
        """
        effective_wait_time = wait_time if wait_time is not None else self.default_timeout
        temp_wait = WebDriverWait(self.driver, effective_wait_time)

        # CSS Selector for partial match: [attribute*='value_part']
        css_selector = f"{tag}[{attribute_name}*='{attribute_value_part}']"
        locator = (By.CSS_SELECTOR, css_selector)

        condition_func = self._get_expected_condition_func(condition)

        try:
            element = temp_wait.until(
                condition_func(locator),
                message=f"Element with {attribute_name} containing '{attribute_value_part}' not found or not {condition} within {effective_wait_time} seconds."
            )

            current_url = self._get_current_url_or_default()
            automation_logger.info(f"Located element by partial attribute '{attribute_name}': '{attribute_value_part}'", extra={"locator": locator, "page_url": current_url})
            return element
        except TimeoutException as e:
            error_msg = f"Timeout finding element with {attribute_name} containing '{attribute_value_part}' ({condition}) after {effective_wait_time}s."
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"find_by_partial_attr_{attribute_name}_{attribute_value_part}")
            current_url = self._get_current_url_or_default()
            raise ElementNotFoundError(
                element=f"Attr: {attribute_name}, Part: {attribute_value_part}",
                page=current_url,
                locator=str(locator),
                timeout=effective_wait_time,
                details={"condition": condition}
            ) from e

    def find_relative_to_element(
        self,
        base_element_locator: Tuple[By, str],
        target_element_locator: Tuple[By, str],
        direction: str = "to_right_of",
        wait_time: Optional[int] = None
    ) -> Union[str, bool]:
        """
        Locate an element based on its spatial relationship to a reference element.

        This method leverages Selenium 4's advanced relative locator capabilities to
        find elements based on their visual position relative to other elements on
        the page. This approach is particularly powerful for finding elements in
        complex layouts, tables, forms, or dynamic interfaces where traditional
        locators might be unreliable due to positioning changes or dynamic content.

        The method first locates the reference (base) element, then searches for
        the target element in the specified spatial relationship. This two-step
        approach ensures accurate positioning calculations and handles scenarios
        where elements may be temporarily obscured or moving.

        Args:
            base_element_locator (Tuple[selenium.webdriver.common.by.By, str]): A tuple
                                containing the locator strategy and value for the reference element.
                                Example: (By.ID, "main-container") or (By.CLASS_NAME, "card")
            target_element_locator (Tuple[selenium.webdriver.common.by.By, str]): A tuple
                                containing the locator strategy and value for the target element
                                type to find relative to the base element.
                                Example: (By.TAG_NAME, "button") or (By.CLASS_NAME, "status")
            direction (str, optional): The spatial relationship to search for.
                                    Valid options are:
                                    - 'to_right_of': Target element is positioned to the right of base
                                    - 'to_left_of': Target element is positioned to the left of base
                                    - 'above': Target element is positioned above the base
                                    - 'below': Target element is positioned below the base
                                    - 'near': Target element is positioned near the base (within 50px)
                                    Defaults to 'to_right_of'.
            wait_time (Optional[int], optional): Maximum time in seconds to wait for both
                                    the base element and the target element
                                    to be found. If None (default), uses the
                                    class's default_timeout value set during
                                    initialization.

        Returns:
            selenium.webdriver.remote.webelement.WebElement: The target WebElement that
            meets the specified spatial relationship criteria, ready for subsequent
            operations like clicking, sending keys, or retrieving text content.

        Raises:
            ElementNotFoundError: When either the base element cannot be found or the
                               target element cannot be located in the specified
                               spatial relationship within the timeout period.
                               The exception includes detailed context about both
                               search operations and current page state.
            ValueError: When an unsupported direction string is provided. The error message
                       includes the invalid direction and a list of supported options.
            TimeoutException: When the base element or target element search exceeds
                            the specified timeout period.

        Example:
            >>> helper = SeleniumHelper(driver, default_timeout=10)
            >>> # Find a delete button that appears to the right of a specific row
            >>> delete_btn = helper.find_relative_to_element(
            ...     (By.ID, "user-row-123"),
            ...     (By.CLASS_NAME, "delete-button"),
            ...     direction="to_right_of"
            ... )
            >>> delete_btn.click()
            >>> # Find a label above a specific input field
            >>> label = helper.find_relative_to_element(
            ...     (By.NAME, "email-input"),
            ...     (By.TAG_NAME, "label"),
            ...     direction="above",
            ...     wait_time=15
            ... )
            >>> print(label.text)  # Get the label text
        """
        # Import inside function to avoid dependency issues if not used
        from selenium.webdriver.support.relative_locator import locate_with

        effective_wait_time = wait_time if wait_time is not None else self.default_timeout
        temp_wait = WebDriverWait(self.driver, effective_wait_time)

        # Wait for the base element to be present using the stored driver
        try:
            base_element = temp_wait.until(
                EC.presence_of_element_located(base_element_locator),
                message=f"Base element for relative locator not found within {effective_wait_time} seconds."
            )
        except TimeoutException as e:
            error_msg = f"Timeout finding base element for relative locator: {base_element_locator} after {effective_wait_time}s."
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context="find_relative_base_timeout")
            current_url = self._get_current_url_or_default()
            raise ElementNotFoundError(
                element=str(base_element_locator),
                page=current_url,
                locator=str(base_element_locator),
                timeout=effective_wait_time,
                details={"step": "find_base_element_for_relative"}
            ) from e

        direction_map = {
            "to_right_of": lambda x: locate_with(x[0], x[1]).to_right_of(base_element),
            "to_left_of": lambda x: locate_with(x[0], x[1]).to_left_of(base_element),
            "above": lambda x: locate_with(x[0], x[1]).above(base_element),
            "below": lambda x: locate_with(x[0], x[1]).below(base_element),
            "near": lambda x: locate_with(x[0], x[1]).near(base_element)
        }

        if direction not in direction_map:
            msg = f"Unsupported direction: {direction}. Use one of: {list(direction_map.keys())}"
            automation_logger.error(msg)
            raise ValueError(msg)

        relative_locator = direction_map[direction](target_element_locator)

        try:
            element = temp_wait.until(
                lambda d: d.find_element(*relative_locator), # This lambda finds the element using the relative locator
                message=f"Target element relative to base element ({direction}) not found within {effective_wait_time} seconds."
            )
            current_url = self._get_current_url_or_default()
            automation_logger.info(f"Located element relative to base: {direction}", extra={"base_locator": base_element_locator, "target_locator": target_element_locator, "page_url": current_url})
            return element
        except TimeoutException as e:
            error_msg = f"Timeout finding element relative to base ({direction}) after {effective_wait_time}s."
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"find_relative_{direction}_timeout")
            current_url = self._get_current_url_or_default()
            raise ElementNotFoundError(
                element=f"Relative ({direction}) to {base_element_locator}",
                page=current_url,
                locator=f"Relative locator using base: {base_element_locator}, target: {target_element_locator}, dir: {direction}",
                timeout=effective_wait_time,
                details={"direction": direction, "base_locator": base_element_locator, "target_locator": target_element_locator}
            ) from e


    # --- JAVASCRIPT EXECUTION METHODS ---
    def execute_js_script(self, script: str, *args):
        """
        Execute a JavaScript script in the current browser context and return the result.

        This method provides direct access to the browser's JavaScript execution engine,
        enabling advanced interactions that may not be possible through standard Selenium
        commands. It's particularly useful for manipulating page elements, triggering
        JavaScript events, modifying page state, or retrieving complex data structures
        from the browser.

        The method accepts variable arguments that can be passed to the JavaScript
        function, allowing for dynamic script execution with runtime parameters.

        Args:
            script (str): The JavaScript code to execute. Can be a simple expression
                    or a complex function call. The script should return a value
                    that can be serialized by Selenium's JavaScript engine.
            *args: Variable arguments to pass to the JavaScript function. These arguments
                    will be available within the script execution context and can include
                    strings, numbers, booleans, or WebElements.

        Returns:
            The result of the JavaScript execution, which can be a primitive value
            (string, number, boolean), an array, an object, or None depending on
            what the script returns. Selenium automatically converts JavaScript
            objects to Python equivalents where possible.

        Example:
            >>> helper = SeleniumHelper(driver)
            >>> # Get the current scroll position
            >>> scroll_pos = helper.execute_js_script("return window.pageYOffset;")
            >>> # Highlight an element with red border
            >>> element = driver.find_element(By.ID, "my-element")
            >>> helper.execute_js_script("arguments[0].style.border='3px solid red'", element)
        """
        return self.driver.execute_script(script, *args)

    def insert_text_from_file(
        self,
        file_path: str,
        locator: Tuple[By, str],
        clear_before_insert: bool = True,
        wait_time: Optional[int] = None,
        condition: str = "clickable"
    ) -> None:
        """
        Read content from a text file and populate a web input field or text area with its contents.

        This method streamlines the process of entering large amounts of text into web forms
        by reading content from external files rather than embedding it directly in test code.
        It's particularly valuable for testing scenarios involving content management,
        document uploads, or form submissions with substantial text inputs.

        The method handles file reading with proper encoding, waits for the target element
        to reach the specified readiness state, optionally clears existing content, and then
        simulates user typing to populate the field. This approach ensures that JavaScript
        events are properly triggered and form validation occurs as expected.

        Args:
            file_path (str): The complete path to the text file containing the content to insert.
                        The file must be readable and contain UTF-8 encoded text.
                        Example: "/path/to/content/article.txt" or "./test_data/input.md"
            locator (Tuple[By, str]): A tuple containing the locator strategy and value
                        to identify the target input field or text area.
                        Example: (By.ID, "content-editor") or (By.CSS_SELECTOR, "textarea[name='description']")
            clear_before_insert (bool, optional): When True (default), clears any existing
                        content in the target element before
                        inserting the new text. Set to False to
                        append to existing content.
            wait_time (Optional[int], optional): Maximum time in seconds to wait for the
                        target element to meet the specified condition.
                        If None (default), uses the class's
                        default_timeout value set during initialization.
            condition (str, optional): The expected state condition the target element
                        must satisfy before text insertion. Valid options are:
                        - 'clickable': Element must be present, visible, and enabled
                        - 'visible': Element must be present and visible
                        - 'present': Element must be present in the DOM (any state)
                        Defaults to 'clickable' for interactive input fields.

        Raises:
            FileNotFoundError: When the specified file_path does not exist or is not accessible.
                        The exception includes the file path for easy identification.
            UnicodeDecodeError: When the file cannot be decoded using UTF-8 encoding.
                        The original error details are preserved for troubleshooting.
            ElementNotFoundError: When the target element cannot be located within the
                        specified timeout period under the requested condition.
                        The exception includes detailed context about the search
                        parameters and current page state.
            ActionFailedError: When clearing the element or sending keys fails after the
                        element is successfully located. This may indicate issues
                        with element state, permissions, or JavaScript interference.
            ValueError: When an unsupported condition string is provided. The error message
                        includes the invalid condition and a list of supported options.

        Example:
            >>> helper = SeleniumHelper(driver, default_timeout=10)
            >>> # Insert article content from a markdown file into an editor
            >>> helper.insert_text_from_file(
            ...     file_path="./test_data/article_content.md",
            ...     locator=(By.ID, "editor-content"),
            ...     clear_before_insert=True,
            ...     wait_time=15
            ... )
            >>> # Append signature to an existing text area
            >>> helper.insert_text_from_file(
            ...     file_path="./test_data/signature.txt",
            ...     locator=(By.NAME, "signature"),
            ...     clear_before_insert=False  # Don't clear existing content
            ... )
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except FileNotFoundError:
            error_msg = f"File not found for insertion: {file_path}"
            automation_logger.error(error_msg)
            raise

        except UnicodeDecodeError as e:
            error_msg = f"Could not decode file ({file_path}): {e}"
            automation_logger.error(error_msg)
            raise # Re-raises the UnicodeDecodeError

        effective_wait_time = wait_time if wait_time is not None else self.default_timeout
        temp_wait = WebDriverWait(self.driver, effective_wait_time)

        condition_func = self._get_expected_condition_func(condition)

        try:
            element = temp_wait.until(
                condition_func(locator),
                message=f"Target element for text insertion not found or not {condition} within {effective_wait_time} seconds. Locator: {locator}"
            )
        except TimeoutException as e:
            error_msg = f"Timeout finding element for text insertion ({condition}) using locator {locator} after {effective_wait_time}s."
            automation_logger.error(error_msg)

            automation_logger.capture_debug_info(driver=self.driver, context=f"insert_text_file_element_not_found_{locator[1]}")
            current_url = self._get_current_url_or_default()
            raise ElementNotFoundError(
                element=f"Target for file {file_path}",
                page=current_url,
                locator=str(locator),
                timeout=effective_wait_time,
                details={"condition": condition, "file_path": file_path}
            ) from e

        try:
            if clear_before_insert:
                element.clear()
            element.send_keys(text_content)
            # Log success if needed
            automation_logger.info(f"Inserted content from file '{file_path}' into element located by {locator}.")
        except Exception as e: # Catch potential issues with clear/send_keys
            error_msg = f"Failed to clear or send keys to element located by {locator} during text insertion from '{file_path}'. Error: {e}"
            automation_logger.error(error_msg)

            automation_logger.capture_debug_info(driver=self.driver, context=f"insert_text_file_action_failed_{locator[1]}")
            current_url = self._get_current_url_or_default()
            raise ActionFailedError(
                action_type="insert_text_from_file",
                element=str(locator),
                page=current_url,
                reason=str(e),
                details={"file_path": file_path, "clear_before_insert": clear_before_insert}
            ) from e

    def scroll_to_element(
        self,
        locator: Tuple[By, str],
        wait_time: Optional[int] = None,
        condition: str = "visible",
        scroll_behavior: str = "auto",
        scroll_block: str = "center"
    ) -> None:
        """
        Scrolls the browser window or parent container to bring the specified element into view.

        This method first waits for the element to be present/visible/clickable based on the
        provided 'condition'. Once the element is located, it uses JavaScript's
        `scrollIntoView()` method to scroll it into the viewport. This approach offers more
        control and reliability than relying solely on Selenium's implicit scrolling during
        actions like `click()`.

        Args:
            locator: A tuple (By, locator_string) identifying the target element to scroll to.
            wait_time: Maximum time (in seconds) to wait for the element to meet the condition.
                      Uses the instance's default timeout if not provided.
            condition: The expected condition to wait for on the target element before scrolling.
                       Options are 'clickable', 'visible', 'present'. Defaults to 'visible'.
                       'visible' is often appropriate for scrolling as it ensures the element
                       has dimensions and is not hidden.
            scroll_behavior: Defines the animation behavior of the scroll. Options are "auto"
                             (instant) or "smooth". Defaults to "auto".
            scroll_block: Defines vertical alignment of the element after scrolling.
                          Options are "start", "center", "end", "nearest". Defaults to "center".

        Raises:
            ElementNotFoundError: If the element specified by 'locator' is not found within
                                 the specified 'wait_time' under the given 'condition'.
            ValueError: If an unsupported 'condition', 'scroll_behavior', or 'scroll_block'
                        string is provided.
        """
        valid_scroll_behaviors = {"auto", "smooth"}
        valid_scroll_blocks = {"start", "center", "end", "nearest"}

        if scroll_behavior not in valid_scroll_behaviors:
            msg = f"Unsupported scroll_behavior: {scroll_behavior}. Use one of: {valid_scroll_behaviors}"
            automation_logger.error(msg)
            raise ValueError(msg)

        if scroll_block not in valid_scroll_blocks:
            msg = f"Unsupported scroll_block: {scroll_block}. Use one of: {valid_scroll_blocks}"
            automation_logger.error(msg)
            raise ValueError(msg)

        effective_wait_time = wait_time if wait_time is not None else self.default_timeout
        temp_wait = WebDriverWait(self.driver, effective_wait_time)

        condition_func = self._get_expected_condition_func(condition)

        try:
            element = temp_wait.until(
                condition_func(locator),
                message=f"Target element for scrolling not found or not {condition} within {effective_wait_time} seconds. Locator: {locator}"
            )
        except TimeoutException as e:
            error_msg = f"Timeout finding element for scrolling ({condition}) using locator {locator} after {effective_wait_time}s."
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"scroll_to_element_not_found_{locator[1]}")
            current_url = self._get_current_url_or_default()
            raise ElementNotFoundError(
                element=f"Target for scrolling: {locator}",
                page=current_url,
                locator=str(locator),
                timeout=effective_wait_time,
                details={"condition": condition}
            ) from e

        try:
            js_options = f"{{behavior: '{scroll_behavior}', block: '{scroll_block}'}}"
            self.driver.execute_script(f"arguments[0].scrollIntoView({js_options});", element)
            automation_logger.info(f"Scrolled to element located by {locator}. Options: {js_options}")
        except Exception as e:
            error_msg = f"Failed to scroll to element located by {locator}. Error: {e}"
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"scroll_to_element_js_failed_{locator[1]}")
            current_url = self._get_current_url_or_default()
            raise ActionFailedError(
                action_type="scroll_to_element",
                element=str(locator),
                page=current_url,
                reason=str(e),
                details={"locator": locator, "scroll_behavior": scroll_behavior, "scroll_block": scroll_block}
            ) from e

    def extract_links_with_js(
        self,
        container_locator: Tuple[By, str],
        link_selector: str = "a[href]",
        wait_time: Optional[int] = None,
        single_link_index: Optional[int] = None
    ) -> List[str]:
        """
        Extracts href links from specific elements within a designated container using JavaScript.

        This method waits for the container element(s) to be present, then executes JavaScript
        within the browser to find child elements matching the link_selector and extract their
        'href' attributes. This approach is highly efficient for collecting multiple links
        simultaneously and avoids potential 'StaleElementReferenceException' issues associated
        with iterating through Selenium WebElements in Python.

        Args:
            container_locator: A tuple (By, locator_string) identifying the parent container(s)
                    from which links should be extracted.
            link_selector: A CSS selector string to identify the link elements within the
                    container(s). Defaults to "a[href]" to find anchor tags with an href.
            wait_time: Maximum time (in seconds) to wait for at least one container element
                    identified by 'container_locator'. Uses the instance's default timeout if not provided.
            single_link_index: If provided (0-based index), only the href from the link element
                    at this specific position within *each* container will be returned.
                    If a container has fewer matching links than the index, that container contributes
                    nothing. If None (default), all matching links from all containers are returned.

        Returns:
            List[str]: A list of href attribute values found. Relative URLs are preserved as
                    they are in the HTML source. Returns an empty list if no containers are found,
                    no matching link elements exist within found containers, or if the operation fails.

        Raises:
            ValueError: If `single_link_index` is provided and is negative.
            ElementNotFoundError: If the container element specified by 'container_locator' is not found
                                within the specified 'wait_time'.
        """
        if single_link_index is not None and single_link_index < 0:
            raise ValueError("single_link_index must be a non-negative integer or None.")

        effective_wait_time = wait_time if wait_time is not None else self.default_timeout
        temp_wait = WebDriverWait(self.driver, effective_wait_time)

        try:
            temp_wait.until(
                EC.presence_of_element_located(container_locator),
                message=f"Container element for link extraction not found within {effective_wait_time} seconds. Locator: {container_locator}"
            )
        except TimeoutException as e:
            error_msg = f"Timeout waiting for container element for link extraction using locator {container_locator} after {effective_wait_time}s."
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"extract_links_container_not_found_{container_locator[1]}")
            current_url = self._get_current_url_or_default()
            raise ElementNotFoundError(
                element=f"Container for link extraction: {container_locator}",
                page=current_url,
                locator=str(container_locator),
                timeout=effective_wait_time,
                details={"link_selector": link_selector, "single_link_index": single_link_index}
            ) from e

        if single_link_index is not None:
            script = """
            const containers = document.querySelectorAll(arguments[0]);
            const linkSelector = arguments[1];
            const targetIndex = arguments[2];
            const allLinks = [];

            containers.forEach(container => {
                const links = container.querySelectorAll(linkSelector);
                if (links.length > targetIndex) {
                    const href = links[targetIndex].href;
                    if (href) allLinks.push(href);
                }
            });

            return allLinks;
            """
            script_args = (container_locator[1], link_selector, single_link_index)
        else:
            script = """
            const containers = document.querySelectorAll(arguments[0]);
            const linkSelector = arguments[1];
            const allLinks = [];

            containers.forEach(container => {
                const links = container.querySelectorAll(linkSelector);
                links.forEach(link => {
                    const href = link.href;
                    if (href) allLinks.push(href);
                });
            });

            return allLinks;
            """
            script_args = (container_locator[1], link_selector)

        try:
            extracted_links = self.driver.execute_script(script, *script_args)
            if not isinstance(extracted_links, list):
                automation_logger.warning(f"JavaScript for link extraction returned non-list type: {type(extracted_links)}. Treating as empty list.")
                return []
            automation_logger.info(f"Successfully extracted {len(extracted_links)} links from container {container_locator} using selector '{link_selector}'.")
            return extracted_links
        except Exception as e:
            error_msg = f"Failed to execute JavaScript for link extraction using locator {container_locator} and selector '{link_selector}'. Error: {e}"
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"extract_links_js_failed_{container_locator[1]}")
            return []

    # --- INTERACTION METHODS ---
    def click_element(
        self,
        locator: Tuple[By, str],
        wait_time: Optional[int] = None,
        condition: str = "clickable"
    ) -> None:
        """
        Wait for an element to reach the specified state and perform a click action.

        This method provides a reliable way to interact with elements by first ensuring
        they are in the appropriate state for interaction before attempting to click.
        It combines element location with readiness verification and action execution
        in a single, atomic operation that handles timing and synchronization concerns.

        The method supports different readiness conditions to accommodate various
        element types and states, ensuring that clicks are only attempted when
        the element is ready for interaction. This prevents common issues like
        clicking on invisible or disabled elements.

        Args:
            locator (Tuple[By, str]): A tuple containing the locator strategy and value
                        to identify the target element for clicking.
                        Example: (By.ID, "submit-button") or (By.DATA_TESTID, "logout-link")
            wait_time (Optional[int], optional): Maximum time in seconds to wait for the
                        element to meet the specified condition.
                        If None (default), uses the class's
                        default_timeout value set during initialization.
            condition (str, optional): The expected state condition the element must satisfy
                        before clicking. Valid options are:
                            - 'clickable': Element must be present, visible, and enabled
                            - 'visible': Element must be present and visible
                            - 'present': Element must be present in the DOM (any state)
                        Defaults to 'clickable' as this is most appropriate for
                        interactive elements that require clicking.

        Raises:
            ElementNotFoundError: When the target element cannot be located within the
                        pecified timeout period under the requested condition.
                        The exception includes detailed context about the search
                        parameters and current page state.
            ActionFailedError: When the click action fails after the element is successfully
                        located. This may indicate that the element became disabled,
                        moved, or became obscured between the wait and click operations.
            ValueError: When an unsupported condition string is provided. The error message
                        includes the invalid condition and a list of supported options.

        Example:
            >>> helper = SeleniumHelper(driver, default_timeout=10)
            >>> # Click a submit button when it becomes clickable
            >>> helper.click_element((By.ID, "submit-form"))
            >>> # Click a menu item with custom timeout and visibility requirement
            >>> helper.click_element(
            ...     (By.DATA_TESTID, "menu-item-settings"),
            ...     wait_time=15,
            ...     condition="visible"
            ... )
        """
        effective_wait_time = wait_time if wait_time is not None else self.default_timeout
        temp_wait = WebDriverWait(self.driver, effective_wait_time)
        condition_func = self._get_expected_condition_func(condition)

        try:
            element = temp_wait.until(
                condition_func(locator),
                message=f"Element to click not found or not {condition} within {effective_wait_time} seconds. Locator: {locator}"
            )
        except TimeoutException as e:
            error_msg = f"Timeout finding element to click ({condition}) using locator {locator} after {effective_wait_time}s."
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"click_element_not_found_{locator[1]}")
            current_url = self._get_current_url_or_default()
            raise ElementNotFoundError(
                element=f"Element to click: {locator}",
                page=current_url,
                locator=str(locator),
                timeout=effective_wait_time,
                details={"condition": condition}
            ) from e

        try:
            element.click()
            automation_logger.info(f"Clicked element located by {locator}.")
        except Exception as e:
            error_msg = f"Failed to click element located by {locator}. Error: {e}"
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"click_element_failed_{locator[1]}")
            current_url = self._get_current_url_or_default()
            raise ActionFailedError(
                action_type="click_element",
                element=str(locator),
                page=current_url,
                reason=str(e),
                details={"locator": locator}
            ) from e

    def type_text(
        self,
        locator: Tuple[By, str],
        text: str,
        clear_before: bool = True,
        wait_time: Optional[int] = None,
        condition: str = "visible" 
    ) -> None:
        """
        Wait for an input field or textarea to reach the specified state and populate it with text.

        This method provides a comprehensive solution for text input operations by combining
        element readiness verification, optional content clearing, and text population in
        a single, reliable operation. It ensures that text fields are properly prepared
        for input and that the entered text triggers appropriate JavaScript events.

        The method handles both appending to existing content and replacing it entirely
        based on the clear_before parameter, making it suitable for various input scenarios
        including form filling, content editing, and search operations.

        Args:
            locator (Tuple[By, str]): A tuple containing the locator strategy and value
                        to identify the target input field or textarea.
                        Example: (By.NAME, "email") or (By.CSS_SELECTOR, "textarea.comment-box")
            text (str): The text string to input into the target element. This text will
                        be sent character by character to simulate natural typing behavior
                        and trigger JavaScript events as expected by web applications.
            clear_before (bool, optional): When True (default), clears any existing content
                        in the target element before typing the new text.
                        When False, appends the new text to existing content.
            wait_time (Optional[int], optional): Maximum time in seconds to wait for the
                        element to meet the specified condition.
                        If None (default), uses the class's
                        default_timeout value set during initialization.
            condition (str, optional): The expected state condition the element must satisfy
                        before typing. Valid options are:
                            - 'clickable': Element must be present, visible, and enabled
                            - 'visible': Element must be present and visible
                            - 'present': Element must be present in the DOM (any state)
                            Defaults to 'visible' as this is often sufficient for
                            input fields that need to be visible for proper interaction.

        Raises:
            ElementNotFoundError: When the target input element cannot be located within
                        the specified timeout period under the requested condition.
                        The exception includes detailed context about the search
                        parameters and current page state.
            ActionFailedError: When clearing the element or sending keys fails after the
                        element is successfully located. This may indicate issues
                        with element state, permissions, or JavaScript interference.
            ValueError: When an unsupported condition string is provided. The error message
                        includes the invalid condition and a list of supported options.

        Example:
            >>> helper = SeleniumHelper(driver, default_timeout=10)
            >>> # Fill an email field with new content
            >>> helper.type_text((By.NAME, "email"), "user@example.com")
            >>> # Append to an existing text area without clearing
            >>> helper.type_text(
            ...     (By.ID, "comment-box"),
            ...     "Additional comment",
            ...     clear_before=False,
            ...     wait_time=8
            ... )
        """
        effective_wait_time = wait_time if wait_time is not None else self.default_timeout
        temp_wait = WebDriverWait(self.driver, effective_wait_time)
        condition_func = self._get_expected_condition_func(condition)

        try:
            element = temp_wait.until(
                condition_func(locator),
                message=f"Input element for typing not found or not {condition} within {effective_wait_time} seconds. Locator: {locator}"
            )
        except TimeoutException as e:
            error_msg = f"Timeout finding input element for typing ({condition}) using locator {locator} after {effective_wait_time}s."
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"type_text_element_not_found_{locator[1]}")
            current_url = self._get_current_url_or_default()
            raise ElementNotFoundError(
                element=f"Input element for typing: {locator}",
                page=current_url,
                locator=str(locator),
                timeout=effective_wait_time,
                details={"condition": condition}
            ) from e

        try:
            if clear_before:
                element.clear()
            element.send_keys(text)
            automation_logger.info(f"Typed text into element located by {locator}.")
        except Exception as e:
            error_msg = f"Failed to type text into element located by {locator}. Error: {e}"
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context=f"type_text_failed_{locator[1]}")
            current_url = self._get_current_url_or_default()
            raise ActionFailedError(
                action_type="type_text",
                element=str(locator),
                page=current_url,
                reason=str(e),
                details={"locator": locator, "clear_before": clear_before}
            ) from e

    # --- UTILITY METHODS ---
    def close_current_tab(self) -> str:
        """
        Close the currently focused browser tab or window and return the URL of the closed tab.

        This method safely closes the active browser tab or window, handling the operation
        with proper error management and logging. When closing the last remaining tab,
        the entire WebDriver session will terminate. The method captures the current URL
        before closing the tab, allowing for proper session tracking and cleanup.

        This operation is particularly useful for managing multiple tabs during complex
        automation scenarios or cleaning up resources after completing specific tasks.
        The caller should be aware that focus will shift to another available tab after
        the current one is closed, or the driver will become invalid if no other tabs exist.

        Returns:
            str: The URL of the tab that was successfully closed. Returns 'Unknown_Closed_Tab'
                if the URL could not be retrieved before closing due to driver unavailability
                or connection issues. This allows callers to track which page was on the
                closed tab for logging or validation purposes.

        Example:
            >>> helper = SeleniumHelper(driver)
            >>> # Navigate to a page and open new tab
            >>> driver.get("https://example.com")
            >>> driver.execute_script("window.open('https://google.com', '_blank');")
            >>> # Switch to new tab and close it
            >>> driver.switch_to.window(driver.window_handles[1])
            >>> closed_url = helper.close_current_tab()
            >>> print(closed_url)  # "https://google.com"
        """
        current_url = self._get_current_url_or_default(default="Unknown_Closed_Tab")
        try:
            self.driver.close()
            automation_logger.info(f"Closed the current browser tab/window. URL was: {current_url}")
        except Exception as e:
            error_msg = f"Failed to close the current browser tab/window. Error: {e}"
            automation_logger.error(error_msg)
            automation_logger.capture_debug_info(driver=self.driver, context="close_current_tab_failed")
        return current_url

    def quit_driver(self) -> str:
        """
        Terminate the entire WebDriver session, closing all associated windows and tabs.

        This method performs a complete shutdown of the WebDriver session, terminating
        all browser instances and releasing all associated resources. Unlike closing
        individual tabs, this operation ends the entire automation session and invalidates
        the WebDriver instance. This should typically be called at the end of test
        execution or when all automation tasks are complete.

        The method includes comprehensive error handling to ensure proper cleanup even
        if the quit operation encounters issues. It captures the current URL before
        termination for logging and debugging purposes, though this may not be possible
        if the driver is already in an invalid state.

        Returns:
            str: The URL of the current page before the session was terminated. Returns
                'Unknown_Before_Quit' if the URL could not be retrieved before quitting
                due to driver unavailability or connection issues. This allows for
                session tracking and post-execution analysis.

        Example:
            >>> helper = SeleniumHelper(driver)
            >>> # Perform automation tasks
            >>> driver.get("https://example.com")
            >>> # Complete all tasks and clean up
            >>> final_url = helper.quit_driver()
            >>> print(f"Session ended from: {final_url}")
        """
        current_url = self._get_current_url_or_default(default="Unknown_Before_Quit")
        try:
            self.driver.quit()
            automation_logger.info(f"Quit the WebDriver session. Last URL was: {current_url}")
        except Exception as e:
            error_msg = f"Failed to quit the WebDriver session. Error: {e}"
            automation_logger.error(error_msg)
            try:
                automation_logger.capture_debug_info(driver=self.driver, context="quit_driver_failed")
            except:
                automation_logger.warning("Could not capture debug info during quit_driver due to driver state.")
        return current_url




