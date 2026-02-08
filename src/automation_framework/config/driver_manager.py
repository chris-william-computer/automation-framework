"""
automation_framework.config.driver_manager - WebDriver creation and management with anti-detection.

This module provides DriverManager, a factory class for creating Chrome/Chromium
WebDriver instances with sophisticated anti-detection capabilities. The driver
configuration includes multiple layers of stealth measures to avoid bot detection
while maintaining reliable automation functionality.

The manager uses centralized settings from the framework's configuration system
to ensure consistent behavior across different automation scenarios. It handles
all aspects of driver creation including binary location, window sizing,
anti-detection measures, user profile persistence, and timeout configuration.

Key Features:
- Advanced anti-detection configuration (fingerprint modification, behavioral obfuscation)
- Persistent user profile support for session continuity
- Headless/visible browser mode toggle
- Comprehensive timeout and wait configuration
- Runtime JavaScript modifications for enhanced stealth

Example Usage:
    >>> from automation_framework.config.driver_manager import DriverManager
    >>> driver = DriverManager.get_driver()
    >>> driver.get("https://example.com")
    >>> # Perform automation tasks
    >>> driver.quit()
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from .settings import settings


class DriverManager:
    """
    Comprehensive WebDriver manager with advanced anti-detection capabilities.

    This class provides a factory method for creating Chrome/Chromium drivers
    with sophisticated anti-detection measures. The implementation carefully
    balances automation functionality with stealth characteristics to minimize
    the likelihood of detection by website protection systems while maintaining
    reliable automation capabilities.

    The driver configuration includes multiple layers of anti-detection
    techniques including browser fingerprint modification, behavioral
    obfuscation, and network-level adjustments. All configuration is driven
    by the centralized settings module for consistent behavior across
    different automation scenarios.
    """

    @staticmethod
    def get_driver():
        """
        Create and configure a Chrome/Chromium WebDriver with anti-detection measures.

        This method constructs a WebDriver instance with comprehensive
        anti-detection configuration applied through Chrome options.
        The configuration includes multiple techniques to avoid bot detection
        while preserving normal browser functionality for automation tasks.

        The method handles driver creation, option configuration, service
        setup, and post-creation modifications to ensure optimal performance
        and stealth characteristics. It applies both command-line arguments
        and runtime JavaScript modifications to alter browser fingerprints.

        Returns:
            Configured Chrome/Chromium WebDriver instance ready for automation.
            The driver includes all specified anti-detection measures and
            timeout configurations from the settings module.

        Example:
            >>> driver = DriverManager.get_driver()
            >>> driver.get("https://example.com")
            >>> # Perform automation tasks
            >>> driver.quit()
        """
        
        # Create Chrome options instance for driver configuration
        options = Options()
        options.binary_location = settings.CHROMIUM_BINARY

        # Configure browser window dimensions for consistent viewport
        options.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")

        # Apply foundational anti-detection arguments to reduce bot indicators
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Configure persistent user profile for session continuity
        options.add_argument(f"--user-data-dir={settings.USER_DATA_DIR}")
        options.add_argument(f"--profile-directory={settings.PROFILE_NAME}")

        # Apply comprehensive anti-detection measures when enabled
        if settings.AVOID_DETECTION:
            # Disable features that reveal automation presence
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript")  # Remove if site requires JS
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Set realistic user agent string to mimic human browsing
            options.add_argument(
                "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36"
            )

        # Configure headless mode based on settings preference
        if settings.BROWSER_HEADLESS:
            options.add_argument("--headless=new")

        # Create service instance with specified ChromeDriver path
        service = Service(settings.CHROMEDRIVER_PATH)

        # Create driver instance with configured options and service
        driver = webdriver.Chrome(service=service, options=options)

        # Apply runtime anti-detection JavaScript modifications
        if settings.AVOID_DETECTION:
            # Remove webdriver property that indicates automation
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            # Simulate realistic plugin count
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            # Set realistic language preferences
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")

        # Configure driver timeouts for reliable operation
        driver.implicitly_wait(settings.IMPLICIT_WAIT)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)

        return driver
