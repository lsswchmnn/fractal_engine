from mapping import COLOR_MAP
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
#============================================================
'''
GUI soll ein Fenster erzeugen, in dem das Fraktal abgebildet ist.
Der Nutzer kann nun ein Fenster ziehen, um den Ausschnitt zu ver-
kleinern. Anschließend wird das Bild neu berechnet.
'''
class GUI():
    def __init__(self, width=800, height=600):
        # Höhe und Breite
        self.width          = width
        self.height         = height
        self.aspect_ratio   = self.width / self.height

        # Hauptfenster
        self.root = tk.Tk()
        self.root.title("Fractal Viewer")

        # Canvas
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()

        # Referenz auf das aktuelle Bild
        self._photo = None

        # Für Zoom-Funktionalität
        self._zoom_callback     = None
        self._rect              = None
        self._start_x           = None
        self._start_y           = None

        self.canvas.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)

        self._reset_callback = None

        # Button für Reset
        self.reset_button = tk.Button(
            self.root,
            text="⟳",
            font=("Arial", 12, "bold"),
            width=3,
            bg="white",
            relief="raised",
            command=self._on_reset_clicked
        )

        self.reset_button.place(
            relx=1.0,
            rely=0.0,
            anchor="ne",
            x=-10,
            y=10
        )

# ------------------------------------------------------------
# VERSCHIEDENES

    def run(self):
        self.root.mainloop()

    # Bild anzeigen
    def display_image(self, pixel_array):
        image = Image.fromarray(pixel_array, "RGB")                     # numpy -> PIL
        self._photo = ImageTk.PhotoImage(image)                         # PIL -> Tkinter-Image
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo)  # Bild anzeigen

    def set_zoom_callback(self, callback):
        self._zoom_callback = callback

# ------------------------------------------------------------
# EVENT-METHODEN (Zoom-Funktinonalität)

    def _on_mouse_press(self, event):
        self._start_x = event.x
        self._start_y = event.y
        self._rect = self.canvas.create_rectangle(
            self._start_x,
            self._start_y,
            self._start_x,
            self._start_y,
            outline=COLOR_MAP["col_rect"],
            width=5.0
        )

    def _on_mouse_drag(self, event):
        dx = event.x - self._start_x
        dy = event.y - self._start_y

        # Richtung merken
        sign_x = 1 if dx >= 0 else -1
        sign_y = 1 if dy >= 0 else -1

        dx = abs(dx)
        dy = abs(dy)

        # Aspect Ratio erzwingen
        if dx / self.aspect_ratio > dy:
            dy = dx / self.aspect_ratio
        else:
            dx = dy * self.aspect_ratio

        end_x = self._start_x + sign_x * dx
        end_y = self._start_y + sign_y * dy

        self.canvas.coords(
            self._rect,
            self._start_x,
            self._start_y,
            end_x,
            end_y
        )

    def _on_mouse_release(self, event):
        coords = self.canvas.coords(self._rect)
        x0, y0, x1, y1 = coords

        if self._zoom_callback:
            self._zoom_callback(x0, y0, x1, y1)

        self.canvas.delete(self._rect)
        self._rect = None

# ------------------------------------------------------------
# BUTTON (Zurück zu Standardansicht)

    def set_reset_callback(self, callback):
        self._reset_callback = callback

    def _on_reset_clicked(self):
        if self._reset_callback:
            self._reset_callback()