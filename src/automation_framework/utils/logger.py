"""
Professional logging utilities for automation debugging.

This module provides a comprehensive logging system that integrates with
the debugging infrastructure to provide detailed, contextual logs for
both successful operations and failures. It ensures all automation events
are properly recorded for analysis and troubleshooting.

The logging system implements a hierarchical approach with multiple output
channels, ensuring appropriate information reaches the right audience while
maintaining comprehensive audit trails for post-mortem analysis. It provides
seamless integration with the debug helper system to automatically capture
relevant artifacts during error conditions.

Example:
    >>> from utils.logger import automation_logger
    >>> automation_logger.info("Starting login flow")
    >>> # During failure
    >>> automation_logger.capture_debug_info(driver, context="login_test")
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from selenium.webdriver.remote.webdriver import WebDriver

from automation_framework.utils.debug_helper import DebugHelper


class AutomationLogger:
    """
    Professional logging system for automation with integrated debug capture.

    This class provides a comprehensive logging solution that not only records
    operational events but also integrates with the debug system to automatically
    capture relevant artifacts when failures occur. It maintains consistency
    across different automation contexts (web, desktop, hybrid).

    The implementation follows best practices for enterprise logging including
    structured logging formats, multi-channel output, and automatic debug
    artifact correlation. It handles concurrent access safely and provides
    configurable log levels for different execution environments.
    """

    def __init__(self):
        """
        Initialize the automation logger with comprehensive handler configuration.

        Sets up multiple logging channels including console output for real-time
        monitoring and file output for persistent storage. The initialization
        ensures that duplicate handlers are not added to prevent redundant
        log entries while maintaining all necessary output streams.

        The method also initializes the debug helper component for integrated
        artifact capture during error conditions, creating a cohesive logging
        and debugging ecosystem.
        """

        self.logger = logging.getLogger("Automation")
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers if logger already configured
        if not self.logger.handlers:
            self._setup_handlers()

        self.debug_helper = DebugHelper()

    def _setup_handlers(self):
        """
        Configure comprehensive logging handlers for both console and file output.

        This method establishes two distinct logging channels: a console handler
        for real-time operational feedback and a file handler for detailed
        historical records. Each channel has appropriate formatting and filtering
        to optimize information delivery while maintaining comprehensive logging
        coverage for troubleshooting and analysis purposes.
        """
        # Console handler for real-time feedback during test execution
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for detailed persistent logs with full context information
        file_handler = logging.FileHandler(
            "logs/automation.log",
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(funcName)s() - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def info(self, message: str, extra: Optional[dict] = None):
        """
        Record informational events that track normal operational flow.

        Informational logs document significant milestones in the automation
        process, providing visibility into the progression of tests and operations.
        These logs serve as checkpoints for monitoring progress and identifying
        where processes succeed or begin to encounter issues.

        Args:
            message: Descriptive message about the informational event.
                    Should be concise yet informative about the operation.
            extra: Optional additional context data to include with the log.
                  Useful for including identifiers, parameters, or state information.

        Example:
            >>> automation_logger.info("User logged in successfully", extra={"user_id": 12345})
        """
        if extra:
            message = f"{message} | Context: {extra}"
        self.logger.info(message)

    def warning(self, message: str, extra: Optional[dict] = None):
        """
        Log potential issues that don't halt execution but warrant attention.

        Warning logs indicate conditions that may affect test reliability or
        represent suboptimal states that could lead to future failures.
        These logs help identify areas for improvement and potential problem
        sources before they become critical failures.

        Args:
            message: Description of the warning condition or potential issue.
            extra: Optional additional context data to include with the log.
                  Useful for capturing state information or environmental factors.

        Example:
            >>> automation_logger.warning("Slow response detected", extra={"response_time": 5.2})
        """
        if extra:
            message = f"{message} | Context: {extra}"
        self.logger.warning(message)

    def error(self, message: str, extra: Optional[dict] = None):
        """
        Document errors that impact test execution or expected behavior.

        Error logs record issues that prevent operations from completing as
        expected. These logs are critical for identifying functional problems
        and serve as triggers for the automatic debug artifact capture system.

        Args:
            message: Detailed description of the error condition.
            extra: Optional additional context data to include with the log.
                  Essential for capturing relevant state information for debugging.

        Example:
            >>> automation_logger.error("Login failed", extra={"attempt": 1, "user": "test@example.com"})
        """
        if extra:
            message = f"{message} | Context: {extra}"
        self.logger.error(message)

    def critical(self, message: str, extra: Optional[dict] = None):
        """
        Record critical system failures that halt operations or compromise stability.

        Critical logs indicate severe issues that may affect the entire
        automation framework or system stability. These logs typically
        trigger immediate attention and may indicate infrastructure problems
        or fundamental system failures.

        Args:
            message: Comprehensive description of the critical failure.
            extra: Optional additional context data to include with the log.
                  Critical for understanding the scope and impact of the failure.

        Example:
            >>> automation_logger.critical("System unavailable", extra={"service": "authentication"})
        """
        if extra:
            message = f"{message} | Context: {extra}"
        self.logger.critical(message)

    def capture_debug_info(
        self,
        driver: Optional[WebDriver] = None,
        context: str = "Unknown",
        save_screenshot: bool = True,
        save_page_source: bool = True,
        save_console_logs: bool = True,
        save_system_info: bool = True
    ) -> dict:
        """
        Orchestrate comprehensive debug artifact capture for failure analysis.

        This method serves as the central point for gathering all relevant
        information when failures occur. It coordinates multiple data sources
        to create a complete picture of the failure context, enabling efficient
        troubleshooting and root cause analysis. The method is designed to
        continue operating even when individual capture operations fail,
        ensuring maximum information preservation.

        The debug capture process is highly configurable, allowing different
        combinations of artifacts based on the specific automation context
        and resource constraints.

        Args:
            driver: Optional Selenium WebDriver instance for web automation artifacts.
                   Required for page source and console log capture.
            context: Descriptive name for the test scenario or operation.
                    Used for organizing and identifying debug artifacts.
            save_screenshot: Whether to capture visual state representation.
            save_page_source: Whether to capture HTML source (requires driver).
            save_console_logs: Whether to capture browser console output (requires driver).
            save_system_info: Whether to capture system resource and platform details.

        Returns:
            Dictionary mapping artifact type identifiers to their file paths.
            Enables easy access to all captured debug information for analysis.

        Example:
            >>> from selenium import webdriver
            >>> driver = webdriver.Chrome()
            >>> try:
            ...     # Some operation that might fail
            ...     pass
            ... except Exception as e:
            ...     artifacts = automation_logger.capture_debug_info(
            ...         driver=driver,
            ...         context="login_flow",
            ...         save_screenshot=True,
            ...         save_page_source=True
            ...     )
            ...     print(f"Debug artifacts: {artifacts}")
        """

        artifacts = self.debug_helper.capture_all(
            context=context,
            error="Manual debug capture",
            driver=driver,
            save_screenshot=save_screenshot,
            save_page_source=save_page_source,
            save_console_logs=save_console_logs,
            save_system_info=save_system_info
        )
        
        self.logger.error(f"Debug artifacts captured for context '{context}': {artifacts}")
        return artifacts

    def capture_pyautogui_debug(
        self,
        operation: str,
        target: str,
        error: str,
        context: str = "desktop_automation"
    ) -> dict:
        """
        Specialized debug capture for PyAutoGUI desktop automation failures.

        Desktop automation presents unique challenges for debugging due to
        system-level interactions and environmental dependencies. This method
        captures the specific information needed to diagnose desktop automation
        issues, including screen state, operation context, and environmental
        factors that may affect coordinate-based operations.

        Args:
            operation: PyAutoGUI operation that failed (e.g., 'click', 'locateImage').
                      Provides operational context for the failure.
            target: Target of the operation (coordinates, image file, etc.).
                   Specifies what the operation was attempting to interact with.
            error: Error message or exception from the failed operation.
            context: Contextual name for the operation, defaults to 'desktop_automation'.

        Returns:
            Dictionary mapping PyAutoGUI-specific artifact types to file paths.
            Includes both visual and metadata artifacts for comprehensive debugging.

        Example:
            >>> try:
            ...     import pyautogui
            ...     pyautogui.click(100, 100)
            ... except Exception as e:
            ...     artifacts = automation_logger.capture_pyautogui_debug(
            ...         operation="click",
            ...         target="(100, 100)",
            ...         error=str(e),
            ...         context="file_dialog_interaction"
            ...     )
        """

        artifacts = self.debug_helper.capture_pyautogui_debug(
            operation=operation,
            target=target,
            error=error,
            context=context
        )
        
        self.logger.error(f"PyAutoGUI debug artifacts captured for context '{context}': {artifacts}")
        return artifacts


automation_logger = AutomationLogger()
'''
Global instance of the class AutomationLogger
'''
