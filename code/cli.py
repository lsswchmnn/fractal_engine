from utils import print_heading, enter_continue, clear_cli, print_thin_separation, show_error
from fractal import MandelbrotFractal, JuliaFractal
from visualize import Visualizer
from mapping import FRACTALS_MAP
from color import PALETTES
import fractal
#============================================================
class CLI():
    def __init__(self):
        self.fractal                 = None
        self.visualizer              = None
        self.fractal_loaded : bool   = False
        self.fractal_name   : str    = None     # Name für Anzeige

#------------------------------------------------------------
# HAUPTMENÜ

    def run(self):
        while True:
            print_heading("FRACTAL-SIMULATION")
            print(f"Current Fractal: {self.fractal_name if self.fractal_name else "None"}\n")
            print("1 - Load fractal")
            print("2 - Start visualizer")
            print("H - Help")
            print("S - Settings")
            print("C - Close program")
            print_thin_separation(linebreak=False)
            choice = input("> ").lower().strip()

            if choice == "1":
                self.menu_load_fractal()
                continue

            elif choice == "2":
                if not self.fractal:
                    show_error(True, "AttributeError", "No Fractal loaded.")
                    continue

                self.menu_visualize()
                continue

            elif choice == "h":
                self.menu_help()
                continue

            elif choice == "s":
                if not self.fractal:
                    show_error(True, "AttributeError", "No Fractal loaded.")

                self.menu_settings()
                continue

            elif choice == "c":
                clear_cli()
                enter_continue("Press enter to leave the program", seperation=True)
                clear_cli()
                print("Goodbye!\n")
                break

            else:
                continue

#------------------------------------------------------------
# UNTERMENÜS

    # Menüpunkt 1: Fraktal als Instanz laden
    def menu_load_fractal(self):
        while True:
            print_heading("LOAD FRACTAL")
            
            keys = list(FRACTALS_MAP.keys())

            print("Choose Fractal:")
            for i, key in enumerate(keys, start=1):
                meta = FRACTALS_MAP[key]
                print(f"{i} - {meta['name']}")

            print("C - Cancel")
            print_thin_separation(linebreak=False)
            choice = input("> ").strip().lower()

            if choice == "c":
                return
            
            try:
                idx = int(choice)
            except:
                show_error(True, "InputError", "Input must be 'C' or Integer")
                continue

            if 1 <= idx <= len(keys):
                class_name = keys[idx - 1]

                try:
                    name_class = getattr(fractal, class_name)
                    self.fractal = name_class()
                except AttributeError:
                    show_error(True, "TransitionError", f"Function {class_name} not found in Dictionary.")
                    continue

            self.visualizer = Visualizer(self.fractal)  # Visualizer bereits hier erstellen
            self.fractal_name = class_name

            print_heading("FRACTAL LOADED")
            enter_continue(f"Fractal {class_name} loaded. Press enter to continue.", seperation=False)
            return

    # Menüpunkt 2: Fraktal graphisch visualisieren | Visualizer bereit in load_fractal instanziiert
    def menu_visualize(self):
        clear_cli()
        print()
        self.visualizer.start()    # CLI startet nur das Visualisierungfenster und spielt danach keine aktive Rolle mehr.
        clear_cli()
        return
    
    # Menü: Hilfe
    def menu_help(self):
        print_heading("HELP MENU")
        print("...")

        enter_continue("Press enter to return to main menu.")

    # Menü: Einstellungen
    def menu_settings(self):
        while True:
            print_heading("SETTINGS")
            print("1 - Color settings")
            print("C - Close")
            print_thin_separation(linebreak=False)
            choice = input("> ").strip().lower()

            if choice == "1":
                self.cli_load_palette()
                continue

            elif choice == "c":
                break

#------------------------------------------------------------
# EINSTELLUNGEN

    def cli_load_palette(self):
        while True:
            print_heading("LOAD PALETTE")

            keys = list(PALETTES.keys())

            print("Choose Palette:")
            for i, key in enumerate(keys, start=1):
                print(f"{i} - {key}")

            print("C - Cancel")
            print_thin_separation(linebreak=False)
            choice = input("> ").strip().lower()

            if choice == "c":
                return
            
            try:
                idx = int(choice)
            except:
                show_error(True, "InputError", "Input must be 'C' or Integer")
                continue

            if 1 <= idx <= len(keys):
                name = keys[idx - 1]

                try:
                    self.visualizer.colormap.set_palette(f"{name}")
                except ValueError as e:
                    show_error(True, "TransitionError", f"{e}")
                    continue

            return