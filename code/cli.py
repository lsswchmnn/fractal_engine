from utils import print_heading, enter_continue, clear_cli, print_thin_separation, show_error, input_float, input_int
from visualize import Visualizer
from mapping import FRACTALS_MAP, ORBIT_TRAP_MAP
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
            print_heading("FRACTAL-ENGINE")
            print(f"Current Fractal: {self.fractal._name if self.fractal else "None"}\n")
            print("1 - Load fractal")
            if self.fractal:
                print("2 - Start visualizer")
                print("3 - Settings")
            print("H - Help")
            print("C - Close program")
            print_thin_separation(linebreak=False)
            choice = input("> ").lower().strip()

            if choice == "1":
                self.menu_load_fractal()
                continue

            elif choice == "2" and self.fractal:
                if not self.fractal:
                    show_error(True, "AttributeError", "No Fractal loaded.")
                    continue
                self.menu_visualize()
                continue

            elif choice == "3" and self.fractal:
                if not self.fractal:
                    show_error(True, "AttributeError", "No Fractal loaded.")
                self.menu_settings()
                continue

            elif choice == "h":
                self.menu_help()
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

    # Menüpunkt 3: Einstellungen
    def menu_settings(self):
        while True:
            print_heading("SETTINGS")
            print("1 - Formula manipulation")
            print("2 - Rendering")
            print("3 - Postprocessing")
            print("4 - Orbit trap")
            print("5 - Export")
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

            elif choice == "3":
                self.cli_change_postprocessing_settings()
                continue

            elif choice == "4":
                self.cli_change_orbit_trap_settings()
                continue

            elif choice == "5":
                self.cli_export_settings()
                continue

            elif choice == "h":
                print_heading("HELP - SETTINGS")
                print("Manipulate Formula: Change the start value and exponent used in the fractal formula. Note that non-standard settings can lead to very different and often less stable fractals, especially for complex exponents.")
                print()
                print("Rendering settings: Adjust the base number of iterations and the adaptive iteration factor k, which controls how many additional iterations are added as you zoom in. Higher k can improve detail accuracy at strong zooms but also increases rendering time and can lead to more fragile images at less deep zooms.")
                print()
                print("Orbit trap settings: Customize the type of orbit trap used for coloring, as well as the position and radius of the trap. Different types and settings can produce a wide variety of visual effects.")
                print()
                print("Export settings: Adjust the export resolution factor, which determines how much the resolution is increased when exporting the fractal image. Higher factors produce higher resolution images suitable for printing or detailed viewing, but also increase export time and file size.")
                enter_continue("Press enter to return to settings menu.")
                continue

            elif choice == "c":
                break

    # Menü: Hilfe
    def menu_help(self):
        print_heading("HELP MENU")
        print(
            "This program allows you to load and visualize different types of fractals, " \
            "as well as manipulate the underlying formula and rendering settings for more customized results." \
            "\n\n" \
            "Fractals are complex mathematical sets that exhibit self-similarity and intricate patterns at every scale. " \
            "The Mandelbrot set, for example, is defined by iterating the formula z = z^2 + c, where z and c are complex " \
            "numbers. By changing the parameters of this formula, you can create a wide variety of fractal images." 
        )

        enter_continue("Press enter to return to main menu.")

#------------------------------------------------------------
# EINSTELLUNGEN

    # Einstellungen: Formelmanipulation (Startwert und Exponent)
    def cli_manipulate_formula(self):
        while True:

            print_heading("MANIPULATE FORMULA")
            print(f"Current formula: {self.fractal._formula}")
            print("\nAvailable manipulations:")
            print(f"1 - Change startvalue (current: {self.fractal.start_real} + {self.fractal.start_imag}i)")
            print(f"2 - Change exponent (current: {self.fractal.exp_real} + {self.fractal.exp_imag}i)")
            print("H - Help")
            print("C - Cancel")
            print_thin_separation(linebreak=False)
            choice = input("> ").strip().lower()

            if choice == "1":
                print_heading("CHANGE STARTVALUE")
                print(f"Current startvalue: z0 = {self.fractal.start_real} + {self.fractal.start_imag}i\n")
                print("Recommended: Startvalue close to the critical point (0 for Mandelbrot) for more interesting results, but feel free to experiment!")
                print_thin_separation()
                print()

                real = input_float(-100.0, 100.0, 0.0, msg="Enter real part of startvalue z0", cli=True, loop=True)
                imag = input_float(-100.0, 100.0, 0.0, msg="Enter imaginary part of startvalue z0", cli=True, loop=True)
                self.fractal.start_real = real
                self.fractal.start_imag = imag
                enter_continue(f"Startvalue changed to z0 = {real} + {imag}i. Press enter to continue.", seperation=False)

                # Warnungen für potenziell instabile Einstellungen
                if imag != 0 or real != 2:
                    self.cli_settings_warning(imag, real, "startvalue")
                    break
            
            elif choice == "2":
                print_heading("CHANGE EXPONENT")
                print(f"Current exponent: {self.fractal.exp_real} + {self.fractal.exp_imag}i\n")
                print("Note: Changing the exponent can lead to very different and often less stable fractals, especially for non-integer or complex exponents. Experiment with caution!")
                print_thin_separation()
                print()

                real = input_float(-20.0, 20.0, 2.0, [1], msg="Enter real part of Exponent", cli=True, loop=False)
                imag = input_float(-20.0, 20.0, 0.0,      msg="Enter imaginary part of Exponent", cli=True, loop=False)
                self.fractal.exp_real = real
                self.fractal.exp_imag = imag
                enter_continue(f"Exponent changed to {real} + {imag}i. Press enter to continue.", seperation=False)

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

    # Einstellungen: Rendering (Basis-Iterationen und adaptiver Iterationsfaktor)
    def cli_change_rendering_settings(self): 
        while True:

            print_heading("CHANGE RENDERING SETTINGS")
            print(f"1 - Base Iterations (current: {self.fractal.max_iterations})")
            print(f"2 - Factor for adaptive iteration depth (current: {self.visualizer.render_settings.iterate_factor_k})")
            print(f"3 - Toggle Supersampling (current: {'On' if self.visualizer.render_settings.supersampling_enabled else 'Off'})")
            print("H - Help")
            print("C - Cancel")
            print_thin_separation(linebreak=False)
            choice = input("> ").strip().lower()

            if choice == "1":
                print_heading("CHANGE BASE ITERATIONS")
                print(f"Current base iterations: {self.fractal.max_iterations}")
                print_thin_separation()
                print()

                max_iter = input_int(10, 10000, 100, msg="Enter new base iterations", cli=True)
                self.fractal.max_iterations = max_iter
                enter_continue(f"Base iterations changed to {max_iter}. Press enter to continue.", seperation=False)

            elif choice == "2":
                print_heading("CHANGE ADAPTIVE ITERATION FACTOR")
                print(f"Current adaptive iteration factor k: {self.visualizer.render_settings.iterate_factor_k}")
                print_thin_separation()
                print()

                k = input_int(1, 1000, 100, msg="Enter new adaptive iteration factor k", cli=True)
                self.visualizer.render_settings.iterate_factor_k = k
                enter_continue(f"Adaptive iteration factor changed to {k}. Press enter to continue.", seperation=False)

            if choice == "3":
                print_heading("TOGGLE SUPERSAMPLING")
                current_state = self.visualizer.render_settings.supersampling_enabled
                new_state = not current_state
                self.visualizer.render_settings.supersampling_enabled = new_state
                enter_continue(f"Supersampling turned {'On' if new_state else 'Off'}. Press enter to continue.", seperation=False)

            elif choice == "h":
                print_heading("HELP - RENDERING SETTINGS")
                print("Base iterations: Number of iterations used as a baseline for the adaptive iteration depth.")
                print("Adaptive iteration factor (k): Tuning for quantitative improvement of detail accuracy at strong zooms. Higher k means more iterations added as you zoom in.")
                enter_continue("Press enter to return to settings menu.", seperation=False)

            elif choice == "c":
                break

    # Einstellungen: Postprocessing
    def cli_change_postprocessing_settings(self):
        while True:

            print_heading("CHANGE POSTPROCESSING SETTINGS")
            print(f"1 - Activate/Deactivate postprocessing (current: {'On' if self.visualizer.render_settings.post_process_bool else 'Off'})")
            print(f"2 - Contrast factor for postprocessing (current: {self.visualizer.render_settings.contrast_factor})")
            print(f"3 - Gamma factor for postprocessing (current: {self.visualizer.render_settings.gamma_factor})")
            print("H - Help")
            print("C - Cancel")
            choice = input("> ").strip().lower()

            if choice == "1":
                print_heading("TOGGLE POSTPROCESSING")
                current_state = self.visualizer.render_settings.post_process_bool
                new_state = not current_state
                self.visualizer.render_settings.post_process_bool = new_state
                enter_continue(f"Postprocessing turned {'On' if new_state else 'Off'}. Press enter to continue.", seperation=False)

            elif choice == "2":
                print_heading("CHANGE CONTRAST FACTOR")
                print(f"Current contrast factor: {self.visualizer.render_settings.contrast_factor}")
                print("Choose contrast = 1 for no change, contrast < 1 for lower contrast, contrast > 1 for higher contrast.")
                print_thin_separation()
                print()

                contrast = input_float(0.1, 5.0, 1.2, msg="Enter new contrast factor for postprocessing", cli=True)
                self.visualizer.render_settings.contrast_factor = contrast
                enter_continue(f"Contrast factor changed to {contrast}. Press enter to continue.", seperation=False)

            elif choice == "3":
                print_heading("CHANGE GAMMA FACTOR")
                print(f"Current gamma factor: {self.visualizer.render_settings.gamma_factor}")
                print("Choose gamma = 1 for no correction, gamma < 1 for brighter images, gamma > 1 for darker images.")
                print_thin_separation()
                print()

                gamma = input_float(0.1, 5.0, 1.5, msg="Enter new gamma factor for postprocessing", cli=True)
                self.visualizer.render_settings.gamma_factor = gamma
                enter_continue(f"Gamma factor changed to {gamma}. Press enter to continue.", seperation=False)

            elif choice == "h":
                print_heading("HELP - POSTPROCESSING SETTINGS")
                print("Postprocessing: Toggle the application of postprocessing effects on the rendered image.")
                print("Contrast factor: Adjusts the contrast of the image. A value of 1 means no change, less than 1 reduces contrast, and greater than 1 increases contrast.")
                print("Gamma factor: Adjusts the gamma correction applied to the image. A value of 1 means no correction, less than 1 brightens the image, and greater than 1 darkens the image.")
                enter_continue("Press enter to return to settings menu.", seperation=False)

            elif choice == "c":
                break

    # Einstellungen: Formel-Trap-Coloring (Offset, Radius und Methode)
    def cli_change_orbit_trap_settings(self):
        while True:

            # aktuelles Label anhand des Index finden
            current_type_idx = self.fractal.trap_type
            current_label = next(
                (info["label"] for info in ORBIT_TRAP_MAP.values() if info["idx"] == current_type_idx),
                "Unknown")

            print_heading("CHANGE ORBIT-TRAP SETTINGS")
            print(f"1 - Change Type (current: {current_label})")
            print(f"2 - Change X-Offset (current: {self.fractal.trap_x})")
            print(f"3 - Change Y-Offset (current: {self.fractal.trap_y})")
            print(f"4 - Change trap radius (current: {self.fractal.trap_radius})")
            print("H - Help")
            print("C - Cancel")
            print_thin_separation(linebreak=False)
            choice = input("> ").strip().lower()

            if choice == "1":       # Type
                trap_keys = list(ORBIT_TRAP_MAP.keys())
                
                while True:
                    print_heading("CHANGE TYPE")
                    print(f"Current Type: {self.fractal.trap_type}\n")

                    for i, key in enumerate(trap_keys, start=1):
                        label = ORBIT_TRAP_MAP[key]["label"]
                        print(f"{i} - {label}")

                    print_thin_separation(linebreak=False)
                    choice = input("> ").strip().lower()

                    if not choice.isdigit():
                        continue

                    idx = int(choice) - 1

                    if idx < 0 or idx >= len(trap_keys):
                        continue

                    selected_key = trap_keys[idx]
                    trap_info = ORBIT_TRAP_MAP[selected_key]

                    # Einstellungen übernehmen
                    self.fractal.trap_type = trap_info["idx"]
                    self.fractal.trap_type_name = trap_info["label"]

                    enter_continue(f"\nOrbit trap set to: {trap_info['label']}. Press Enter to continue")
                    break

            elif choice == "2":     # X-Offset
                print_heading("CHANGE X-OFFSET")
                print(f"Current X-Offset: {self.fractal.trap_x}")
                print_thin_separation()
                print()

                x_offset = input_float(-5, 5, 0.2, forbidden=[0], msg="Enter new adaptive iteration factor k", cli=True)
                self.fractal.trap_x = x_offset
                enter_continue(f"Adaptive iteration factor changed to {self.fractal.trap_x}. Press enter to continue.", seperation=False)

            elif choice == "3":     # Y-Offset
                print_heading("CHANGE Y-OFFSET")
                print(f"Current Y-Offset: {self.fractal.trap_y}")
                print_thin_separation()
                print()

                y_offset = input_float(-5, 5, 0.2, forbidden=[0], msg="Enter new adaptive iteration factor k", cli=True)
                self.fractal.trap_y = y_offset
                enter_continue(f"Adaptive iteration factor changed to {self.fractal.trap_y}. Press enter to continue.", seperation=False)

            elif choice == "4":     # Radius
                print_heading("CHANGE RADIUS")
                print(f"Current Radius: {self.fractal.trap_radius}")
                print_thin_separation()
                print()

                radius = input_float(0.0, 5, 0.2, forbidden=[0], msg="Enter new adaptive iteration factor k", cli=True)
                self.fractal.trap_radius = radius
                enter_continue(f"Adaptive iteration factor changed to {self.fractal.trap_radius}. Press enter to continue.", seperation=False)

            elif choice == "h":
                print_heading("HELP - ORBIT TRAP SETTINGS")
                print("Type: Choose the method used for orbit trap coloring. Different methods can produce very different visual effects.")
                print("X-Offset and Y-Offset: Adjust the position of the trap in the complex plane. This can create interesting variations in the resulting image.")
                print("Trap Radius: The radius around the trap point that determines how close an orbit must come to be affected by the trap. Smaller radii create sharper features, while larger radii produce softer effects.")
                enter_continue("Press enter to return to settings menu.", seperation=False)

            elif choice == "c":
                break

    # Einsellungen: Export
    def cli_export_settings(self):
        while True:
            res_x = self.visualizer.viewport.width_px * self.visualizer.render_settings.export_factor
            res_y = self.visualizer.viewport.height_px * self.visualizer.render_settings.export_factor
            res = f"{res_x:.0f} x {res_y:.0f}"

            print_heading("EXPORT SETTINGS")
            print(f"1 - Change export resolution factor (current: {self.visualizer.render_settings.export_factor})")
            print("H - Help")
            print("C - Cancel")
            choice = input("> ").strip().lower()

            if choice == "1":
                print_heading("CHANGE EXPORT RESOLUTION FACTOR")
                print(f"Current export resolution factor: {self.visualizer.render_settings.export_factor}")
                print(f"Current export resolution: {res} (Viewport size multiplied by export factor)")
                print_thin_separation()
                print()

                factor = input_int(1, 10, 4, msg="Enter new export resolution factor", cli=True)
                self.visualizer.render_settings.export_factor = factor
                enter_continue(f"Export resolution factor changed to {factor}. Press enter to continue.", seperation=False)

            elif choice == "h":
                print_heading("HELP - EXPORT SETTINGS")
                print("Export resolution factor: This factor determines how much the resolution is increased when exporting the fractal image. For example, a factor of 4 means that the exported image will have 4 times the width and height of the current viewport, resulting in a much higher resolution suitable for printing or detailed viewing.")
                enter_continue("Press enter to return to settings menu.", seperation=False)

            elif choice == "c":
                break

    # Warnungen für potenziell instabile Einstellungen bei Formelmanipulation
    def cli_settings_warning(self, imag: float, real: float, setting_type: str):
        print_heading("STABILITY WARNING")

        if setting_type == "startvalue":
            if imag != 0:
                show_error(
                    False, "StabilityWarning", 
                    "Complex startvalues are experimental and can cause inappropriate image cropping, long rendering-times and unpredictable results.")

            if abs(real) > 0.5 or abs(imag) > 0.5:
                show_error(
                    False, "StabilityWarning", 
                    "Visualizer is not optimized for startvalues far from the critical point (0+0i for Mandelbrot); can cause inappropriate image cropping, long rendering-times and unpredictable results.")

        elif setting_type == "exponent":

            if real < 0:
                show_error(
                    False, "StabilityWarning",
                    "Negative exponents introduce poles (1/z^n) and may cause numerical instability.")

            if abs(imag) > 0.5:
                show_error(False, "StabilityWarning",
                    "Large imaginary parts of the exponent can strongly distort the dynamics and slow down rendering.")

            if real > 5:
                show_error(False, "StabilityWarning",
                    "Very large exponents may produce extremely thin structures and long rendering times.")

        else:
            show_error(False, "StabilityWarning", "Unusual settings can lead to unpredictable results, long rendering times and inappropriate image cropping. Experiment with caution!")

        enter_continue("Press enter to continue.")
