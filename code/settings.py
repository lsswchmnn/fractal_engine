import json
import os
from dataclasses import dataclass, asdict
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

#============================================================
# Repository für das Speichern und Laden von RenderSettings als JSON-Dateien.
# Temporär in cli.py erzeugtes Objekt.
class SettingsRepository:
    def __init__(self, directory: str = "settings"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def _get_path(self, name: str) -> str:
        return os.path.join(self.directory, f"{name}.json")
    
    def save(self, name: str, settings: RenderSettings):
        path = self._get_path(name)
        with open(path, 'w') as f:
            json.dump(asdict(settings), f, indent=4)

    def load(self, name: str) -> RenderSettings:
        path = self._get_path(name)
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Settings file '{name}' not found.")
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        return RenderSettings(**data)
    
    def list(self) -> list[str]:
        files = os.listdir(self.directory)
        return [f.replace(".json", "") for f in files if f.endswith(".json")]