from utils import print_heading, enter_continue, clear_cli, print_thin_separation, show_error
from fractal import MandelbrotFractal, JuliaFractal
from visualize import Visualizer
from mapping import FRACTALS_MAP
#from color import PALETTES
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
            if self.fractal:
                print("2 - Start visualizer")
                print("S - Settings")
            print("H - Help")
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
                print("Goodbye!")
                print_thin_separation()
                print()
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

            self.fractal_name = class_name
            self.visualizer = Visualizer(self.fractal, self.fractal_name)  # Visualizer bereits hier erstellen

            print_heading("FRACTAL LOADED")
            enter_continue(f"Fractal {class_name} loaded. Press enter to continue.", seperation=False)
            return

    # Menüpunkt 2: Fraktal graphisch visualisieren (Visualizer bereit in load_fractal instanziiert)
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
            print("1 - Manipulate Formula")
            print("2 - Rendering settings")
            print("C - Close")
            print_thin_separation(linebreak=False)
            choice = input("> ").strip().lower()

            if choice == "1":
                self.cli_manipulate_formula()
                continue

            elif choice == "2":
                self.cli_change_rendering_settings()
                continue

            elif choice == "c":
                break

#------------------------------------------------------------
# EINSTELLUNGEN

    def cli_manipulate_formula(self):
        if self.fractal_name == "MandelbrotFractal" or self.fractal_name == "InvertedMandelbrotFractal" or self.fractal_name == "BurningShipFractal":

            while True:
                print_heading("MANIPULATE FORMULA")
                print(f"Current formula: {FRACTALS_MAP[self.fractal_name]['formula']}")
                print("\nAvailable manipulations:")
                print("1 - Change startvalue")
                print("2 - Change exponent")
                print("C - Cancel")
                print_thin_separation(linebreak=False)
                choice = input("> ").strip().lower()

                if choice == "1":
                    print_heading("CHANGE STARTVALUE")
                    print(f"Current startvalue: z0 = {self.fractal.start_real} + {self.fractal.start_imag}i\n")
                    print("Recommended: Startvalue close to the critical point (0 for Mandelbrot) for more interesting results, but feel free to experiment!\n")

                    try:
                        real = float(input("Enter real part of startvalue z0: "))
                        imag = float(input("Enter imaginary part of startvalue z0: "))
                        self.fractal.start_real = real
                        self.fractal.start_imag = imag
                        enter_continue(f"Startvalue changed to z0 = {real} + {imag}i. Press enter to continue.", seperation=False)

                    except ValueError:
                        show_error(True, "InputError", "Invalid input. Please enter valid numbers.")
                        continue
                
                elif choice == "2":
                    pass

                elif choice == "c":
                    break

    def cli_change_rendering_settings(self):
        while True:

            print_heading("CHANGE RENDERING SETTINGS")
            print("1 - Change base Iterations")
            print("2 - Change factor for adaptive iteration depth (k)")
            print("H - Help")
            print("C - Cancel")
            print_thin_separation(linebreak=False)
            choice = input("> ").strip().lower()

            if choice == "1":
                print_heading("CHANGE BASE ITERATIONS")
                print(f"Current base iterations: {self.fractal.max_iterations}\n")
                try:
                    max_iter = int(input("Enter new base iterations: "))
                    self.fractal.max_iterations = max_iter
                    enter_continue(f"Base iterations changed to {max_iter}. Press enter to continue.", seperation=False)
                except ValueError:
                    show_error(True, "InputError", "Invalid input. Please enter a valid number.")
                    continue

            elif choice == "2":
                print_heading("CHANGE ADAPTIVE ITERATION FACTOR")
                print(f"Current adaptive iteration factor k: {self.visualizer.iterate_factor_k}\n")
                try:
                    k = int(input("Enter new adaptive iteration factor k: "))
                    self.visualizer.iterate_factor_k = k
                    enter_continue(f"Adaptive iteration factor changed to {k}. Press enter to continue.", seperation=False)
                except ValueError:
                    show_error(True, "InputError", "Invalid input. Please enter a valid number.")
                    continue

            elif choice == "h":
                print_heading("HELP - RENDERING SETTINGS")
                print("Base iterations: Number of iterations used as a baseline for the adaptive iteration depth.")
                print("Adaptive iteration factor (k): Tuning for quantitative improvement of detail accuracy at strong zooms. Higher k means more iterations added as you zoom in.")
                enter_continue("Press enter to return to settings menu.", seperation=False)

            elif choice == "c":
                break