"""
Конфигурация библиотеки Polaroid.
Центр управления всеми параметрами генерации.
"""

# === 1. GEOMETRY ===
BORDER_SIDE_RATIO = 0.06
BORDER_TOP_RATIO = 0.08
BORDER_BOTTOM_RATIO = 0.3

# === 2. VALIDATION ===
MIN_ASPECT_RATIO = 0.3
MAX_ASPECT_RATIO = 3.0
MIN_IMAGE_SIZE = 50

# === 3. CHASSIS COLORS ===
PAPER_COLOR = (235, 235, 235)
GRIP_COLOR = (240, 240, 240)
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
FRAME_CORNER_RADIUS_TOP = 0.01
FRAME_CORNER_RADIUS_BOTTOM = 0.02

PHOTO_CORNER_RADIUS = 0.005

# --- MATERIALS ---
CHASSIS_PAPER_NOISE = 0.1
CHASSIS_GRIP_NOISE = 0.07

# Цвет стыка (Seam) между бумагой и хваталкой
SEAM_HEIGHT = 0.006
SEAM_OPACITY = 40
SEAM_BLUR_RADIUS = 0.01

# --- DEPTH / INNER SHADOW ---
SHADOW_STRENGTH = 230
SHADOW_DEPTH = 0.025
SHADOW_BLUR = 0.05

# --- LAMINATION ---
# 0.15 - легкий отблеск, не перекрывающий фото.
PHOTO_ROTATION_LIMIT = 0.03
PHOTO_ROTATION_OVERSIZE = 1.06

# === ПАРАМЕТРЫ ФИОЛЕТОВОЙ КАЙМЫ (PURPLE FRINGE / EDGE LEAK) ===
FRINGE_COLOR = (200, 50, 255)
FRINGE_STRENGTH = 130
FRINGE_DEPTH = 0.01
FRINGE_BLUR = 0.03

GRIP_SHADE_STRENGTH = 0.13