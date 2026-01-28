import pytest
from PIL import Image
from polaroid.core import process_image
from polaroid.exceptions import ImageValidationError
from polaroid.data import PolaroidResult

def test_core_validates_bad_image():
    """
    Проверяем, что process_image реально вызывает валидацию.
    Создаем картинку 10x10 (недопустимо мало).
    """
    img = Image.new("RGB", (10, 10))
    
    with pytest.raises(ImageValidationError):
        process_image(img)

def test_core_process_success():
    """
    Проверяем, что библиотека реально возвращает картинку с рамкой.
    """
    # Исходник 1000x1000
    img = Image.new("RGB", (1000, 1000), color="red")
    
    result = process_image(img)
    
    # 1. Проверяем тип возврата
    assert isinstance(result, PolaroidResult)
    
    # 2. Проверяем, что размер вырос (добавилась рамка)
    # 1000 + 60 + 60 = 1120
    # 1000 + 60 + 180 = 1240
    assert result.image.size == (1120, 1240)
    
    # 3. (Опционально) Можно проверить цвет пикселя рамки
    # Проверяем точку (0, 0) - это левый верхний угол рамки
    pixel_color = result.image.getpixel((0, 0))
    # Должен быть наш "PAPER_BASE_COLOR" из конфига (254, 252, 247)
    assert pixel_color == (254, 252, 247)