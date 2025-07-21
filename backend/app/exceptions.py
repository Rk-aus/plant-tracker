class UniquePlantConstraintError(Exception):
    """Base class for unique constraint violations in PlantDB."""
    pass

class UniqueBotanicalNameError(UniquePlantConstraintError):
    """Raised when botanical_name uniqueness is violated."""
    pass

class UniqueImagePathError(UniquePlantConstraintError):
    """Raised when image_path uniqueness is violated."""
    pass


class NotFoundError(Exception):
    """
    Base exception for all 'not found' errors in the application.

    This class can be inherited by more specific exceptions such as
    PlantNotFoundError, FamilyNotFoundError, and LocationNotFoundError
    to provide consistent error handling and response formatting.

    Attributes:
        message (str): Description of the error.
        status_code (int): HTTP status code for API responses (default: 404).
    """
    def __init__(self, message=None, status_code=404):
        self.message = message or "Resource was not found."
        self.status_code = status_code
        super().__init__(self.message)

class PlantNotFoundError(NotFoundError):
    """
    Raised when a plant could not be found by the provided identifier.

    Attributes:
        identifier (str): The plant name or unique key used in the lookup.
        message (str): Optional custom error message.
        status_code (int): HTTP status code (default: 404).
    """
    def __init__(self, identifier, message=None, status_code=404):
        self.identifier = identifier
        default_msg = f"Plant with identifier '{identifier}' not found."
        super().__init__(message or default_msg, status_code)

class FamilyNotFoundError(NotFoundError):
    """
    Raised when a plant family could not be found by the provided identifier.

    Attributes:
        identifier (str): The family name or unique key used in the lookup.
        message (str): Optional custom error message.
        status_code (int): HTTP status code (default: 404).
    """
    def __init__(self, identifier, message=None, status_code=404):
        self.identifier = identifier
        default_msg = f"Family with identifier '{identifier}' not found."
        super().__init__(message or default_msg, status_code)

class LocationNotFoundError(NotFoundError):
    """
    Raised when a location could not be found by the provided identifier.

    Attributes:
        identifier (str): The location name or unique key used in the lookup.
        message (str): Optional custom error message.
        status_code (int): HTTP status code (default: 404).
    """
    def __init__(self, identifier, message=None, status_code=404):
        self.identifier = identifier
        default_msg = f"Location with identifier '{identifier}' not found."
        super().__init__(message or default_msg, status_code)


class InvalidLanguageError(ValueError):
    """
    Raised when an unsupported language code is provided.

    Attributes:
        language (str): The invalid language code.
        message (str): Explanation of accepted values ('en' or 'ja').
    """
    def __init__(self, language):
        super().__init__(f"Invalid language '{language}'. Must be 'en' or 'ja'.")

