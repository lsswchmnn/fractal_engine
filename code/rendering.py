import numpy    as     np
from numba      import njit
from time       import perf_counter
from settings   import RenderSettings
from utils      import printProgressBar, clear_cli, print_thin_separation
#============================================================
# NUMBAR-RENDERING-Funktion (Unterscheidung zwischen zwei Typen, nötig für Julia)

@njit
def render_tile_kernel(kernel, iterations, escaped, y0, y1, width, height,
                       xmin, xmax, ymin, ymax, max_iter, escape_radius,
                       pixel_is_c, c_real, c_imag, start_real, start_imag,
                       exp_real, exp_imag,
                       trap, trap_type, trap_x, trap_y, trap_radius):
    
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

#============================================================
# RENDERER: Berechnet die Iterationen und wendet die Farbzuweisung an
class Renderer():

    # Hauptfunktion: unterscheidet zwischen normalem Rendering und Supersampling
    def render(self, fractal, viewport, colorizer, coloring_mode="smooth", render_settings=RenderSettings()):
            
        if not render_settings.supersampling_enabled:
            image = self._render_single(fractal, viewport, colorizer, coloring_mode, render_settings)
        
        else:
            high_res_viewport = viewport.copy()
            high_res_viewport.width_px *= render_settings.supersampling_factor
            high_res_viewport.height_px *= render_settings.supersampling_factor

            image = self._render_single(fractal, high_res_viewport, colorizer, coloring_mode, render_settings)
            image = self._downsample(image, factor=render_settings.supersampling_factor)
                
        image = self._apply_postprocessing(colorizer, image, render_settings)

        return image

    # Normales tile-basiertes Rendering
    def _render_single(self, fractal, viewport, Colorizer, coloring_mode="smooth", render_settings=None):
        start = perf_counter()

        # Adaptive Iterationsberechnung
        adaptive_iter, original_iter, span = self._compute_adaptive_iterations(fractal, viewport, k=render_settings.iterate_factor_k)
        effective_max_iter = adaptive_iter

        height, width = viewport.height_px, viewport.width_px

        iterations = np.zeros((height, width), dtype=np.float64)
        escaped = np.zeros((height, width), dtype=np.uint8)
        trap = np.full((height, width), np.inf, dtype=np.float64)

        tile_h = render_settings.tile_height

        # Rendering in Kacheln (Tile-basiert)
        for y0 in range(0, height, tile_h):

            y1 = min(y0 + tile_h, height)

            render_tile_kernel(
                fractal.kernel,
                iterations,
                escaped,
                y0, y1,
                width,
                height,
                viewport.xmin,
                viewport.xmax,
                viewport.ymin,
                viewport.ymax,
                effective_max_iter,
                fractal.escape_radius,
                fractal.pixel_is_c,
                fractal.c_real,
                fractal.c_imag,
                fractal.start_real,
                fractal.start_imag,
                fractal.exp_real,
                fractal.exp_imag,

                # Orbit-Trap (neu, vollständig)
                trap,
                fractal.trap_type,
                fractal.trap_x,
                fractal.trap_y,
                fractal.trap_radius
            )

            printProgressBar(y1, height, prefix="Rendering:", suffix="Complete", length=50)

        end = perf_counter()
        length = round(number=end - start, ndigits=4)

        self._print_debug_info(fractal, viewport, Colorizer, coloring_mode, adaptive_iter, original_iter, span, length, settings=render_settings)  # Debug-Info

        fractal.max_iterations = original_iter  # Iterationszahl zurücksetzen

        # Farbzuweisung
        image = self._apply_coloring(Colorizer, iterations, escaped, effective_max_iter, trap, coloring_mode)

        return image

#------------------------------------------------------------
# Private Hilfsfunktionen für Renderer

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

    def _print_debug_info(self, fractal, viewport, Colorizer, coloring_mode, adaptive_iter, original_iter, span, length, settings=None):
        clear_cli()
        total_iter, total_pixels = self._estimate_workload(viewport, adaptive_iter, settings, render_settings=RenderSettings())

        print_thin_separation(linebreak=False)
        print("FRACTAL:")
        print(f"Fractal:                {fractal._name}")
        print(f"Formula:                {fractal._formula}")
        print(f"Startvalue:             {fractal.start_real} + {fractal.start_imag}i")
        print(f"Exponent:               {fractal.exp_real} + {fractal.exp_imag}i")
        print("\nCOLORING:")
        print(f"Coloring mode:          {coloring_mode}")
        if coloring_mode == "orbit trap":
            print(f"Orbit-Trap type:        {fractal.trap_type_name}")
        print(f"Palette:                {Colorizer.palette_name}")
        print("\nRENDERING:")
        if settings:
            print(f"Supersampling:          {f'Enabled (factor: {settings.supersampling_factor})' if settings.supersampling_enabled else 'Disabled'}")
        print(f"Viewport:               x[{viewport.xmin:.2e}, {viewport.xmax:.2e}] y[{viewport.ymin:.2e}, {viewport.ymax:.2e}]")
        print(f"Adaptive iterations:    {adaptive_iter:.0f} (base: {original_iter}, span: {span:.2e})")
        print(f"Rendering-Time:         {length} sec")
        print(f"Estimated workload:     {total_iter:.2e} iterations ({total_pixels:.2e} pixels)")
        print_thin_separation(linebreak=False)
        print()

    def _estimate_workload(self, viewport, adaptive_iter, settings, render_settings):
        if settings.supersampling_enabled:
            factor = render_settings.supersampling_factor
            total_pixels = (viewport.width_px * factor) * (viewport.height_px * factor)
        else:
            total_pixels = viewport.width_px * viewport.height_px
        
        total_iterations = total_pixels * adaptive_iter
        return total_iterations, total_pixels

    def _apply_coloring(self, Colorizer, iterations, escaped, effective_max_iter, trap, coloring_mode):
        if coloring_mode == "basic":
            image = Colorizer.apply_basic(iterations, escaped)   # max_iter nicht nötig

        elif coloring_mode == "histogram":
            image = Colorizer.apply_histogram(iterations, escaped, effective_max_iter)

        elif coloring_mode == "smooth":
            image = Colorizer.apply_smooth(iterations, escaped, effective_max_iter)

        elif coloring_mode == "orbit trap":
            image = Colorizer.apply_orbit_trap(trap, escaped)

        elif coloring_mode == "hybrid":
            image = Colorizer.apply_hybrid(iterations, escaped, effective_max_iter)

        else:
            raise ValueError(f"Unknown coloring mode: {coloring_mode}")
        
        return image

    def _apply_postprocessing(self, colorizer, image, render_settings):
        if not render_settings.post_process_enabled:
            return image
        image = colorizer.apply_contrast(image, contrast=render_settings.contrast_factor)
        image = colorizer.apply_gamma(image, gamma=render_settings.gamma_factor)
        return image