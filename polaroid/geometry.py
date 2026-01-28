from dataclasses import dataclass
from typing import Tuple
from . import config

@dataclass
class Layout:
    """
    Контейнер для хранения рассчитанной геометрии снимка.

    Attributes:
        total_size (Tuple[int, int]): Размеры итогового изображения (ширина, высота).
        photo_pos (Tuple[int, int]): Координаты верхнего левого угла фотографии (x, y) 
                                     относительно итогового изображения.
    """
    total_size: Tuple[int, int]
    photo_pos: Tuple[int, int]

def calculate_layout(image_width: int, image_height: int) -> Layout:
    """
    Рассчитывает геометрию рамки Polaroid на основе размеров входного изображения.

    Все размеры (поля, отступы) вычисляются пропорционально ширине исходного фото
    с использованием коэффициентов из конфигурации.

    Args:
        image_width (int): Ширина исходного изображения в пикселях.
        image_height (int): Высота исходного изображения в пикселях.

    Returns:
        Layout: Объект с рассчитанными размерами рамки и позицией фото.
    """
    margin_side = int(image_width * config.BORDER_SIDE_RATIO)
    margin_top = int(image_width * config.BORDER_TOP_RATIO)
    margin_bottom = int(image_width * config.BORDER_BOTTOM_RATIO)

    total_width = image_width + (margin_side * 2)
    total_height = image_height + margin_top + margin_bottom

    photo_x = margin_side
    photo_y = margin_top

    return Layout(
        total_size=(total_width, total_height),
        photo_pos=(photo_x, photo_y)
    )