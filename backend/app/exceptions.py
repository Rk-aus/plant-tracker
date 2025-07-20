class UniquePlantConstraintError(Exception):
    """Base class for unique constraint violations in PlantDB."""

class UniqueBotanicalNameError(UniquePlantConstraintError):
    """Raised when botanical_name uniqueness is violated."""

class UniqueImagePathError(UniquePlantConstraintError):
    """Raised when image_path uniqueness is violated."""
