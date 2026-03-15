import tkinter as tk
import numpy as np
from mapping import GUI_MAP
from PIL import Image, ImageTk
from tkinter import filedialog, Toplevel, Label, ttk
#============================================================
# Klasse für Text bei Hovern über Buttons
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display test in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x,y))
        label = Label(
            tw, text=self.text, justify="left", 
            background=GUI_MAP["hover_bg"], relief="flat",
            borderwidth=1, font=(GUI_MAP["font_basic"], "8", "normal")
        )
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

#============================================================
# Zentrale GUI
class GUI():
    def __init__(self, width=800, height=600, julia: bool = False):
        # Höhe und Breite
        self.width          = width
        self.height         = height
        self.aspect_ratio   = self.width / self.height

        # Hauptfenster
        self.root = tk.Tk()
        self.root.resizable(False, False)   # Fenster NICHT vergrößerbar 
        self.root.title("Fractal Viewer")
        self.root.configure(bg=GUI_MAP["canvas_bg"])

        # Button-Design definieren
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Modern.TButton",
            font=GUI_MAP["font_button"],
        )
        style.map(
            "Modern.TButton",
            background=[
                ("active", GUI_MAP["button_bg_active"]),
                ("!active", GUI_MAP["button_bg_inactive"])
            ],
            foreground=[
                ("!disabled", GUI_MAP["button_fg"])
            ]
        )

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

        # Für Julia-Menge und Paramter C
        self._change_c_callback = None
        self._c_select_mode = False
        self._c_callback = None
        self._mandelbrot_overlay = None

        # Cursor
        self.canvas.config(cursor="crosshair")

# ------------------------------------------------------------
# BUTTONS in der Control Bar (Zoom-Interaktion links, Farbwechsel rechts)

        # Button für Reset
        self.reset_button = ttk.Button(
            self.control_bar,
            text="⟳",
            width=GUI_MAP["button_width"],
            style="Modern.TButton",
            command=self._on_reset_clicked
        )
        self.reset_button.pack(side="left", padx=10, pady=5)
        CreateToolTip(self.reset_button, "Reset viewport")

        # Button für Schritt zurück im Zoom-Verlauf
        self.back_step_button = ttk.Button(
            self.control_bar,
            text="←",
            width=GUI_MAP["button_width"],
            style="Modern.TButton",
            command=self._on_back_step_clicked
        )
        self.back_step_button.pack(side="left", padx=10, pady=5)
        CreateToolTip(self.back_step_button, "Step back in zoom-history")

        # Button für Schritt vorwärts im Zoom-Verlauf
        self.forward_step_button = ttk.Button(
            self.control_bar,
            text="→",
            width=GUI_MAP["button_width"],
            style="Modern.TButton",
            command=self._on_forward_step_clicked
        )
        self.forward_step_button.pack(side="left", padx=10, pady=5)
        CreateToolTip(self.forward_step_button, "Step forward in zoom-history")

        # Farbpalette des Fraktals wechseln
        self.change_color_button = ttk.Button(
            self.control_bar,
            text="🎨",
            width=GUI_MAP["button_width"],
            style="Modern.TButton",
            command=self._on_change_color_clicked
        )
        self.change_color_button.pack(side="right", padx=10, pady=5)
        self.palette_menu = tk.Menu(self.root, tearoff=0, bg=GUI_MAP["button_bg_active"], fg="white")    # Farbpalette Dropdown-Menü
        CreateToolTip(self.change_color_button, "Change color palette")

        # Färbungsmethode wechseln
        self.change_coloring_button = ttk.Button(
            self.control_bar,
            text="🌈",
            width=GUI_MAP["button_width"],
            style="Modern.TButton",
            command=self._on_change_coloring_clicked
        )
        self.change_coloring_button.pack(side="right", padx=10, pady=5)
        self.coloring_menu = tk.Menu(self.root, tearoff=0, bg=GUI_MAP["button_bg_active"], fg="white")    # Färbungsmethode Dropdown-Menü
        CreateToolTip(self.change_coloring_button, "Change coloring method")

        # Als Hochauflöndes Bild speichern (exp)
        self.save_button = ttk.Button(
            self.control_bar,
            text="💾",
            width=GUI_MAP["button_width"],
            style="Modern.TButton",
            command=self._on_export_clicked
        )
        self.save_button.pack(side="right", padx=10, pady=5)
        CreateToolTip(self.save_button, "Export current view as png")

        # Für Julia: C ändern
        if julia:
            self.change_c_button = ttk.Button(
                self.control_bar,
                text="C",
                width=GUI_MAP["button_width"],
                style="Modern.TButton",
                command=self._on_change_c_clicked
            )
            self.change_c_button.pack(side="right", padx=10, pady=5)
            CreateToolTip(self.change_c_button, "Change parameter 'C'")

#------------------------------------------------------------
# VERSCHIEDENES

    def run(self):
        self.root.mainloop()

    # Bild anzeigen
    def display_image(self, pixel_array):
        image = Image.fromarray(pixel_array, "RGB")                     # numpy -> PIL
        self._photo = ImageTk.PhotoImage(image)                         # PIL -> Tkinter-Image
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo)  # Bild anzeigen

#------------------------------------------------------------
# ZOOM-FUNKTIONALITÄT

    def set_zoom_callback(self, callback):
        self._zoom_callback = callback

    def _on_mouse_press(self, event):
        self._start_x = event.x
        self._start_y = event.y

        # Für Julia-Menge: C auswählen statt Zoom
        if not self._c_select_mode:
            self._rect = self.canvas.create_rectangle(
                self._start_x,
                self._start_y,
                self._start_x,
                self._start_y,
                outline=GUI_MAP["col_rect"],
                width=GUI_MAP["width_rect"]
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
        # Für Julia-Menge: C auswählen statt Zoom
        if self._c_select_mode:     

            x = event.x
            y = event.y

            if self._c_callback:
                self._c_callback(x, y)

            self._c_select_mode = False
            return

        # Normaler Zoom-Fall
        coords = self.canvas.coords(self._rect)
        x0, y0, x1, y1 = coords

        if self._zoom_callback:
            self._zoom_callback(x0, y0, x1, y1)

        self.canvas.delete(self._rect)
        self._rect = None

#------------------------------------------------------------
# RESET-BUTTON (Zurück zu Standardansicht)

    def set_reset_callback(self, callback):
        self._reset_callback = callback

    def _on_reset_clicked(self):
        if self._reset_callback:
            if not self._c_select_mode:
                self._reset_callback()

#------------------------------------------------------------
# STEP-BUTTONS (Schritt zurück/vorwärts im Zoom-Verlauf)

    def set_back_step_callback(self, callback):
        self._back_step_callback = callback

    def _on_back_step_clicked(self):
        if self._back_step_callback:
            if not self._c_select_mode:   
                self._back_step_callback()

    def set_forward_step_callback(self, callback):
        self._forward_step_callback = callback

    def _on_forward_step_clicked(self):
        if self._forward_step_callback:
            if not self._c_select_mode:
                self._forward_step_callback()

#------------------------------------------------------------
# COLOR-BUTTON (Farbpalette und Coloring wechseln)

    def set_change_color_callback(self, callback):
        self._change_color_callback = callback

    def _on_change_color_clicked(self):
        if self._c_select_mode:
            return
        
        try:
            x = self.change_color_button.winfo_rootx()
            y = self.change_color_button.winfo_rooty() + self.change_color_button.winfo_height()
            self.palette_menu.tk_popup(x, y)
        finally:
            self.palette_menu.grab_release()

    def set_palette_menu(self, palette_names, callback):
        self.palette_menu.delete(0, "end")

        for name in palette_names:
            self.palette_menu.add_command(
                label=name,
                command=lambda n=name: callback(n)
            )

    def set_change_coloring_callback(self, callback):
        self._change_coloring_callback = callback

    def _on_change_coloring_clicked(self):
        if self._c_select_mode:
            return
        
        try:
            x = self.change_coloring_button.winfo_rootx()
            y = self.change_coloring_button.winfo_rooty() + self.change_coloring_button.winfo_height()
            self.coloring_menu.tk_popup(x, y)
        finally:
            self.coloring_menu.grab_release()

    def set_coloring_menu(self, coloring_names, callback):
        self.coloring_menu.delete(0, "end")

        for name in coloring_names:
            self.coloring_menu.add_command(
                label=name,
                command=lambda n=name: callback(n)
            )

#------------------------------------------------------------
# EXPORT-BUTTON (Hochauflösendes Bild speichern)

    def set_export_callback(self, callback):
        self._export_callback = callback

    def _on_export_clicked(self):
        if self._export_callback:
            if not self._c_select_mode:
                self._export_callback()

    def ask_save_path(self, default_name="fractal.png"):
        return filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialfile=default_name
        )

#------------------------------------------------------------
# Für JULIA-SET: C ändern

    def set_change_c_callback(self, callback):
        self._change_c_callback = callback

    def set_c_select_callback(self, callback):
        self._c_callback = callback

    def _on_change_c_clicked(self):
        self._c_select_mode = True
        if self._change_c_callback:
            self._change_c_callback()

    # Overlay
    def show_overlay(self, pixel_array, alpha=120):
        image = Image.fromarray(pixel_array, "RGB").convert("RGBA")

        overlay = np.array(image)
        overlay[:,:,3] = alpha

        image = Image.fromarray(overlay, "RGBA")

        self._mandelbrot_overlay = ImageTk.PhotoImage(image)
        self.canvas.create_image(
            0,0,
            anchor="nw",
            image=self._mandelbrot_overlay
        )

    def clear_overlay(self):
        self.canvas.delete("all")

        if self._photo:
            self.canvas.create_image(0,0,anchor="nw",image=self._photo)