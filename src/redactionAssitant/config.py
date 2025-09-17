import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración centralizada para el redactor automático."""

    def __init__(self, default_hu_code: str | None = "USRNM"):
        self.API_KEY = os.getenv("DS_API_KEY")

        if not self.API_KEY:
            raise ValueError("DS_API_KEY no encontrada en las variables de entorno")

        hu_code = os.getenv("HU_CODE")
        if hu_code:
            self.code_hu = hu_code
        elif default_hu_code is not None:
            self.code_hu = default_hu_code
        else:
            raise ValueError(
                "HU_CODE no encontrada en las variables de entorno y no se proporcionó valor por defecto"
            )

        # Usar Path para mejor manejo de rutas
        self.input_dir = Path("data/raw/")
        self.output_dir = Path("data/processed/")
        
        # Crear directorios si no existen
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_paths = {
            "hus": "UserStory.txt",
            "cps": "TestCases.txt", 
            "exp": "expectedResults.txt"
        }

    def input_path(self, key: str) -> Path:
        """Retorna la ruta completa del archivo de entrada."""
        if key not in self.data_paths:
            raise ValueError(f"Clave '{key}' no válida. Claves disponibles: {list(self.data_paths.keys())}")
        return self.input_dir / self.data_paths[key]

    def output_path(self, key: str) -> Path:
        """Retorna la ruta completa del archivo de salida."""
        if key not in self.data_paths:
            raise ValueError(f"Clave '{key}' no válida. Claves disponibles: {list(self.data_paths.keys())}")
        return self.output_dir / self.data_paths[key]
    
    def all_output_paths(self) -> tuple[Path, Path, Path]:
        """Retorna todas las rutas de salida como tupla."""
        return (
            self.output_path("cps"),  
            self.output_path("exp"),  
            self.output_dir / "feedback.txt",
        )