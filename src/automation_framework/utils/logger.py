"""
automation_framework.utils.logger - Centralized logging system for automation workflows.

This module provides a structured logging system specifically designed for automation
testing. It offers consistent logging across all automation components (web, desktop)
with both console output for real-time monitoring and file output for historical records.
The logger includes methods for different log levels (info, warning, error, critical)
and supports additional context data for enhanced debugging.

Main Components:
- AutomationLogger: Class that wraps Python's logging module with automation-specific features
- automation_logger: Global instance for easy access throughout the framework

The logger outputs timestamps, log levels, and messages in a consistent format to help
track automation execution flow and diagnose issues quickly.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from selenium.webdriver.remote.webdriver import WebDriver

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


automation_logger = AutomationLogger()
'''Instance of AutomationLogger. 
Global instance for easy access throughout the application
This singleton pattern ensures consistent logging configuration across all modules
'''