import numpy as np
from PIL        import Image
from datetime   import datetime
#============================================================
class PNGExporter:

    @staticmethod
    def save(pixel_array: np.ndarray, path: str):
        """
        Speichert ein RGB-NumPy-Array als PNG.
        """
        image = Image.fromarray(pixel_array, "RGB")
        image.save(path, format="PNG")

    @staticmethod
    def generate_default_filename(prefix="fractal", name=None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if name:
            return f"{prefix}_{name}_{timestamp}.png"
        return f"{prefix}_{timestamp}.png"