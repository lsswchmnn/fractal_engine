import numpy        as     np
from numba          import njit
from time           import perf_counter
from settings       import RenderSettings
from utils          import printProgressBar, clear_cli, print_thin_separation, finishProgressBar
from results        import RenderResult
#============================================================
# NUMBAR-RENDERING-Funktion (Unterscheidung zwischen zwei Typen, nötig für Julia)

@njit
def render_tile_kernel(
    kernel, iterations, escaped, y0, y1, width, height,
    xmin, xmax, ymin, ymax, max_iter, escape_radius,
    pixel_is_c, c_real, c_imag, start_real, start_imag,
    exp_real, exp_imag, z_real, z_imag,
    trap, trap_type, trap_x, trap_y, trap_radius
    ):
    
    # Einmalige Unterscheidung
    if pixel_is_c:
        mode = 0    # Fall 1: Mandelbrot oder andere Fraktale außer Julia
    else:       
        mode = 1    # Fall 2: Julia

    # Einmalige Berechnung der Schrittweiten
    dx = (xmax - xmin) / (width - 1)
    dy = (ymax - ymin) / (height - 1)

    # Äußerer Loop: Imaginärteil / Y-Achse
    for y in range(y0, y1):
        imag = ymax - y * dy

        # Innerer Loop: Realteil / X-Achse
        for x in range(width):
            real = xmin + x * dx

            # Rollenverteilung je nach Modus
            if mode == 0:
                c_r, c_i = real, imag
                z_r, z_i = start_real, start_imag
            else:
                c_r, c_i = c_real, c_imag
                z_r, z_i = real, imag

            # Aufruf des Fraktal-Kernels (fractal.py) (Positionsbasiert wegen Numba)
            it, esc, zr, zi, trap_val = kernel(
                c_r, c_i,
                max_iter, escape_radius,
                z_r, z_i,
                exp_real, exp_imag,
                trap_y, trap_x, 
                trap_type, trap_radius
            )

            # Speichern der Ergebnisse
            iterations[y, x] = it           # Iterations (Geometrie)
            escaped[y, x] = esc             # Escaped (Topologie)
            trap[y, x] = trap_val           # Orbit-Trap-Wert
            z_real[y, x] = zr
            z_imag[y, x] = zi

#============================================================
# RENDERER (Berechnet die Iterationen, ruft Hilfsmethoden auf)
class Renderer():

    def render(
            self, 
            fractal, 
            viewport, 
            render_settings=RenderSettings()
            ) -> np.ndarray:
            
        if not render_settings.supersampling_enabled:
            result = self._render_single(fractal, viewport, render_settings)

        else:
            high_res_viewport = viewport.copy()
            high_res_viewport.width_px *= render_settings.supersampling_factor
            high_res_viewport.height_px *= render_settings.supersampling_factor

            result = self._render_single(fractal, high_res_viewport, render_settings)
            result = self._downsample(result, factor=render_settings.supersampling_factor)

        return result

    def _render_single(self, fractal, viewport, render_settings=None):
        start = perf_counter()

        # Adaptive Iterationsberechnung
        adaptive_iter, original_iter, span = self._compute_adaptive_iterations(fractal, viewport, k=render_settings.iterate_factor_k)
        effective_max_iter = adaptive_iter

        height, width = viewport.height_px, viewport.width_px

        iterations = np.zeros((height, width), dtype=np.float64)
        escaped = np.zeros((height, width), dtype=np.uint8)
        trap = np.full((height, width), np.inf, dtype=np.float64)
        z_real = np.zeros((height, width), dtype=np.float64)
        z_imag = np.zeros((height, width), dtype=np.float64)

        tile_h = render_settings.tile_height

        clear_cli()     # Informationsausgabe vor Progressbar entfernen

        # Rendering in Kacheln (Tile-basiert)
        for y0 in range(0, height, tile_h):

            y1 = min(y0 + tile_h, height)

            render_tile_kernel(

                fractal.kernel,             # Kernel-Funktion des Fraktals (Callable)
                iterations,                 # Output-Array: kontinuierliche Iterationszahl
                escaped,                    # Punkt entkommen oder nicht (0/1)
                y0, y1,                     # Typ: int | definiert den vertikalen Ausschnitt (Tile), der berechnet wird
                
                # Bilddimensionen
                width,                     
                height,

                # Ausschnitt der komplexen Ebene definieren          
                viewport.xmin,              
                viewport.xmax,
                viewport.ymin,
                viewport.ymax,
                
                # Iterationskontrolle
                effective_max_iter,         # Abbruchbedingungen
                fractal.escape_radius,      # Divergenz-Kriterium (Theoretisch unendlich, praktisch ein hoher Wert)

                # Fraktalparameter (gesplittet in je zwei floats)
                fractal.pixel_is_c,
                fractal.c_real,
                fractal.c_imag,
                fractal.start_real,
                fractal.start_imag,
                fractal.exp_real,
                fractal.exp_imag,
                z_real,
                z_imag,

                # Orbit-Trap
                trap,
                fractal.trap_type,
                fractal.trap_x,
                fractal.trap_y,
                fractal.trap_radius
            )

            printProgressBar(y1, height, prefix="Rendering:", suffix="Complete", length=50)

        # Zeitmessung beenden
        end = perf_counter()
        render_time = round(number=end - start, ndigits=4)

        # Progressbar entfernen
        finishProgressBar()
        clear_cli()

        fractal.max_iterations = original_iter  # Iterationszahl zurücksetzen

        return RenderResult(iterations, escaped, trap, z_real, z_imag, effective_max_iter, render_time)

#------------------------------------------------------------
# HILFSMETHODEN für Renderer

    def _downsample(self, image: np.ndarray, factor: int=2) -> np.ndarray:
        if factor <= 1:
            return image
        
        h, w, c = image.shape

        if h % factor != 0 or w % factor != 0:
            raise ValueError(f"Image dimensions must be divisible by the downsampling factor. Got {h}x{w} with factor {factor}.")
        
        new_h = h // factor
        new_w = w // factor

        reshaped = image.reshape(new_h, factor, new_w, factor, c)
        downsampled = reshaped.mean(axis=(1, 3)).astype(np.uint8)
        return downsampled

    def _compute_adaptive_iterations(self, fractal, viewport, k=40):
        span = viewport.width
        original_iter = fractal.max_iterations
        safe_span = max(span, 1e-16)
        zoom_factor = 1.0 / safe_span

        adaptive_iter = int(original_iter + k * max(0, np.log10(zoom_factor)))
        adaptive_iter = max(original_iter, adaptive_iter)

        return adaptive_iter, original_iter, span

    def _estimate_workload(self, viewport, adaptive_iter, settings, render_settings):
        if settings.supersampling_enabled:
            factor = render_settings.supersampling_factor
            total_pixels = (viewport.width_px * factor) * (viewport.height_px * factor)
        else:
            total_pixels = viewport.width_px * viewport.height_px
        
        total_iterations = total_pixels * adaptive_iter
        return total_iterations, total_pixels
