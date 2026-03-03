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
    "col_rect": "lightgrey",
    "canvas_bg": "#ddd",
    "button_bg": "#eee",

    # Größen für GUI-Elemente
    "button_width": 5,
}