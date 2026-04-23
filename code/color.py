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

        cumulative = np.cumsum(smoothed)    # Kumulative Summe

        total = cumulative[-1]
        if total <= 0.0:
            return None

        cumulative /= total
        return cumulative

    def _prepare_orbit_trap_range(self, 
                                  trap_dist: np.ndarray, 
                                  escaped: np.ndarray
                                  ) -> tuple[float, float, float, float] | None:

        valid = trap_dist[(escaped == 1) & np.isfinite(trap_dist)]      # Gültige Werte filtern

        if len(valid) == 0:
            return None
        
        # Minimum / Maximum
        d_min = np.min(valid)
        d_max = np.max(valid)

        if d_max == d_min:
            d_max = d_min + 1e-12

        # Logarithmus-Skalierung für bessere Verteilung
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
        t = (ld - log_min) / (log_max - log_min)    # Normierung
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

        t = (1.0 - f) * t0 + f * t1     # Kontinuierliche Transformationsfunktion
        return max(0.0, min(1.0, t))

    def _paint_from_t_map(self, t_map: np.ndarray, escaped: np.ndarray) -> np.ndarray:
        height, width = t_map.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)    # Bild initialisieren

        # Pixelweise Mapping
        for y in range(height):
            for x in range(width):
                if not escaped[y, x]:
                    image[y, x] = (0, 0, 0)
                else:
                    t = t_map[y, x]
                    image[y, x] = self._sample_palette(t)   # Kontinuierlich interpolieren

        return image
    
#------------------------------------------------------------
# FÄRBUNGSMETHODEN als Kompositionsmethoden

    # Förbung: Basic (spezielle, kristalline Struktur, allerdings etwas pixelig)
    def apply_basic(self, 
                    iterations: np.ndarray,     # Iterationswerte (Im Rendering-Kernel berechnet)
                    escaped: np.ndarray         # Punkt divergiert oder nicht (binäre Unterscheidung)
                    ) -> np.ndarray:            # Rückgabe: RGB-Bild des Fraktal-Ausschnitts

        # Bild initialisieren (leeres schwarzes RGB-Bild)
        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

        # Palette vorbereiten
        palette_size = len(self.palette)

        # 2D-Loop (Pixelweise Verarbeitung)
        for y in range(height):
            for x in range(width):

                if not escaped[y, x]:
                    image[y, x] = (0, 0, 0)           # Punkte innerhalb von Menge schwarz
                else:
                    iteration = iterations[y, x]      # Iterationswert extrahieren

                    # Färbung
                    index = int(iteration) % palette_size   # Banding durch Diskretisierung; zyklisches Wiederholen durch % (Beispiel: int(257.4)%256 = int(513.8)%256)
                    image[y, x] = self.palette[index]       # Farbzuweisung

        return image

    # Färbung: Smooth (gut für mitteltiefe Zooms, stark abhängig von Iterationszahl, schlechter Kontrast in tiefen Zooms)
    def apply_smooth(self, 
                    iterations: np.ndarray,     # Iterationswerte (Im Rendering-Kernel berechnet)
                    escaped: np.ndarray,        # Punkt divergiert oder nicht (binäre Unterscheidung)
                    max_iterations: int         # Maximale Iterationszahl aus Rendering-Prozess
                    ) -> np.ndarray:            # Rückgabe: RGB-Bild des Fraktal-Ausschnitts

        # Initialisierung
        height, width = iterations.shape
        t_map = np.zeros((height, width), dtype=np.float64)

        # 2D-Loop (Pixelweise Verarbeitung)
        for y in range(height):
            for x in range(width):

                # Innenpunkte überspringen
                if not escaped[y, x]:
                    continue

                nu = iterations[y, x]   # Iterationswert laden

                # Validitätsprüfung
                if not np.isfinite(nu):
                        continue

                # Normierung (zentraler Schritt)
                t_map[y, x] = self._smooth_t(nu, max_iterations)

        # Farbzuweisung (externalisiert)
        image = self._paint_from_t_map(t_map, escaped)
        return image

    # Färbung: Histogramm (Sehr gute Farbverteilung, aber verwaschene Details und z.T. Artefakte)
    def apply_histogram(self,
                        iterations: np.ndarray,     # Iterationswerte (Im Rendering-Kernel berechnet)
                        escaped: np.ndarray,        # Punkt divergiert oder nicht (binäre Unterscheidung)
                        max_iterations: int         # Maximale Iterationszahl aus Rendering-Prozess
                        ) -> np.ndarray:            # Rückgabe: RGB-Bild des Fraktal-Ausschnitts

        # Initialisierung
        height, width = iterations.shape
        t_map = np.zeros((height, width), dtype=np.float64)

        # Globale Analyse (CDF berechnen)
        cumulative = self._build_histogram_cdf(iterations, escaped, max_iterations)
        if cumulative is None:
            return np.zeros((height, width, 3), dtype=np.uint8)

        # 2D-Loop (Pixelweise Verarbeitung)
        for y in range(height):
            for x in range(width):
                if not escaped[y, x]:
                    continue

                nu = iterations[y, x]
                if not np.isfinite(nu):
                    continue

                t_map[y, x] = self._histogram_t(nu, cumulative, max_iterations)

        # Farbzuweisung
        image = self._paint_from_t_map(t_map, escaped)
        return image

    # Färbung: Orbit-Trap (Sehr spezielle, experimentelle Färbung)
    def apply_orbit_trap(self,
                        trap_dist: np.ndarray,          # Für jeden Punkt: Abstand zu Trap-Objekt
                        escaped: np.ndarray             # Punkt divergiert oder nicht (binäre Unterscheidung)
                        ) -> np.ndarray:                # Rückgabe: RGB-Bild des Fraktal-Ausschnitts

        # Initialisierung
        height, width = trap_dist.shape
        t_map = np.zeros((height, width), dtype=np.float64)

        # Wertebereich vorbereiten
        prep = self._prepare_orbit_trap_range(trap_dist, escaped)
        if prep is None:
            return np.zeros((height, width, 3), dtype=np.uint8)

        _, _, log_min, log_max = prep

        # 2D-Loop (Pixelweise Verarbeitung)
        for y in range(height):
            for x in range(width):

                # Überspringen
                if not escaped[y, x]:
                    continue

                # Verarbeitung
                d = trap_dist[y, x]
                if not np.isfinite(d):
                    continue

                t_map[y, x] = self._orbit_trap_t(d, log_min, log_max)

        # Farbzuweisung
        image = self._paint_from_t_map(t_map, escaped)   
        return image

    # Färbung: Basic und histogramm kombiniert
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

                base_index = int(nu) % palette_size

                hist_t = self._histogram_t(nu, cumulative, max_iterations)
                hist_index = int(hist_t * (palette_size - 1))

                mixed_index = int(
                    (1.0 - hist_strength) * base_index +
                    hist_strength * hist_index
                ) % palette_size

                image[y, x] = self.palette[mixed_index]

        return image

    # Färbung: cyclic_banding (Supersampling empfohlen)
    def apply_cyclic_banding(self,
                    iterations: np.ndarray,
                    escaped: np.ndarray,
                    max_iterations: int,
                    hist_strength: float = 0.2
                    ) -> np.ndarray:

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

                frac = nu - np.floor(nu)   # lokale Phase in [0,1)

                hist_t = self._histogram_t(nu, cumulative, max_iterations)

                frequency = 1.0   # testen: 0.5, 1.0, 2.0
                band = np.sin(2 * np.pi * frac * frequency) * 0.5

                t = hist_t + hist_strength * band
                t = 0.5 * t + 0.25 * (
                    hist_t
                )

                t = max(0.0, min(1.0, t))

                image[y, x] = self._sample_palette(t)

        return image

    # Färbung: Schachbrett Muster
    def apply_chess(self,
                    iterations: np.ndarray,
                    escaped: np.ndarray,
                    zr_final: np.ndarray,
                    zi_final: np.ndarray,
                    max_iterations: int) -> np.ndarray:
        
        sectors     = 14       # gerade Zahl!
        stripe_width = 10

        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

        palette = np.array(self.palette, dtype=np.uint8)
        palette_size = len(palette)

        valid = escaped.astype(bool) & np.isfinite(iterations)

        nu  = iterations[valid]
        zr  = zr_final[valid]
        zi  = zi_final[valid]

        # Achse 1: Iterationsband
        nu_scaled = nu * (1.0 / stripe_width)
        band_int  = np.floor(nu_scaled).astype(int)

        # Achse 2: Winkelsektor (sectors muss gerade sein!)
        angle      = np.arctan2(zi, zr)                              # -π … +π
        angle_norm = (angle + np.pi) / (2 * np.pi)                  # 0..1
        sector_int = np.floor(angle_norm * sectors).astype(int) % sectors

        # XOR für saubere Übergänge an beiden Achsen
        chess = (band_int ^ sector_int) % 2

        # Farbindex
        frac  = nu_scaled % 1.0
        index = (np.floor(frac * palette_size).astype(int)
                + chess * (palette_size // 2)) % palette_size

        image[valid] = palette[index]
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