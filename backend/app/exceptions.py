class UniquePlantConstraintError(Exception):
    """Base class for unique constraint violations in PlantDB."""
    pass

class UniqueBotanicalNameError(UniquePlantConstraintError):
    """Raised when botanical_name uniqueness is violated."""
    pass

class UniqueImagePathError(UniquePlantConstraintError):
    """Raised when image_path uniqueness is violated."""
    pass


class PlantNotFoundError(Exception):
    """
    Raised when a plant could not be found by the provided identifier.

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



class InvalidSearchFieldError(ValueError):
    """Raised when an invalid search field is provided to the search_plants method."""
    def __init__(self, field: str):
        message = f"Invalid search field: '{field}'. Must be 'name', 'family', or 'location'."
        super().__init__(message)
        self.field = field

class InvalidLanguageError(ValueError):
    """
    Raised when an unsupported language code is provided.

    Attributes:
        language (str): The invalid language code that triggered the error.
    """
    def __init__(self, language: str):
        message = f"Invalid language '{language}'. Must be 'en' or 'ja'."
        super().__init__(message)
        self.language = language

