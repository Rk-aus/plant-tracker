class AppError(Exception):
    """Base class for all application-specific exceptions."""
    status_code: int = 500

    def __init__(self, message: str = "An unexpected error occurred.", status_code: int = None):
        super().__init__(message)
        self.message = message
        if status_code:
            self.status_code = status_code

class UniqueImagePathError(AppError):
    """Raised when the image_path field violates the uniqueness constraint.

    Attributes:
        message (str): Description of the error (default: "Invalid input.").
        status_code (int): HTTP status code (default: 409).
    """
    def __init__(self, message: str = "Invalid input."):
        super().__init__(message, status_code=409)

class ValidationError(AppError):
    """Raised when input validation fails for a request or operation.

    Attributes:
        message (str): Description of the error (default: "Invalid input.").
        status_code (int): HTTP status code (default: 400).
    """
    def __init__(self, message: str = "Invalid input."):
        super().__init__(message, status_code=400)

class PlantNotFoundError(AppError):
    """Raised when a plant could not be found by the provided identifier.

    Attributes:
        identifier (str): The plant name or unique key used in the lookup.
        message (str): Description of the error.
        status_code (int): HTTP status code (default: 404).
    """
    def __init__(self, identifier: str, message: str = None, status_code: int = 404):
        self.identifier = identifier
        self.message = message or f"Plant with identifier '{identifier}' not found."
        self.status_code = status_code
        super().__init__(self.message)



class InvalidSearchFieldError(AppError):
    """Raised when an invalid search field is provided to the search_plants method."""
    def __init__(self, field: str):
        message = f"Invalid search field: '{field}'. Must be 'name', 'family', or 'location'."
        super().__init__(message)
        self.field = field

class InvalidLanguageError(AppError):
    """Raised when an unsupported language code is provided.

    Attributes:
        language (str): The invalid language code that triggered the error.
    """
    def __init__(self, language: str):
        message = f"Invalid language '{language}'. Must be 'en' or 'ja'."
        super().__init__(message)
        self.language = language

