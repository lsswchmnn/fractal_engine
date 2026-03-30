import numpy as np
from numba import njit
from time import perf_counter
from color import ColorMap
from utils import printProgressBar, clear_cli, print_thin_separation
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
                max_iter,
                escape_radius,
                z_r, z_i,
                exp_real, exp_imag,
                trap_type, trap_x, trap_y, trap_radius
            )

            # Speichern der Ergebnisse
            iterations[y, x] = it           # Iterations (Geometrie)
            escaped[y, x] = esc             # Escaped (Topologie)+
            trap[y, x] = trap_val

#------------------------------------------------------------
# RENDERER: Berechnet die Iterationen und wendet die Farbzuweisung an
class Renderer():

    def render(self, fractal, viewport, colormap, coloring_mode="smooth", k=40, gamma=1.5, contrast=1.2):
        start = perf_counter()

        span = viewport.xmax - viewport.xmin

        original_iter = fractal.max_iterations
        safe_span = max(span, 1e-16)
        zoom_factor = 1.0 / safe_span

        #adaptive_iter = int(original_iter + k * np.log10(zoom_factor))
        adaptive_iter = int(original_iter + k * max(0, np.log10(zoom_factor)))
        adaptive_iter = max(original_iter, adaptive_iter)

        fractal.max_iterations = adaptive_iter

        height, width = viewport.height_px, viewport.width_px

        iterations = np.zeros((height, width), dtype=np.float64)
        escaped = np.zeros((height, width), dtype=np.uint8)
        trap = np.full((height, width), np.inf, dtype=np.float64)

        tile_h = 32        

        for y0 in range(0, height, tile_h):

            y1 = min(y0 + tile_h, height)

            # Allgemeinen Rendering-Kernel (NJIT) aufrufen
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
                fractal.max_iterations,
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

        # Debug-Ausgabe der aktuellen Einstellungen im CLI; gehört eigentlich nicht hierher, aber so haben wir es an einer zentralen Stelle, wo alle relevanten Informationen vorliegen
        clear_cli()
        print_thin_separation(linebreak=False)
        print(f"Fractal:                {fractal._name}")
        print(f"Formula:                {fractal._formula}")
        print(f"Startvalue:             {fractal.start_real} + {fractal.start_imag}i")
        print(f"Exponent:               {fractal.exp_real} + {fractal.exp_imag}i")
        print(f"Coloring mode:          {coloring_mode}")
        if coloring_mode == "orbit trap":
            print(f"Orbit-Trap type:        {fractal.trap_type_name}")
        print(f"Palette:                {colormap.palette_name}")
        print(f"Viewport:               x[{viewport.xmin:.2e}, {viewport.xmax:.2e}] y[{viewport.ymin:.2e}, {viewport.ymax:.2e}]")
        print(f"Adaptive iterations:    {adaptive_iter:.0f} (base: {original_iter}, span: {span:.2e})")
        print(f"Rendering-Time:         {length} sec")
        
        print_thin_separation(linebreak=False)
        print()

        # Farbzuweisung
        if coloring_mode == "basic":
            image = colormap.apply_basic(iterations, escaped, adaptive_iter)

        elif coloring_mode == "histogram":
            image = colormap.apply_histogram(iterations, escaped, adaptive_iter)

        elif coloring_mode == "smooth":
            image = colormap.apply_smooth(iterations, escaped, adaptive_iter)

        elif coloring_mode == "orbit trap":
            image = colormap.apply_orbit_trap(trap, escaped)

        else:
            raise ValueError(f"Unknown coloring mode: {coloring_mode}")

        fractal.max_iterations = original_iter

        # Postprocessing
        image = colormap.apply_contrast(image, contrast=contrast)
        image = colormap.apply_gamma(image, gamma=gamma)

        return image
