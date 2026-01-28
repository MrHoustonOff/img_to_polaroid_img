"""
Конфигурация библиотеки Polaroid.
Центр управления всеми параметрами генерации.
"""

# === 1. GEOMETRY ===
BORDER_SIDE_RATIO = 0.06
BORDER_TOP_RATIO = 0.06
BORDER_BOTTOM_RATIO = 0.18

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
CHEMISTRY_BLACK_POINT = 30

# Shadow Tint.
# < 1.0 - уменьшаем канал, > 1.0 - усиливаем.
# Убираем красный и зеленый, оставляем синий -> получаем холодные тени.
CHEMISTRY_SHADOW_RED_SCALE = 0.85
CHEMISTRY_SHADOW_GREEN_SCALE = 0.95
CHEMISTRY_SHADOW_BLUE_SCALE = 1.10

# === 5. OPTICS ===
VIGNETTE_STRENGTH = 0.5
VIGNETTE_RADIUS = 0.4

# Aberration
# 0.003 = 0.3% сдвига
ABERRATION_OFFSET = 0.003

# Soft Focus
OPTICS_BLUR_RADIUS = 0.6

# === 6. GRAIN ===
GRAIN_INTENSITY = 0.12

# Grain Scale
GRAIN_SCALE = 2.0

# Clipping
GRAIN_CUTOFF = 180
