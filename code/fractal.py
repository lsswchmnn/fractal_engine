from abc import ABC
from dataclasses import dataclass
from numba import njit
import math
#============================================================
# ITERATIONSKERNELS (eigentliche Berechnungen, vom Render-Kernel aus aufgerufen)
@njit
def calculate_orbit_trap(zr, zi, trap_type, trap_x, trap_y, trap_radius):
    
    trap_type = int(trap_type)

    if trap_type == 0:  # POINT
        dx = zr - trap_x
        dy = zi - trap_y
        return dx*dx + dy*dy

    elif trap_type == 1:  # CIRCLE
        dx = zr - trap_x
        dy = zi - trap_y
        dist = (dx*dx + dy*dy)**0.5
        return abs(dist - trap_radius)

    elif trap_type == 2:  # LINE (horizontal)
        return abs(zi - trap_y)

    else:
        return 1e10
    
#============================================================
# ITERATIONSKERNELS (eigentliche Berechnungen, vom Render-Kernel aus aufgerufen)

@njit
def mandelbrot_kernel(
    c_real, c_imag,
    max_iter, escape_radius,
    z_real=0.0, z_imag=0.0,
    exp_real=2.0, exp_imag=0.0,
    trap_y=0.1, trap_x=0.1,
    trap_type=0, trap_radius=0.5):

    trap_min = 1e10     # Für Orbit-Trap
    escape_sq = escape_radius * escape_radius
    zr = z_real
    zi = z_imag

    # 1) Standard Mandelbrot (Exponent 2)
    if exp_imag == 0.0 and exp_real == 2.0:

        for i in range(max_iter):

            # Für Orbit-Trap
            dist = calculate_orbit_trap(zr, zi, trap_type, trap_x, trap_y, trap_radius)
            if dist < trap_min:
                trap_min = dist

            zr2 = zr * zr
            zi2 = zi * zi
            r2 = zr2 + zi2

            if r2 > escape_sq:
                abs_z = math.sqrt(r2)
                nu = i + 1 - math.log(math.log(abs_z)) / math.log(2)
                return float(nu), 1, zr, zi, trap_min

            zi = 2.0 * zr * zi + c_imag
            zr = zr2 - zi2 + c_real

        return float(max_iter), 0, zr, zi, trap_min

    # 2) Höhere ganzzahlige Exponenten
    if exp_imag == 0.0 and exp_real == float(int(exp_real)):

        d = int(exp_real)
        log_exp = math.log(exp_real)

        for i in range(max_iter):

            # Orbit-Trap
            dist = calculate_orbit_trap(zr, zi, trap_type, trap_x, trap_y, trap_radius)
            if dist < trap_min:
                trap_min = dist

            r2 = zr * zr + zi * zi

            if r2 > escape_sq:

                abs_z = math.sqrt(r2)
                nu = i + 1 - math.log(math.log(abs_z)) / log_exp

                return float(nu), 1, zr, zi, trap_min

            # z^d via wiederholte komplexe Multiplikation
            zr_pow = zr
            zi_pow = zi

            for _ in range(d - 1):
                temp = zr_pow * zr - zi_pow * zi
                zi_pow = zr_pow * zi + zi_pow * zr
                zr_pow = temp

            zr = zr_pow + c_real
            zi = zi_pow + c_imag

        return float(max_iter), 0, zr, zi, trap_min

    # 3) Komplexer Exponent (allgemeiner Fall)
    else:
        a = exp_real
        b = exp_imag
        log_exp = math.log(math.sqrt(a*a + b*b))

        for i in range(max_iter):
            
            # Orbit-Trap
            dist = calculate_orbit_trap(zr, zi, trap_type, trap_x, trap_y, trap_radius)
            if dist < trap_min:
                trap_min = dist
            
            r2 = zr * zr + zi * zi
            
            if r2 > escape_sq:
                abs_z = math.sqrt(r2)
                nu = i + 1 - math.log(math.log(abs_z)) / log_exp
                return float(nu), 1, zr, zi, trap_min

            if r2 == 0.0:
                zr = c_real
                zi = c_imag
                continue

            r = math.sqrt(r2)
            log_r = math.log(r)
            theta = math.atan2(zi, zr)

            real_part = a * log_r - b * theta
            imag_part = a * theta + b * log_r

            exp_r = math.exp(real_part)

            zr = exp_r * math.cos(imag_part) + c_real
            zi = exp_r * math.sin(imag_part) + c_imag

        return float(max_iter), 0, zr, zi, trap_min

@njit
def inverted_mandelbrot_kernel(
    c_real, c_imag,
    max_iter,
    escape_radius,
    z_real=0.0, z_imag=0.0,
    exp_real=2.0, exp_imag=0.0):

    # Singularität vermeiden (c = 0)
    if c_real == 0.0 and c_imag == 0.0:
        c_real = 1e10
        c_imag = 0.0

    escape_sq = escape_radius * escape_radius

    # 1/c einmal berechnen
    denom = c_real * c_real + c_imag * c_imag
    c_inv_real = c_real / denom
    c_inv_imag = -c_imag / denom

    zr = z_real
    zi = z_imag

    # 1) Exponent = 2 (Fast Path)
    if exp_imag == 0.0 and exp_real == 2.0:

        log_exp = math.log(2.0)

        for i in range(max_iter):

            zr2 = zr * zr
            zi2 = zi * zi
            r2 = zr2 + zi2

            if r2 > escape_sq:

                abs_z = math.sqrt(r2)
                nu = i + 1 - math.log(math.log(abs_z)) / log_exp

                return float(nu), 1, zr, zi

            zi = 2.0 * zr * zi + c_inv_imag
            zr = zr2 - zi2 + c_inv_real

        return float(max_iter), 0, zr, zi

    # 2) Ganzzahliger Exponent
    if exp_imag == 0.0 and exp_real == float(int(exp_real)):

        d = int(exp_real)
        log_exp = math.log(exp_real)

        for i in range(max_iter):

            r2 = zr * zr + zi * zi

            if r2 > escape_sq:

                abs_z = math.sqrt(r2)
                nu = i + 1 - math.log(math.log(abs_z)) / log_exp

                return float(nu), 1, zr, zi

            zr_pow = zr
            zi_pow = zi

            for _ in range(d - 1):
                temp = zr_pow * zr - zi_pow * zi
                zi_pow = zr_pow * zi + zi_pow * zr
                zr_pow = temp

            zr = zr_pow + c_inv_real
            zi = zi_pow + c_inv_imag

        return float(max_iter), 0, zr, zi

    # 3) Komplexer Exponent (allgemeiner Fall)
    a = exp_real
    b = exp_imag
    log_exp = math.log(math.sqrt(a*a + b*b))

    for i in range(max_iter):
        r2 = zr * zr + zi * zi

        if r2 > escape_sq:
            abs_z = math.sqrt(r2)
            nu = i + 1 - math.log(math.log(abs_z)) / log_exp
            return float(nu), 1, zr, zi

        if r2 == 0.0:
            zr = c_inv_real
            zi = c_inv_imag
            continue

        r = math.sqrt(r2)
        log_r = math.log(r)
        theta = math.atan2(zi, zr)

        real_part = a * log_r - b * theta
        imag_part = a * theta + b * log_r

        exp_r = math.exp(real_part)

        zr = exp_r * math.cos(imag_part) + c_inv_real
        zi = exp_r * math.sin(imag_part) + c_inv_imag

    return float(max_iter), 0, zr, zi

@njit
def julia_kernel(
    c_real, c_imag,
    max_iter,
    escape_radius,
    z_real, z_imag,
    exp_real=2.0, exp_imag=0.0):

    # Julia: z0 = Pixel, c = konstante Parameter
    return mandelbrot_kernel(
        c_real,
        c_imag,
        max_iter,
        escape_radius,
        z_real,
        z_imag,
        exp_real,
        exp_imag
    )

@njit
def burning_ship_kernel(
    c_real, c_imag,
    max_iter,
    escape_radius,
    z_real=0.0, z_imag=0.0,
    exp_real=2.0, exp_imag=0.0):

    escape_sq = escape_radius * escape_radius
    zr = z_real
    zi = z_imag

    # 1) Standard Burning Ship (Exponent 2)
    if exp_imag == 0.0 and exp_real == 2.0:
        log_exp = math.log(2.0)

        for i in range(max_iter):
            zr_abs = abs(zr)
            zi_abs = abs(zi)

            zr2 = zr_abs * zr_abs
            zi2 = zi_abs * zi_abs
            r2 = zr2 + zi2

            if r2 > escape_sq:
                abs_z = math.sqrt(r2)
                nu = i + 1 - math.log(math.log(abs_z)) / log_exp
                return float(nu), 1, zr, zi

            zi = 2.0 * zr_abs * zi_abs + c_imag
            zr = zr2 - zi2 + c_real

        return float(max_iter), 0, zr, zi

    # 2) Ganzzahliger Exponent
    if exp_imag == 0.0 and exp_real == float(int(exp_real)):

        d = int(exp_real)
        log_exp = math.log(exp_real)

        for i in range(max_iter):
            zr_abs = abs(zr)
            zi_abs = abs(zi)

            zr_pow = zr_abs
            zi_pow = zi_abs

            for _ in range(d - 1):
                temp = zr_pow * zr_abs - zi_pow * zi_abs
                zi_pow = zr_pow * zi_abs + zi_pow * zr_abs
                zr_pow = temp

            r2 = zr_pow * zr_pow + zi_pow * zi_pow

            if r2 > escape_sq:
                abs_z = math.sqrt(r2)
                nu = i + 1 - math.log(math.log(abs_z)) / log_exp
                return float(nu), 1, zr, zi

            zr = zr_pow + c_real
            zi = zi_pow + c_imag

        return float(max_iter), 0, zr, zi

    # 3) Komplexer Exponent
    a = exp_real
    b = exp_imag
    log_exp = math.log(math.sqrt(a*a + b*b))

    for i in range(max_iter):
        zr_abs = abs(zr)
        zi_abs = abs(zi)

        r2 = zr_abs * zr_abs + zi_abs * zi_abs

        if r2 > escape_sq:
            abs_z = math.sqrt(r2)
            nu = i + 1 - math.log(math.log(abs_z)) / log_exp
            return float(nu), 1, zr, zi

        if r2 == 0.0:
            zr = c_real
            zi = c_imag
            continue

        r = math.sqrt(r2)
        log_r = math.log(r)
        theta = math.atan2(zi_abs, zr_abs)

        real_part = a * log_r - b * theta
        imag_part = a * theta + b * log_r

        exp_r = math.exp(real_part)

        zr = exp_r * math.cos(imag_part) + c_real
        zi = exp_r * math.sin(imag_part) + c_imag

    return float(max_iter), 0, zr, zi

@njit
def tricorn_kernel(
    c_real, c_imag,
    max_iter,
    escape_radius,
    z_real=0.0, z_imag=0.0,
    exp_real=2.0, exp_imag=0.0):

    escape_sq = escape_radius * escape_radius

    zr = z_real
    zi = z_imag

    # 1) Standard Tricorn (Exponent 2)
    if exp_imag == 0.0 and exp_real == 2.0:
        log_exp = math.log(2.0)

        for i in range(max_iter):

            # komplexe Konjugation
            zr_c = zr
            zi_c = -zi

            # z^2 + c
            zr2 = zr_c * zr_c
            zi2 = zi_c * zi_c

            zr_new = zr2 - zi2 + c_real
            zi_new = 2.0 * zr_c * zi_c + c_imag

            zr = zr_new
            zi = zi_new

            r2 = zr * zr + zi * zi
            if r2 > escape_sq:
                abs_z = math.sqrt(r2)
                nu = i + 1 - math.log(math.log(abs_z)) / log_exp
                return float(nu), 1, zr, zi

        return float(max_iter), 0, zr, zi

    # 2) Ganzzahliger Exponent
    if exp_imag == 0.0 and exp_real == float(int(exp_real)):

        d = int(exp_real)
        log_exp = math.log(exp_real)

        for i in range(max_iter):

            # komplexe Konjugation
            zr_c = zr
            zi_c = -zi

            # z^d via wiederholte komplexe Multiplikation
            zr_pow = zr_c
            zi_pow = zi_c
            for _ in range(d - 1):
                temp = zr_pow * zr_c - zi_pow * zi_c
                zi_pow = zr_pow * zi_c + zi_pow * zr_c
                zr_pow = temp

            zr = zr_pow + c_real
            zi = zi_pow + c_imag

            r2 = zr * zr + zi * zi
            if r2 > escape_sq:
                abs_z = math.sqrt(r2)
                nu = i + 1 - math.log(math.log(abs_z)) / log_exp
                return float(nu), 1, zr, zi

        return float(max_iter), 0, zr, zi

    # 3) Komplexer Exponent (allgemeiner Fall)
    a = exp_real
    b = exp_imag
    log_exp = math.log(math.sqrt(a*a + b*b))

    for i in range(max_iter):
        # komplexe Konjugation
        zr_c = zr
        zi_c = -zi

        r2 = zr_c * zr_c + zi_c * zi_c
        if r2 > escape_sq:
            abs_z = math.sqrt(r2)
            nu = i + 1 - math.log(math.log(abs_z)) / log_exp
            return float(nu), 1, zr, zi

        if r2 == 0.0:
            zr = c_real
            zi = c_imag
            continue

        r = math.sqrt(r2)
        log_r = math.log(r)
        theta = math.atan2(zi_c, zr_c)

        real_part = a * log_r - b * theta
        imag_part = a * theta + b * log_r

        exp_r = math.exp(real_part)
        zr = exp_r * math.cos(imag_part) + c_real
        zi = exp_r * math.sin(imag_part) + c_imag

    return float(max_iter), 0, zr, zi

#============================================================
# KLASSEN für Fraktale
class Fractal(ABC):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        self.max_iterations = max_iterations                # Wie lange prüft man, ob der Wert "ausbricht"? - höhere Werte → detailliertere Bilder, aber längere Berechnungszeit
        self.escape_radius = escape_radius                  # Für Mandelbrot z.B. 2
        self._default_bounds = (-2.0, 1.0, -1.2, 1.2)       # Standard-Ausschnitt der komplexen Ebene, mit dem gearbeitet wird. Kann von Fraktal zu Fraktal unterschiedlich sein.
        self.kernel = None          # Platzhalter für die Iterationsfunktion, wird in den Unterklassen gesetzt
        self.pixel_is_c = True      # Pixel repräsentiert c (Alles außer Julia, standad)

        # Anzeige
        self._name = "Fractal"                              # Name des Fraktals (wird in Mapping überschrieben)
        self._formula = "z_{n+1} = z_n^2 + c"

        # Startwert
        self.start_real = 0.0
        self.start_imag = 0.0
        
        # Exponent
        self.exp_real = 2.0
        self.exp_imag = 0.0

        # Faktor C
        self.c_real = 0.0
        self.c_imag = 0.0

        # Für Orbit-Trap
        self.trap_type = 1  # 0 = Punkt, 1 = Kreis, 2 = Linie etc.
        self.trap_x = 0.3
        self.trap_y = 0.2
        self.trap_radius = 0.05

#------------------------------------------------------------
class MandelbrotFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)
        self._default_bounds = (-2.0, 1.0, -1.2, 1.2)
        self._name = "Mandelbrot-Set"
        self._formula = "z_{n+1} = z_n^2 + c"
        self.kernel = mandelbrot_kernel

#------------------------------------------------------------
class InvertedMandelbrotFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)
        self._default_bounds = (-2, 4.5, -2.4, 2.4)   # zu Fraktal
        self._name = "Inverted Mandelbrot-Set"
        self._formula = "z_{n+1} = z_n^2 + 1/c"
        self.kernel = inverted_mandelbrot_kernel

#------------------------------------------------------------
class JuliaFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0, c_real: float = 0.355, c_imag: float = 0.355):
        super().__init__(max_iterations, escape_radius)
        self._default_bounds = (-2.0, 1.0, -1.2, 1.2)
        self._name = "Julia-Set"
        self._formula = "z_{n+1} = z_n^2 + c"
        self.c_real = c_real
        self.c_imag = c_imag
        self.kernel = julia_kernel
        self.pixel_is_c = False     # Pixel repräsentiert z (nur bei Julia!)

#------------------------------------------------------------
class BurningShipFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)
        self._default_bounds = (-2.2, 1.2, -2.5, 1.5)
        self._name = "Burning Ship"
        self._formula = "z_{n+1} = (|Re(z_n)| + i|Im(z_n)|)^2 + c"
        self.kernel = burning_ship_kernel
    
#------------------------------------------------------------
class TricornFractal(Fractal):
    def __init__(self, max_iterations: int = 100, escape_radius: float = 2.0):
        super().__init__(max_iterations, escape_radius)
        self._default_bounds = (-2.0, 2.0, -1.5, 1.5)
        self.kernel = tricorn_kernel
        self._name = "Tricorn"
        self._formula = "z_{n+1} = conjugate(z_n)^2 + c"
