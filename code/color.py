from mapping import PALETTES
import numpy as np
#============================================================
class ColorMap():
    def __init__(self):
        self.palette_name   = "default"
        self.palette        = []
        self.set_palette("default")

#------------------------------------------------------------
# FPALETTE MANAGEMENT

    # Palette als Attribut setzen
    def set_palette(self, name:str):
        if name not in PALETTES:
            raise ValueError(f"Unknown palette:  {name}")
        
        self.palette_name = name
        
        key_colors = PALETTES[name]
        self.palette = self._interpolate_palette(key_colors, 256)

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

    # Förbung: simpel und grundlegend
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

    # Färbung: Histogramm
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

    def apply_smooth(self, iterations: np.ndarray,
                    escaped: np.ndarray,
                    max_iterations: int) -> np.ndarray:

        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)
        palette_size = len(self.palette)

        for y in range(height):
            for x in range(width):

                if not escaped[y, x]:
                    image[y, x] = (0, 0, 0)

                else:
                    t = iterations[y, x] / max_iterations

                    t = max(0.0, min(1.0,t))    # t dampen (wichtig)

                    idx = t * (palette_size - 1)
                    i0 = int(idx)
                    i1 = min(i0 + 1, palette_size - 1)

                    frac = idx - i0

                    c0 = self.palette[i0]
                    c1 = self.palette[i1]

                    r = int(c0[0] + frac * (c1[0] - c0[0]))
                    g = int(c0[1] + frac * (c1[1] - c0[1]))
                    b = int(c0[2] + frac * (c1[2] - c0[2]))

                    image[y, x] = (r, g, b)

        return image
    

    def apply_orbit_trap(self, iterations: np.ndarray,
                        escaped: np.ndarray,
                        max_iterations: int) -> np.ndarray:

        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)
        palette_size = len(self.palette)

        # Zentrum der Trap (z.B. Kreis in der Mitte)
        trap_center = np.array([0.0, 0.0])  # komplexer Mittelpunkt (Re, Im)
        trap_radius = 0.05                   # kleiner Radius

        for y in range(height):
            for x in range(width):

                if not escaped[y, x]:
                    image[y, x] = (0, 0, 0)
                else:
                    # Iterierter Punkt als komplexe Zahl
                    z = self.iterated_points[y, x]  # du musst dafür das Array der letzten z-Werte speichern

                    # Abstand zur Trap
                    dist = np.abs(np.array([z.real, z.imag]) - trap_center)

                    # Skalierung auf [0,1] (0 = auf der Trap, 1 = weit weg)
                    t = min(dist / trap_radius, 1.0)

                    # Palette index
                    index = int(t * (palette_size - 1))
                    image[y, x] = self.palette[index]

        return image