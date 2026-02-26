from color import ColorMap
from gui import GUI
from utils import printProgressBar, clear_cli
from numba import njit
from fractal import MandelbrotFractal, InvertedMandelbrotFractal
import numpy as np
#============================================================
# NUMBA-FUNKTIONEN (für Performance in der Iteration)
@njit
def _render_mandelbrot(
    xmin, xmax, ymin, ymax,
    width, height,
    max_iterations,
    escape_radius
):
    iterations = np.zeros((height, width), dtype=np.float64)
    escaped = np.zeros((height, width), dtype=np.uint8)

    escape_sq = escape_radius * escape_radius

    for y in range(height):
        imag = ymax - (y / (height - 1)) * (ymax - ymin)

        for x in range(width):
            real = xmin + (x / (width - 1)) * (xmax - xmin)

            zr = 0.0
            zi = 0.0

            for i in range(max_iterations):
                zr2 = zr * zr
                zi2 = zi * zi

                if zr2 + zi2 > escape_sq:
                    # Smooth Coloring berechnen
                    mod_z = zr2 + zi2
                    nu = i + 1 - np.log(np.log(mod_z))/np.log(2.0)
                    iterations[y, x] = nu
                    escaped[y, x] = 1
                    break

                zi = 2.0 * zr * zi + imag
                zr = zr2 - zi2 + real
            else:
                iterations[y, x] = max_iterations
                escaped[y, x] = 0

    return iterations, escaped

@njit
def _render_inverted_mandelbrot(
    xmin, xmax, ymin, ymax,
    width, height,
    max_iterations,
    escape_radius
):
    iterations = np.zeros((height, width), dtype=np.float64)
    escaped = np.zeros((height, width), dtype=np.uint8)

    escape_sq = escape_radius * escape_radius

    for y in range(height):
        imag = ymax - (y / (height - 1)) * (ymax - ymin)

        for x in range(width):
            real = xmin + (x / (width - 1)) * (xmax - xmin)

            # Inverse Koordinate
            if real == 0.0 and imag == 0.0:
                c_real = 1e10
                c_imag = 0.0
            else:
                denom = real*real + imag*imag
                c_real = real / denom
                c_imag = -imag / denom

            zr = 0.0
            zi = 0.0

            for i in range(max_iterations):
                zr2 = zr * zr
                zi2 = zi * zi

                if zr2 + zi2 > escape_sq:
                    mod_z = zr2 + zi2
                    nu = i + 1 - np.log(np.log(mod_z))/np.log(2.0)
                    iterations[y, x] = nu
                    escaped[y, x] = 1
                    break

                # klassische Mandelbrot-Iteration
                zi = 2.0 * zr * zi + c_imag
                zr = zr2 - zi2 + c_real
            else:
                iterations[y, x] = max_iterations
                escaped[y, x] = 0

    return iterations, escaped
#============================================================
'''
Der Visualizer orchestriert nur. Er ist kein Renderer und keine GUI, 
sondern Session-Controller - er steuert den Ablauf und verwaltet 
Zustände.
'''
class Visualizer():
    def __init__(self, fractal):
        self.fractal                  = fractal                                     # Aktuelles Fraktal
        self.colormap   : ColorMap    = ColorMap()                                  # Management der Färbung
        self.viewport   : Viewport    = Viewport(self.fractal._default_bounds)      # Aktueller Ausschnitt, mit dem gearbeitet wird
        self.renderer   : Renderer    = Renderer()                                  # Numerische Berechnung
        self.gui        : GUI         = None                                        # Graphische Schnittstelle zum User

# ------------------------------------------------------------

    def start(self):
        self.gui = GUI(self.viewport.width_px, self.viewport.height_px)     # GUI erzeugen
        self.gui.set_zoom_callback(self._handle_zoom)           # Für Zoom
        self.gui.set_reset_callback(self._handle_reset)         # Für Reset-Button

        # Bild berechnen
        pixels = self.renderer.render(
            self.fractal,
            self.viewport,
            self.colormap
        )

        self.gui.display_image(pixels)      # Bild anzeigen
        self.gui.run()                      # Eventloop starten

    # Für Zoom in GUI
    def _handle_zoom(self, x0, y0, x1, y1):
        self.viewport.zoom_to_pixels(x0, y0, x1, y1)

        pixels = self.renderer.render(
            self.fractal,
            self.viewport,
            self.colormap
        )

        self.gui.display_image(pixels)

    # Für Reset-Button in GUI
    def _handle_reset(self):
        self.viewport.reset()

        pixels = self.renderer.render(
            self.fractal,
            self.viewport,
            self.colormap
        )

        self.gui.display_image(pixels)

#============================================================
'''
Renderer iteriert über alle Pixel im Viewport. Er färbt diese
mit Colormap. Er darf nicht selbst berechnen.
'''
class Renderer():

    def render(self, fractal, viewport, colormap):
        span = viewport.xmax - viewport.xmin
        base_iter = fractal.max_iterations
        k = 40  # Feintuning-Faktor

        if span > 0:
            adaptive_iter = int(base_iter + k * np.log10(1.0 / span))
        else:
            adaptive_iter = base_iter

        adaptive_iter = max(base_iter, adaptive_iter)

        # Kernel-Aufruf je nach Fraktaltyp
        if isinstance(fractal, MandelbrotFractal):
            iterations, escaped = _render_mandelbrot(
                viewport.xmin,
                viewport.xmax,
                viewport.ymin,
                viewport.ymax,
                viewport.width_px,
                viewport.height_px,
                adaptive_iter,
                fractal.escape_radius
            )
        
        elif isinstance(fractal, InvertedMandelbrotFractal):
            iterations, escaped = _render_inverted_mandelbrot(
                viewport.xmin,
                viewport.xmax,
                viewport.ymin,
                viewport.ymax,
                viewport.width_px,
                viewport.height_px,
                adaptive_iter,
                fractal.escape_radius
            )
            
        # Farbzuweisung (beliebige apply-methode nutzen)
        image = colormap.apply_smooth(
            iterations,
            escaped,
            adaptive_iter
        )

        clear_cli()
        return image

# #============================================================
'''
Viewport definiert den sichtbaren (berechneten) Ausschnitt der
komplexen Zahlenebene.
'''
class Viewport():
    def __init__(self, bounds:tuple):
        self.bounds = bounds
        self.reset()
        self.width_px  : int    = 800
        self.height_px : int    = 600

# ------------------------------------------------------------
    def reset(self):
        self.xmin, self.xmax, self.ymin, self.ymax = self.bounds

    def pixel_to_complex(self, x, y) -> complex:
        real = self.xmin + (x / (self.width_px - 1)) * (self.xmax - self.xmin)
        imag = self.ymax - (y / (self.height_px - 1)) * (self.ymax - self.ymin)
        num = complex(real, imag)
        return num
    
    # Für Zoom in GUI
    def zoom_to_pixels(self, x0, y0, x1, y1):

        x_min_px = min(x0, x1)
        x_max_px = max(x0, x1)
        y_min_px = min(y0, y1)
        y_max_px = max(y0, y1)

        c1 = self.pixel_to_complex(x_min_px, y_min_px)
        c2 = self.pixel_to_complex(x_max_px, y_max_px)

        self.xmin = c1.real
        self.xmax = c2.real
        self.ymin = c2.imag
        self.ymax = c1.imag