from dataclasses import dataclass
#============================================================
@dataclass
class RenderSettings:
    # Rendering
    iterate_factor_k        : int   = 250       # Feintuning-Faktor für quantitative Verbesserung der Detailgenauigkeit bei starken Zooms
    export_factor           : int   = 4         # Faktor für die Hochskalierung bei Export
    tile_height             : int   = 32        # Höhe der Kacheln für das tile-basierte Rendering (Performance-Optimierung)
    supersampling_enabled   : bool  = False     # Supersampling aktivieren/deaktivieren
    supersampling_factor    : int   = 2         # Faktor für Supersampling (z.B. 2 = 4x Supersampling, 3 = 9x Supersampling, etc.)

    # Postprocessing
    post_process_enabled    : bool  = True      # Postprocessing aktivieren/deaktivieren
    gamma_factor            : float = 1.2       # Gamma-Korrektur-Faktor für Postprocessing
    contrast_factor         : float = 1.2       # Kontrast-Faktor für Postprocessing
    inversion_enabled       : bool  = False     # Negativwert
