import  numpy       as     np
from    mapping     import PALETTES
from    utils       import printProgressBar
#============================================================
class Colorizer():
    def __init__(self):
        self.palette_name       = "default"
        self.palette            = []
        self.set_palette("default")

#------------------------------------------------------------

    def apply(
            self,
            result,
            coloring_mode: str
            ) -> np.ndarray:
        
        iterations = result.iterations
        escaped = result.escaped
        trap = result.trap
        zr = result.z_real
        zi = result.z_imag
        max_iter = result.max_iter

        # Progressbar als callback festlegen
        progress_callback = lambda i, t: printProgressBar(i, t, prefix="Coloring", suffix="Complete", length=50)

        # Unterscheidung nach aktivem Coloring-Mode
        if coloring_mode == "basic":
            image = self.apply_basic(
                iterations, 
                escaped, 
                progress_callback)   # max_iter nicht nötig

        elif coloring_mode == "histogram":
            image = self.apply_histogram(
                iterations, 
                escaped, 
                max_iter,
                progress_callback)

        elif coloring_mode == "smooth":
            image = self.apply_smooth(
                iterations, 
                escaped, 
                max_iter,
                progress_callback)

        elif coloring_mode == "orbit trap":
            image = self.apply_orbit_trap(
                trap, 
                escaped,
                progress_callback)

        elif coloring_mode == "hybrid":
            image = self.apply_hybrid(
                iterations, 
                escaped, 
                max_iter,
                progress_callback)

        elif coloring_mode == "cyclic banding":
            image = self.apply_cyclic_banding(
                iterations, 
                escaped, 
                max_iter,
                progress_callback)

        elif coloring_mode == "chess pattern":
            image = self.apply_chess(
                iterations, 
                escaped, 
                zr, zi, 
                max_iter,
                progress_callback)

        else:
            raise ValueError(f"Unknown coloring mode: {coloring_mode}")
        
        return image

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

    # Färbung: Overlay (nur zur Visualisierung der Struktur)
    def apply_overlay(self,
                    iterations: np.ndarray,
                    escaped: np.ndarray,
                    max_iterations: int
                    ) -> np.ndarray:
        
        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

        mask = escaped.astype(bool)
        
        if np.any(mask):
            t = iterations[mask] / max_iterations
            t = np.clip(t, 0.0, 1.0)
            val = (t * 255).astype(np.uint8)
            image[mask, 0] = val
            image[mask, 1] = val
            image[mask, 2] = val

        return image

    # Förbung: Basic (spezielle, kristalline Struktur, allerdings etwas pixelig)
    def apply_basic(self, 
                    iterations: np.ndarray,
                    escaped: np.ndarray,
                    progress_callback=None,
                    chunk_size: int = 32
                    ) -> np.ndarray:

        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

        palette = np.array(self.palette, dtype=np.uint8)
        palette_size = len(palette)

        for y0 in range(0, height, chunk_size):
            y1 = min(y0 + chunk_size, height)

            # Chunk extrahieren
            iter_chunk = iterations[y0:y1]
            esc_chunk  = escaped[y0:y1]

            # Maske: nur gültige (escaped) Punkte
            mask = esc_chunk.astype(bool)

            if np.any(mask):
                # Iterationswerte holen
                nu = iter_chunk[mask]

                # identische Logik wie vorher
                index = (nu.astype(int) % palette_size)

                # Farbzuweisung (vektorisiert)
                image[y0:y1][mask] = palette[index]

            # Innenpunkte bleiben automatisch schwarz (Initialisierung)

            # Progress
            if progress_callback:
                progress_callback(y1, height)

        return image

    # Färbung: Smooth (gut für mitteltiefe Zooms, stark abhängig von Iterationszahl, schlechter Kontrast in tiefen Zooms)
    def apply_smooth(self, 
                    iterations: np.ndarray,
                    escaped: np.ndarray,
                    max_iterations: int,
                    progress_callback=None,
                    chunk_size: int = 32
                    ) -> np.ndarray:

        height, width = iterations.shape
        t_map = np.zeros((height, width), dtype=np.float64)

        if max_iterations <= 0:
            return np.zeros((height, width, 3), dtype=np.uint8)

        for y0 in range(0, height, chunk_size):
            y1 = min(y0 + chunk_size, height)

            iter_chunk = iterations[y0:y1]
            esc_chunk  = escaped[y0:y1]

            # gültige Punkte: escaped + finite
            mask = esc_chunk.astype(bool) & np.isfinite(iter_chunk)

            if np.any(mask):
                nu = iter_chunk[mask]

                # exakt gleiche Logik wie _smooth_t, nur vektorisiert
                t = nu / max_iterations
                t = np.clip(t, 0.0, 1.0)

                t_map[y0:y1][mask] = t

            if progress_callback:
                progress_callback(y1, height)
        
        # unverändert: zentrale Farbabbildung
        image = self._paint_from_t_map(t_map, escaped)
        return image

    # Färbung: Histogramm (Sehr gute Farbverteilung, aber verwaschene Details und z.T. Artefakte)
    def apply_histogram(self,
                        iterations: np.ndarray,
                        escaped: np.ndarray,
                        max_iterations: int,
                        progress_callback=None,
                        chunk_size: int = 32
                        ) -> np.ndarray:

        height, width = iterations.shape
        t_map = np.zeros((height, width), dtype=np.float64)

        # Globale Analyse (unverändert)
        cumulative = self._build_histogram_cdf(iterations, escaped, max_iterations)
        if cumulative is None:
            return np.zeros((height, width, 3), dtype=np.uint8)

        for y0 in range(0, height, chunk_size):
            y1 = min(y0 + chunk_size, height)

            iter_chunk = iterations[y0:y1]
            esc_chunk  = escaped[y0:y1]

            # gültige Punkte
            mask = esc_chunk.astype(bool) & np.isfinite(iter_chunk)

            if np.any(mask):
                nu = iter_chunk[mask]

                # --- Vektorisierte Entsprechung von _histogram_t ---

                i0 = np.floor(nu).astype(int)
                i0 = np.clip(i0, 0, max_iterations)

                i1 = np.minimum(i0 + 1, max_iterations)
                f  = nu - i0

                t0 = cumulative[i0]
                t1 = cumulative[i1]

                t = (1.0 - f) * t0 + f * t1
                t = np.clip(t, 0.0, 1.0)

                t_map[y0:y1][mask] = t

            if progress_callback:
                progress_callback(y1, height)

        image = self._paint_from_t_map(t_map, escaped)
        return image

    # Färbung: Orbit-Trap (Sehr spezielle, experimentelle Färbung)
    def apply_orbit_trap(self,
                        trap_dist: np.ndarray,
                        escaped: np.ndarray,
                        progress_callback=None,
                        chunk_size: int = 32
                        ) -> np.ndarray:

        height, width = trap_dist.shape
        t_map = np.zeros((height, width), dtype=np.float64)

        # Globaler Schritt (unverändert)
        prep = self._prepare_orbit_trap_range(trap_dist, escaped)
        if prep is None:
            return np.zeros((height, width, 3), dtype=np.uint8)

        _, _, log_min, log_max = prep
        denom = (log_max - log_min)

        for y0 in range(0, height, chunk_size):
            y1 = min(y0 + chunk_size, height)

            dist_chunk = trap_dist[y0:y1]
            esc_chunk  = escaped[y0:y1]

            # gültige Punkte
            mask = esc_chunk.astype(bool) & np.isfinite(dist_chunk)

            if np.any(mask):
                d = dist_chunk[mask]

                # --- Vektorisierte Entsprechung von _orbit_trap_t ---
                ld = np.log(d + 1e-12)
                t = (ld - log_min) / denom
                t = np.clip(t, 0.0, 1.0)

                t_map[y0:y1][mask] = t

            if progress_callback:
                progress_callback(y1, height)

        image = self._paint_from_t_map(t_map, escaped)
        return image

    # Färbung: Basic und histogramm kombiniert
    def apply_hybrid(self,
                    iterations: np.ndarray,
                    escaped: np.ndarray,
                    max_iterations: int,
                    progress_callback=None,
                    hist_strength: float = 0.45,
                    chunk_size: int = 32
                    ) -> np.ndarray:

        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

        cumulative = self._build_histogram_cdf(iterations, escaped, max_iterations)
        if cumulative is None:
            return image

        palette = np.array(self.palette, dtype=np.uint8)
        palette_size = len(palette)

        for y0 in range(0, height, chunk_size):
            y1 = min(y0 + chunk_size, height)

            iter_chunk = iterations[y0:y1]
            esc_chunk  = escaped[y0:y1]

            mask = esc_chunk.astype(bool) & np.isfinite(iter_chunk)

            if np.any(mask):
                nu = iter_chunk[mask]

                # --- Base (diskret) ---
                base_index = (nu.astype(int) % palette_size)

                # --- Histogramm (kontinuierlich → Index) ---
                i0 = np.floor(nu).astype(int)
                i0 = np.clip(i0, 0, max_iterations)

                i1 = np.minimum(i0 + 1, max_iterations)
                f  = nu - i0

                t0 = cumulative[i0]
                t1 = cumulative[i1]

                hist_t = (1.0 - f) * t0 + f * t1
                hist_t = np.clip(hist_t, 0.0, 1.0)

                hist_index = (hist_t * (palette_size - 1)).astype(int)

                # --- Mischung im Indexraum ---
                mixed_index = (
                    (1.0 - hist_strength) * base_index +
                    hist_strength * hist_index
                ).astype(int) % palette_size

                image[y0:y1][mask] = palette[mixed_index]

            if progress_callback:
                progress_callback(y1, height)

        return image

    # Färbung: cyclic_banding (Supersampling empfohlen)
    def apply_cyclic_banding(self,
                    iterations: np.ndarray,
                    escaped: np.ndarray,
                    max_iterations: int,
                    progress_callback=None,
                    hist_strength: float = 0.4,
                    chunk_size: int = 32
                    ) -> np.ndarray:

        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

        cumulative = self._build_histogram_cdf(iterations, escaped, max_iterations)
        if cumulative is None:
            return image

        palette = np.array(self.palette, dtype=np.uint8)
        palette_size = len(palette)

        for y0 in range(0, height, chunk_size):
            y1 = min(y0 + chunk_size, height)

            iter_chunk = iterations[y0:y1]
            esc_chunk  = escaped[y0:y1]

            mask = esc_chunk.astype(bool) & np.isfinite(iter_chunk)

            if np.any(mask):
                nu = iter_chunk[mask]

                # Phase
                frac = nu - np.floor(nu)

                # Histogramm (vektorisiert wie vorherige Methoden)
                i0 = np.floor(nu).astype(int)
                i0 = np.clip(i0, 0, max_iterations)

                i1 = np.minimum(i0 + 1, max_iterations)
                f  = nu - i0

                t0 = cumulative[i0]
                t1 = cumulative[i1]

                hist_t = (1.0 - f) * t0 + f * t1

                # Banding
                frequency = 1.0
                band = np.sin(2.0 * np.pi * frac * frequency) * 0.5

                # Mischung (identisch zur Originallogik)
                t = hist_t + hist_strength * band
                t = 0.5 * t + 0.25 * hist_t

                # Clamp
                t = np.clip(t, 0.0, 1.0)

                # DIREKTER LUT-ZUGRIFF (kein _sample_palette)
                idx = (t * (palette_size - 1)).astype(np.int32)
                image[y0:y1][mask] = palette[idx]

            if progress_callback:
                progress_callback(y1, height)

        return image

    # Färbung: Schachbrett Muster
    def apply_chess(self,
                    iterations: np.ndarray,
                    escaped: np.ndarray,
                    zr_final: np.ndarray,
                    zi_final: np.ndarray,
                    max_iterations: int,
                    progress_callback=None,
                    chunk_size: int = 32
                    ) -> np.ndarray:

        sectors     = 14
        stripe_width = 10

        height, width = iterations.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

        palette = np.array(self.palette, dtype=np.uint8)
        palette_size = len(palette)

        for y0 in range(0, height, chunk_size):
            y1 = min(y0 + chunk_size, height)

            iter_chunk = iterations[y0:y1]
            esc_chunk  = escaped[y0:y1]
            zr_chunk   = zr_final[y0:y1]
            zi_chunk   = zi_final[y0:y1]

            valid = esc_chunk.astype(bool) & np.isfinite(iter_chunk)

            if np.any(valid):

                nu = iter_chunk[valid]
                zr = zr_chunk[valid]
                zi = zi_chunk[valid]

                # Achse 1: Iterationsband
                nu_scaled = nu * (1.0 / stripe_width)
                band_int  = np.floor(nu_scaled).astype(int)

                # Achse 2: Winkel
                angle      = np.arctan2(zi, zr)
                angle_norm = (angle + np.pi) / (2 * np.pi)
                sector_int = np.floor(angle_norm * sectors).astype(int) % sectors

                # XOR Struktur
                chess = (band_int ^ sector_int) % 2

                # Fraktionaler Anteil
                frac = nu_scaled % 1.0

                # Palette-Index
                index = (
                    np.floor(frac * palette_size).astype(int)
                    + chess * (palette_size // 2)
                ) % palette_size

                image[y0:y1][valid] = palette[index]

            if progress_callback:
                progress_callback(y1, height)

        return image
