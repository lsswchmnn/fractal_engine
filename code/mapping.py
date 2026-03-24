#------------------------------------------------------------
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

}

#------------------------------------------------------------
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

    "line": {
        "idx": 2,
        "label": "Line"
    }
}

#------------------------------------------------------------
# Farbpaletten
PALETTES = {

    "default": [
        (255,255,255),
        (245,235,220),
        (215,190,150),
        (170,135,95),
        (110,130,185),   # leichter Kaltkontrast
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
        (255,255,255),
        (255,240,180),
        (255,170,40),
        (255,80,10),
        (180,20,0),
        (90,0,20),       # dunkles Rot-Violett statt nur Braun
        (15,0,10)
    ],

    "ice": [
        (255,255,255),
        (220,245,255),
        (150,210,255),
        (80,170,230),
        (90,110,220),    # leichter Blau-Violett-Shift
        (30,40,140),
        (5,10,40)
    ],

    "forest": [
        (255,255,255),
        (210,235,200),
        (130,190,110),
        (60,140,80),
        (30,100,90),     # mehr Türkis im Schatten
        (10,55,60),
        (0,15,20)
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
        (255,255,255),
        (255,245,220),   # warmes Kerzenlicht / Elfenbein
        (240,210,120),   # Blattgold
        (200,60,60),     # Karminrot
        (120,30,90),     # Purpur
        (40,60,160),     # Ultramarin
        (10,100,70),     # Smaragdgrün
        (8,6,20)         # tiefer barocker Schatten
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

#------------------------------------------------------------
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