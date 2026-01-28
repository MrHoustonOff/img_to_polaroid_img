from PIL import Image, ImageEnhance, ImageChops, ImageFilter, ImageOps
from . import config
import math

def apply_optics(image: Image.Image) -> Image.Image:
    """
    Применяет оптические искажения, имитирующие несовершенство пластиковой линзы.

    Включает в себя три этапа обработки:
    1. Хроматическая аберрация (Lateral Chromatic Aberration): Сдвиг красного канала
       относительно центра для создания цветных ореолов по краям.
    2. Мягкий фокус (Soft Focus): Размытие изображения по краям с сохранением
       резкости в центре (имитация малой глубины резкости и кривизны поля).
    3. Виньетирование (Vignette): Естественное затемнение углов изображения.

    Args:
        image (Image.Image): Исходное изображение.

    Returns:
        Image.Image: Изображение с примененными оптическими эффектами.
    """
    # 1. Хроматическая аберрация
    r, g, b = image.split()
    
    w, h = image.size
    offset = config.ABERRATION_OFFSET
    new_w = int(w * (1 + offset))
    new_h = int(h * (1 + offset))
    
    # Увеличиваем красный канал (имитация разной длины волны)
    r_channel = r.resize((new_w, new_h), Image.BICUBIC)
    
    # Обрезаем по центру до исходного размера
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    r_channel = r_channel.crop((left, top, left + w, top + h))
    
    image = Image.merge("RGB", (r_channel, g, b))

    # 2. Мягкий фокус (Blur)
    if config.OPTICS_BLUR_STRENGTH > 0:
        blurred_image = image.filter(ImageFilter.GaussianBlur(radius=config.OPTICS_BLUR_STRENGTH))
        
        # Генерация маски размытия (резкий центр, размытые края)
        # Работаем в уменьшенном разрешении для скорости
        mask_size = (int(w/4), int(h/4))
        blur_mask = Image.new("L", mask_size, 0)
        
        cx, cy = mask_size[0] / 2, mask_size[1] / 2
        max_dist = math.sqrt(cx**2 + cy**2)
        
        pixel_data = []
        sharp_radius = config.OPTICS_BLUR_SHARP_AREA
        
        for y in range(mask_size[1]):
            for x in range(mask_size[0]):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                norm_dist = dist / max_dist
                
                if norm_dist < sharp_radius:
                    val = 0
                else:
                    factor = (norm_dist - sharp_radius) / (1 - sharp_radius)
                    val = int(255 * factor)
                
                pixel_data.append(val)
        
        blur_mask.putdata(pixel_data)
        blur_mask = blur_mask.resize((w, h), Image.BICUBIC)
        
        image = Image.composite(blurred_image, image, blur_mask)
        
    # 3. Виньетирование
    mask_size = (int(w/4), int(h/4)) 
    vignette_mask = Image.new("L", mask_size, 255)
    
    cx, cy = mask_size[0] / 2, mask_size[1] / 2
    max_dist = math.sqrt(cx**2 + cy**2)
    
    pixel_data = []
    for y in range(mask_size[1]):
        for x in range(mask_size[0]):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
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