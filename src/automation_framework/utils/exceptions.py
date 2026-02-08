"""
automation_framework.utils.exceptions - Defines custom error types for automation failures.

This module provides specialized exception classes that handle different types of
automation errors with detailed context information. Instead of generic Python
exceptions, these custom errors capture specific details about what went wrong
during automation, making debugging much easier.

The module includes:
- AutomationError: Base class for all automation-related exceptions
- ElementNotFoundError: When UI elements can't be located on the page
- ActionFailedError: When elements exist but interactions fail (click, type, etc.)
- NavigationError: When page navigation encounters problems
- PyAutoGUIError: When desktop automation operations fail

Each exception stores relevant debugging information like component names,
actions performed, and contextual details to help identify the root cause quickly.
"""

from typing import Optional, Dict, Any


class AutomationError(Exception):
    """Base exception for all automation-related failures providing structured error context.

    This exception serves as the foundation for all automation-specific errors,
    capturing essential debugging information including the component where
    the error occurred, the action being performed, and additional context
    that helps identify the root cause of failures. The exception automatically
    formats a comprehensive error message combining all available context
    information for immediate troubleshooting visibility.

    The design allows for rich error tracking without losing the original
    exception chain, making it suitable for both manual debugging and
    automated error reporting systems.

    Args:
        message: Human-readable description of the error condition
        component: Name of the component where error occurred (e.g., 'LoginPage')
        action: Action being performed when error occurred (e.g., 'login')
        details: Additional context-specific details as dictionary
        original_exception: The original exception that triggered this one

    Attributes:
        component: Component name where error originated
        action: Action being executed when error occurred
        details: Dictionary containing additional debugging context
        original_exception: Reference to the underlying exception if applicable

    Example:
        >>> try:
        ...     # Some automation action
        ...     pass
        ... except Exception as e:
        ...     raise AutomationError(
        ...         message="Failed to login",
        ...         component="LoginPage",
        ...         action="click_login_button",
        ...         details={"username": "john@example.com"},
        ...         original_exception=e
        ...     )
    """

    def __init__(
        self,
        message: str,
        component: str = "Unknown",
        action: str = "Unknown",
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """Initialize the automation error with comprehensive context."""
        self.component = component
        self.action = action
        self.details = details or {}
        self.original_exception = original_exception
        
        # Format complete error message with all available context
        formatted_message = self._format_message(message)
        super().__init__(formatted_message)

    def _format_message(self, message: str) -> str:
        """
        Construct a comprehensive error message combining all context information.

        This method intelligently combines the base message with component,
        action, details, and original exception information to create a
        single, informative error string that provides maximum debugging value
        at first glance.

        Args:
            message: Base error message describing the failure condition

        Returns:
            Complete error message string containing all relevant context
        """
        formatted = f"[{self.component}] {message}"
        if self.action != "Unknown":
            formatted += f" during '{self.action}'"
        if self.details:
            formatted += f" (details: {self.details})"
        if self.original_exception:
            formatted += f" (original: {type(self.original_exception).__name__}: {self.original_exception})"
        return formatted

class ActionFailedError(AutomationError):
    """Raised when a UI interaction action fails despite the element being present.

    This exception handles cases where the target element exists but the
    intended interaction cannot be completed successfully. Common scenarios
    include attempting to click disabled buttons, typing into read-only fields,
    selecting options from disabled dropdowns, or performing actions when
    the UI is in an unexpected state.

    Unlike ElementNotFoundError which indicates missing elements, this
    exception signals that the element exists but the requested action
    cannot proceed due to state constraints, permissions, or UI behavior
    that prevents the interaction.

    Args:
        action_type: Type of action that failed ('click', 'type', 'select', 'hover', etc.)
        element: The element involved in the failed action
        page: The page or context where the action was attempted
        reason: Specific explanation for why the action failed
        details: Additional context-specific details about the failure scenario

    Attributes:
        action_type: Type of interaction that failed
        element: Target element for the action
        page: Location where action was attempted
        reason: Detailed explanation of the failure cause

    Example:
        >>> from utils.exceptions import ActionFailedError
        >>> raise ActionFailedError(
        ...     action_type="click",
        ...     element="submit_button",
        ...     page="CheckoutPage",
        ...     reason="Element was disabled",
        ...     details={"button_state": "disabled", "user_role": "guest"}
        ... )
    """

    def __init__(
        self,
        action_type: str,
        element: str,
        page: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the action failure error with specific interaction context."""
        self.action_type = action_type
        self.element = element
        self.page = page
        self.reason = reason
        
        message = f"Action '{action_type}' failed on element '{element}': {reason}"
        
        super().__init__(
            message=message,
            component=page,
            action=f"{action_type}_{element}",
            details=details or {
                "action_type": action_type,
                "element": element,
                "reason": reason
            }
        )

class ElementNotFoundError(AutomationError):
    """
    Raised when a required UI element cannot be found during automation execution.

    This exception specifically addresses scenarios where expected UI elements
    (buttons, inputs, divs, etc.) are not located within the specified timeout
    period. It's commonly encountered in web automation when dealing with
    dynamic content loading, asynchronous updates, or UI changes that weren't
    anticipated in the test design.

    The exception captures the element identifier, search criteria used,
    timeout duration, and additional context to enable precise diagnosis
    of whether the issue stems from timing problems, incorrect selectors,
    or actual missing elements.

    Args:
        element: The name/description of the element that was not found (e.g., 'login_button')
        page: The page or context where the element was expected to exist
        locator: The selector strategy and value used to locate the element (e.g., "(By.ID, 'submit')")
        timeout: Time waited before giving up on finding the element (in seconds)
        details: Additional context-specific details relevant to the search attempt

    Attributes:
        element: Name of the missing UI element
        page: Location where element was expected
        locator: Search criteria used to find the element
        timeout: Duration waited before declaring element not found

    Example:
        >>> from utils.exceptions import ElementNotFoundError
        >>> raise ElementNotFoundError(
        ...     element="submit_button",
        ...     page="RegistrationForm",
        ...     locator="(By.ID, 'submit')",
        ...     timeout=10,
        ...     details={"form_state": "validated"}
        ... )
    """

    def __init__(
        self,
        element: str,
        page: str,
        locator: str = "Unknown",
        timeout: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the element not found error with specific search context."""
        self.element = element
        self.page = page
        self.locator = locator
        self.timeout = timeout
        
        message = f"Element '{element}' not found"
        if locator != "Unknown":
            message += f" using locator {locator}"
        if timeout is not None:
            message += f" after {timeout}s"
            
        super().__init__(
            message=message,
            component=page,
            action=f"find_{element}",
            details=details or {"element": element, "locator": locator, "timeout": timeout}
        )

class NavigationError(AutomationError):
    """Raised when page navigation fails or unexpected page states are encountered.

    This exception covers navigation-related failures including page load timeouts,
    unexpected redirects, incorrect page titles, broken links, or scenarios where
    the browser lands on an unintended page after a navigation attempt. It's
    particularly useful for identifying issues with URL routing, authentication
    redirects, or application flow problems that manifest as navigation failures.

    The exception captures both expected and actual outcomes to highlight
    discrepancies between intended and actual navigation results, enabling
    rapid identification of routing issues, permission problems, or
    configuration errors.

    Args:
        url: The URL that was attempted to navigate to
        expected_title: Expected page title after navigation (if applicable)
        actual_title: Actual page title encountered after navigation attempt
        timeout: Time waited before considering navigation to have timed out (in seconds)
        details: Additional context-specific details about the navigation attempt

    Attributes:
        url: Target URL that failed to load
        expected_title: Intended destination page title
        actual_title: Page title of the page that was actually loaded
        timeout: Duration waited before navigation timeout

    Example:
        >>> from utils.exceptions import NavigationError
        >>> raise NavigationError(
        ...     url="https://example.com/login",
        ...     expected_title="Login Page",
        ...     actual_title="404 Not Found",
        ...     timeout=15,
        ...     details={"referrer": "home_page"}
        ... )
    """

    def __init__(
        self,
        url: str,
        expected_title: Optional[str] = None,
        actual_title: Optional[str] = None,
        timeout: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the navigation error with URL and page state context."""
        self.url = url
        self.expected_title = expected_title
        self.actual_title = actual_title
        self.timeout = timeout
        
        message = f"Navigation to '{url}' failed"
        if expected_title and actual_title:
            message += f". Expected: '{expected_title}', Got: '{actual_title}'"
        elif expected_title:
            message += f". Expected title: '{expected_title}'"
        elif actual_title:
            message += f". Actual title: '{actual_title}'"
        if timeout:
            message += f" after {timeout}s"
            
        super().__init__(
            message=message,
            component="Navigation",
            action="navigate",
            details=details or {
                "url": url,
                "expected_title": expected_title,
                "actual_title": actual_title,
                "timeout": timeout
            }
        )

class PyAutoGUIError(AutomationError):
    """Raised when PyAutoGUI desktop automation operations encounter failures.

    This exception specifically handles failures in desktop-level automation
    tasks that interact with the operating system directly rather than
    web browsers or applications. Common scenarios include coordinate-based
    clicks that miss their targets, image recognition failures, screen
    region detection issues, or accessibility problems with system-level
    automation APIs.

    The exception is designed to capture the specific PyAutoGUI operation,
    its target parameters, and failure reasons to distinguish desktop
    automation issues from web automation problems, enabling targeted
    troubleshooting approaches.

    Args:
        operation: The specific PyAutoGUI function that failed ('click', 'locate', 'typewrite', etc.)
        target: The target parameter for the operation (coordinates, image file, text, etc.)
        reason: Specific explanation for why the PyAutoGUI operation failed
        details: Additional context-specific details about the desktop environment

    Attributes:
        operation: PyAutoGUI function that encountered the error
        target: Parameter specifying what the operation was targeting
        reason: Detailed explanation of the desktop automation failure

    Example:
        >>> from utils.exceptions import PyAutoGUIError
        >>> raise PyAutoGUIError(
        ...     operation="click",
        ...     target="(500, 300)",
        ...     reason="Coordinate not found on screen",
        ...     details={"screen_size": "(1920, 1080)", "confidence": 0.9}
        ... )
    """

    def __init__(
        self,
        operation: str,
        target: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the PyAutoGUI error with desktop automation context."""
        self.operation = operation
        self.target = target
        self.reason = reason
        
        message = f"PyAutoGUI operation '{operation}' failed on '{target}': {reason}"
        
        super().__init__(
            message=message,
            component="PyAutoGUI",
            action=f"{operation}_{target}",
            details=details or {
                "operation": operation,
                "target": target,
                "reason": reason
            }
        )