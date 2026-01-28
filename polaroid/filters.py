import random
from PIL import Image, ImageChops, ImageEnhance
from . import config

def apply_grain(image: Image.Image, seed: int = None, intensity: float = None) -> Image.Image:
    """
    Наладывает "облачное" пленочное зерно (Grain 2.0).
    Использует параметры из config.py
    """
    if intensity is None:
        intensity = config.GRAIN_INTENSITY
        
    if intensity <= 0:
        return image

    if seed is not None:
        random.seed(seed)

    w, h = image.size
    
    small_w = int(w / config.GRAIN_SCALE)
    small_h = int(h / config.GRAIN_SCALE)
    
    noise_data = [random.randint(0, config.GRAIN_CUTOFF) for _ in range(small_w * small_h)]
    
    noise_layer = Image.new("L", (small_w, small_h))
    noise_layer.putdata(noise_data)
    
    noise_layer = noise_layer.resize((w, h), Image.BICUBIC)
    
    noise_layer = noise_layer.convert("RGB")
    
    return Image.blend(image, noise_layer, alpha=intensity)