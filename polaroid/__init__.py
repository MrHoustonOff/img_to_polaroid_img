"""
Polaroid Generator Library
~~~~~~~~~~~~~~~~~~~~~~~~~~

Библиотека для генерации изображений в стиле моментальной фотографии
с физически корректной эмуляцией оптики, химии и бумаги.
"""

from .core import process_image
from .data import PolaroidResult
from .exceptions import PolaroidError, ImageValidationError

__version__ = "1.0.0"
__all__ = ["process_image", "PolaroidResult", "PolaroidError", "ImageValidationError"]