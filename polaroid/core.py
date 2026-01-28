import random
from PIL import Image, ImageFilter, ImageOps, ImageChops, ImageDraw
from . import validation
from . import geometry
from . import config
from . import filters
from . import chemistry
from . import optics
from . import chassis
from .debug import Debugger
from .data import PolaroidResult

def process_image(image: Image.Image, profile: str = "classic", debug: bool = False, **kwargs) -> PolaroidResult:
    debugger = Debugger(enabled=debug)
    debugger.save(image, "step0_original")

    validation.validate_image_dimensions(image.width, image.height)

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
    
    # 1. Вычисляем размеры с запасом (Oversize)
    # ВАЖНО: Добавляем одинаковое кол-во пикселей к ширине и высоте,
    # чтобы при обрезке тень срезалась равномерно со всех сторон.
    oversize_factor = config.PHOTO_ROTATION_OVERSIZE
    
    # Считаем запас на основе максимальной стороны (чтобы точно хватило на поворот)
    max_dim = max(target_w, target_h)
    buffer_px = int(max_dim * (oversize_factor - 1.0))
    
    # Делаем число четным для чистого центрирования
    if buffer_px % 2 != 0:
        buffer_px += 1
        
    over_w = target_w + buffer_px
    over_h = target_h + buffer_px
    
    # Растягиваем фото на новый размер. 
    # Небольшое искажение пропорций (если фото не квадратное) на 3% незаметно,
    # зато гарантирует равномерность рамки.
    oversized_photo = grainy_photo.resize((over_w, over_h), Image.BICUBIC)
    
    # 2. Маска для увеличенного размера
    photo_mask_over = chassis.create_photo_mask((over_w, over_h), image.width)
    
    # 3. Слой фото
    photo_block_over = Image.new("RGBA", (over_w, over_h), (0, 0, 0, 0))
    photo_content = oversized_photo.convert("RGBA")
    photo_content.putalpha(photo_mask_over)
    photo_block_over.paste(photo_content, (0, 0))
    
    # Вспомогательная функция для генерации кольца
    def create_ring_mask(w, h, depth_ratio, radius_ratio):
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

    # 5. Слой тени (Shadow)
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

    # 6. Вращение
    if rotation_angle != 0:
        rotated_block_over = photo_block_over.rotate(rotation_angle, resample=Image.BICUBIC)
    else:
        rotated_block_over = photo_block_over
        
    # 7. Обрезка (Crop) - Возвращаем к исходному размеру
    # Так как мы добавили одинаковый buffer_px ко всем сторонам,
    # мы обрежем одинаковое количество пикселей сверху и сбоку.
    # Тень останется равномерной.
    left = (over_w - target_w) // 2
    top = (over_h - target_h) // 2
    right = left + target_w
    bottom = top + target_h
    
    final_photo_block = rotated_block_over.crop((left, top, right, bottom))
    
    final_composite.paste(final_photo_block, layout.photo_pos, final_photo_block)
    
    debugger.save(final_composite, "step5_photo_block_rotated_cropped")

    final_composite.alpha_composite(cartridge_layer)

    # === ГЕНЕРАЦИЯ ПРАВИЛЬНОЙ МАСКИ ВЫРЕЗА (MASK EXPORT) ===
    # Нам нужна маска, которая соответствует тому, что видит пользователь:
    # Повернутое фото + черные поля вокруг.
    
    # 1. Создаем черный холст размером с финальное изображение
    final_mask_canvas = Image.new("L", layout.total_size, 0)
    
    # 2. Берем альфа-канал из финального (повернутого и обрезанного) блока фото
    # Этот канал содержит точную форму видимой фотографии
    rotated_photo_shape = final_photo_block.split()[3]
    
    # 3. Вставляем эту форму на черный холст в позицию фото
    final_mask_canvas.paste(rotated_photo_shape, layout.photo_pos)
    
    # Теперь у нас идеальная маска: Белое = Фото, Черное = Всё остальное.

    return PolaroidResult(
        image=final_composite,
        photo_mask=final_mask_canvas, # Возвращаем честную маску
        photo_rect=(layout.photo_pos[0], layout.photo_pos[1], image.width, image.height),
        border_rect=(0, 0, layout.total_size[0], layout.total_size[1]),
        style_info={"profile": profile, "overrides": kwargs, "rotation": rotation_angle}
    )