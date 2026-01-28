from dataclasses import dataclass
from typing import Tuple, Dict, Any
from PIL import Image

@dataclass
class PolaroidResult:
    """
    Контейнер результата обработки.
    См. ТЗ п.12
    """
    image: Image.Image                    # Итоговое изображение
    photo_mask: Image.Image               # Маска области фото
    photo_rect: Tuple[int, int, int, int] # Координаты фото внутри рамки (x, y, w, h)
    border_rect: Tuple[int, int, int, int]# Габариты всего Polaroid (w, h)
    style_info: Dict[str, Any]            # Применённый профиль и параметры
