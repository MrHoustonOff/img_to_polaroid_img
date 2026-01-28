import pytest
from PIL import Image
from polaroid.core import process_image
from polaroid.exceptions import ImageValidationError

def test_core_validates_bad_image():
    """
    Проверяем, что process_image реально вызывает валидацию.
    Создаем картинку 10x10 (недопустимо мало).
    """
    img = Image.new("RGB", (10, 10))
    
    with pytest.raises(ImageValidationError):
        process_image(img)

def test_core_happy_path_stub():
    """
    Проверяем, что если картинка хорошая, мы доходим до логики.
    """
    img = Image.new("RGB", (1000, 1000))
    
    # Пока мы ждем NotImplementedError, так как логика отрисовки еще не написана.
    # Это доказывает, что валидацию мы ПРОШЛИ.
    
    with pytest.raises(NotImplementedError):
        process_image(img)