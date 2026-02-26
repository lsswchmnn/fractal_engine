from mapping import GUI_MAP
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
#============================================================
class GUI():
    def __init__(self, width=800, height=600):
        # Höhe und Breite
        self.width          = width
        self.height         = height
        self.aspect_ratio   = self.width / self.height

        # Hauptfenster
        self.root = tk.Tk()
        self.root.resizable(False, False)   # Fenster NICHT vergrößerbar 
        self.root.title("Fractal Viewer")

        # Hauptlayout-Frames
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(fill="both", expand=True)

        self.control_bar = tk.Frame(self.main_frame, height=40, bg=GUI_MAP["canvas_bg"])
        self.control_bar.pack(fill="x", side="bottom")

        # Canvas in Frame setzen
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.width,
            height=self.height
        )
        self.canvas.pack(fill="both", expand=True)

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

# ------------------------------------------------------------
# BUTTONS in der Control Bar (Zoom-Interaktion links, Farbwechsel rechts)

        # Button für Reset
        self.reset_button = tk.Button(
            self.control_bar,
            text="⟳",
            font=("Arial", 12, "bold"),
            width=GUI_MAP["button_width"],
            bg=GUI_MAP["button_bg"],
            relief="raised",
            command=self._on_reset_clicked
        )
        self.reset_button.pack(side="left", padx=10, pady=5)

        # Button für Schritt zurück im Zoom-Verlauf
        self.back_step_button = tk.Button(
            self.control_bar,
            text="←",
            font=("Arial", 12, "bold"),
            width=GUI_MAP["button_width"],
            bg=GUI_MAP["button_bg"],
            relief="raised",
            command=self._on_back_step_clicked
        )
        self.back_step_button.pack(side="left", padx=10, pady=5)

        # Button für Schritt vorwärts im Zoom-Verlauf
        self.forward_step_button = tk.Button(
            self.control_bar,
            text="→",
            font=("Arial", 12, "bold"),
            width=GUI_MAP["button_width"],
            bg=GUI_MAP["button_bg"],
            relief="raised",
            command=self._on_forward_step_clicked
        )
        self.forward_step_button.pack(side="left", padx=10, pady=5)

        # Farbpalette des Fraktals wechseln
        self.change_color_button = tk.Button(
            self.control_bar,
            text="🎨",
            font=("Arial", 12, "bold"),
            width=GUI_MAP["button_width"],
            bg=GUI_MAP["button_bg"],
            relief="raised",
            command=self._on_change_color_clicked
        )
        self.change_color_button.pack(side="right", padx=10, pady=5)

        # Färbungsmethode wechseln
        self.change_coloring_button = tk.Button(
            self.control_bar,
            text="🌈",
            font=("Arial", 12, "bold"),
            width=GUI_MAP["button_width"],
            bg=GUI_MAP["button_bg"],
            relief="raised",
            command=self._on_change_coloring_clicked
        )
        self.change_coloring_button.pack(side="right", padx=10, pady=5)

# ------------------------------------------------------------
# VERSCHIEDENES

    def run(self):
        self.root.mainloop()

    # Bild anzeigen
    def display_image(self, pixel_array):
        image = Image.fromarray(pixel_array, "RGB")                     # numpy -> PIL
        self._photo = ImageTk.PhotoImage(image)                         # PIL -> Tkinter-Image
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo)  # Bild anzeigen

# ------------------------------------------------------------
# ZOOM-FUNKTIONALITÄT

    def set_zoom_callback(self, callback):
        self._zoom_callback = callback

    def _on_mouse_press(self, event):
        self._start_x = event.x
        self._start_y = event.y
        self._rect = self.canvas.create_rectangle(
            self._start_x,
            self._start_y,
            self._start_x,
            self._start_y,
            outline=GUI_MAP["col_rect"],
            width=3.0
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
# RESET-BUTTON (Zurück zu Standardansicht)

    def set_reset_callback(self, callback):
        self._reset_callback = callback

    def _on_reset_clicked(self):
        if self._reset_callback:
            self._reset_callback()

# ------------------------------------------------------------
# STEP-BUTTONS (Schritt zurück/vorwärts im Zoom-Verlauf)

    def set_back_step_callback(self, callback):
        self._back_step_callback = callback

    def _on_back_step_clicked(self):
        if self._back_step_callback:
            self._back_step_callback()

    def set_forward_step_callback(self, callback):
        self._forward_step_callback = callback

    def _on_forward_step_clicked(self):
        if self._forward_step_callback:
            self._forward_step_callback()

#------------------------------------------------------------
# COLOR-BUTTON (Farbpalette und Coloring wechseln)

    def set_change_color_callback(self, callback):
        self._change_color_callback = callback

    def _on_change_color_clicked(self):
        if self._change_color_callback:
            self._change_color_callback()

    def set_change_coloring_callback(self, callback):
        self._change_coloring_callback = callback

    def _on_change_coloring_clicked(self):
        if self._change_coloring_callback:
            self._change_coloring_callback()