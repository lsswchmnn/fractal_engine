
#============================================================
PALETTES = {

    "default": [
        (0,0,0),
        (100,100,50),
        (255,255,255)
    ],

    "fire": [
        (0,0,0),
        (120,0,0),
        (255,80,0),
        (255,200,0),
        (255,255,255)
    ],

    "ice": [
        (0,0,0),
        (0,50,120),
        (0,150,255),
        (200,240,255),
        (255,255,255)
    ],

    "grayscale": [
        (0,0,0),
        (255,255,255)
    ]
}

#============================================================
class ColorMap():
    def __init__(self):
        self.palette_name   = ""
        self.palette        = []            # vollständige Palette
        self.set_palette("default")

#------------------------------------------------------------
# FARBPROFILE SETZEN

    # Palette als Attribut setzen
    def set_palette(self, name:str):
        if name not in PALETTES:
            raise ValueError(f"Unknown palette:  {name}")
        
        self.palette_name = name
        
        key_colors = PALETTES[name]
        self.palette = self._interpolate_palette(key_colors, 256)

#------------------------------------------------------------
# INTERPOLATION UND LOGIK

    # sauber interpolieren
    def _interpolate_palette(self, key_colors, size):
        palette = []
        segments = len(key_colors) - 1

        for i in range(size):
            t = i / (size - 1)
            pos = t * segments

            idx = int(pos)
            frac = pos - idx
            c1 = key_colors[idx]
            c2 = key_colors[min(idx + 1, segments)]

            r = int(c1[0] + frac * (c2[0] - c1[0]))
            g = int(c1[1] + frac * (c2[1] - c1[1]))
            b = int(c1[2] + frac * (c2[2] - c1[2]))

            palette.append((r, g, b))

        return palette

    # Iterationszahl in RGB-Wert umwandeln
    def map(self, iteration: int, max_iterations: int) -> tuple:
        if iteration >= max_iterations:
            return (0,0,0)  # Menge
        
        index = iteration % len(self.palette)
        return self.palette[index]