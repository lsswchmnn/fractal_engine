from utils import print_heading, enter_continue, clear_cli, print_thin_separation, show_error
from visualize import Visualizer
from mapping import FRACTALS_MAP
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
            print(f"Current Fractal: {self.fractal._name if self.fractal else "None"}\n")
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
            
            # Lesbare Namen und Formeln aus Mapping
            self.fractal._name = FRACTALS_MAP[class_name]["name"]
            self.fractal._formula = FRACTALS_MAP[class_name]["formula"]

            self.visualizer = Visualizer(self.fractal, self.fractal._name)  # Visualizer erstellen

            print_heading("FRACTAL LOADED")
            enter_continue(f"Fractal {class_name} loaded. Press enter to continue.", seperation=False)
            return

    # Menüpunkt 2: Fraktal graphisch visualisieren (Visualizer bereit in load_fractal instanziert)
    def menu_visualize(self):
        clear_cli()
        print()
        self.visualizer.start()
        clear_cli()
        return
    
    # Menü: Hilfe
    def menu_help(self):
        print_heading("HELP MENU")
        print(
            "This program allows you to load and visualize different types of fractals, " \
            "as well as manipulate the underlying formula and rendering settings for more customized results." \
            "\n" \
            "Fractals are complex mathematical sets that exhibit self-similarity and intricate patterns at every scale. " \
            "The Mandelbrot set, for example, is defined by iterating the formula z = z^2 + c, where z and c are complex " \
            "numbers. By changing the parameters of this formula, you can create a wide variety of fractal images." 
        )

        enter_continue("Press enter to return to main menu.")

    # Menü: Einstellungen
    def menu_settings(self):
        while True:
            print_heading("SETTINGS")
            print("1 - Manipulate Formula")
            print("2 - Rendering settings")
            print("H - Help")
            print("C - Close")
            print_thin_separation(linebreak=False)
            choice = input("> ").strip().lower()

            if choice == "1":
                self.cli_manipulate_formula()
                continue

            elif choice == "2":
                self.cli_change_rendering_settings()
                continue

            elif choice == "h":
                print_heading("HELP - SETTINGS")
                print("Manipulate Formula: Change the start value and exponent used in the fractal formula. Note that non-standard settings can lead to very different and often less stable fractals, especially for complex exponents.")
                print()
                print("Rendering settings: Adjust the base number of iterations and the adaptive iteration factor k, which controls how many additional iterations are added as you zoom in. Higher k can improve detail accuracy at strong zooms but also increases rendering time.")
                enter_continue("Press enter to return to settings menu.")

            elif choice == "c":
                break

#------------------------------------------------------------
# EINSTELLUNGEN

    # Einstellungen: Formelmanipulation (Startwert und Exponent)
    def cli_manipulate_formula(self):
        if self.fractal._name is not None:  # später Einschränkung, falls manche Fraktale bestimmte Manipulationen nicht unterstützen

            while True:
                print_heading("MANIPULATE FORMULA")
                print(f"Current formula: {self.fractal._formula}")
                print("\nAvailable manipulations:")
                print("1 - Change startvalue")
                print("2 - Change exponent")
                print("H - Help")
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

                    # Warnungen für potenziell instabile Einstellungen
                    if imag != 0 or real != 2:
                        self.cli_settings_warning(imag, real, "startvalue")
                        break
                
                elif choice == "2":
                    print_heading("CHANGE EXPONENT")
                    print(f"Current exponent: {self.fractal.exp_real} + {self.fractal.exp_imag}i\n")
                    print("Note: Changing the exponent can lead to very different and often less stable fractals, especially for non-integer or complex exponents. Experiment with caution!\n")

                    try:
                        real = float(input("Enter real part of exponent: "))
                        imag = float(input("Enter imaginary part of exponent: "))
                        self.fractal.exp_real = real
                        self.fractal.exp_imag = imag
                        enter_continue(f"Exponent changed to {real} + {imag}i. Press enter to continue.", seperation=False)

                    except ValueError:
                        show_error(True, "InputError", "Invalid input. Please enter valid numbers.")
                        continue

                    # Warnungen für potenziell instabile Einstellungen
                    if imag != 0 or real != 2:
                        self.cli_settings_warning(imag, real, "exponent")
                        break

                elif choice == "h":
                    print_heading("HELP - MANIPULATE FORMULA")
                    print("Startvalue: The initial value z0 used in the fractal formula. For the Mandelbrot set, z0 is typically 0, but changing it can produce different and interesting variations.")
                    print("Exponent: The power to which z is raised in the formula. The standard Mandelbrot uses an exponent of 2, but changing it can create a wide variety of fractal shapes. Note that non-integer or complex exponents can lead to very different and often less stable fractals.")
                    enter_continue("Press enter to return to formula manipulation menu.")

                elif choice == "c":
                    break
    
    # Warnungen für potenziell instabile Einstellungen bei Formelmanipulation
    def cli_settings_warning(self, imag, real, setting_type: str):
        print_heading("STABILITY WARNING")

        if setting_type == "startvalue":
            if imag != 0:
                show_error(False, "StabilityWarning", "Visualizer is not optimized for complex startvalues; can cause inappropriate image cropping, long rendering-times and unpredictable results.")

            if real > 0.5:
                show_error(False, "StabilityWarning", "Visualizer is not optimized for startvalues far from the critical point (0 for Mandelbrot); can cause inappropriate image cropping, long rendering-times and unpredictable results.")

        elif setting_type == "exponent":

            if imag != 0:
                show_error(False, "StabilityWarning", "Visualizer is not optimized for complex exponents; can cause inappropriate image cropping, long rendering-times and unpredictable results.")

            if real > 2:
                show_error(False, "StabilityWarning", "Visualizer is not optimized for exponents higher than two; can cause inappropriate image cropping.")
            
        else:
            show_error(False, "StabilityWarning", "Unusual settings can lead to unpredictable results, long rendering times and inappropriate image cropping. Experiment with caution!")

        enter_continue("Press enter to continue.")

    # Einstellungen: Rendering (Basis-Iterationen und adaptiver Iterationsfaktor)
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