"""
Конфигурация библиотеки Polaroid.
Центр управления всеми параметрами генерации.
"""

# === 1. GEOMETRY ===
BORDER_SIDE_RATIO = 0.06
BORDER_TOP_RATIO = 0.08
BORDER_BOTTOM_RATIO = 0.22

# === 2. VALIDATION ===
MIN_ASPECT_RATIO = 0.3
MAX_ASPECT_RATIO = 3.0
MIN_IMAGE_SIZE = 50

# === 3. CHASSIS COLORS ===
PAPER_COLOR = (246, 242, 235)
GRIP_COLOR = (250, 250, 250)
GRIP_RATIO = 0.8

# === 4. CHEMISTRY ===
# Насколько "поднимаем" черный цвет (0-255).
CHEMISTRY_BLACK_POINT = 15

# Shadow Tint.
# < 1.0 - уменьшаем канал, > 1.0 - усиливаем.
# Убираем красный и зеленый, оставляем синий -> получаем холодные тени.
CHEMISTRY_SHADOW_RED_SCALE = 0.85
CHEMISTRY_SHADOW_GREEN_SCALE = 0.95
CHEMISTRY_SHADOW_BLUE_SCALE = 1.10

# === 5. OPTICS ===
VIGNETTE_STRENGTH = 0.4
VIGNETTE_RADIUS = 0.55

# 0.0 - нет размытия. 2.0 - заметное "мыло" по краям.
OPTICS_BLUR_STRENGTH = 3
# 0.6 означает, что 60% изображения от центра будут оставаться резкими,
OPTICS_BLUR_SHARP_AREA = 0.6

# Aberration
# 0.003 = 0.3% сдвига
ABERRATION_OFFSET = 0.0045


# === 6. GRAIN ===
GRAIN_INTENSITY = 0.11

# Grain Scale
GRAIN_SCALE = 2.5

# Clipping
GRAIN_CUTOFF = 100

# === 7. CHASSIS & ASSEMBLY ===

# --- SHAPE ---
FRAME_CORNER_RADIUS_TOP = 0.02
FRAME_CORNER_RADIUS_BOTTOM = 0.04

PHOTO_CORNER_RADIUS = 0.01

# --- MATERIALS ---
CHASSIS_PAPER_NOISE = 0.04
CHASSIS_GRIP_NOISE = 0.02

# Цвет стыка (Seam) между бумагой и хваталкой
SEAM_COLOR = (220, 215, 210)
SEAM_HEIGHT = 0.003

# --- DEPTH / INNER SHADOW ---
# Сила тени (0-255). 220 = очень темная тень на стыке.
SHADOW_OPACITY = 220
# Меньше = резче срез (как ножницами), Больше = мягче
SHADOW_BLUR_SIZE = 0.015
# Сдвиг тени (имитация света сверху-слева)
SHADOW_OFFSET_X = 0.002
SHADOW_OFFSET_Y = 0.004

# --- LAMINATION ---
# 0.15 - легкий отблеск, не перекрывающий фото.
LAMINATION_STRENGTH = 0.15
