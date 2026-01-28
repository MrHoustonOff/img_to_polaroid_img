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
    
    # 0. Инициализация Дебаггера
    debugger = Debugger(enabled=debug)
    debugger.save(image, "original_input")

    # 1. Валидация
    validation.validate_image_dimensions(image.width, image.height)

    # 2. ХИМИЯ (Обработка самого фото) =================================
    # Сначала применяем цветокоррекцию (Curves/Color Grading)
    developed_photo = chemistry.develop_image(image)
    debugger.save(developed_photo, "chemistry_developed")

    # Потом накладываем зерно (Grain)
    seed = kwargs.get('seed', None)
    grain_intensity = kwargs.get('grain_intensity', config.GRAIN_INTENSITY)
    
    # Зерно накладываем на уже проявленное фото
    noisy_photo = filters.apply_grain(developed_photo, grain_intensity, seed)
    debugger.save(noisy_photo, "chemistry_grain")
    
    # ==================================================================

    # 3. Расчет геометрии (Layout)
    layout = geometry.calculate_layout(image.width, image.height)

    # 4. Создаем основу (рамку)
    # Используем цвет из обновленного конфига (PAPER_COLOR)
    result_image = Image.new("RGB", layout.total_size, config.PAPER_COLOR)

    # 5. Сборка (пока простая, без теней, это следующий этап)
    result_image.paste(noisy_photo, layout.photo_pos)
    debugger.save(result_image, "composite_flat")

    # 6. Маска (заглушка)
    photo_mask = Image.new("L", image.size, 255)

    return PolaroidResult(
        image=result_image,
        photo_mask=photo_mask,
        photo_rect=(layout.photo_pos[0], layout.photo_pos[1], image.width, image.height),
        border_rect=(0, 0, layout.total_size[0], layout.total_size[1]),
        style_info={"profile": profile, "overrides": kwargs}
    )