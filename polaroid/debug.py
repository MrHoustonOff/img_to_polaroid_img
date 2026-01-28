import os
from PIL import Image

class Debugger:
    """
    Помощник для сохранения промежуточных этапов обработки.
    Работает только если при инициализации передан флаг enabled=True.
    """
    def __init__(self, enabled: bool = False, output_dir: str = "_debug"):
        self.enabled = enabled
        self.output_dir = output_dir
        self.step_counter = 1

        if self.enabled:
            self._ensure_dir()

    def _ensure_dir(self):
        """Создает папку для дебага, если её нет."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save(self, image: Image.Image, name: str):
        """
        Сохраняет изображение с префиксом (номером шага).
        Пример: 01_raw_input.png
        """
        if not self.enabled:
            return

        # Формируем имя: 01_name.png
        filename = f"{self.step_counter:02d}_{name}.png"
        path = os.path.join(self.output_dir, filename)
        
        image.save(path)
        print(f"[DEBUG] Saved: {path}")
        
        self.step_counter += 1