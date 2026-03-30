
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