from PIL import Image
import numpy as np
from datetime import datetime
import os


class PNGExporter:

    @staticmethod
    def save(pixel_array: np.ndarray, path: str):
        """
        Speichert ein RGB-NumPy-Array als PNG.
        """
        image = Image.fromarray(pixel_array, "RGB")
        image.save(path, format="PNG")

    @staticmethod
    def generate_default_filename(prefix="fractal"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.png"