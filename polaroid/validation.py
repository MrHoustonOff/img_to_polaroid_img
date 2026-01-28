from PIL import Image
from . import config
from .exceptions import ImageValidationError

def validate_image_dimensions(width: int, height: int) -> None:
    """
    Проверяет, соответствует ли изображение минимальным требованиям.

    Args:
        width (int): Ширина изображения.
        height (int): Высота изображения.

    Raises:
        ImageValidationError: Если изображение слишком маленькое или имеет 
                              экстремальное соотношение сторон.
    """
    # 1. Проверка минимального размера
    min_size = config.MIN_IMAGE_SIZE
    if width < min_size or height < min_size:
        raise ImageValidationError(
            f"Image is too small ({width}x{height}). "
            f"Minimum dimension is {min_size}px."
        )

    # 2. Проверка соотношения сторон (Aspect Ratio)
    # Чтобы не обрабатывать узкие "сосиски" или плоские линии
    ratio = width / height
    if ratio < config.MIN_ASPECT_RATIO or ratio > config.MAX_ASPECT_RATIO:
        raise ImageValidationError(
            f"Extreme aspect ratio ({ratio:.2f}). "
            f"Supported range: {config.MIN_ASPECT_RATIO} to {config.MAX_ASPECT_RATIO}."
        )