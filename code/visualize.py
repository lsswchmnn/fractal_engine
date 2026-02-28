from color import ColorMap
from gui import GUI
from utils import printProgressBar, clear_cli
from numba import njit
from fractal import MandelbrotFractal, InvertedMandelbrotFractal
from mapping import PALETTES
from export import PNGExporter
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
        self.exporter   : PNGExporter = PNGExporter()                               # Export-Funktionalität
        self.gui        : GUI         = None                                        # Graphische Schnittstelle zum User
        self.history    : list        = []                                          # Für Zoom-History
        self.history_index            = -1
        self.palette_names = list(PALETTES.keys())
        self.palette_index = self.palette_names.index("default")  # Start mit "default"-Palette

# ------------------------------------------------------------

    # STARTING POINT
    def start(self):
        # GUI erzeugen und Callbacks setzen
        self.gui = GUI(self.viewport.width_px, self.viewport.height_px)         # GUI erzeugen
        self.gui.set_zoom_callback(self._handle_zoom)                           # Zoom
        self.gui.set_reset_callback(self._handle_reset)                         # Reset-Button
        self.gui.set_back_step_callback(self._handle_back)                      # Zoom-History
        self.gui.set_forward_step_callback(self._handle_forward)                # Zoom-History
        self.gui.set_change_color_callback(self._handle_change_color)           # Farbwechsel-Button
        self.gui.set_change_coloring_callback(self._handle_change_coloring)     # Coloring-Method wechseln
        self.gui.set_export_callback(self._handle_export)                       # Export-Button 

        self.coloring_modes = ["basic", "smooth", "histogram"]     # Verfügbare Coloring-Methoden
        self.coloring_index = 1                                             # Start mit "smooth"-Coloring
        self.coloring_mode = self.coloring_modes[self.coloring_index]       # Aktuelle Coloring-Methode

        self._push_history()                                   
        self._rerender()                      # Erstes Bild rendern (inkl. Anzeige)
        self.gui.run()                      # Eventloop starten

    # Callback: Für Zoom in GUI
    def _handle_zoom(self, x0, y0, x1, y1):
        self.viewport.zoom_to_pixels(x0, y0, x1, y1)
        self._push_history()    # Aktuellen Viewport in History speichern
        self._rerender()

#------------------------------------------------------------
# Zoom-History: Back, Forward, Reset

    # Callback: Für Reset-Button in GUI
    def _handle_reset(self):
        self.viewport.reset()
        self._rerender()

    # Callback: Für Zoom-History
    def _push_history(self):
        bounds = (self.viewport.xmin, self.viewport.xmax, self.viewport.ymin, self.viewport.ymax)
        self.history = self.history[:self.history_index + 1]  # Alle "vorwärts"-Einträge löschen
        self.history.append(bounds)
        self.history_index += 1

    def _handle_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self._apply_history()

    def _handle_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._apply_history()

    # Hilfsfunktion: Aktuellen Viewport aus History anwenden
    def _apply_history(self):
        xmin, xmax, ymin, ymax = self.history[self.history_index]
        self.viewport.xmin = xmin
        self.viewport.xmax = xmax
        self.viewport.ymin = ymin
        self.viewport.ymax = ymax

        self._rerender()

    # Hilfsfunktion: Aktuelles Bild rendern und in GUI anzeigen
    def _rerender(self):
        pixels = self.renderer.render(
            self.fractal,
            self.viewport,
            self.colormap,
            coloring_mode=self.coloring_mode
        )
        self.gui.display_image(pixels)

#------------------------------------------------------------
# HANDLING (Farbwechsel, Coloring-Methode wechseln, Exportieren)

    def _handle_change_color(self):
        self.palette_index = (self.palette_index + 1) % len(self.palette_names)
        new_name = self.palette_names[self.palette_index]
        self.colormap.set_palette(new_name)
        self._rerender()
        print(f"Switched to palette: {new_name}")   # vorrübergehende Ausgabe im CLI

    def _handle_change_coloring(self):
        self.coloring_index = (self.coloring_index + 1) % len(self.coloring_modes)
        self.coloring_mode = self.coloring_modes[self.coloring_index]
        self._rerender()
        print(f"Switched to coloring method: {self.coloring_mode}")  # vorrübergehende Ausgabe im CLI

    def _handle_export(self):
        # Hochauflösende Größe definieren (z.B. 4K)
        factor = 4
        highres_width = 800 * factor
        highres_height = 600 * factor

        # Neues Viewport für Export
        export_viewport = self.viewport.copy()  # wir nehmen den gleichen Ausschnitt
        export_viewport.width_px = highres_width
        export_viewport.height_px = highres_height

        # Adaptive Iterationen für mehr Detail
        scale_factor = highres_width / self.viewport.width_px
        max_iter = int(self.fractal.max_iterations * scale_factor)

        # Neues Rendering
        pixels = self.renderer.render(
            self.fractal,
            export_viewport,
            self.colormap,
            coloring_mode=self.coloring_mode,
        )

        # Speicherort
        default_name = self.exporter.generate_default_filename()
        path = self.gui.ask_save_path(default_name)

        if path:
            self.exporter.save(pixels, path)

#============================================================
'''
Renderer iteriert über alle Pixel im Viewport. Er färbt diese
mit Colormap. Er darf nicht selbst berechnen.
'''
class Renderer():

    # Render-Funktion: Berechnet die Iterationen und wendet die Colormap an
    def render(self, fractal, viewport, colormap, coloring_mode="smooth"):
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
            
        # Farbzuweisung (beliebige apply-methode nutzbar)
        if coloring_mode == "basic":
            image = colormap.apply_basic(
                iterations,
                escaped,
                adaptive_iter
            )

        elif coloring_mode == "histogram":
            image = colormap.apply_histogram(
                iterations,
                escaped,
                adaptive_iter
            )

        elif coloring_mode == "smooth":  # smooth
            image = colormap.apply_smooth(
                iterations,
                escaped,
                adaptive_iter
            )

        elif coloring_mode == "ultra":  # ultra, später implementieren
            image = colormap.apply_ultra(
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

    # Für Export: Kopie des Viewports mit neuer Pixelgröße, um GUI nicht zu beeinflussen
    def copy(self):
        new_vp = Viewport(self.bounds)
        new_vp.xmin, new_vp.xmax, new_vp.ymin, new_vp.ymax = self.xmin, self.xmax, self.ymin, self.ymax
        new_vp.width_px = self.width_px
        new_vp.height_px = self.height_px
        return new_vp