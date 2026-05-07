
#============================================================
# VIEWPORT: Definiert den sichtbaren Ausschnitt der komplexen Zahlenebene
class Viewport():
    def __init__(self, center_real, center_imag, width,
                 width_px:int=800, height_px:int=600):
        
        '''
        bounds: (xmin, xmax, ymin, ymax)
        width_px, height_px: Auflösung des Viewports in Pixeln
        '''

        self.center_real = center_real
        self.center_imag = center_imag
        self.width = width

        self.width_px  : int    = width_px
        self.height_px : int    = height_px

#------------------------------------------------------------
# Properties: Berechnung von Breite, Höhe und Zentrum des Viewports

    @property
    def aspect(self) -> float:
        return self.width_px / self.height_px

    @property
    def height(self) -> float:
        return self.width / self.aspect

    @property
    def xmin(self):
        return self.center_real - self.width / 2

    @property
    def xmax(self):
        return self.center_real + self.width / 2

    @property
    def ymin(self):
        return self.center_imag - self.height / 2

    @property
    def ymax(self):
        return self.center_imag + self.height / 2

    @property
    def bounds(self):
        return (self.xmin, self.xmax, self.ymin, self.ymax)

    @property
    def center(self):
        return self.center_real, self.center_imag

#------------------------------------------------------------
# Setzen der Eigenschaften des Viewports

    def set_center(self, real, imag):
        self.center_real = real
        self.center_imag = imag

    def set_zoom(self, width):
        self.width = width

#------------------------------------------------------------
# Methoden zur Umrechnung von Pixelkoordinaten in komplexe Zahlen und zum Zoomen

    def pixel_to_complex(self, x, y) -> complex:
        dx = self.width / max(self.width_px - 1, 1)
        dy = self.height / max(self.height_px - 1, 1)

        real = self.xmin + x * dx
        imag = self.ymax - y * dy

        return complex(real, imag)

    def zoom_to_pixels(self, x0, y0, x1, y1):
        x_min_px = min(x0, x1)
        x_max_px = max(x0, x1)
        y_min_px = min(y0, y1)
        y_max_px = max(y0, y1)

        c1 = self.pixel_to_complex(x_min_px, y_min_px)
        c2 = self.pixel_to_complex(x_max_px, y_max_px)

        self.center_real = (c1.real + c2.real) / 2
        self.center_imag = (c1.imag + c2.imag) / 2

        self.width = abs(c2.real - c1.real)

    def copy(self):
        return Viewport(
            center_real=self.center_real,
            center_imag=self.center_imag,
            width=self.width,
            width_px=self.width_px,
            height_px=self.height_px
        )

# ------------------------------------------------------------
# Speichern / Laden

    def to_dict(self) -> dict:
        return {
            "center_real": self.center_real,
            "center_imag": self.center_imag,
            "width": self.width,
            "width_px": self.width_px,
            "height_px": self.height_px
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Viewport":
        return cls(
            center_real=data["center_real"],
            center_imag=data["center_imag"],
            width=data["width"],
            width_px=data["width_px"],
            height_px=data["height_px"]
        )
