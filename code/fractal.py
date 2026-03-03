from abc import ABC, abstractmethod
from dataclasses import dataclass
from numba import njit
import numpy as np
#============================================================
# ITERATIONSKERNELS (eigentliche Berechnungen, in den Fraktal-Klassen aufgerufen)
@njit
def mandelbrot_kernel(c_real, c_imag, max_iterations, escape_radius, z_real=0.0, z_imag=0.0):
    """
    Berechnet die Iterationszahl für c = c_real + i*c_imag.
    Liefert float-Iteration, escaped (0/1), last_z_real, last_z_imag
    """
    escape_sq = escape_radius * escape_radius
    zr = z_real
    zi = z_imag

    for i in range(max_iterations):
        zr2 = zr * zr
        zi2 = zi * zi

        if zr2 + zi2 > escape_sq:
            return float(i), 1, zr, zi

        temp_zr = zr2 - zi2 + c_real
        zi = 2.0 * zr * zi + c_imag
        zr = temp_zr

    return float(max_iterations), 0, zr, zi

@njit
def inverted_mandelbrot_kernel(c_real, c_imag, max_iterations, escape_radius, z_real=0.0, z_imag=0.0):
    """
    Inverted Mandelbrot:
    Iteriert z_{n+1} = z_n^2 + 1/c
    c_real, c_imag : Re/Im Teil des aktuellen Pixelpunkts
    z_real, z_imag : optionaler Startwert
    """
    # Singularität vermeiden: c=0 → sehr großer Wert
    if c_real == 0.0 and c_imag == 0.0:
        c_real, c_imag = 1e10, 0.0

    # Startwerte
    z_real = z_real
    z_imag = z_imag

    # Berechnung
    escape_sq = escape_radius * escape_radius

    for i in range(max_iterations):
        # z^2
        zr2 = z_real * z_real
        zi2 = z_imag * z_imag

        # Abbruch
        if zr2 + zi2 > escape_sq:
            return i, True, z_real, z_imag

        # z = z^2 + 1/c
        # 1/c = (a - bi)/(a^2 + b^2)
        denom = c_real * c_real + c_imag * c_imag
        c_inv_real = c_real / denom
        c_inv_imag = -c_imag / denom

        # Iteration
        z_imag = 2.0 * z_real * z_imag + c_inv_imag
        z_real = zr2 - zi2 + c_inv_real

    return max_iterations, False, z_real, z_imag

@njit
def burning_ship_kernel(c_real, c_imag, max_iter, escape_radius, z_real=0.0, z_imag=0.0):
    zr = z_real
    zi = z_imag
    escape_sq = escape_radius * escape_radius

    for i in range(max_iter):
        # Betrag auf Real- und Imaginärteil anwenden
        zr_abs = abs(zr)
        zi_abs = abs(zi)

        # (a + ib)^2 = (a^2 - b^2) + 2ab i
        zr_new = zr_abs * zr_abs - zi_abs * zi_abs + c_real
        zi_new = 2.0 * zr_abs * zi_abs + c_imag

        zr = zr_new
        zi = zi_new

        if zr * zr + zi * zi > escape_sq:
            return i, True, zr, zi

    return max_iter, False, zr, zi

@njit
def tricorn_kernel(c_real, c_imag, max_iter, escape_radius, z_real=0.0, z_imag=0.0):
    zr = z_real
    zi = z_imag
    escape_sq = escape_radius * escape_radius

    for i in range(max_iter):
        # komplexe Konjugation: z -> z_bar
        zr_conj = zr
        zi_conj = -zi

        # (a + ib)^2 = a^2 - b^2 + i*2ab
        zr_new = zr_conj * zr_conj - zi_conj * zi_conj + c_real
        zi_new = 2.0 * zr_conj * zi_conj + c_imag

        zr = zr_new
        zi = zi_new

        if zr * zr + zi * zi > escape_sq:
            return i, True, zr, zi

    return max_iter, False, zr, zi


#============================================================
# KLASSE FÜR ERGEBNIS
@dataclass(frozen=True)
class IterationResult:
    iterations: int         # Anzahl duchlaufener Iterationen
    escaped: bool           # Escape-Radius überschritten?
    z_real: float           # Realteil des letzten berechneten Wertes
    z_imag: float           # Imaginärteil des letzten berechneten Wertes

#============================================================
# KLASSEN FÜR FRAKTALE
class Fractal(ABC):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        self.max_iterations = max_iterations                # Wie lange prüft man, ob der Wert "ausbricht"?
        self.escape_radius = escape_radius                  # Für Mandelbrot z.B. 2
        self._default_bounds = (-2.0, 1.0, -1.2, 1.2)       # Standard-Ausschnitt der komplexen Ebene, mit dem gearbeitet wird. Kann von Fraktal zu Fraktal unterschiedlich sein.
        self.start_real = 0.0
        self.start_imag = 0.0

    # Berechnet die Iterationszahl für einen Punkt c in der komplexen Ebene. Zentrale Kernemthode.
    @abstractmethod # muss implementiert sien
    def iterate(self, c:complex) -> IterationResult:
        pass    # bleibt leer

#------------------------------------------------------------
class MandelbrotFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)
        self._default_bounds = (-2.0, 1.0, -1.2, 1.2)
        self.start_real = 0.0
        self.start_imag = 0.0

    # Iterater: ruft njit-Funktion auf
    def iterate(self, c: complex) -> IterationResult:
        iterations, escaped, zr, zi = mandelbrot_kernel(
            c.real,
            c.imag,
            self.max_iterations,
            self.escape_radius,
            z_imag=self.start_imag,
            z_real=self.start_real
        )

        return IterationResult(
            iterations=iterations,
            escaped=escaped,
            z_imag=zi,
            z_real=zr
        )
    
#------------------------------------------------------------
class InvertedMandelbrotFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)
        self._default_bounds = (-2, 4.5, -2.4, 2.4)   # zu Fraktal
        self.start_real = 0.0
        self.start_imag = 0.0

    def iterate(self, c: complex) -> IterationResult:
        # Singularität vermeiden (Division durch 0)
        if c == 0:
            c_inv = complex(1e10, 0)  # praktisch "unendlich"
        else:
            c_inv = 1 / c

        iterations, escaped, zr, zi = mandelbrot_kernel(
            c_inv.real,
            c_inv.imag,
            self.max_iterations,
            self.escape_radius,
            z_real=self.start_real,
            z_imag=self.start_imag
        )

        return IterationResult(
            iterations=iterations,
            escaped=escaped,
            z_real=zr,
            z_imag=zi
        )

#------------------------------------------------------------
class JuliaFractal(Fractal):
    def __init__(self):
        super().__init__()
        self.k : complex = 0

    # ...
#------------------------------------------------------------
class BurningShipFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)
        self._default_bounds = (-2.2, 1.2, -2.5, 1.5)
        self.start_real = 0.0
        self.start_imag = 0.0

    def iterate(self, c: complex) -> IterationResult:
        iterations, escaped, zr, zi = burning_ship_kernel(
            c.real,
            c.imag,
            self.max_iterations,
            self.escape_radius,
            z_real=self.start_real,
            z_imag=self.start_imag
        )

        return IterationResult(
            iterations=iterations,
            escaped=escaped,
            z_real=zr,
            z_imag=zi
        )
    
#------------------------------------------------------------
class TricornFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)

        # Typische sinnvolle Bounds für Tricorn
        self._default_bounds = (-2.0, 2.0, -1.5, 1.5)

        self.start_real = 0.0
        self.start_imag = 0.0

    def iterate(self, c: complex) -> IterationResult:
        iterations, escaped, zr, zi = tricorn_kernel(
            c.real,
            c.imag,
            self.max_iterations,
            self.escape_radius,
            z_real=self.start_real,
            z_imag=self.start_imag
        )

        return IterationResult(
            iterations=iterations,
            escaped=escaped,
            z_real=zr,
            z_imag=zi
        )