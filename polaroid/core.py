from PIL import Image
from . import validation
from .data import PolaroidResult

def process_image(image: Image.Image, profile: str = "classic", **kwargs) -> PolaroidResult:
    """
    Основная точка входа в библиотеку.
    Превращает обычное изображение в Polaroid Style.

    Args:
        image: Исходное изображение (PIL.Image)
        profile: Имя стиля (по умолчанию "classic")
        **kwargs: Дополнительные параметры

    Returns:
        PolaroidResult: Объект PolaroidResult с итоговым изображением и метаданными.
    """
    
    # 1. Валидация входных данных
    validation.validate_image_dimensions(image.width, image.height)

    raise NotImplementedError("WIP")
