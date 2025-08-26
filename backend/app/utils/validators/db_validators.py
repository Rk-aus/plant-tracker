from datetime import date
from typing import Any
from app.exceptions import ValidationError

def validate_positive_int(value: Any, name: str) -> None:
    """
    Validates that a value is a positive integer.

    Args:
        value (Any): The value to validate.
        name (str): The name of the field for error messages.

    Raises:
        ValidationError: If the value is not an integer or not positive.
    """
    if not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer. Got {type(value).__name__}.")
    if value <= 0:
        raise ValidationError(f"{name} must be a positive integer. Got {value!r}.")

def validate_non_empty_str(value: Any, name: str) -> None:
    """
    Validates that a value is a non-empty string (not just whitespace).

    Args:
        value (Any): The value to validate.
        name (str): The name of the field for error messages.

    Raises:
        ValidationError: If the value is not a string, or if it is empty/whitespace only.
    """
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string. Got {type(value).__name__}.")
    if not value.strip():
        raise ValueError(f"{name} must be a non-empty string. Got {value!r}.")

def validate_and_strip_str(value: Any, field: str) -> str:
    """
    Validates that the input is a non-empty string and strips whitespace.

    Args:
        value (Any): The value to validate and strip.
        field (str): The name of the field for error messages.

    Raises:
        ValidationError: If the value is not a string, or if it is empty/whitespace only.

    Returns:
        str: The stripped string.
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be a string, got {type(value).__name__}")
    stripped = value.strip()
    if not stripped:
        raise ValidationError(f"{field} must not be empty or whitespace only")
    return stripped
    
def validate_date_or_none(value: Any, name: str = "date") -> None:
    """
    Validates that a value is either a datetime.date instance or None.

    Args:
        value (Any): The value to validate.
        name (str): Field name to include in the error message.

    Raises:
        ValidationError: If the value is neither a date nor None.
    """
    if value is not None and not isinstance(value, date):
        raise ValidationError(f"{name} must be a datetime.date object or None. Got {type(value).__name__}.")
