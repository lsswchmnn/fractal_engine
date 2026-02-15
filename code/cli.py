from utils import print_heading, enter_continue, clear_cli, print_thin_separation, show_error
from fractal import MandelbrotFractal, JuliaFractal
from visualize import Visualizer
from mapping import fractals_map
import fractal
#============================================================
class CLI():
    def __init__(self):
        self.fractal                 = None
        self.visualizer              = Visualizer()
        self.fractal_loaded : bool   = False

#------------------------------------------------------------
# HAUPTMENÜ

    def run(self):
        while True:
            print_heading("FRACTAL-SIMULATION")
            print("1 - Load fractal")
            print("2 - Visualize")
            print("...")
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
                pass

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
            
            keys = list(fractals_map.keys())

            print("Choose Fractal:")
            for i, key in enumerate(keys, start=1):
                meta = fractals_map[key]
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
                    self.fractal = getattr(fractal, class_name)
                except AttributeError:
                    show_error(True, "TransitionError", f"Function {class_name} not found in Dictionary.")
                    continue

            enter_continue("Press enter to return to main menu.")

    # Menüpunkt 2: Fraktal graphisch visualisieren
    def menu_visualize(self):
        self.visualizer.start(self.fractal)    # CLI startet nur das Visualisierungfenster und spielt danach keine aktive Rolle mehr.
        return