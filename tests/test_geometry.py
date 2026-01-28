from polaroid.geometry import calculate_layout
from polaroid import config


def test_layout_calculation():
    """
    Проверяем математику на круглых числах.
    Пусть ширина фото = 1000px.
    """
    w, h = 1000, 1000

    layout = calculate_layout(w, h)

    # Проверяем поля согласно конфигу:
    # Side = 0.06 * 1000 = 60
    # Top = 0.06 * 1000 = 60
    # Bottom = 0.18 * 1000 = 180

    expected_width = 1000 + 60 + 60    # 1120
    expected_height = 1000 + 60 + 180  # 1240

    assert layout.total_size == (1120, 1240)
    assert layout.photo_pos == (60, 60)  # Фото сдвинуто на side и top
