from color import ColorMap
from gui import GUI
from utils import printProgressBar, clear_cli, print_thin_separation
from numba import njit
from fractal import Fractal#, MandelbrotFractal, InvertedMandelbrotFractal, mandelbrot_kernel, inverted_mandelbrot_kernel
from mapping import PALETTES
from export import PNGExporter
import numpy as np
#============================================================
# VISUALIZER: Verbindet Komponenten und steuert Ablauf der Visualisierung
class Visualizer():
    def __init__(self, fractal, fractal_name=None):
        # Klasseninstanzen
        self.fractal          : Fractal      = fractal                                     # Aktuelles Fraktal
        self.colormap         : ColorMap     = ColorMap()                                  # Management der Färbung
        self.viewport         : Viewport     = Viewport(self.fractal._default_bounds)      # Aktueller Ausschnitt, mit dem gearbeitet wird
        self.renderer         : Renderer     = Renderer()                                  # Numerische Berechnung
        self.exporter         : PNGExporter  = PNGExporter()                               # Export-Funktionalität
        self.gui              : GUI          = None                                        # Graphische Schnittstelle zum User
        
        # Zustände und Settings
        self.fractal_name     : str          = fractal_name                                # Name des Fraktals für Anzeige und Export
        self.history          : list         = []                                          # Für Zoom-History
        self.history_index    : int          = -1                                          # Aktuelle Position in der Zoom-History
        self.palette_names    : list         = list(PALETTES.keys())                       # Verfügbare Paletten
        self.palette_index    : int          = self.palette_names.index("default")         # Start mit "default"-Palette
        self.iterate_factor_k : int          = 500                                         # Feintuning-Faktor für quantitative Verbesserung der Detailgenauigkeit bei starken Zooms

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
        self.coloring_index = 0                                             # Start mit "smooth"-Coloring
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
        self._push_history()
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
            coloring_mode=self.coloring_mode,
            k = self.iterate_factor_k,
        )
        self.gui.display_image(pixels)

#------------------------------------------------------------
# HANDLING (Farbwechsel, Coloring-Methode wechseln, Exportieren)

    def _handle_change_color(self):
        self.palette_index = (self.palette_index + 1) % len(self.palette_names)
        new_name = self.palette_names[self.palette_index]
        self.colormap.set_palette(new_name)
        self._rerender()

    def _handle_change_coloring(self):
        self.coloring_index = (self.coloring_index + 1) % len(self.coloring_modes)
        self.coloring_mode = self.coloring_modes[self.coloring_index]
        self._rerender()

    def _handle_export(self):
        # Hochauflösende Größe definieren (z.B. 4K)
        factor = 4
        highres_width = self.viewport.width_px * factor
        highres_height = self.viewport.height_px * factor

        # Neues Viewport für Export
        export_viewport = self.viewport.copy()  # wir nehmen den gleichen Ausschnitt
        export_viewport.width_px = highres_width
        export_viewport.height_px = highres_height

        # Adaptive Iterationen für mehr Detail
        scale_factor = highres_width / self.viewport.width_px
        max_iter = int(self.fractal.max_iterations * scale_factor)

        original_iter = self.fractal.max_iterations
        self.fractal.max_iterations = max_iter

        # Neues Rendering
        pixels = self.renderer.render(
            self.fractal,
            export_viewport,
            self.colormap,
            coloring_mode=self.coloring_mode,
            k = self.iterate_factor_k)

        # Speicherort
        default_name = self.exporter.generate_default_filename(name=f"{self.fractal_name}")
        path = self.gui.ask_save_path(default_name)

        if path:
            self.exporter.save(pixels, path)
            print(f"Image exported to {path}")
            print_thin_separation()

#============================================================
'''
Renderer iteriert über alle Pixel im Viewport und färbt diese
mit Colormap. Er darf nicht selbst berechnen.
'''
class Renderer():

    # DRINGEND AN NJIT DELEGIEREN
    def render(self, fractal, viewport, colormap, coloring_mode="smooth", k=40):
        span = viewport.xmax - viewport.xmin
        k = k                       # Feintuning-Faktor für quantitative Verbesserung der Detailgenauigkeit bei starken Zooms

        # Adaptive Iterationstiefe
        original_iter = fractal.max_iterations
        safe_span = max(span, 1e-16)
        zoom_factor = 1.0 / safe_span
        adaptive_iter = int(original_iter + k * np.log10(zoom_factor))
        adaptive_iter = max(original_iter, adaptive_iter)
        fractal.max_iterations = adaptive_iter

        height, width = viewport.height_px, viewport.width_px
        iterations = np.zeros((height, width), dtype=np.float64)
        escaped = np.zeros((height, width), dtype=np.uint8)

        for y in range(height): 
            imag = viewport.ymax - (y / (height - 1)) * (viewport.ymax - viewport.ymin)
            for x in range(width):
                real = viewport.xmin + (x / (width - 1)) * (viewport.xmax - viewport.xmin)

                c = complex(real, imag)
                result = fractal.iterate(c) # Iterate-Methode des Fraktals aufrufen
                iterations[y, x] = result.iterations
                escaped[y, x] = 1 if result.escaped else 0
            
            printProgressBar(y+1, height, prefix='Rendering:', suffix='Complete', length=50)

        # Farbzuweisung
        if coloring_mode == "basic":
            image = colormap.apply_basic(iterations, escaped, adaptive_iter)
        elif coloring_mode == "histogram":
            image = colormap.apply_histogram(iterations, escaped, adaptive_iter)
        elif coloring_mode == "smooth":
            image = colormap.apply_smooth(iterations, escaped, adaptive_iter)
        elif coloring_mode == "ultra":
            image = colormap.apply_ultra(iterations, escaped, adaptive_iter)

        # Debug-Ausgabe der aktuellen Einstellungen im CLI; gehört eigentlich nicht hierher
        clear_cli()
        print_thin_separation(linebreak=False)
        print(f"Fractal:                {fractal._name}")
        print(f"Formula:                {fractal._formula}") # ?
        print(f"Startvalue:             {fractal.start_real} + {fractal.start_imag}i")
        print(f"Exponent:               {fractal.exp_real} + {fractal.exp_imag}i")
        print(f"Coloring mode:          {coloring_mode}")
        print(f"Palette:                {colormap.palette_name}")
        print(f"Viewport:               x[{viewport.xmin:.2e}, {viewport.xmax:.2e}] y[{viewport.ymin:.2e}, {viewport.ymax:.2e}]")
        print(f"Adaptive iterations:    {adaptive_iter:.0f} (base: {original_iter}, span: {span:.2e})")
        print_thin_separation(linebreak=False)
        print()

        fractal.max_iterations = original_iter 
        return image

#============================================================
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

#------------------------------------------------------------
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