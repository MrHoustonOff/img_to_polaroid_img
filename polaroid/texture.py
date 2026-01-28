from PIL import Image, ImageChops, ImageFilter, ImageEnhance
import random

def generate_noise_layer(width: int, height: int, roughness: int) -> Image.Image:
    """
    Генерирует карту высот (Height Map) из шума.
    roughness: сила шума (чем больше, тем грубее поверхность).
    """
    # 1. Генерируем случайный шум
    # Используем L (Grayscale). 128 - это "ноль" высоты.
    noise = Image.effect_noise((width, height), sigma=roughness)
    
    # 2. Размываем, чтобы получить "холмы", а не просто битые пиксели.
    # Это имитирует волокна бумаги.
    noise = noise.filter(ImageFilter.GaussianBlur(radius=1.0))
    
    return noise

def height_to_normal(height_map: Image.Image, intensity: float = 1.0) -> Image.Image:
    """
    Превращает черно-белую карту высот в фиолетовую карту нормалей (Normal Map).
    
    Математика (упрощенная для скорости):
    dX = Pixel(x+1) - Pixel(x)
    dY = Pixel(y+1) - Pixel(y)
    Normal = (dX, dY, Z) -> RGB mapping
    """
    # Сдвигаем картинку на 1 пиксель влево и вверх
    x_shifted = ImageChops.offset(height_map, -1, 0)
    y_shifted = ImageChops.offset(height_map, 0, -1)
    
    # Вычисляем разницу (производную)
    # 128 + (Original - Shifted) * intensity
    
    # R channel (X slope)
    diff_x = ImageChops.difference(height_map, x_shifted)
    # Инвертируем половину, чтобы получить отрицательные значения через наложение...
    # Простой хак PIL для Normal Map:
    
    pixels = height_map.load()
    w, h = height_map.size
    
    normal_img = Image.new("RGB", (w, h))
    normal_pixels = normal_img.load()
    
    # ВАЖНО: Питон медленный в циклах. Но для разрешения / 2 (1000px) это займет ~0.2 сек.
    # Если нужно быстрее - придется подключать NumPy, но мы договорились без лишних либ.
    
    # Оптимизация: работаем не с каждым пикселем, а используем матричные фильтры PIL.
    # Kernel Filter для поиска краев (Sobel lite)
    
    kernel_x = (
        -1, 0, 1,
        -2, 0, 2,
        -1, 0, 1
    )
    kernel_y = (
        -1, -2, -1,
         0,  0,  0,
         1,  2,  1
    )
    
    dx = height_map.filter(ImageFilter.Kernel((3, 3), kernel_x, scale=1))
    dy = height_map.filter(ImageFilter.Kernel((3, 3), kernel_y, scale=1))
    
    # Собираем каналы
    # R = dx, G = dy, B = 255 (Z-up)
    # Нам нужно маппить (-255..255) в (0..255), где 0 = 128.
    
    # Усиление нормали
    dx = ImageEnhance.Contrast(dx).enhance(intensity)
    dy = ImageEnhance.Contrast(dy).enhance(intensity)
    
    # Инвертируем и смешиваем для получения правильного бампа
    # Но самый быстрый способ собрать Normal Map в PIL без циклов:
    
    blue = Image.new("L", (w, h), 255) # Z всегда смотрит вверх
    
    # Смещение серого (128)
    gray = Image.new("L", (w, h), 128)
    
    # R channel: 128 + dx
    r = ImageChops.add(gray, dx, scale=0.5) # scale приглушает
    # G channel: 128 - dy (Y в текстурах часто инвертирован, пробуем так)
    g = ImageChops.subtract(gray, dy, scale=0.5)

    return Image.merge("RGB", (r, g, blue))

def create_combined_normal(
    total_size: tuple, 
    photo_rect: tuple, 
    scale_factor: float = 0.5
) -> Image.Image:
    """
    Собирает итоговую карту нормалей.
    
    total_size: (W, H) полного снимка.
    photo_rect: (x, y, w, h) зоны фото.
    scale_factor: во сколько раз уменьшать карту (0.5 = в 2 раза меньше).
    """
    w, h = total_size
    
    # Целевой размер карты
    target_w = int(w * scale_factor)
    target_h = int(h * scale_factor)
    
    # Координаты фото в уменьшенном масштабе
    px = int(photo_rect[0] * scale_factor)
    py = int(photo_rect[1] * scale_factor)
    pw = int(photo_rect[2] * scale_factor)
    ph = int(photo_rect[3] * scale_factor)
    
    # 1. Генерируем Шум КАРТОНА (Грубый)
    # sigma=15 - выраженные волокна
    base_height = generate_noise_layer(target_w, target_h, roughness=20)
    
    # 2. Генерируем Шум ФОТО (Мелкий, химический)
    # sigma=5 - мелкое зерно
    photo_height = generate_noise_layer(pw, ph, roughness=5)
    
    # Вклеиваем фото-шум в базу
    base_height.paste(photo_height, (px, py))
    
    # 3. Конвертируем в Normal Map (Фиолетовый)
    # intensity=2.0 - сила рельефа
    normal_map = height_to_normal(base_height, intensity=2.0)
    
    return normal_map