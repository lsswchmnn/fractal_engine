from color          import Colorizer
import fractal
from postprocess    import PostProcesser
from results        import ProcessingTimes
from settings       import RenderSettings
from viewport       import Viewport
from rendering      import Renderer
from gui            import GUI
from utils          import print_thin_separation
from fractal        import Fractal, MandelbrotFractal
from mapping        import PALETTES, COLORING_NAMES
from export         import PNGExporter
from debug          import print_debug_info
from time           import perf_counter
#============================================================
# VISUALIZER: Verbindet Komponenten und steuert Ablauf der Visualisierung
class Visualizer():
    
    def __init__(self, fractal, fractal_name=None):

        cr, ci, w = self.convert_bonds_to_center_width(fractal._default_bounds)

        # Klasseninstanzen
        self.fractal        : Fractal           = fractal                                  # Aktuelles Fraktal
        self.colorizer      : Colorizer         = Colorizer()                              # Management der Färbung
        self.viewport       : Viewport          = Viewport(cr, ci, w)                      # Aktueller Ausschnitt, mit dem gearbeitet wird
        self.renderer       : Renderer          = Renderer()                               # Numerische Berechnung
        self.exporter       : PNGExporter       = PNGExporter()                            # Export-Funktionalität
        self.gui            : GUI               = None                                     # Graphische Schnittstelle zum User
        self.render_settings: RenderSettings    = RenderSettings()                         # Alle einstellbaren Parameter für Rendering und Postprocessing
        self.postprocesser  : PostProcesser     = PostProcesser()                          # Management der Postprocessing-Effekte

        # Zustände und Settings
        self.fractal_name     : str          = fractal_name                                # Name des Fraktals für Anzeige und Export
        self.history          : list         = []                                          # Für Zoom-History
        self.history_index    : int          = -1                                          # Aktuelle Position in der Zoom-History
        self.palette_names    : list         = list(PALETTES.keys())                       # Verfügbare Paletten
        self.palette_index    : int          = self.palette_names.index("default")         # Start mit "default"-Palette                                   # Höhe der Kacheln für das tile-basierte Rendering (Performance-Optimierung)

# ------------------------------------------------------------

    # Fraktal-Definitionen umformen
    def convert_bonds_to_center_width(self, bounds):
        xmin, xmax, ymin, ymax = bounds

        center_real = (xmin + xmax) / 2
        center_imag = (ymin + ymax) / 2

        width = xmax - xmin  # oder alternativ x-span als Basis

        return center_real, center_imag, width

    # Starting Point Rendering-Prozess
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
        self.coloring_modes = COLORING_NAMES                                # Verfügbare Coloring-Methoden
        self.coloring_index = 1
        self.coloring_mode = self.coloring_modes[self.coloring_index]       # Aktuelle Coloring-Methode

        # Dropdown-Menüs
        self.gui.set_coloring_menu(self.coloring_modes, self._handle_change_coloring)    # Coloring-Method Dropdown-Menü
        self.gui.set_palette_menu(self.palette_names, self._handle_palette_select)      # Farbpalette Dropdown-Menü

        # Methoden aufrufen
        self._push_history()                # Start-Viewport in History speichern                   
        self._rerender()                    # Erstes Bild rendern (inkl. Anzeige)
        self.gui.run()                      # Eventloop starten

    # Callback: Für Zoom in GUI
    def _handle_zoom(self, x0, y0, x1, y1):

        c1 = self.viewport.pixel_to_complex(x0, y0)
        c2 = self.viewport.pixel_to_complex(x1, y1)

        center = (c1 + c2) / 2

        width = abs(c2.real - c1.real)

        self.viewport.center_real = center.real
        self.viewport.center_imag = center.imag
        self.viewport.width = width

        self._push_history()
        self._rerender()

#------------------------------------------------------------
# Hilfsfunktionen

    # Callback: Für Zoom-History
    def _push_history(self):
        bounds = self.viewport.bounds
        self.history = self.history[:self.history_index + 1]  # Alle "vorwärts"-Einträge löschen
        
        self.history.append((self.viewport.center_real, self.viewport.center_imag, self.viewport.width))

        self.history_index += 1

    # Hilfsfunktion: Aktuellen Viewport aus History anwenden
    def _apply_history(self):
        center_real, center_imag, width = self.history[self.history_index]
        self.viewport.center_real = center_real
        self.viewport.center_imag = center_imag
        self.viewport.width = width

        self._rerender()

    # Render-Pipeline Entry Point
    def _rerender(self):

        start = perf_counter()
        result = self.renderer.render(
            self.fractal,
            self.viewport,
            self.render_settings
        )
        end = perf_counter()
        render_time = round(number=end - start, ndigits=4)

        start = perf_counter()
        image = self.colorizer.apply(
            result,
            self.coloring_mode
        )
        end = perf_counter()
        coloring_time = round(number=end - start, ndigits=4)

        start = perf_counter()
        if self.render_settings.supersampling_enabled:
            image = self.renderer._downsample(image, factor=self.render_settings.supersampling_factor)
        end = perf_counter()
        downsample_time = round(number=end - start, ndigits=4)

        image = self.postprocesser.process(
            self.render_settings,
            image
        )

        render_times = ProcessingTimes(render_time, coloring_time, downsample_time)     # Objekt mit Zeitangaben für Debug-Info

        print_debug_info(
            self.fractal,
            self.viewport,
            self.coloring_mode,
            adaptive_iter=result.max_iter,
            original_iter=self.fractal.max_iterations,
            span=self.viewport.width,
            times=render_times,
            palette_name=self.colorizer.palette_name,
            settings=self.render_settings
        )

        self.gui.display_image(image)

#------------------------------------------------------------
# HANDLING 

    def _handle_reset(self):
        cr, ci, w = self.convert_bonds_to_center_width(self.fractal._default_bounds)
        self.viewport.center_real = cr
        self.viewport.center_imag = ci
        self.viewport.width = w

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
        self.colorizer.set_palette(palette_name)
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

        # Hochauflösende Größe definieren
        highres_width = self.viewport.width_px * self.render_settings.export_factor
        highres_height = self.viewport.height_px * self.render_settings.export_factor

        # Neues Viewport für Export
        export_viewport = self.viewport.copy()  # wir nehmen den gleichen Ausschnitt
        export_viewport.width_px = highres_width
        export_viewport.height_px = highres_height

        # Adaptive Iterationen für mehr Detail
        scale_factor = highres_width / self.viewport.width_px
        max_iter = int(self.fractal.max_iterations * scale_factor)

        original_iter = self.fractal.max_iterations
        self.fractal.max_iterations = max_iter

        try:
            # 1. RAW RENDERING
            result = self.renderer.render(
                self.fractal,
                export_viewport,
                self.render_settings
            )

            # 2. COLORING
            image = self.colorizer.apply(
                result,
                self.coloring_mode
            )

            # 3. POSTPROCESSING
            image = self.postprocesser.process(
                self.render_settings,
                image
            )

        finally:
            self.fractal.max_iterations = original_iter

        # Speicherort
        default_name = self.exporter.generate_default_filename(name=f"{self.fractal_name}")
        path = self.gui.ask_save_path(default_name)

        if path:
            self.exporter.save(image, path)
            print(f"Image ({highres_height} x {highres_width} px) exported to {path}")
            print_thin_separation()
            print()

    def _handle_change_c(self):
        mandelbrot = MandelbrotFractal()
    
        pixels = self.renderer.render(
            mandelbrot,
            self.viewport,
            self.colorizer,
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
