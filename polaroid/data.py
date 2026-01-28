from dataclasses import dataclass
from typing import Tuple, Dict, Any
from PIL import Image

@dataclass
class PolaroidResult:
    """
    Контейнер для хранения результатов генерации снимка Polaroid.

    Attributes:
        image (Image.Image): Итоговое композитное изображение (RGBA).
        photo_mask (Image.Image): Маска видимой области фотографии (L-mode). 
                                  Белый пиксель = фото, Черный = рамка.
        photo_rect (Tuple[int, int, int, int]): Координаты области фотографии внутри рамки 
                                                в формате (x, y, width, height).
        border_rect (Tuple[int, int, int, int]): Габариты всего изображения 
                                                 в формате (x, y, width, height).
        style_info (Dict[str, Any]): Словарь метаданных, содержащий имя профиля, 
                                     seed, угол поворота и переопределенные параметры.
    """
    image: Image.Image
    photo_mask: Image.Image
    photo_rect: Tuple[int, int, int, int]
    border_rect: Tuple[int, int, int, int]
    style_info: Dict[str, Any]
    normal_map: Image.Image = None