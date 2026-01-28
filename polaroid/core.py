import random
from PIL import Image, ImageFilter, ImageChops, ImageDraw
from . import validation
from . import geometry
from . import config
from . import filters
from . import chemistry
from . import optics
from . import chassis
from . import texture
from .debug import Debugger
from .data import PolaroidResult

def process_image(image: Image.Image, profile: str = "classic", debug: bool = False, generate_normal: bool = True, **kwargs) -> PolaroidResult:
    """
    Основной пайплайн обработки изображения: от проявки до сборки в картридж.

    Этапы:
    1. Валидация размеров.
    2. Химическая проявка (цветокоррекция).
    3. Оптические искажения (виньетка, аберрации).
    4. Наложение пленочного зерна.
    5. Генерация корпуса (рамки) с учетом брака (поворота).
    6. Сборка финального композита с тенями, каймой и масками.

    Args:
        image (Image.Image): Исходное изображение.
        profile (str, optional): Профиль обработки (пока только "classic"). Defaults to "classic".
        debug (bool, optional): Сохранять ли промежуточные этапы в папку _debug. Defaults to False.
        **kwargs: Дополнительные параметры (seed, rotation_angle и др.).

    Returns:
        PolaroidResult: Объект с финальным изображением и метаданными (маска, координаты).
    """
    debugger = Debugger(enabled=debug)
    debugger.save(image, "step0_original")

    validation.validate_image_dimensions(image.width, image.height)

    # === ОПТИМИЗАЦИЯ: SMART CAP ===
    # Ограничиваем максимальную сторону до 2500px для ускорения рендера,
    # сохраняя качество за счет алгоритма LANCZOS.
    max_dimension = 2500
    if max(image.width, image.height) > max_dimension:
        image.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

    limit = config.PHOTO_ROTATION_LIMIT
    rotation_angle = random.uniform(-limit, limit)
    
    if 'rotation_angle' in kwargs:
        rotation_angle = kwargs['rotation_angle']

    developed_photo = chemistry.develop_image(image)
    optical_photo = optics.apply_optics(developed_photo)
    seed = kwargs.get('seed', None)
    grainy_photo = filters.apply_grain(optical_photo, seed=seed)
    
    debugger.save(grainy_photo, "step3_grain")

    layout = geometry.calculate_layout(image.width, image.height)

    cartridge_layer = chassis.create_chassis(
        layout, 
        image.width, 
        (image.width, image.height),
        rotation_angle=rotation_angle
    )
    debugger.save(cartridge_layer, "step4_chassis")

    final_composite = Image.new("RGBA", layout.total_size, (0, 0, 0, 0))

    # === СБОРКА ФОТО-БЛОКА (С РАВНОМЕРНЫМ ОВЕРСКАНОМ) ===
    
    target_w, target_h = grainy_photo.size
    
    # Расчет увеличенных размеров для компенсации поворота (Oversize)
    # Добавляем буфер равномерно ко всем сторонам.
    oversize_factor = config.PHOTO_ROTATION_OVERSIZE
    max_dim = max(target_w, target_h)
    buffer_px = int(max_dim * (oversize_factor - 1.0))
    
    if buffer_px % 2 != 0:
        buffer_px += 1
        
    over_w = target_w + buffer_px
    over_h = target_h + buffer_px
    
    oversized_photo = grainy_photo.resize((over_w, over_h), Image.BICUBIC)
    
    # Генерация маски и подложки для увеличенного размера
    photo_mask_over = chassis.create_photo_mask((over_w, over_h), image.width)
    
    photo_block_over = Image.new("RGBA", (over_w, over_h), (0, 0, 0, 0))
    photo_content = oversized_photo.convert("RGBA")
    photo_content.putalpha(photo_mask_over)
    photo_block_over.paste(photo_content, (0, 0))
    
    def create_ring_mask(w, h, depth_ratio, radius_ratio):
        """Вспомогательная функция для создания кольцевых масок (тень, кайма)."""
        depth_px = int(image.width * depth_ratio)
        mask_outer = photo_mask_over.copy()
        mask_inner = Image.new("L", (w, h), 0)
        draw_inner = ImageDraw.Draw(mask_inner)
        
        inner_x0 = depth_px
        inner_y0 = depth_px
        inner_x1 = w - depth_px
        inner_y1 = h - depth_px
        
        r_photo = int(image.width * radius_ratio)
        r_inner = max(0, r_photo - (depth_px // 2))

        if inner_x1 > inner_x0 and inner_y1 > inner_y0:
            draw_inner.rounded_rectangle(
                (inner_x0, inner_y0, inner_x1, inner_y1),
                radius=r_inner,
                fill=255
            )
        return ImageChops.difference(mask_outer, mask_inner)

    # 4. Слой фиолетовой каймы (Purple Fringe)
    if config.FRINGE_STRENGTH > 0:
        fringe_ring = create_ring_mask(over_w, over_h, config.FRINGE_DEPTH, config.PHOTO_CORNER_RADIUS)
        
        fringe_blur_px = int(image.width * config.FRINGE_BLUR)
        if fringe_blur_px > 0:
            fringe_ring = fringe_ring.filter(ImageFilter.GaussianBlur(fringe_blur_px))
        
        fringe_alpha = ImageChops.multiply(fringe_ring, photo_mask_over)
        
        fringe_opacity = config.FRINGE_STRENGTH / 255.0
        fringe_alpha = fringe_alpha.point(lambda x: int(x * fringe_opacity))
        
        fringe_color = config.FRINGE_COLOR
        fringe_layer = Image.new("RGBA", (over_w, over_h), (fringe_color[0], fringe_color[1], fringe_color[2], 255))
        fringe_layer.putalpha(fringe_alpha)
        
        photo_block_over.alpha_composite(fringe_layer)

    # 5. Слой внутренней тени (Shadow)
    shadow_ring = create_ring_mask(over_w, over_h, config.SHADOW_DEPTH, config.PHOTO_CORNER_RADIUS)
    
    blur_px = int(image.width * config.SHADOW_BLUR)
    if blur_px > 0:
        shadow_ring = shadow_ring.filter(ImageFilter.GaussianBlur(blur_px))
    
    shadow_alpha = ImageChops.multiply(shadow_ring, photo_mask_over)
    opacity = config.SHADOW_STRENGTH / 255.0
    shadow_alpha = shadow_alpha.point(lambda x: int(x * opacity))
    
    shadow_fill = Image.new("RGBA", (over_w, over_h), (0, 0, 0, 255))
    shadow_fill.putalpha(shadow_alpha)
    
    photo_block_over.alpha_composite(shadow_fill)

    # 6. Вращение всего блока (Фото + Эффекты)
    if rotation_angle != 0:
        rotated_block_over = photo_block_over.rotate(rotation_angle, resample=Image.BICUBIC)
    else:
        rotated_block_over = photo_block_over
        
    # 7. Финальная обрезка (Crop) до исходного размера
    left = (over_w - target_w) // 2
    top = (over_h - target_h) // 2
    right = left + target_w
    bottom = top + target_h
    
    final_photo_block = rotated_block_over.crop((left, top, right, bottom))
    
    final_composite.paste(final_photo_block, layout.photo_pos, final_photo_block)
    debugger.save(final_composite, "step5_photo_block_rotated_cropped")

    final_composite.alpha_composite(cartridge_layer)

    # Генерация маски видимой области для экспорта
    final_mask_canvas = Image.new("L", layout.total_size, 0)
    rotated_photo_shape = final_photo_block.split()[3]
    final_mask_canvas.paste(rotated_photo_shape, layout.photo_pos)
    
    if config.MASK_OUTPUT_SCALE != 1.0:
        new_w = int(layout.total_size[0] * config.MASK_OUTPUT_SCALE)
        new_h = int(layout.total_size[1] * config.MASK_OUTPUT_SCALE)
        
        final_mask_canvas = final_mask_canvas.resize((new_w, new_h), Image.LANCZOS)

    normal_map_img = None
    if generate_normal:
        normal_map_img = texture.create_combined_normal(
            total_size=layout.total_size,
            photo_rect=(layout.photo_pos[0], layout.photo_pos[1], target_w, target_h),
            scale_factor=0.5
        )

    return PolaroidResult(
        image=final_composite,
        photo_mask=final_mask_canvas,
        photo_rect=(layout.photo_pos[0], layout.photo_pos[1], image.width, image.height),
        border_rect=(0, 0, layout.total_size[0], layout.total_size[1]),
        style_info={"profile": profile, "overrides": kwargs, "rotation": rotation_angle},
        normal_map=normal_map_img
    )