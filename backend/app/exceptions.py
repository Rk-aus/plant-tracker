class UniquePlantConstraintError(Exception):
    """Base class for unique constraint violations in PlantDB."""

class UniqueBotanicalNameError(UniquePlantConstraintError):
    """Raised when botanical_name uniqueness is violated."""

class UniqueImagePathError(UniquePlantConstraintError):
    """Raised when image_path uniqueness is violated."""

class PlantNotFoundError(Exception):
    """
    Exception raised when a requested plant record is not found in the database.

    Attributes:
        plant_id (int): ID of the plant that was not found.
        message (str): Optional custom error message.
        status_code (int): Optional HTTP status code for API responses (default: 404).
    """

    def __init__(self, plant_id, message=None, status_code=404):
        self.plant_id = plant_id
        self.message = message or f"Plant with ID {plant_id} was not found."
        self.status_code = status_code
        super().__init__(self.message)
