from PIL import Image

def develop_image(image: Image.Image) -> Image.Image:
    """
    Эмуляция химического процесса проявки Instax.
    Меняет контраст, точку черного и цветовой баланс.
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # 1. S-Curve + Lifted Blacks (Выцветание)
    
    # R (Red): Тени делаем темнее (меньше красного = больше циана)
    r_curve = []
    for x in range(256):
        # В тенях (x < 60) убавляем красный сильнее -> тени зеленеют/синеют
        # Точка черного приподнята до 20 (нет идеального черного)
        val = x
        if x < 128:
            val = x * 0.9  # Затемняем красный в тенях
        
        # Lifted black: минимум 20
        val = max(20, val) 
        r_curve.append(int(val))

    # G (Green): Чуть поднимаем середин, чтобы кожа светилась
    g_curve = []
    for x in range(256):
        # Линейно, но черный тоже не 0
        val = max(25, x) 
        g_curve.append(int(val))

    # B (Blue): Поднимаем тени сильнее всего (синий отлив в темном)
    b_curve = []
    for x in range(256):
        val = max(30, x * 1.05) # Чуть больше синего везде + высокий пол
        # Обрезаем сверху, чтобы не вылезало за 255
        b_curve.append(min(255, int(val)))

    # Применяем кривые к каналам
    # .point принимает одну длинную колбасу [R_lut + G_lut + B_lut]
    developed = image.point(r_curve + g_curve + b_curve)

    return developed