# Mapping für Fraktale
FRACTALS_MAP =  {
    "MandelbrotFractal": {
        "name": "Mandelbrot-Set",
        "desc": ("..."),
        "formula": "z_{n+1} = z_n^2 + c"
    },

    "InvertedMandelbrotFractal": {
        "name": "Inverted Mandelbrot-Set",
        "desc": ("..."),
        "formula": "z_{n+1} = z_n^2 + 1/c"
    },

    "JuliaFractal": {
        "name": "Julia-Set",
        "desc": ("..."),
        "formula": "z_{n+1} = z_n^2 + c"
    },

    "BurningShipFractal": {
        "name": "Burning Ship",
        "desc": ("..."),
        "formula": "z_{n+1} = (|Re(z_n)| + i|Im(z_n)|)^2 + c"
    },

    "TricornFractal": {
        "name": "Tricorn",
        "desc": ("..."),
        "formula": "z_{n+1} = conj(z_n)^2 + c"
    },

    "PhoenixFractal": {
        "name": "Phoenix",
        "desc": ("..."),
        "formula": "z_{n+1} = z_n^2 + c + p * z_{n-1}",
    },

    "PhoenixJuliaFractal": {
        "name": "Phoenix Julia",
        "desc": ("..."),
        "formula": "z_{n+1} = z_n^2 + c + p * z_{n-1}",
    }


}

# Mapping für Orbit-Traps
ORBIT_TRAP_MAP = {
    "point": {
        "idx": 0,
        "label": "Point"
    },

    "circle": {
        "idx": 1,
        "label": "Circle"
    },

    "horizontal_line": {
        "idx": 2,
        "label": "Horizontal Line"
    },

    "vertical_line": {
        "idx": 3,
        "label": "Vertical Line"
    },
}

# Farbpaletten
PALETTES = {

    "default": [
        (255,255,255),
        (245,235,220),
        (215,190,150),
        (170,135,95),
        (110,130,185),
        (55,75,140),
        (15,15,30)
    ],

    "fairytale": [
        (255, 255, 255),   # klarer Start (Glow)
        (245, 225, 255),   # sehr helles Lavendel
        (220, 170, 255),   # weiches Violett
        (255, 140, 220),   # leichter Rosa-Shift (unerwartet, „magisch“)
        (150, 110, 255),   # zurück ins kühle Violett
        (90, 60, 255),     # tiefer, gesättigter Kern
        (140, 200, 255),   # kühler Kontrast (bläulicher Schimmer)
        (60, 30, 180)      # dunkler Abschluss statt reinem Blau
    ],

    "fire": [
        (255, 255, 255),   # weißer Kern
        (255, 245, 200),   # heißes, leicht gelbliches Weiß
        (255, 200, 90),    # Goldton
        (255, 140, 30),    # kräftiges Orange
        (255, 90, 10),     # Flammenorange
        (200, 50, 0),      # dunkleres Rot
        (120, 20, 10),     # Glutkern
        (160, 60, 20),     # Rückkehr zu Wärme (zyklisch, Glühen)
        (80, 10, 20),      # abkühlend, violetter Stich
        (20, 0, 10)        # fast schwarz
    ],

    "ice": [
        (255, 255, 255),   # Eisweiß
        (235, 250, 255),   # kaltes Licht
        (180, 225, 255),   # klares Eisblau
        (120, 190, 245),   # tieferes Blau
        (140, 210, 255),   # Rückhellung (Reflexion, zyklisch)
        (90, 150, 230),    # wieder kühler
        (70, 110, 210),    # dichteres Blau
        (40, 70, 160),     # Tiefe
        (60, 100, 200),    # leichter Rücksprung (Schimmer)
        (10, 20, 60)       # dunkler Kern
    ],

    "forest": [
        (255, 252, 245),   # sehr helles, warmes Licht (nicht reinweiß)
        (235, 240, 210),   # blasses Blattgrün, leicht gelblich
        (190, 210, 140),   # junges Grün
        (140, 170, 100),   # mittleres Waldgrün
        (110, 120, 85),    # entsättigt, birkenrindenartig
        (120, 90, 60),     # warmes Holzbraun (wichtiger Kontrastanker)
        (70, 110, 75),     # zurück ins Grün, aber dunkler und gedämpft
        (40, 80, 70),      # feucht-kühles Waldgrün
        (20, 50, 55),      # tiefer Schatten, leicht blaugrün
        (5, 20, 25)        # fast schwarz, aber mit Farbrest
    ],

    "sunset": [
        (255,255,255),
        (255,230,200),
        (255,160,100),
        (255,90,80),
        (200,40,140),    # stärkeres Magenta
        (90,20,110),
        (20,0,50)
    ],

    "neon": [
        (255,255,255),
        (150,255,230),
        (0,255,170),
        (0,180,255),
        (150,0,255),
        (255,0,180),     # zusätzlicher Neon-Pink-Shift
        (10,5,30)
    ],

    "rainbow": [
        (255,255,255),
        (210,160,255),
        (120,120,255),
        (0,200,255),
        (0,255,150),
        (255,255,80),
        (255,150,40),
        (255,50,80)
    ],

    "baroque": [
        (255, 252, 240),   # Kerzenlicht, fast weiß, warm
        (245, 225, 170),   # gedämpftes Blattgold
        (210, 160, 80),    # tieferes Gold, erdig
        (170, 60, 60),     # Karmin (gedämpft)
        (110, 40, 80),     # Purpur, entsättigt
        (60, 50, 100),     # kühler Schatten (blauviolett)
        (140, 100, 60),    # Rückkehr zu warmem Braun/Gold (zyklisch)
        (20, 15, 35)       # tiefer Schatten, nicht rein schwarz
    ],


    "grayscale": [
        (255,255,255),
        (230,230,235),   # minimaler Blaustich
        (190,190,200),
        (140,140,150),
        (95,95,105),
        (45,45,55),
        (8,8,12)
    ]

}

# Namen der Farbmethoden
COLORING_NAMES = [
    "basic", 
    "smooth", 
    "histogram", 
    "orbit trap", 
    "hybrid", 
    "cyclic banding",
    "chess pattern"
    ]

# Mapping für GUI
GUI_MAP = {
    # Farben für GUI-Elemente
    "col_rect": "#7D7D7D",      # Zoom-Rechteck (sichtbar aber nicht aggressiv)
    "canvas_bg": "#1e1e1e",     # dunkler neutraler Hintergrund für Fraktal
    "button_bg_active": "#404040", 
    "button_bg_inactive": "#2b2b2b",
    "button_fg": "white",
    "hover_bg": "#7D7D7D",

    # Größen für GUI-Elemente
    "button_width": 5,
    "width_rect": 2,

    # Font
    "font_basic": "tahoma",
    "font_button": ("Segoe UI", 11, "bold"),

}
