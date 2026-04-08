import  numpy as np
from    mapping import PALETTES
#============================================================
class Colorizer():
    def __init__(self):
        self.palette_name   = "default"
        self.palette        = []
        self.set_palette("default")

#------------------------------------------------------------
# PALETTE-MANAGEMENT (definieren, interpolieren, sampeln)

    # Palette als Attribut setzen
    def set_palette(self, name:str):
        if name not in PALETTES:
            raise ValueError(f"Unknown palette:  {name}")
        
        self.palette_name = name
        
        key_colors = PALETTES[name]
        self.palette = self._interpolate_palette(key_colors, 256)

    # Palette sampeln (t in [0,1])
    def _sample_palette(self, t: float) -> tuple[int, int, int]:
        t = max(0.0, min(1.0, t))   # Sicherstellen, dass t in [0,1] liegt
        
        # lineare Interpolation
        palette_size = len(self.palette)
        idx = t * (palette_size - 1)

        # Indizes für die beiden nächsten Farben in der Palette
        i0 = int(idx)
        i1 = min(i0 + 1, palette_size - 1)

        frac = idx - i0     # Bruchteil für die Interpolation

        # Interpolierte Farbe berechnen
        c0 = self.palette[i0]
        c1 = self.palette[i1]

        # lineare Interpolation der RGB-Komponenten
        r = int(c0[0] + frac * (c1[0] - c0[0]))
        g = int(c0[1] + frac * (c1[1] - c0[1]))
        b = int(c0[2] + frac * (c1[2] - c0[2]))

        return (r, g, b)

    # sauber interpolieren
    def _interpolate_palette(self, key_colors, size):
        if len(key_colors) < 2:
            raise ValueError("At least two key colors are required for interpolation.")
        
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
# VORVERARBEITUNG
    def _build_histogram_cdf(self,
                            iterations: np.ndarray,
                            escaped: np.ndarray,
                            max_iterations: int) -> np.ndarray:
        
        histogram = np.zeros(max_iterations + 1, dtype=np.float64)

        height, width = iterations.shape

        # Histogramm aufbauen
        for y in range(height):
            for x in range(width):
                if not escaped[y, x]:
                    continue

                nu = iterations[y, x]
                i = int(np.floor(nu))

                if i < 0:
                    i = 0
                elif i > max_iterations:
                    i = max_iterations

                histogram[i] += 1.0

        if np.sum(histogram) == 0:
            return None

        # leicht glätten
        smoothed = histogram.copy()
        for i in range(1, max_iterations):
            smoothed[i] = (
                0.25 * histogram[i - 1] +
                0.50 * histogram[i] +
                0.25 * histogram[i + 1]
            )

        cumulative = np.cumsum(smoothed)

        total = cumulative[-1]
        if total <= 0.0:
            return None

        cumulative /= total
        return cumulative

    def _prepare_orbit_trap_range(self, trap_dist: np.ndarray, escaped: np.ndarray) -> tuple[float, float, float, float] | None:
        valid = trap_dist[(escaped == 1) & np.isfinite(trap_dist)]

        if len(valid) == 0:
            return None
        
        d_min = np.min(valid)
        d_max = np.max(valid)

        if d_max == d_min:
            d_max = d_min + 1e-12

        log_min = np.log(d_min + 1e-12)
        log_max = np.log(d_max + 1e-12)

        if log_max == log_min:
            log_max = log_min + 1e-12

        return d_min, d_max, log_min, log_max

#------------------------------------------------------------
# PIXELWEISE Signale

    def _smooth_t(self, nu: float, max_iterations: int) -> float:
        if max_iterations <= 0:
            return 0.0
        t = nu / max_iterations
        return max(0.0, min(1.0, t))

    def _orbit_trap_t(self, d: float, log_min: float, log_max: float) -> float:
        ld = np.log(d + 1e-12)
        t = (ld - log_min) / (log_max - log_min)
        return max(0.0, min(1.0, t))

    def _histogram_t(self, nu: float, cumulative: np.ndarray, max_iterations: int) -> float:
        i0 = int(np.floor(nu))

        if i0 < 0:
            i0 = 0
        elif i0 > max_iterations:
            i0 = max_iterations

        i1 = min(i0 + 1, max_iterations)
        f = nu - i0

        t0 = cumulative[i0]
        t1 = cumulative[i1]

        t = (1.0 - f) * t0 + f * t1
        return max(0.0, min(1.0, t))

    def _paint_from_t_map(self, t_map: np.ndarray, escaped: np.ndarray) -> np.ndarray:
        height, width = t_map.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

        for y in range(height):
            for x in range(width):
                if not escaped[y, x]:
                    image[y, x] = (0, 0, 0)
                else:
                    t = t_map[y, x]
                    image[y, x] = self._sample_palette(t)

        return image
    
#------------------------------------------------------------
# FÄRBUNGSMETHODEN als Kompositionsmethoden

    # Förbung: Basic (spezielle, kristalline Struktur, allerdings etwas pixelig)
    def apply_basic(self, iterations: np.ndarray,
                    escaped: np.ndarray) -> np.ndarray:

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

    # Färbung: Smooth (gut für mitteltiefe Zooms und stark abhängig von Iterationszahl)
    def apply_smooth(self, iterations: np.ndarray,
                    escaped: np.ndarray,
                    max_iterations: int) -> np.ndarray:

        height, width = iterations.shape
        t_map = np.zeros((height, width), dtype=np.float64)

        for y in range(height):
            for x in range(width):
                if not escaped[y, x]:
                    continue

                nu = iterations[y, x]
                if not np.isfinite(nu):
                        continue

                t_map[y, x] = self._smooth_t(nu, max_iterations)

        image = self._paint_from_t_map(t_map, escaped)
        return image

    # Färbung: Histogramm
    def apply_histogram(self,
                        iterations: np.ndarray,
                        escaped: np.ndarray,
                        max_iterations: int) -> np.ndarray:

        height, width = iterations.shape
        t_map = np.zeros((height, width), dtype=np.float64)

        cumulative = self._build_histogram_cdf(iterations, escaped, max_iterations)
        if cumulative is None:
            return np.zeros((height, width, 3), dtype=np.uint8)

        for y in range(height):
            for x in range(width):
                if not escaped[y, x]:
                    continue

                nu = iterations[y, x]
                if not np.isfinite(nu):
                    continue

                t_map[y, x] = self._histogram_t(nu, cumulative, max_iterations)

        image = self._paint_from_t_map(t_map, escaped)
        return image

    # Färbung: Orbit-Trap (Sehr spezielle, experimentelle Färbung)
    def apply_orbit_trap(self,
                        trap_dist: np.ndarray,
                        escaped: np.ndarray) -> np.ndarray:

        height, width = trap_dist.shape
        t_map = np.zeros((height, width), dtype=np.float64)

        prep = self._prepare_orbit_trap_range(trap_dist, escaped)
        if prep is None:
            return np.zeros((height, width, 3), dtype=np.uint8)

        _, _, log_min, log_max = prep

        for y in range(height):
            for x in range(width):
                if not escaped[y, x]:
                    continue

                d = trap_dist[y, x]
                if not np.isfinite(d):
                    continue

                t_map[y, x] = self._orbit_trap_t(d, log_min, log_max)

        return self._paint_from_t_map(t_map, escaped)   
     
    # Färbung: Basic und histogramm kombiniert+
    def apply_hybrid(self,
                    iterations: np.ndarray,
                    escaped: np.ndarray,
                    max_iterations: int,
                    hist_strength: float = 0.45) -> np.ndarray:

        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

        cumulative = self._build_histogram_cdf(iterations, escaped, max_iterations)
        if cumulative is None:
            return image

        palette_size = len(self.palette)

        for y in range(height):
            for x in range(width):

                if not escaped[y, x]:
                    image[y, x] = (0, 0, 0)
                    continue

                nu = iterations[y, x]
                if not np.isfinite(nu):
                    image[y, x] = (0, 0, 0)
                    continue

                # --- BASIC-KERN ---
                base_index = int(nu) % palette_size

                # --- HISTOGRAMM-SKALIERUNG ---
                hist_t = self._histogram_t(nu, cumulative, max_iterations)
                hist_index = int(hist_t * (palette_size - 1))

                # --- KOMPOSITION ---
                mixed_index = int(
                    (1.0 - hist_strength) * base_index +
                    hist_strength * hist_index
                ) % palette_size

                image[y, x] = self.palette[mixed_index]

        return image

#------------------------------------------------------------
# POSTPROCESSING für Farbgebungsergebnisse

    def apply_gamma(self, image: np.ndarray, gamma: float = 2.2) -> np.ndarray:
        if gamma <= 0:
            return image

        img = image.astype(np.float64) / 255.0
        img = np.power(img, 1.0 / gamma)
        img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
        return img
    
    def apply_contrast(self, image: np.ndarray, contrast: float = 1.2) -> np.ndarray:
        img = image.astype(np.float64) / 255.0
        img = (img - 0.5) * contrast + 0.5
        img = np.clip(img, 0.0, 1.0)
        return (img * 255).astype(np.uint8)