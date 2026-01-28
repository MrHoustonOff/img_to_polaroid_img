class PolaroidError(Exception):
    """
    Базовое исключение для библиотеки Polaroid.
    Все остальные ошибки библиотеки должны наследоваться от него.
    """
    pass

class ImageValidationError(PolaroidError):
    """
    Исключение, возникающее при нарушении треований к входному изображению
    """
    pass