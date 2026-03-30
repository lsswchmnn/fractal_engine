
#============================================================
# VIEWPORT: Definiert den sichtbaren Ausschnitt der komplexen Zahlenebene
class Viewport():
    def __init__(self, bounds:tuple[float, float, float, float],
                 width_px:int=800, height_px:int=600):
        
        '''
        bounds: (xmin, xmax, ymin, ymax)
        width_px, height_px: Auflösung des Viewports in Pixeln
        '''

        self.bounds = bounds
        self.reset()
        self.width_px  : int    = width_px
        self.height_px : int    = height_px

#------------------------------------------------------------
# Properties: Berechnung von Breite, Höhe und Zentrum des Viewports

    @property
    def width(self) -> float:
        return self.xmax - self.xmin

    @property
    def height(self) -> float:
        return self.ymax - self.ymin

    @property
    def center(self) -> complex:
        real = 0.5 * (self.xmin + self.xmax)
        imag = 0.5 * (self.ymin + self.ymax)
        return complex(real, imag)

#------------------------------------------------------------
# Methoden

    def reset(self):
        self.xmin, self.xmax, self.ymin, self.ymax = self.bounds

    def pixel_to_complex(self, x, y) -> complex:

        # Vermeidung von Division durch Null
        width_den = max(self.width_px - 1, 1)
        height_den = max(self.height_px - 1, 1)

        real = self.xmin + (x / width_den) * (self.xmax - self.xmin)
        imag = self.ymax - (y / height_den) * (self.ymax - self.ymin)

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
        new_vp = Viewport(
            bounds=self.bounds,
            width_px=self.width_px,
            height_px=self.height_px
        )
        new_vp.xmin = self.xmin
        new_vp.xmax = self.xmax
        new_vp.ymin = self.ymin
        new_vp.ymax = self.ymax
        return new_vp