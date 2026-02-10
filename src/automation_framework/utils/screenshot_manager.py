"""
Screenshot management utilities for cross-platform debugging.

This module provides a unified interface for capturing screenshots regardless
of whether the failure originated from Selenium, PyAutoGUI, or other sources.
It ensures consistent naming, storage, and retrieval of debug screenshots.

Example:
    >>> from utils.screenshot_manager import ScreenshotManager
    >>> manager = ScreenshotManager()
    >>> # In a test
    >>> try:
    ...     # Some failing operation
    ...     pass
    ... except Exception:
    ...     screenshot_path = manager.capture_on_failure(
    ...         context="login_flow",
    ...         error_type="ElementNotFound"
    ...     )
    ...     print(f"Screenshot saved: {screenshot_path}")
"""

import os
import time
import mss
from PIL import ImageGrab
from datetime import datetime
from typing import Optional, Union
from pathlib import Path
import platform

class ScreenshotManager:
    """
    Manages screenshot capture for debugging purposes across different platforms.

    This class provides a unified interface for taking screenshots when failures
    occur, regardless of whether they originate from web automation (Selenium)
    or desktop automation (PyAutoGUI). It handles file naming, directory
    organization, and platform-specific considerations. The implementation
    prioritizes reliability by implementing multiple fallback strategies
    for different operating systems and available libraries.

    The manager supports both system-level screenshots and driver-specific
    screenshots for web automation, ensuring comprehensive coverage of
    different automation scenarios. It also provides automatic cleanup
    capabilities to prevent disk space issues from accumulating screenshots.
    """

    def __init__(self, base_directory: str = "logs/screenshots"):
        """
        Initialize the screenshot manager with organized storage structure.

        Creates the base directory for screenshot storage and ensures all
        parent directories exist. The directory structure supports organized
        storage of debugging artifacts with clear separation from other
        project files.

        Args:
            base_directory: Base directory path for storing screenshots.
                        Will be created if it doesn't exist, along with
                        any necessary parent directories.
        """
        self.base_directory = Path(base_directory)
        self.base_directory.mkdir(parents=True, exist_ok=True)

    def capture_on_failure(
        self,
        context: str = "unknown",
        error_type: str = "general",
        prefix: str = "",
        suffix: str = ""
    ) -> str:
        """
        Capture a screenshot immediately upon failure with descriptive naming.

        This method implements a multi-platform approach to screenshot capture,
        automatically detecting the operating system and using the most
        appropriate screenshot mechanism available. It creates a descriptive
        filename that incorporates the context, error type, and timestamp
        for easy identification during debugging sessions.

        The method includes comprehensive fallback mechanisms to ensure
        screenshot availability even when primary capture methods fail,
        making it robust for production environments where debugging
        information is critical.

        Args:
            context: Context or page where failure occurred (e.g., 'login_page').
                    Used in filename generation to identify the test scenario.
            error_type: Type of error (e.g., 'timeout', 'element_not_found').
                       Provides classification for debugging analysis.
            prefix: Optional prefix to add to filename for additional context.
            suffix: Optional suffix to add to filename for supplementary info.

        Returns:
            Absolute path to the saved screenshot file as a string.
            The path can be used for logging, reporting, or automated analysis.

        Example:
            >>> manager = ScreenshotManager()
            >>> path = manager.capture_on_failure(
            ...     context="payment_form",
            ...     error_type="validation_error"
            ... )
            >>> print(path)
            'logs/screenshots/payment_form_validation_error_20231201_143022.png'
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitize context and error_type for filename compatibility
        sanitized_context = self._sanitize_filename(context)
        sanitized_error_type = self._sanitize_filename(error_type)
        
        # Build comprehensive filename with all components
        filename_parts = []
        if prefix:
            filename_parts.append(self._sanitize_filename(prefix))
        filename_parts.extend([sanitized_context, sanitized_error_type, timestamp])
        if suffix:
            filename_parts.append(self._sanitize_filename(suffix))
        
        filename = "_".join(filename_parts) + ".png"
        filepath = self.base_directory / filename
        
        # Take screenshot using platform-appropriate method
        if platform.system() == "Windows":
            self._capture_windows_screenshot(filepath)
        elif platform.system() in ["Darwin", "Linux"]:
            self._capture_unix_screenshot(filepath)
        else:
            # Fallback: try PIL/Pillow if available
            self._capture_fallback_screenshot(filepath)
        
        return str(filepath)

    def capture_with_driver(
        self,
        driver: object,
        context: str = "web",
        action: str = "screenshot"
    ) -> str:
        """
        Capture screenshot using Selenium WebDriver for web automation debugging.

        This method leverages the WebDriver's native screenshot capability,
        which typically provides higher fidelity and accuracy than system-level
        screenshots for web content. It's particularly valuable for capturing
        exact browser viewport states including dynamic content that might
        not be visible in system screenshots.

        The method includes graceful fallback handling for drivers that
        don't support screenshot functionality, ensuring consistent behavior
        across different browser types and configurations.

        Args:
            driver: Selenium WebDriver instance with screenshot capability.
                   Must implement the save_screenshot method.
            context: Context for the screenshot (e.g., 'checkout_page').
                    Used for filename generation and debugging identification.
            action: Action being performed (e.g., 'payment_failed').
                   Provides additional classification for the failure scenario.

        Returns:
            Path to the saved screenshot file as a string, ready for
            inclusion in test reports or debugging logs.

        Example:
            >>> from selenium import webdriver
            >>> driver = webdriver.Chrome()
            >>> manager = ScreenshotManager()
            >>> path = manager.capture_with_driver(
            ...     driver,
            ...     context="checkout_page",
            ...     action="payment_failed"
            ... )
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{context}_{action}_{timestamp}.png"
        filepath = self.base_directory / filename
        
        # Attempt to save screenshot from driver
        try:
            driver.save_screenshot(str(filepath))
        except AttributeError:
            # Driver doesn't support screenshots (e.g., PhantomJS)
            # Fall back to system screenshot
            self._capture_system_screenshot(filepath)
        
        return str(filepath)

    def _sanitize_filename(self, name: str) -> str:
        """
        Transform potentially unsafe strings into filename-compatible format.

        This method removes or replaces characters that are invalid or
        problematic in filenames across different operating systems,
        preventing filesystem errors and ensuring consistent behavior.

        Args:
            name: Original string that may contain unsafe characters for filenames.

        Returns:
            Clean, filename-safe string with problematic characters removed or replaced.
        """
        # Replace problematic characters with underscores
        sanitized = name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        # Remove other potentially problematic characters that cause issues on various platforms
        for char in '<>:"/\\|?*':
            sanitized = sanitized.replace(char, "")
        return sanitized

    def _capture_windows_screenshot(self, filepath: Path):
        """
        Capture high-quality screenshot on Windows systems using optimized methods.

        This method prioritizes the mss library for fast, efficient screenshot
        capture on Windows, falling back to PIL/Pillow when mss is unavailable.
        The implementation focuses on reliability and performance for
        automated testing scenarios.

        Args:
            filepath: Destination path where the screenshot should be saved.
                     Should have .png extension for optimal compatibility.
        """
        try:
            with mss.mss() as sct:
                sct.shot(output=str(filepath))
        except ImportError:
            # Fallback to PIL if mss not available
            self._capture_fallback_screenshot(filepath)
        except Exception:
            # Fallback on any error to ensure screenshot availability
            self._capture_fallback_screenshot(filepath)

    def _capture_unix_screenshot(self, filepath: Path):
        """
        Capture screenshot on Unix-like systems using native tools.

        This method utilizes system-native screenshot utilities for optimal
        performance and quality on macOS and Linux systems. It includes
        specific handling for each platform's preferred screenshot tools
        and gracefully degrades to alternative methods when primary tools
        are unavailable.

        Args:
            filepath: Path where the screenshot should be stored.
                     Should have .png extension for standardization.
        """
        import subprocess
        import platform
        
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                subprocess.run(["screencapture", "-x", str(filepath)], check=True)
            elif system == "Linux":
                # Try scrot first (common on Linux distributions)
                subprocess.run(["scrot", str(filepath)], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to PIL when native tools aren't available
            self._capture_fallback_screenshot(filepath)

    def _capture_fallback_screenshot(self, filepath: Path):
        """
        Universal fallback screenshot method using PIL/Pillow.

        This method serves as the ultimate backup when platform-specific
        screenshot methods fail. It uses PIL's ImageGrab functionality
        which works across most platforms but requires PIL/Pillow to be installed.

        When no screenshot capability is available, it creates a placeholder
        file with diagnostic information to maintain debugging workflow continuity.

        Args:
            filepath: Target location for saving the screenshot.
                     If screenshot fails, creates a diagnostic text file instead.
        """
        try:
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
        except ImportError:
            # No screenshot capability available - create diagnostic file
            filepath.write_text(f"Screenshot unavailable on {platform.system()}")
        except Exception as e:
            # Log the error but continue with diagnostic file
            filepath.write_text(f"Screenshot failed: {str(e)}")

    def cleanup_old_screenshots(self, days_to_keep: int = 7):
        """
        Maintain disk space by removing outdated screenshot files.

        This method implements automatic cleanup of old screenshots to prevent
        unbounded growth of the logs directory. It uses file modification time
        to determine which files exceed the retention period, ensuring that
        only truly old files are removed while preserving recent debugging data.

        The cleanup process is designed to be safe and non-disruptive,
        only removing PNG files within the managed directory structure.

        Args:
            days_to_keep: Number of days to retain screenshots before deletion.
                        Default is 7 days, balancing debugging needs with
                        disk space conservation.

        Example:
            >>> manager = ScreenshotManager()
            >>> manager.cleanup_old_screenshots(days_to_keep=3)
        """
        import time
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        
        for screenshot_file in self.base_directory.glob("*.png"):
            if screenshot_file.stat().st_mtime < cutoff_time:
                screenshot_file.unlink()