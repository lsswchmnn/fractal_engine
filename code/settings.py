from dataclasses import dataclass
#============================================================
@dataclass
class RenderSettings:
    iterate_factor_k    : int          = 250       # Feintuning-Faktor für quantitative Verbesserung der Detailgenauigkeit bei starken Zooms
    export_factor       : int          = 4         # Faktor für die Hochskalierung bei
    tile_height         : int          = 32        # Höhe der Kacheln für das tile-basierte Rendering (Performance-Optimierung)
    
    # Postprocessing
    post_process_bool   : bool         = True      # Postprocessing aktivieren/deaktivieren
    gamma_factor        : float        = 1.2       # Gamma-Korrektur-Faktor für Postprocessing
    contrast_factor     : float        = 1.2       # Kontrast-Faktor für Postprocessing

@dataclass
class DisplaySettings:
    pass