import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.API_KEY = os.getenv("DS_API_KEY")
        self.code_hu = "USRNM"

        if not self.API_KEY:
            raise ValueError("API_KEY no encontrada en el entorno")

        # Renombrar para no pisar los métodos xd
        self.input_dir = "data/raw/"
        self.output_dir = "data/processed/"
        self.data_paths = {
            "hus": "UserStory.txt",
            "cps": "TestCases.txt",
            "exp": "expectedResults.txt"
        }

    def input_path(self, key):
        return os.path.join(self.input_dir, self.data_paths[key])

    def output_path(self, key):
        return os.path.join(self.output_dir, self.data_paths[key])
    
    def all_output_paths(self):
        return (
            self.output_path("cps"),  
            self.output_path("exp"),  
            os.path.join(self.output_dir, "feedback.txt"),
        )