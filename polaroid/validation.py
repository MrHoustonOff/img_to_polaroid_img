from . import config
from .exceptions import ImageValidationError


def validate_image_dimensions(width: int, height: int) -> None:
    """
    Проверяет корректность размеров изображения.

    Args:
        width (int): Ширина изображения в пикселях.
        height (int): Высота изображения в пикселях.

    Raises:
        ImageValidationError: Если размеры слишком малы или нарушено соотношение сторон.
    """
    # 1. Проверка на минимальный физический размер
    if width < config.MIN_IMAGE_SIZE or height < config.MIN_IMAGE_SIZE:
        raise ImageValidationError(
            f"Image is too small ({width}x{height}). "
            f"Minimum dimension is {config.MIN_IMAGE_SIZE}px."
        )

    # 2. Проверка соотношения сторон
    aspect_ratio = width / height

    if not (config.MIN_ASPECT_RATIO <= aspect_ratio <= config.MAX_ASPECT_RATIO):
        raise ImageValidationError(
            f"Invalid aspect ratio {aspect_ratio:.2f}. "
            f"Allowed range: [{config.MIN_ASPECT_RATIO} - {config.MAX_ASPECT_RATIO}]."
        )
