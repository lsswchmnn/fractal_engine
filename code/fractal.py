from abc import ABC, abstractmethod
from dataclasses import dataclass
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

    # Berechnet die Iterationszahl für einen Punkt c in der komplexen Ebene. Zentrale Kernemthode.
    @abstractmethod # muss implementiert sien
    def iterate(self, c:complex) -> IterationResult:
        pass    # bleibt leer

#------------------------------------------------------------
class MandelbrotFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)
    
    # Ergebnis als Instanz von 
    def iterate(self, c: complex) -> int:
        z = 0 + 0j  # Startwert ist im Mandelbrot-Set immer 0

        for iteration in range(self.max_iterations):
            z = z * z + c   # Iterationsvorschrift

            if abs(z) > self.escape_radius: # Betrag größer als Escape-Radius?
                return IterationResult(
                    iterations=iteration,
                    escaped=True,
                    last_z=z
                )
            
        return IterationResult(
            iterations=self.max_iterations,
            escaped=False,
            last_z=z
        )

#------------------------------------------------------------
class JuliaFractal(Fractal):
    def __init__(self):
        super().__init__()
        self.k : complex = 0

    # ...

