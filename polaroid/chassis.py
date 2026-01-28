from PIL import Image, ImageDraw, ImageFilter
from . import config
from . import filters
from .geometry import Layout

def create_chassis(layout: Layout, width: int) -> Image.Image:
    """
    Создает "болванку" картриджа:
    1. Форма с асимметричными углами.
    2. Текстура бумаги (с шумом).
    3. Текстура хваталки (с ДРУГИМ шумом).
    4. Линия стыка.
    
    Возвращает изображение RGBA (на прозрачном фоне).
    """
    total_w, total_h = layout.total_size
    
    # 1. Готовим слои
    paper_layer = Image.new("RGB", (total_w, total_h), config.PAPER_COLOR)
    paper_layer = filters.apply_grain(paper_layer, intensity=config.CHASSIS_PAPER_NOISE)

    # 2. Готовим слой хваталки (Grip)
    grip_height = int(layout.total_size[1] * (config.BORDER_BOTTOM_RATIO * config.GRIP_RATIO))
    grip_y = total_h - grip_height
    
    grip_layer = Image.new("RGB", (total_w, grip_height), config.GRIP_COLOR)
    grip_layer = filters.apply_grain(grip_layer, intensity=config.CHASSIS_GRIP_NOISE)

    # 3. Склеиваем слои (на прямоугольный холст)
    base = paper_layer
    base.paste(grip_layer, (0, grip_y))

    # 4. Рисуем стык (Seam) - Тень над хваталкой
    draw = ImageDraw.Draw(base, "RGBA")
    seam_h = int(width * config.SEAM_HEIGHT)
    shape = [(0, grip_y - seam_h), (total_w, grip_y)]
    draw.rectangle(shape, fill=config.SEAM_COLOR)

    # 5. Вырубка формы (Shape Masking)
    mask = Image.new("L", (total_w, total_h), 0)
    d_mask = ImageDraw.Draw(mask)
    
    r_top = int(width * config.FRAME_CORNER_RADIUS_TOP)
    r_bottom = int(width * config.FRAME_CORNER_RADIUS_BOTTOM)
    
    d_mask.rounded_rectangle((0, 0, total_w, total_h - r_bottom), radius=r_top, fill=255)
    
    try:
        d_mask.rounded_rectangle(
            (0, 0, total_w, total_h), 
            corners=(r_top, r_top, r_bottom, r_bottom), 
            fill=255
        )
    except TypeError:
        d_mask.rounded_rectangle((0, 0, total_w, total_h), radius=r_top, fill=255)

    result = base.convert("RGBA")
    result.putalpha(mask)

    return result

def create_photo_mask(size: tuple, width_ref: int) -> Image.Image:
    """
    Генерирует маску для фото (скругленный квадрат).
    """
    w, h = size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    radius = int(width_ref * config.PHOTO_CORNER_RADIUS)
    draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    return mask