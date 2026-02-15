from color import ColorMap
from gui import GUI
#============================================================
'''
Der Visualizer orchestriert nur. Er ist kein Renderer und keine GUI, 
sondern Session-Controller.

Visualizer erzeugt ein Pixelraster, welches die komplexe Zahlenebene repräsentiert.
Für jeden Punkt wird fractal.iterate aufgerufen und anhand der Anzahl an Iterationen 
Der Punkt eingefärbt.
'''
class Visualizer():
    def __init__(self):
        self.renderer   : Renderer    = Renderer()
        self.colormap   : ColorMap    = ColorMap()
        self.gui        : GUI         = GUI()

    def start(self, fractal):
        pass

#============================================================
'''
Die Komponente, die wirklich rechnet und anhand des vom User definierten
Ausschnittes das Fraktal berechnet.
'''
class Renderer():
    def __init__(self):
        pass