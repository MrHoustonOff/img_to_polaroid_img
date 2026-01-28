from PIL import Image
from . import validation, geometry, config, filters
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
    
    validation.validate_image_dimensions(image.width, image.height)

    layout = geometry.calculate_layout(image.width, image.height)

    seed = kwargs.get('seed', None)
    
    grain_intensity = kwargs.get('grain_intensity', config.GRAIN_INTENSITY)

    processed_photo = filters.apply_grain(image, grain_intensity, seed)

    result_image = Image.new("RGB", layout.total_size, config.PAPER_BASE_COLOR)

    result_image.paste(processed_photo, layout.photo_pos)

    photo_mask = Image.new("L", image.size, 255) # L = Grayscale, 255 = White

    # 6. Сборка результата
    return PolaroidResult(
        image=result_image,
        photo_mask=photo_mask,
        # Разворачиваем координаты (x, y) и добавляем ширину/высоту
        photo_rect=(layout.photo_pos[0], layout.photo_pos[1],
                    image.width, image.height),
        border_rect=(0, 0, layout.total_size[0], layout.total_size[1]),
        style_info={"profile": profile, "overrides": kwargs}
    )
