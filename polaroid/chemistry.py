from PIL import Image

def develop_image(image: Image.Image) -> Image.Image:
    """
    Эмулирует химический процесс проявки снимка Instax.

    Изменяет контраст, приподнимает точку черного и корректирует цветовой баланс
    через манипуляцию кривыми (Look-Up Tables) для каждого канала.
    Создает характерный "выцветший" вид с холодными тенями.

    Args:
        image (Image.Image): Исходное изображение.

    Returns:
        Image.Image: Изображение с примененной цветокоррекцией.
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Генерация LUT для Красного канала (R)
    # Тени делаем темнее (сдвиг в циан), точка черного приподнята до 20.
    r_curve = []
    for x in range(256):
        val = x
        if x < 128:
            val = x * 0.9 
        
        val = max(20, val) 
        r_curve.append(int(val))

    # Генерация LUT для Зеленого канала (G)
    # Линейная кривая, но с поднятой точкой черного до 25.
    g_curve = []
    for x in range(256):
        val = max(25, x) 
        g_curve.append(int(val))

    # Генерация LUT для Синего канала (B)
    # Усиление синего по всему диапазону и сильный подъем теней (до 30).
    b_curve = []
    for x in range(256):
        val = max(30, x * 1.05)
        b_curve.append(min(255, int(val)))

    # Применение кривых: метод point принимает объединенный список [R_lut + G_lut + B_lut]
    developed = image.point(r_curve + g_curve + b_curve)

    return developed