from abc import ABC, abstractmethod
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
# Abstrakte Basisklasse
class Fractal(ABC):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        self.max_iterations = max_iterations     # Wie lange prüft man, ob der Wert "ausbricht"?
        self.escape_radius = escape_radius       # Für Mandelbrot z.B. 2

    # Berechnet die Iterationszahl für einen Punkt c in der komplexen Ebene. Zentrale Kernemthode.
    @abstractmethod # muss implementiert sien
    def iterate(self, c:complex) -> int:
        pass    # bleibt leer

#============================================================^+ 
class MandelbrotFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)
    
    def iterate(self, c: complex) -> int:
        z = 0 + 0j  # Startwert ist im Mandelbrot-Set immer 0

        for iteration in range(self.max_iterations):
            z = z * z + c   # Iterationsvorschrift

            if abs(z) > self.escape_radius: # Betrag größer als Escape-Radius?
                return iteration
            
        return self.max_iterations

#------------------------------------------------------------
class JuliaFractal(Fractal):
    def __init__(self):
        super().__init__()
        self.k : complex = 0

    # ...