from fractal import IterationResult
from mapping import PALETTES
import numpy as np
import math
#============================================================
class ColorMap():
    def __init__(self):
        self.palette_name   = "default"
        self.palette        = []            # vollständige Palette
        self.set_palette("default")

#------------------------------------------------------------
# FARBPROFILE UND PALETTE

    # Palette als Attribut setzen
    def set_palette(self, name:str):
        if name not in PALETTES:
            raise ValueError(f"Unknown palette:  {name}")
        
        self.palette_name = name
        
        key_colors = PALETTES[name]
        self.palette = self._interpolate_palette(key_colors, 256)

    # Kontinuierliches Palette-Sampling
    def _sample_palette(self, t: float) -> tuple:
        t = max(0.0, min(1.0, t))

        pos = t * (len(self.palette) - 1)
        idx = int(pos)
        frac = pos - idx

        c1 = self.palette[idx]
        c2 = self.palette[min(idx+1, len(self.palette) - 1)]

        r = int(c1[0] + frac * (c2[0] - c1[0]))
        g = int(c1[1] + frac * (c2[1] - c1[1]))
        b = int(c1[2] + frac * (c2[2] - c1[2]))

        return (r, g, b)

#------------------------------------------------------------
# INTERPOLATION für Palette

    # sauber interpolieren
    def _interpolate_palette(self, key_colors, size):
        palette = []
        segments = len(key_colors) - 1

        for i in range(size):
            t = i / (size - 1)
            pos = t * segments

            idx = int(pos)
            frac = pos - idx
            c1 = key_colors[idx]
            c2 = key_colors[min(idx + 1, segments)]

            r = int(c1[0] + frac * (c2[0] - c1[0]))
            g = int(c1[1] + frac * (c2[1] - c1[1]))
            b = int(c1[2] + frac * (c2[2] - c1[2]))

            palette.append((r, g, b))

        return palette

#------------------------------------------------------------
# FÄRBUNGSMETHODEN für Iterationsergebnisse

    # Klassiche Färbung
    def apply_basic(self, iterations: np.ndarray,
                    escaped: np.ndarray,
                    max_iterations: int) -> np.ndarray:

        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

        palette_size = len(self.palette)

        for y in range(height):
            for x in range(width):

                if not escaped[y, x]:
                    # Punkt liegt in der Menge
                    image[y, x] = (0, 0, 0)
                else:
                    iteration = iterations[y, x]

                    # klassische Modulo-Färbung
                    index = int(iteration) % palette_size
                    image[y, x] = self.palette[index]

        return image

    # Histogramm-basierte Färbung
    def apply_histogram(self, iterations: np.ndarray,
                        escaped: np.ndarray,
                        max_iterations: int) -> np.ndarray:

        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

        # Histogramm der Iterationszahlen
        histogram = np.zeros(max_iterations + 1, dtype=np.int64)
        for y in range(height):
            for x in range(width):
                if escaped[y, x]:
                    histogram[int(iterations[y, x])] += 1

        # Kumulative Verteilung
        total = histogram.sum()
        if total == 0:
            total = 1  # verhindert Division durch Null
        cumulative = np.cumsum(histogram) / total  # Werte zwischen 0 und 1

        palette_size = len(self.palette)

        # Farbzuweisung
        for y in range(height):
            for x in range(width):
                if not escaped[y, x]:
                    image[y, x] = (0, 0, 0)
                else:
                    iter_value = int(iterations[y, x])
                    t = cumulative[iter_value]  # 0.1
                    index = int(t * (palette_size - 1))
                    image[y, x] = self.palette[index]

        return image

    # Smooth-Färbung
    def apply_smooth(self, iterations: np.ndarray,
                    escaped: np.ndarray,
                    max_iterations: int) -> np.ndarray:
        """
        Smooth Coloring mit linearer Interpolation in der Palette
        """
        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)
        palette_size = len(self.palette)

        for y in range(height):
            for x in range(width):
                if not escaped[y, x]:
                    image[y, x] = (0, 0, 0)
                else:
                    # float Iteration → interpolate Palette
                    t = iterations[y, x] / max_iterations  # 0..1
                    idx = t * (palette_size - 1)
                    i0 = int(np.floor(idx))
                    i1 = min(i0 + 1, palette_size - 1)
                    frac = idx - i0

                    c0 = self.palette[i0]
                    c1 = self.palette[i1]

                    r = int(c0[0] + frac * (c1[0] - c0[0]))
                    g = int(c0[1] + frac * (c1[1] - c0[1]))
                    b = int(c0[2] + frac * (c1[2] - c0[2]))

                    image[y, x] = (r, g, b)

        return image
