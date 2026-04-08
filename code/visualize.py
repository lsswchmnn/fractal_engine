from color      import Colorizer
from settings   import RenderSettings
from viewport   import Viewport
from rendering  import Renderer
from gui        import GUI
from utils      import print_thin_separation
from fractal    import Fractal, MandelbrotFractal
from mapping    import PALETTES
from export     import PNGExporter
#============================================================
# VISUALIZER: Verbindet Komponenten und steuert Ablauf der Visualisierung
class Visualizer():
    def __init__(self, fractal, fractal_name=None):
        # Klasseninstanzen
        self.fractal        : Fractal           = fractal                                  # Aktuelles Fraktal
        self.colorizer      : Colorizer         = Colorizer()                              # Management der Färbung
        self.viewport       : Viewport          = Viewport(self.fractal._default_bounds)   # Aktueller Ausschnitt, mit dem gearbeitet wird
        self.renderer       : Renderer          = Renderer()                               # Numerische Berechnung
        self.exporter       : PNGExporter       = PNGExporter()                            # Export-Funktionalität
        self.gui            : GUI               = None                                     # Graphische Schnittstelle zum User
        self.render_settings: RenderSettings    = RenderSettings()                         # Alle einstellbaren Parameter für Rendering und Postprocessing

        # Zustände und Settings
        self.fractal_name     : str          = fractal_name                                # Name des Fraktals für Anzeige und Export
        self.history          : list         = []                                          # Für Zoom-History
        self.history_index    : int          = -1                                          # Aktuelle Position in der Zoom-History
        self.palette_names    : list         = list(PALETTES.keys())                       # Verfügbare Paletten
        self.palette_index    : int          = self.palette_names.index("default")         # Start mit "default"-Palette                                   # Höhe der Kacheln für das tile-basierte Rendering (Performance-Optimierung)

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
        self.coloring_modes = ["basic", "smooth", "histogram", "orbit trap", "hybrid"]              # Verfügbare Coloring-Methoden
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
            self.colorizer,
            coloring_mode=self.coloring_mode,
            render_settings=self.render_settings
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
        # Hochauflösende Größe definieren (z.B. 4K)
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
            pixels = self.renderer.render(
                self.fractal,
                export_viewport,
                self.colorizer,
                coloring_mode=self.coloring_mode,
                render_settings=self.render_settings
            )
        finally:
            self.fractal.max_iterations = original_iter

        # Speicherort
        default_name = self.exporter.generate_default_filename(name=f"{self.fractal_name}")
        path = self.gui.ask_save_path(default_name)

        if path:
            self.exporter.save(pixels, path)
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
