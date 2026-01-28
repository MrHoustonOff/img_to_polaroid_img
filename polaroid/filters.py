import random
from PIL import Image, ImageChops, ImageEnhance

def apply_grain(image: Image.Image, intensity: float, seed: int = None) -> Image.Image:
    """
    Наладывает эффект пленочного зерна на изображение.
    
    Args:
        image: Исходное изображение.
        intensity: Сила эффекта (0.0 - 1.0).
        seed: Число для генератора случайных чисел.
        
    Returns:
        Новое изображение с наложенным зерном.
    """
    if intensity <= 0:
        return image.copy()

    if seed is not None:
        random.seed(seed)

    width, height = image.size
    
    # 2. Генерируем карту шума
    noise_data = [random.randint(0, 255) for _ in range(width * height)]
    
    # Создаем из этих данных картинку (L = черно-белая)
    noise_layer = Image.new("L", (width, height))
    noise_layer.putdata(noise_data)

    # 3. Смешивание (Blending)
    noise_layer = noise_layer.convert("RGB")

    noise_layer.save("mask.jpg")

    return Image.blend(image, noise_layer, alpha=intensity)
