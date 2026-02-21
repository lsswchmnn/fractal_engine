from fractal import IterationResult
import math
#============================================================
PALETTES = {

    "default": [ 
        (255, 255, 255),    # Erste Farbe IMMER weiß für Hintergrund
        (180, 200, 255), 
        (50, 80, 200), 
        (0, 0, 0) ], 

    "fire": [
        (255, 255, 255),
        (255, 170, 60),
        (220, 60, 0),
        (40, 0, 0)
    ],

    "ice": [
        (255, 255, 255),
        (180, 230, 255),
        (70, 150, 220),
        (0, 30, 80)
    ],

    "forest": [
        (255, 255, 255),
        (140, 210, 140),
        (40, 120, 60),
        (0, 30, 10)
    ],

    "sunset": [
        (255, 255, 255),
        (255, 160, 120),
        (200, 70, 140),
        (30, 0, 40)
    ],

    "neon": [
        (255, 255, 255),
        (0, 255, 200),
        (180, 0, 255),
        (10, 10, 20)
    ],

    "rainbow": [
        (255, 255, 255),
        (138, 43, 226), # violett
        (28,134,238),  # blau
        (0,191,255), # Indigo
        (0, 238, 118), # Grün
        (238,201,0), # gelb
        (255,127,0), # Orange
        (255,127,80) # rot
    ],

    "grayscale": [
        (255, 255, 255),
        (211, 211, 211),
        (3, 3, 3)
    ]
}
#============================================================
class ColorMap():
    def __init__(self):
        self.palette_name   = "default"
        self.palette        = []            # vollständige Palette
        self.set_palette("default")

#------------------------------------------------------------
# FARBPROFILE UND PALETTE

    # Palette als Attribut setzen
    def set_palette(self, name:str):
        if name not in PALETTES:
            raise ValueError(f"Unknown palette:  {name}")
        
        self.palette_name = name
        
        key_colors = PALETTES[name]
        self.palette = self._interpolate_palette(key_colors, 256)

    # Kontinuierliches Palette-Sampling
    def _sample_palette(self, t: float) -> tuple:
        t = max(0.0, min(1.0, t))

        pos = t * (len(self.palette) - 1)
        idx = int(pos)
        frac = pos - idx

        c1 = self.palette[idx]
        c2 = self.palette[min(idx+1, len(self.palette) - 1)]

        r = int(c1[0] + frac * (c2[0] - c1[0]))
        g = int(c1[1] + frac * (c2[1] - c1[1]))
        b = int(c1[2] + frac * (c2[2] - c1[2]))

        return (r, g, b)

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
    def map(self, result: IterationResult, max_iterations: int) -> tuple:
        if not result.escaped:
            return (0,0,0)
        
        smooth_value = self._compute_smooth_value(result)   # Smooth iteration count
        normalized = smooth_value / max_iterations          # Normalisierung auf [0,1]
        return self._sample_palette(normalized)             # Palette kontinuierlich abtasten

    # Smooth-Wert berechnen
    def _compute_smooth_value(self, result: IterationResult) -> float:
        z = result.last_z
        modulus = abs(z)

        if modulus == 0:
            return float(result.iterations)
        
        return (
            result.iterations
            + 1
            - math.log(math.log(modulus)) / math.log(2)
        )