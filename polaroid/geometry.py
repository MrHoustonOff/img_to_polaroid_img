from dataclasses import dataclass
from typing import Tuple
from . import config

@dataclass
class Layout:
    """
    Результат расчета геометрии.
    Хранит размеры итогового Polaroid и координаты фото внутри.
    """
    total_size: Tuple[int, int]    # (width, height) всего снимка
    photo_pos: Tuple[int, int]     # (x, y) верхнего левого угла фото

def calculate_layout(image_width: int, image_height: int) -> Layout:
    """
    Рассчитывает геометрию Polaroid на основе ширины изображения.
    Все размеры округляются до целых чисел (пикселей).
    
    """
    # Вычисляем размеры полей (отступов)
    margin_side = int(image_width * config.BORDER_SIDE_RATIO)
    margin_top = int(image_width * config.BORDER_TOP_RATIO)
    margin_bottom = int(image_width * config.BORDER_BOTTOM_RATIO)

    total_width = image_width + (margin_side * 2)

    total_height = image_height + margin_top + margin_bottom

    # Координаты фото
    photo_x = margin_side
    photo_y = margin_top

    return Layout(
        total_size=(total_width, total_height),
        photo_pos=(photo_x, photo_y)
    )
