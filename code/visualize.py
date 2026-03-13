from color import ColorMap
from gui import GUI
from utils import printProgressBar, clear_cli, print_thin_separation
from numba import njit
from fractal import Fractal, MandelbrotFractal
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
        self.iterate_factor_k : int          = 250                                         # Feintuning-Faktor für quantitative Verbesserung der Detailgenauigkeit bei starken Zooms

# ------------------------------------------------------------

    # STARTING POINT
    def start(self):
        # GUI erzeugen (Unterscheidung für Julia-Set, da hier zusätzliches Feature "C ändern" im GUI benötigt wird)
        if self.fractal._name == "Julia-Set":
            self.gui = GUI(self.viewport.width_px, self.viewport.height_px, julia=True)             # GUI erzeugen
        else:
            self.gui = GUI(self.viewport.width_px, self.viewport.height_px, julia=False)             # GUI erzeugen

        # Callbacks setzen
        self.gui.set_zoom_callback(self._handle_zoom)                               # Zoom
        self.gui.set_reset_callback(self._handle_reset)                             # Reset-Button
        self.gui.set_back_step_callback(self._handle_back)                          # Zoom-History
        self.gui.set_forward_step_callback(self._handle_forward)                    # Zoom-History
        self.gui.set_change_color_callback(self._handle_change_coloring)            # Farbwechsel-Button
        self.gui.set_change_coloring_callback(self._handle_change_coloring)         # Coloring-Method wechseln
        self.gui.set_export_callback(self._handle_export)                           # Export-Button 
        self.gui.set_change_c_callback(self._handle_change_c)
        self.gui.set_c_select_callback(self._handle_c_select)
        
        # Coloring initialisieren
        self.coloring_modes = ["basic", "smooth", "histogram"]              # Verfügbare Coloring-Methoden
        self.coloring_index = 1
        self.coloring_mode = self.coloring_modes[self.coloring_index]       # Aktuelle Coloring-Methode

        # Dropdown-Menüs
        self.gui.set_coloring_menu(self.coloring_modes, self._handle_change_coloring)    # Coloring-Method Dropdown-Menü
        self.gui.set_palette_menu(self.palette_names, self._handle_palette_select)      # Farbpalette Dropdown-Menü

        # Methoden aufrufen
        self._push_history()                                   
        self._rerender()                      # Erstes Bild rendern (inkl. Anzeige)
        self.gui.run()                      # Eventloop starten

    # Callback: Für Zoom in GUI
    def _handle_zoom(self, x0, y0, x1, y1):
        self.viewport.zoom_to_pixels(x0, y0, x1, y1)
        self._push_history()    # Aktuellen Viewport in History speichern
        self._rerender()

#------------------------------------------------------------
# Hilfsfunktionen

    # Callback: Für Zoom-History
    def _push_history(self):
        bounds = (self.viewport.xmin, self.viewport.xmax, self.viewport.ymin, self.viewport.ymax)
        self.history = self.history[:self.history_index + 1]  # Alle "vorwärts"-Einträge löschen
        self.history.append(bounds)
        self.history_index += 1

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
# HANDLING 

    def _handle_reset(self):
        self.viewport.reset()
        self._push_history()
        self._rerender()

    def _handle_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self._apply_history()

    def _handle_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._apply_history()

    def _handle_palette_select(self, palette_name):
        self.colormap.set_palette(palette_name)
        self.palette_index = self.palette_names.index(palette_name)
        self._rerender()

    def _handle_change_coloring(self, coloring_name=None):
        if coloring_name is not None:
            self.coloring_index = self.coloring_modes.index(coloring_name)
        else:
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

    def _handle_change_c(self):
        mandelbrot = MandelbrotFractal()
    
        pixels = self.renderer.render(
            mandelbrot,
            self.viewport,
            self.colormap,
            coloring_mode=self.coloring_mode
        )

        self.gui.show_overlay(pixels)

    def _handle_c_select(self, x, y):
        real = self.viewport.xmin + (x / (self.viewport.width_px - 1)) * \
            (self.viewport.xmax - self.viewport.xmin)

        imag = self.viewport.ymax - (y / (self.viewport.height_px - 1)) * \
            (self.viewport.ymax - self.viewport.ymin)

        self.fractal.c_real = real
        self.fractal.c_imag = imag
        self.gui.clear_overlay()
        self._rerender()

#============================================================
# NUMBAR-RENDERING-Funktion (Unterscheidung zwischen zwei Typen, nötig für Julia)

@njit
def render_tile_kernel(kernel, iterations, escaped, y0, y1, width, height,
                       xmin, xmax, ymin, ymax, max_iter, escape_radius,
                       pixel_is_c, c_real, c_imag, start_real, start_imag,
                       exp_real=2.0, exp_imag=0.0):

    if pixel_is_c:

        for y in range(y0, y1):
            imag = ymax - (y / (height-1)) * (ymax - ymin)

            for x in range(width):
                real = xmin + (x / (width-1)) * (xmax - xmin)

                c_r = real
                c_i = imag
                z_r = start_real
                z_i = start_imag

                it, esc, zr, zi = kernel(
                    c_r, c_i,
                    max_iter,
                    escape_radius,
                    z_real=z_r,
                    z_imag=z_i,
                    exp_real=exp_real,
                    exp_imag=exp_imag
                )

                iterations[y, x] = it
                escaped[y, x] = esc

    else:

        for y in range(y0, y1):
            imag = ymax - (y / (height-1)) * (ymax - ymin)

            for x in range(width):
                real = xmin + (x / (width-1)) * (xmax - xmin)

                c_r = c_real
                c_i = c_imag
                z_r = real
                z_i = imag

                it, esc, zr, zi = kernel(
                    c_r, c_i,
                    max_iter,
                    escape_radius,
                    z_real=z_r,
                    z_imag=z_i,
                    exp_real=exp_real,
                    exp_imag=exp_imag
                )

                iterations[y, x] = it
                escaped[y, x] = esc

#------------------------------------------------------------
# RENDERER: Berechnet die Iterationen und wendet die Farbzuweisung an
class Renderer():

    def render(self, fractal, viewport, colormap, coloring_mode="smooth", k=40):
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

        tile_h = 32        

        for y0 in range(0, height, tile_h):

            y1 = min(y0 + tile_h, height)

            c_real = fractal.c_real
            c_imag = fractal.c_imag

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
                fractal.exp_imag
            )

            printProgressBar(y1, height, prefix="Rendering:", suffix="Complete", length=50)

        # Debug-Ausgabe der aktuellen Einstellungen im CLI; gehört eigentlich nicht hierher, aber so haben wir es an einer zentralen Stelle, wo alle relevanten Informationen vorliegen
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

        # Farbzuweisung
        if coloring_mode == "basic":
            image = colormap.apply_basic(iterations, escaped, adaptive_iter)

        elif coloring_mode == "histogram":
            image = colormap.apply_histogram(iterations, escaped, adaptive_iter)

        elif coloring_mode == "smooth":
            image = colormap.apply_smooth(iterations, escaped, adaptive_iter)

        elif coloring_mode == "ultra":
            image = colormap.apply_ultra(iterations, escaped, adaptive_iter)

        fractal.max_iterations = original_iter

        return image

#============================================================
# VIEWPORT: Definiert den sichtbaren Ausschnitt der komplexen Zahlenebene
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