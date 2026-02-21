from color import ColorMap
from gui import GUI
from utils import printProgressBar, clear_cli
from numba import njit
import numpy as np
#============================================================
# NUMBA-FUNKTION (für Performance in der Iteration); später anbinden, wenn klar ist, wie
@njit
def _render_mandelbrot(
    xmin, xmax, ymin, ymax,
    width, height,
    max_iterations,
    escape_radius
):
    iterations = np.zeros((height, width), dtype=np.int32)
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
                    iterations[y, x] = i
                    escaped[y, x] = 1
                    break

                zi = 2.0 * zr * zi + imag
                zr = zr2 - zi2 + real
            else:
                iterations[y, x] = max_iterations
                escaped[y, x] = 0
        
        #printProgressBar(y, height, prefix="Loading Viewer")    # Ladeleiste, wo kann ich die implementieren?

    return iterations, escaped

#============================================================
'''
Der Visualizer orchestriert nur. Er ist kein Renderer und keine GUI, 
sondern Session-Controller - er steuert den Ablauf und verwaltet 
Zustände.
'''
class Visualizer():
    def __init__(self, fractal):
        self.colormap   : ColorMap    = ColorMap()      # Management der Färbung
        self.viewport   : Viewport    = Viewport()      # Aktueller Ausschnitt, mit dem gearbeitet wird
        self.renderer   : Renderer    = Renderer()      # Numerische Berechnung
        self.fractal                  = fractal         # Aktuelles Fraktal
        self.gui        : GUI         = None            # Graphische Schnittstelle zum User

# ------------------------------------------------------------

    def start(self):
        self.gui = GUI(self.viewport.width_px, self.viewport.height_px)     # GUI erzeugen
        self.gui.set_zoom_callback(self._handle_zoom)       # Für Zoom
        self.gui.set_reset_callback(self._handle_reset)     # Für Reset-Button

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
        image = np.zeros(
            (viewport.height_px, viewport.width_px, 3),
            dtype=np.uint8
        )

        # Wird irgendwann zu langsam; später z.B. mit NumPy machen:
        for y in range(viewport.height_px):
            for x in range(viewport.width_px):

                c = viewport.pixel_to_complex(x, y)
                result = fractal.iterate(c)      # Mathematik
                color = colormap.map(result, fractal.max_iterations)     # Darstellung
                image[y,x] = color

        clear_cli()
        return image


#     def render(self, fractal, viewport, colormap):

#         iterations, escaped = _render_mandelbrot(
#             viewport.xmin,
#             viewport.xmax,
#             viewport.ymin,
#             viewport.ymax,
#             viewport.width_px,
#             viewport.height_px,
#             fractal.max_iterations,
#             fractal.escape_radius
#         )

#         return colormap.apply(iterations, escaped, fractal.max_iterations)
    
# #============================================================
'''
Viewport definiert den sichtbaren (berechneten) Ausschnitt der
komplexen Zahlenebene.
'''
class Viewport():
    def __init__(self):
        self._default_bounds = (-2.0, 1.0, -1.5, 1.5)   # Default
        self.reset()
        self.width_px  : int    = 800
        self.height_px : int    = 600

# ------------------------------------------------------------
    def reset(self):
        self.xmin, self.xmax, self.ymin, self.ymax = self._default_bounds

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