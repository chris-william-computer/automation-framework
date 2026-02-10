"""
Comprehensive debug information capture utilities.

This module provides utilities to capture various types of debug information
when failures occur, including screenshots, page sources, console logs,
and system information. It integrates seamlessly with both web and desktop
automation scenarios.

The implementation follows a modular design where each debug artifact type
is handled separately, allowing for flexible configuration based on the
specific automation context. The class provides both integrated capture
methods for web automation and specialized methods for desktop automation
scenarios, ensuring comprehensive coverage across different automation types.

Example:
    >>> from utils.debug_helper import DebugHelper
    >>> helper = DebugHelper()
    >>> # In a failure scenario
    >>> try:
    ...     # Some failing operation
    ...     pass
    ... except Exception as e:
    ...     debug_info = helper.capture_all(
    ...         context="login_test",
    ...         error=str(e),
    ...         driver=webdriver_instance  # optional
    ...     )
    ...     print(f"Debug info captured: {debug_info}")
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import platform
import psutil

from automation_framework.utils.screenshot_manager import ScreenshotManager

class DebugHelper:
    """
    Helper class for capturing comprehensive debug information during failures.

    This class orchestrates the collection of multiple types of debug artifacts
    including screenshots, page sources, console logs, and system information
    to provide a complete picture of the failure context. The implementation
    prioritizes reliability and completeness, ensuring that even partial
    debug information is preserved when individual capture methods fail.

    The helper maintains a structured directory layout for debug artifacts
    and includes automatic cleanup capabilities to prevent disk space issues.
    It integrates with the automation logging system to provide traceability
    of debug capture operations.
    """

    def __init__(self, base_directory: str = "logs/debug_artifacts"):
        """
        Initialize the debug helper with organized artifact storage.

        Sets up the directory structure for debug artifact storage and
        initializes supporting components including the screenshot manager.
        The initialization ensures all necessary directories exist and
        creates a clean foundation for subsequent debug capture operations.

        Args:
            base_directory: Base directory path for storing all debug artifacts.
                Will be created with parent directories if needed.
        """
        self.base_directory = Path(base_directory)
        self.base_directory.mkdir(parents=True, exist_ok=True)
        self.screenshot_manager = ScreenshotManager()

    def capture_all(
        self,
        context: str,
        error: str,
        driver: Optional[object] = None,
        save_screenshot: bool = True,
        save_page_source: bool = True,
        save_console_logs: bool = True,
        save_system_info: bool = True
    ) -> Dict[str, str]:
        """
        Coordinate comprehensive debug artifact capture for complete failure analysis.

        This method orchestrates the capture of multiple debug artifact types
        in a single operation, providing a holistic view of the failure context.
        Each capture operation is performed independently to ensure that
        partial information is preserved even if some capture methods fail.

        The method implements intelligent error handling for each artifact type,
        allowing the overall capture process to continue even when individual
        capture operations encounter issues. This resilience is crucial for
        debugging scenarios where the system state may already be compromised.

        Args:
            context: Context or scenario where failure occurred.
                    Used for organizing and identifying debug artifacts.
            error: Error message or exception that triggered the debug capture.
                  Provides the primary failure information for analysis.
            driver: Optional Selenium WebDriver instance for web automation.
                   Required for page source and console log capture.
            save_screenshot: Whether to capture visual state via screenshot.
            save_page_source: Whether to capture HTML source (requires driver).
            save_console_logs: Whether to capture browser console output (requires driver).
            save_system_info: Whether to capture system resource usage and platform details.

        Returns:
            Dictionary mapping artifact type identifiers to their file paths.
            The result enables easy access to all captured debug information
            for automated analysis or manual inspection.

        Example:
            >>> helper = DebugHelper()
            >>> artifacts = helper.capture_all(
            ...     context="payment_processing",
            ...     error="Payment gateway timeout",
            ...     driver=webdriver_instance,
            ...     save_screenshot=True,
            ...     save_page_source=True
            ... )
            >>> print(artifacts)
            {
                'screenshot': 'logs/debug_artifacts/payment_processing_screenshot_20231201_143022.png',
                'page_source': 'logs/debug_artifacts/payment_processing_page_source_20231201_143022.html',
                'system_info': 'logs/debug_artifacts/payment_processing_system_info_20231201_143022.json'
            }
        """
        from automation_framework.utils.logger import automation_logger

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifacts = {}

        # Capture visual state representation
        if save_screenshot:
            screenshot_path = self.screenshot_manager.capture_on_failure(
                context=context,
                error_type="failure"
            )
            artifacts['screenshot'] = screenshot_path

        # Capture web page content for web automation debugging
        if save_page_source and driver is not None:
            page_source_path = self._capture_page_source(driver, context, timestamp)
            artifacts['page_source'] = page_source_path

        # Capture browser console output for JavaScript error analysis
        if save_console_logs and driver is not None:
            console_log_path = self._capture_console_logs(driver, context, timestamp)
            artifacts['console_logs'] = console_log_path

        # Capture system state for resource-related issue diagnosis
        if save_system_info:
            system_info_path = self._capture_system_info(context, timestamp)
            artifacts['system_info'] = system_info_path

        # Capture error details for root cause analysis
        error_info_path = self._save_error_info(context, error, timestamp)
        artifacts['error_info'] = error_info_path

        automation_logger.error(f"Debug artifacts captured: {artifacts}")
        return artifacts

    def capture_pyautogui_debug(
        self,
        operation: str,
        target: str,
        error: str,
        context: str = "desktop_automation"
    ) -> Dict[str, str]:
        """
        Specialized debug capture for PyAutoGUI desktop automation failures.

        This method addresses the unique requirements of desktop automation
        debugging where system-level screenshots and environment information
        are more relevant than web-specific artifacts. It captures both
        visual evidence and operational context specific to desktop automation.

        The implementation recognizes that PyAutoGUI operates at the system
        level, requiring different diagnostic approaches compared to web
        automation. It includes screen size detection and platform-specific
        information that's crucial for desktop automation troubleshooting.

        Args:
            operation: PyAutoGUI operation that failed (e.g., 'click', 'locateImage').
                      Provides context about the type of desktop interaction.
            target: Target of the operation (coordinates, image file, etc.).
                   Specifies what the operation was attempting to interact with.
            error: Error message or exception from the failed operation.
            context: Context for the operation, defaults to 'desktop_automation'.

        Returns:
            Dictionary mapping PyAutoGUI-specific artifact types to file paths.
            Includes both visual and metadata artifacts for comprehensive debugging.

        Example:
            >>> helper = DebugHelper()
            >>> try:
            ...     import pyautogui
            ...     pyautogui.click(100, 100)
            ... except Exception as e:
            ...     artifacts = helper.capture_pyautogui_debug(
            ...         operation="click",
            ...         target="(100, 100)",
            ...         error=str(e),
            ...         context="file_dialog_interaction"
            ...     )
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifacts = {}

        # Capture system-level screenshot showing actual desktop state
        screenshot_path = self.screenshot_manager.capture_on_failure(
            context=f"{context}_pyautogui_{operation}",
            error_type="pyautogui_error"
        )
        artifacts['screenshot'] = screenshot_path

        # Save PyAutoGUI-specific debug info with environmental context
        debug_info = {
            "operation": operation,
            "target": target,
            "error": error,
            "context": context,
            "timestamp": timestamp,
            "platform": platform.platform(),
            "screen_size": self._get_screen_size()
        }

        debug_file = self.base_directory / f"pyautogui_{context}_{timestamp}.json"
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(debug_info, f, indent=2, ensure_ascii=False)

        artifacts['debug_info'] = str(debug_file)
        return artifacts

    def _capture_page_source(
        self,
        driver: object,
        context: str,
        timestamp: str
    ) -> str:
        """
        Extract and save the complete HTML source from the current web page.

        This method retrieves the full HTML content of the current page,
        providing a static snapshot of the DOM structure at the time of failure.
        The page source is invaluable for analyzing element structure, content
        verification, and understanding the exact state of the web application
        when the failure occurred.

        Args:
            driver: Selenium WebDriver instance with page source access capability.
            context: Context identifier for organizing the saved artifact.
            timestamp: Timestamp for creating unique filename.

        Returns:
            Path to the saved HTML page source file, empty string if capture fails.
        """
        from automation_framework.utils.logger import automation_logger

        try:
            page_source = driver.page_source
            filename = f"{context}_page_source_{timestamp}.html"
            filepath = self.base_directory / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(page_source)
            
            return str(filepath)
        except Exception as e:
            automation_logger.warning(f"Could not capture page source: {e}")
            return ""

    def _capture_console_logs(
        self,
        driver: object,
        context: str,
        timestamp: str
    ) -> str:
        """
        Retrieve and persist browser console logs for JavaScript error analysis.

        Console logs often contain critical information about JavaScript errors,
        warnings, and application-level messages that contribute to automation
        failures. This method captures these logs and formats them for easy
        analysis, helping identify client-side issues that may not be apparent
        from other debug artifacts.

        Args:
            driver: Selenium WebDriver instance with console log access.
            context: Context identifier for organizing the saved artifact.
            timestamp: Timestamp for creating unique filename.

        Returns:
            Path to the saved console logs file, empty string if capture fails.
        """
        from automation_framework.utils.logger import automation_logger

        try:
            logs = driver.get_log("browser")
            if logs:
                filename = f"{context}_console_logs_{timestamp}.log"
                filepath = self.base_directory / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    for entry in logs:
                        f.write(f"[{entry['level']}] {entry['message']}\n")
                
                return str(filepath)
        except Exception as e:
            automation_logger.warning(f"Could not capture console logs: {e}")
        
        return ""

    def _capture_system_info(self, context: str, timestamp: str) -> str:
        """
        Gather comprehensive system resource and platform information.

        System information provides crucial context for diagnosing performance
        issues, resource constraints, and environment-specific problems.
        This method collects key metrics including memory usage, CPU load,
        disk space, and platform details that may influence automation behavior.

        Args:
            context: Context identifier for organizing the saved artifact.
            timestamp: Timestamp for creating unique filename.

        Returns:
            Path to the saved system information JSON file, empty string if capture fails.
        """
        from automation_framework.utils.logger import automation_logger

        try:
            system_info = {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "timestamp": datetime.now().isoformat(),
                "context": context
            }

            filename = f"{context}_system_info_{timestamp}.json"
            filepath = self.base_directory / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(system_info, f, indent=2, ensure_ascii=False)
            
            return str(filepath)
        except Exception as e:
            automation_logger.warning(f"Could not capture system info: {e}")
            return ""

    def _save_error_info(self, context: str, error: str, timestamp: str) -> str:
        """
        Persist error details in structured format for analysis.

        This method captures the essential error information including the
        original error message, exception type, and contextual metadata.
        The structured format enables automated parsing and analysis of
        error patterns across multiple test runs.

        Args:
            context: Context where error occurred, providing scenario context.
            error: Error message or exception object to be preserved.
            timestamp: Timestamp for creating unique filename.

        Returns:
            Path to the saved error information JSON file.
        """
        error_info = {
            "context": context,
            "error": str(error),
            "timestamp": datetime.now().isoformat(),
            "type": type(error).__name__
        }

        filename = f"{context}_error_info_{timestamp}.json"
        filepath = self.base_directory / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(error_info, f, indent=2, ensure_ascii=False)
        
        return str(filepath)

    def _get_screen_size(self) -> Dict[str, int]:
        """
        Determine current display resolution for desktop automation context.

        Screen dimensions are crucial for PyAutoGUI operations since they
        rely on absolute coordinates. Knowing the screen size helps diagnose
        coordinate-based failures and understand the desktop environment
        where the automation was running.

        Returns:
            Dictionary containing width and height keys with pixel dimensions,
            or zero values if screen size cannot be determined.
        """
        try:
            import tkinter as tk
            root = tk.Tk()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            return {"width": width, "height": height}
        except Exception:
            return {"width": 0, "height": 0}