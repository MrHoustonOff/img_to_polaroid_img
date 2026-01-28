import pytest
from polaroid import config
from polaroid.validation import validate_image_dimensions
from polaroid.exceptions import ImageValidationError


def test_valid_dimensions():
    """Тест на идеальные размеры."""
    # 1000x1000 — это соотношение 1.0, размер > 50. Все ок.
    validate_image_dimensions(1000, 1000)


def test_image_too_small():
    """Тест: одна из сторон меньше минимума."""
    # Ширина 40 меньше MIN_IMAGE_SIZE (50)
    with pytest.raises(ImageValidationError) as excinfo:
        validate_image_dimensions(40, 1000)

    assert "too small" in str(excinfo.value)


def test_aspect_ratio_too_narrow():
    """Тест: картинка слишком узкая (лапша)."""
    # 100 / 1000 = 0.1 (Меньше минимума 0.3)
    with pytest.raises(ImageValidationError):
        validate_image_dimensions(100, 1000)


def test_aspect_ratio_too_wide():
    """Тест: картинка слишком широкая (панорама)."""
    # 1000 / 100 = 10.0 (Больше максимума 3.0)
    with pytest.raises(ImageValidationError):
        validate_image_dimensions(1000, 100)
