from datetime import date
from typing import Any
from app.exceptions import (
    UniquePlantConstraintError, 
    UniqueBotanicalNameError, 
    UniqueImagePathError,
    )

def validate_positive_int(value: Any, name: str) -> None:
    """
    Validates that a value is a positive integer.

    Args:
        value (Any): The value to validate.
        name (str): The name of the field for error messages.

    Raises:
        TypeError: If the value is not an int.
        ValueError: If the value is not positive.
    """
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer. Got {type(value).__name__}.")
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer. Got {value!r}.")

def validate_non_empty_str(value: Any, name: str) -> None:
    """
    Validates that a value is a non-empty string (not just whitespace).

    Args:
        value (Any): The value to validate.
        name (str): The name of the field for error messages.

    Raises:
        TypeError: If the value is not a string.
        ValueError: If the string is empty or contains only whitespace.
    """
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string. Got {type(value).__name__}.")
    if not value.strip():
        raise ValueError(f"{name} must be a non-empty string. Got {value!r}.")

def validate_and_strip_str(val: Any, field: str) -> str:
    """
    Validates that the input is a non-empty string and strips whitespace.

    Args:
        val (Any): The value to validate and strip.
        field (str): The name of the field for error messages.

    Raises:
        TypeError: If val is not a string.
        ValueError: If val is an empty or whitespace-only string.

    Returns:
        str: The stripped string.
    """
    if not isinstance(val, str):
        raise TypeError(f"{field} must be a string, got {type(val).__name__}")
    stripped = val.strip()
    if not stripped:
        raise ValueError(f"{field} must not be empty or whitespace only")
    return stripped
    
def validate_date_or_none(value: Any, name: str = "date") -> None:
    """
    Validates that a value is either a datetime.date instance or None.

    Args:
        value (Any): The value to validate.
        name (str): Field name to include in the error message.

    Raises:
        TypeError: If the value is neither a date nor None.
    """
    if value is not None and not isinstance(value, date):
        raise TypeError(f"{name} must be a datetime.date object or None. Got {type(value).__name__}.")

def handle_unique_violation(e: Exception) -> None:
    """
    Parses a database UniqueViolation exception and raises a custom error.

    Args:
        e (Exception): The original exception from the database.

    Raises:
        UniqueBotanicalNameError: If the error is due to botanical name uniqueness.
        UniqueImagePathError: If the error is due to image path uniqueness.
        UniquePlantConstraintError: For other unique constraint violations.
    """
    error_msg = str(e)

    if "unique_botanical_name" in error_msg:
        raise UniqueBotanicalNameError("Botanical name already exists.") from e
    elif "unique_image_path" in error_msg:
        raise UniqueImagePathError("Image path already exists.") from e
    else:
        raise UniquePlantConstraintError("Unique constraint violation.") from e
