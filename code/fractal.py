from abc import ABC, abstractmethod
from dataclasses import dataclass
from numba import njit
#============================================================
'''
Die Fractal-Klassen sind Blackboxes und kennen keinerlei Kontext.
Alles was sie tun ist, eine Zahl zurückzugeben.
---
ABC (Abstract Base Class) damit kein "allgemeines Fraktal" 
instanziiert wird. Es gibt nur konkrete Fraktale. Jedes konkrete
Fraktal ist als eigene Klasse definiert, die per CLI geladen werden
kann.
'''
#============================================================
# NUMBA-FUNKTION (für Performance in der Iteration)
@njit
def _mandelbrot_kernel(c_real, c_imag, max_iterations, escape_radius):
    z_real = 0.0
    z_imag = 0.0

    for i in range(max_iterations):
        # z = z^2 + c
        # (a+bi)^2 = (a^2 - b^2) + 2abi

        z_real_sq = z_real * z_real
        z_imag_sq = z_imag * z_imag

        if z_real_sq + z_imag_sq > escape_radius * escape_radius:
            return i, True, z_real, z_imag
        
        z_imag = 2.0 * z_real * z_imag + c_imag
        z_real = z_real_sq - z_imag_sq + c_real

    return max_iterations, False, z_real, z_imag

#============================================================
# KLASSE FÜR ERGEBNIS
@dataclass(frozen=True)
class IterationResult:
    iterations: int         # Anzahl duchlaufener Iterationen
    escaped: bool           # Escape-Radius überschritten?
    last_z: complex         # Letzter berechneter Wert

#============================================================
# KLASSEN FÜR FRAKTALE
class Fractal(ABC):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        self.max_iterations = max_iterations     # Wie lange prüft man, ob der Wert "ausbricht"?
        self.escape_radius = escape_radius       # Für Mandelbrot z.B. 2
        self._default_bounds = (-2.0, 1.0, -1.5, 1.5)   # zu Fraktal

    # Berechnet die Iterationszahl für einen Punkt c in der komplexen Ebene. Zentrale Kernemthode.
    @abstractmethod # muss implementiert sien
    def iterate(self, c:complex) -> IterationResult:
        pass    # bleibt leer

#------------------------------------------------------------
class MandelbrotFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)
        self._default_bounds = (-2.0, 1.0, -1.5, 1.5)   # zu Fraktal

    # Iterater: ruft njit-Funktion auf
    def iterate(self, c: complex) -> IterationResult:
        iterations, escaped, zr, zi = _mandelbrot_kernel(
            c.real,
            c.imag,
            self.max_iterations,
            self.escape_radius
        )

        return IterationResult(
            iterations=iterations,
            escaped=escaped,
            last_z=complex(zr, zi)
        )
    
#------------------------------------------------------------
class InvertedMandelbrotFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)
        self._default_bounds = (-2, 4.5, -2.4, 2.4)   # zu Fraktal

    def iterate(self, c: complex) -> IterationResult:
        # Singularität vermeiden (Division durch 0)
        if c == 0:
            c_inv = complex(1e10, 0)  # praktisch "unendlich"
        else:
            c_inv = 1 / c

        iterations, escaped, zr, zi = _mandelbrot_kernel(
            c_inv.real,
            c_inv.imag,
            self.max_iterations,
            self.escape_radius
        )

        return IterationResult(
            iterations=iterations,
            escaped=escaped,
            last_z=complex(zr, zi)
        )

#------------------------------------------------------------
class JuliaFractal(Fractal):
    def __init__(self):
        super().__init__()
        self.k : complex = 0

    # ...
