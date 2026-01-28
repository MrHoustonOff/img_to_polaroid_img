from PIL import Image, ImageEnhance, ImageChops, ImageFilter, ImageOps
from . import config
import math

def apply_optics(image: Image.Image) -> Image.Image:
    """
    Применяет оптические искажения: размытие, аберрацию, виньетку.
    """
    # 1. Soft Focus
    if config.OPTICS_BLUR_RADIUS > 0:
        image = image.filter(ImageFilter.GaussianBlur(radius=config.OPTICS_BLUR_RADIUS))

    # 2. Chromatic Aberration
    r, g, b = image.split()
    
    w, h = image.size
    offset = config.ABERRATION_OFFSET
    new_w = int(w * (1 + offset))
    new_h = int(h * (1 + offset))
    
    r_channel = r.resize((new_w, new_h), Image.BICUBIC)
    
    # Вырезаем центр (crop)
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    r_channel = r_channel.crop((left, top, left + w, top + h))
    
    image = Image.merge("RGB", (r_channel, g, b))

    # 3. Vignette
    # L = черно-белая маска (White center, Black corners)
    
    mask_size = (int(w/4), int(h/4)) 
    vignette_mask = Image.new("L", mask_size, 255)
    
    margin_x = int(mask_size[0] * config.VIGNETTE_RADIUS)
    margin_y = int(mask_size[1] * config.VIGNETTE_RADIUS)
    
    cx, cy = mask_size[0] / 2, mask_size[1] / 2
    max_dist = math.sqrt(cx**2 + cy**2)
    
    pixel_data = []
    for y in range(mask_size[1]):
        for x in range(mask_size[0]):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            # Нормализуем (0.0 в центре, 1.0 в углу)
            norm_dist = dist / max_dist
            
            if norm_dist < config.VIGNETTE_RADIUS:
                val = 255
            else:
                factor = (norm_dist - config.VIGNETTE_RADIUS) / (1 - config.VIGNETTE_RADIUS)
                darkness = int(255 * (1 - (factor * config.VIGNETTE_STRENGTH)))
                val = max(0, min(255, darkness))
            
            pixel_data.append(val)
            
    vignette_mask.putdata(pixel_data)
    vignette_mask = vignette_mask.resize((w, h), Image.BICUBIC)
    
    black_layer = Image.new("RGB", (w, h), (0, 0, 0))
    image = Image.composite(image, black_layer, vignette_mask)

    return image