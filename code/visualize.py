from color import ColorMap
from gui import GUI
import numpy as np
#============================================================
'''
Der Visualizer orchestriert nur. Er ist kein Renderer und keine GUI, 
sondern Session-Controller - er steuert den Ablauf und verwaltet 
Zustände.
'''
class Visualizer():
    def __init__(self, fractal):
        self.renderer   : Renderer    = Renderer()      # Numerische Berechnung
        self.colormap   : ColorMap    = ColorMap()      # Management der Färbung
        self.viewport   : Viewport    = Viewport()      # Aktueller Ausschnitt, mit dem gearbeitet wird
        self.fractal                  = fractal         # Aktuelles Fraktal
        self.gui        : GUI         = None            # Graphische Schnittstelle zum User

# ------------------------------------------------------------

    def start(self, fractal):
        self.gui = GUI(self.viewport.width_px, self.viewport.height_px)     # GUI erzeugen

        # Bild berechnen
        pixels = self.renderer.render(
            self.fractal,
            self.viewport,
            self.colormap
        )

        self.gui.display_image(pixels)      # Bild anzeigen
        self.gui.run()                      # Eventloop starten

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

        for y in range(viewport.height_px):
            for x in range(viewport.width_px):

                c = viewport.pixel_to_complex(x, y)
                value = fractal.iterate(c)      # Mathematik
                color = colormap.map(value)     # Darstellung
                image[y,x] = color
        
        return image

#============================================================
'''
Viewport definiert den sichtbaren (berechneten) Ausschnitt der
komplexen Zahlenebene.
'''
class Viewport():
    def __init__(self):
        self.xmin      : float  = -2.0
        self.xmax      : float  = 1.0
        self.ymin      : float  = -1.5
        self.ymax      : float  = 1.5
        self.width_px  : int    = 800
        self.height_px : int    = 600

# ------------------------------------------------------------

    def pixel_to_complex(self, x, y) -> complex:
        real = self.xmin + (x / self.width_px) * (self.xmax - self.xmin)
        imag = self.ymax - (y / self.height_px) * (self.ymax - self.ymin)
        num = complex(real, imag)
        return num