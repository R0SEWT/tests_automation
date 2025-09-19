import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class ConfigError(ValueError):
    """Error personalizado para problemas de configuración."""
    pass


class Config:
    """Configuración centralizada para el redactor automático."""

    def __init__(self, default_hu_code: str | None = "USRNM"):
        # Validar PROVIDER
        provider = os.getenv("PROVIDER", "").lower()
        if not provider:
            raise ConfigError(
                "PROVIDER no configurado. Debe ser 'deepseek' o 'openai'.\n"
                "Ejemplo: PROVIDER=deepseek"
            )
        if provider not in ["deepseek", "openai"]:
            raise ConfigError(
                f"PROVIDER inválido: '{provider}'. Debe ser 'deepseek' o 'openai'.\n"
                "Ejemplo: PROVIDER=deepseek"
            )
        self.provider = provider

        # Validar API keys según provider
        if provider == "deepseek":
            api_key = os.getenv("DS_API_KEY")
            if not api_key:
                raise ConfigError(
                    "DS_API_KEY requerida para provider 'deepseek'.\n"
                    "Ejemplo: DS_API_KEY=sk-..."
                )
            if not api_key.startswith("sk-"):
                raise ConfigError(
                    "DS_API_KEY debe comenzar con 'sk-'.\n"
                    f"Valor actual: {api_key[:10]}..."
                )
        else:  # openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ConfigError(
                    "OPENAI_API_KEY requerida para provider 'openai'.\n"
                    "Ejemplo: OPENAI_API_KEY=sk-..."
                )
            if not api_key.startswith("sk-"):
                raise ConfigError(
                    "OPENAI_API_KEY debe comenzar con 'sk-'.\n"
                    f"Valor actual: {api_key[:10]}..."
                )

        self.API_KEY = api_key

        # Validar BATCH_SIZE
        batch_size_str = os.getenv("BATCH_SIZE")
        if not batch_size_str:
            raise ConfigError(
                "BATCH_SIZE no configurado. Debe ser un número entero positivo.\n"
                "Ejemplo: BATCH_SIZE=20"
            )
        try:
            batch_size = int(batch_size_str)
            if batch_size <= 0:
                raise ValueError()
        except ValueError:
            raise ConfigError(
                f"BATCH_SIZE inválido: '{batch_size_str}'. Debe ser un número entero positivo.\n"
                "Ejemplo: BATCH_SIZE=20"
            )
        self.batch_size = batch_size

        # Validar HU_CODE (opcional con formato)
        hu_code = os.getenv("HU_CODE")
        if hu_code:
            if not isinstance(hu_code, str) or len(hu_code.strip()) == 0:
                raise ConfigError(
                    f"HU_CODE inválido: '{hu_code}'. Debe ser una cadena no vacía.\n"
                    "Ejemplo: HU_CODE=USRNM"
                )
            self.code_hu = hu_code.strip()
        elif default_hu_code is not None:
            self.code_hu = default_hu_code
        else:
            raise ConfigError(
                "HU_CODE no encontrada en variables de entorno y no se proporcionó valor por defecto.\n"
                "Configure HU_CODE en .env o pase default_hu_code al constructor."
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