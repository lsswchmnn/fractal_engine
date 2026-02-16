import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
#============================================================
'''
GUI soll ein Fenster erzeugen, in dem das Fraktal abgebildet ist.
Der Nutzer kann nun ein Fenster ziehen, um den Ausschnitt zu ver-
kleinern. Anschließend wird das Bild neu berechnet.
'''
class GUI():
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height

        # Hauptfenster
        self.root = tk.Tk()
        self.root.title("Fractal Viewer")

        # Canvas
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()

        # Referenz auf das aktuelle Bild
        self._photo = None

# ------------------------------------------------------------

    def display_image(self, pixel_array):
        image = Image.fromarray(pixel_array, "RGB")                     # numpy -> PIL
        self._photo = ImageTk.PhotoImage(image)                         # PIL -> Tkinter-Image
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo)  # Bild anzeigen

    def run(self):
        self.root.mainloop()
