from PIL import Image, ImageDraw, ImageFilter, ImageChops
from . import config
from . import filters
from .geometry import Layout

def create_chassis(layout: Layout, width_ref: int, photo_size: tuple, rotation_angle: float = 0.0) -> Image.Image:
    """
    Создает графический слой корпуса картриджа (рамки) с учетом текстуры бумаги, 
    объема нижней части и физических дефектов вырубки.

    Args:
        layout (Layout): Объект с рассчитанной геометрией снимка.
        width_ref (int): Референсная ширина исходного изображения для расчета пропорций.
        photo_size (tuple): Размеры зоны фотографии (ширина, высота).
        rotation_angle (float, optional): Угол поворота вырезанного окна (имитация производственного брака). 
                                          По умолчанию 0.0.

    Returns:
        Image.Image: RGBA изображение рамки с прозрачным окном под фото.
    """
    total_w, total_h = layout.total_size
    photo_w, photo_h = photo_size

    paper_layer = Image.new("RGB", (total_w, total_h), config.PAPER_COLOR)
    paper_layer = filters.apply_grain(paper_layer, intensity=config.CHASSIS_PAPER_NOISE)

    margin_bottom = int(width_ref * config.BORDER_BOTTOM_RATIO)
    grip_height = int(margin_bottom * config.GRIP_RATIO)
    grip_y = total_h - grip_height

    # Генерация градиента для объема "хваталки" (Developer Pod)
    c_top = config.GRIP_COLOR
    dark_factor = 1.0 - config.GRIP_SHADE_STRENGTH
    c_bottom = tuple(int(c * dark_factor) for c in c_top)

    grip_layer = Image.new("RGB", (total_w, grip_height))
    pixels = grip_layer.load()

    for y in range(grip_height):
        ratio = y / max(1, grip_height - 1)
  
        r = int(c_top[0] * (1 - ratio) + c_bottom[0] * ratio)
        g = int(c_top[1] * (1 - ratio) + c_bottom[1] * ratio)
        b = int(c_top[2] * (1 - ratio) + c_bottom[2] * ratio)

        for x in range(total_w):
            pixels[x, y] = (r, g, b)
      
    grip_layer = filters.apply_grain(grip_layer, intensity=config.CHASSIS_GRIP_NOISE)

    base = paper_layer.copy()
    base.paste(grip_layer, (0, grip_y))
    base = base.convert("RGBA")

    seam_layer = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    d_seam = ImageDraw.Draw(seam_layer)
    seam_h = int(width_ref * config.SEAM_HEIGHT)

    d_seam.rectangle(
        [(0, grip_y - seam_h), (total_w, grip_y)], 
        fill=(0, 0, 0, config.SEAM_OPACITY)
    )

    blur_px = int(width_ref * config.SEAM_BLUR_RADIUS)
    if blur_px > 0:
        seam_layer = seam_layer.filter(ImageFilter.GaussianBlur(blur_px))

    base.alpha_composite(seam_layer)

    # Генерация альфа-маски формы картриджа и выреза
    mask_base = Image.new("L", (total_w, total_h), 0)
    d_base = ImageDraw.Draw(mask_base)

    r_top = int(width_ref * config.FRAME_CORNER_RADIUS_TOP)
    r_bottom = int(width_ref * config.FRAME_CORNER_RADIUS_BOTTOM)

    w, h = total_w, total_h
    points = [
        (0, r_top), (r_top, 0),
        (w - r_top, 0), (w, r_top),
        (w, h - r_bottom), (w - r_bottom, h),
        (r_bottom, h), (0, h - r_bottom)
    ]
    d_base.polygon(points, fill=255)
    
    mask_hole_layer = Image.new("L", (total_w, total_h), 0)
    d_hole = ImageDraw.Draw(mask_hole_layer)
    
    px, py = layout.photo_pos
    r_photo = int(width_ref * config.PHOTO_CORNER_RADIUS)
    
    d_hole.rounded_rectangle(
        (px, py, px + photo_w, py + photo_h), 
        radius=r_photo, 
        fill=255
    )
    
    cx = px + photo_w / 2
    cy = py + photo_h / 2
    
    if rotation_angle != 0:
        mask_hole_layer = mask_hole_layer.rotate(
            rotation_angle, 
            resample=Image.BICUBIC, 
            center=(cx, cy)
        )
    
    final_mask = ImageChops.subtract(mask_base, mask_hole_layer)

    base.putalpha(final_mask)
    return base

def create_photo_mask(size: tuple, width_ref: int) -> Image.Image:
    """
    Генерирует маску для скругления углов самой фотографии.

    Args:
        size (tuple): Размеры фото (ширина, высота).
        width_ref (int): Референсная ширина для расчета радиуса скругления.

    Returns:
        Image.Image: L-изображение (маска), где белое — видимая область, черное — прозрачная.
    """
    w, h = size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    radius = int(width_ref * config.PHOTO_CORNER_RADIUS)
    draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    return mask