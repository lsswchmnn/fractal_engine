import json
import os
from settings import RenderSettings
from dataclasses import dataclass, asdict
from viewport import Viewport
#============================================================
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

#============================================================
class ViewportRepository:
    def __init__(self, directory: str = "viewports"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def _get_path(self, name: str) -> str:
        return os.path.join(self.directory, f"{name}.json")

    def save(self, name: str, viewport: Viewport) -> None:
        """
        Speichert einen Viewport als JSON-Datei.

        Parameters:
        name (str): Name des Templates
        viewport (Viewport): Zu speichernder Viewport
        """
        path = self._get_path(name)

        with open(path, "w") as f:
            json.dump(viewport.to_dict(), f, indent=4)

    def load(self, name: str) -> Viewport:
        """
        Lädt einen Viewport aus einer JSON-Datei.

        Parameters:
        name (str): Name des Templates

        Returns:
        Viewport: Geladene Viewport-Instanz
        """
        path = self._get_path(name)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Viewport '{name}' not found.")

        with open(path, "r") as f:
            data = json.load(f)

        return Viewport.from_dict(data)

    def list(self) -> list[str]:
        """
        Listet alle gespeicherten Viewport-Templates auf.

        Returns:
        list[str]: Namen der verfügbaren Templates
        """
        files = os.listdir(self.directory)
        return [f.replace(".json", "") for f in files if f.endswith(".json")]

    def delete(self, name: str) -> None:
        """
        Löscht ein gespeichertes Viewport-Template.

        Parameters:
        name (str): Name des Templates
        """
        path = self._get_path(name)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Viewport '{name}' not found.")

        os.remove(path)
