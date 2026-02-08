"""
automation_framework.config.settings - Configuration management for automation framework.

This module provides centralized configuration settings for browser automation,
including paths to executables, browser behavior parameters, and user profile
settings. The Settings class offers a single source of truth for all
configuration values needed across the automation framework.

The module includes:
- Settings class: Container for all configuration parameters
- settings: Global instance for easy access throughout the framework
- Path validation: Ensures required executables and directories exist

Configuration includes browser executable paths, window dimensions, wait times,
headless mode toggle, and anti-detection settings for web automation.
"""

import os
from pathlib import Path


class Settings:
    """
    Centralized configuration management for browser automation settings.

    This class encapsulates all configuration parameters needed for
    browser automation, including executable paths, user profile settings,
    browser behavior parameters, and anti-detection measures. The configuration
    is designed to be easily customizable while maintaining sensible defaults
    for common automation scenarios.

    The class provides validation capabilities to ensure that all required
    external dependencies are available before automation execution begins,
    preventing runtime failures due to missing files or incorrect paths.
    """

    # Browser executable paths - adjust to match your system installation
    CHROMIUM_BINARY = "/data/program_files/chromium/chrome"
    """
    Path to the Chromium browser executable.
    This should point to the main browser binary that will be launched for automation.
    Ensure this path matches your actual Chromium installation location.
    """

    CHROMEDRIVER_PATH = "/data/program_files/chromedriver/chromedriver"
    """
    Path to the ChromeDriver executable.
    ChromeDriver acts as the bridge between your automation code and the browser,
    translating commands into browser actions. Must be compatible with your
    Chromium version.
    """

    # User profile configuration for persistent browser state
    USER_DATA_DIR = "/home/crealab/.config/chromium"  # Adjust if different
    """
    Directory containing the user profile data.
    This path stores browser settings, bookmarks, history, and other user-specific
    data. Using an existing profile preserves cookies and preferences, improving
    automation reliability for sites requiring authentication or customization.
    """

    PROFILE_NAME = "Default"  # Change if using different profile
    """
    Specific profile name within the user data directory.
    Allows selection of a particular user profile when Chromium supports
    multiple profiles. 'Default' is typically used for the main user profile.
    """

    # Browser behavioral settings for consistent execution
    BROWSER_HEADLESS = False  # Set to True if you don't want to see the browser
    """
    Controls whether the browser runs in headless mode.
    Headless mode runs the browser without GUI, which is faster and suitable
    for server environments. Set to True for CI/CD pipelines or when visual
    feedback isn't needed.
    """

    WINDOW_WIDTH = 1920
    """
    Width of the browser window in pixels.
    Standard Full HD resolution provides good compatibility with most websites
    and ensures elements are displayed as intended for automation scripts.
    """

    WINDOW_HEIGHT = 1080
    """
    Height of the browser window in pixels.
    Standard Full HD resolution maintains consistent viewport size across
    different execution environments, reducing layout-dependent failures.
    """

    IMPLICIT_WAIT = 10
    """
    Implicit wait time in seconds for element discovery.
    The browser will wait up to this duration for elements to appear before
    throwing exceptions. Balances between responsiveness and reliability.
    """

    PAGE_LOAD_TIMEOUT = 30
    """
    Maximum time in seconds to wait for page loads.
    Prevents indefinite waits when pages fail to load completely, ensuring
    automation continues processing rather than hanging indefinitely.
    """

    # Anti-detection and stealth configuration
    AVOID_DETECTION = True
    """
    Enables browser configuration options to avoid automation detection.
    When enabled, applies various techniques to make automation less detectable
    by websites that may block or limit automated access.
    """

    @classmethod
    def validate_paths(cls):
        """
        Verify that all required external files and directories exist.

        This validation method checks that all specified executable paths
        and configuration directories are accessible before automation begins.
        It raises appropriate exceptions when critical dependencies are missing
        and provides warnings for optional directories that don't exist.

        The validation helps prevent runtime failures by catching configuration
        issues early in the execution process, improving the reliability of
        automated tests and operations.

        Raises:
            FileNotFoundError: If required executables or critical files are missing.
        """
        paths = [
            cls.CHROMIUM_BINARY,
            cls.CHROMEDRIVER_PATH
        ]
        
        for path in paths:
            if not Path(path).exists():
                raise FileNotFoundError(f"Required file not found: {path}")
        
        # Check if user data dir exists and create if missing
        if not Path(cls.USER_DATA_DIR).exists():
            print(f"Warning: User data directory not found: {cls.USER_DATA_DIR}")
            print("Creating directory...")
            Path(cls.USER_DATA_DIR).mkdir(parents=True, exist_ok=True)



settings = Settings()
'''
Global settings instance following singleton pattern
This ensures consistent configuration access across all application modules
'''
settings.validate_paths()