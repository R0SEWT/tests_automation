"""
Base interfaces and abstract classes for the HU processing system.

This module provides the foundation for all processing components,
ensuring consistent interfaces and promoting code reuse.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol, runtime_checkable
from pathlib import Path
import logging


@runtime_checkable
class ConfigProtocol(Protocol):
    """Protocol for configuration objects."""
    
    def input_path(self, key: str) -> Path: ...
    def output_path(self, key: str) -> Path: ...
    @property
    def batch_size(self) -> int: ...
    @property
    def code_hu(self) -> str: ...


@runtime_checkable
class ProcessorProtocol(Protocol):
    """Protocol for text processors."""
    
    def process(self, text: str, context: Optional[str] = None) -> tuple[str, str]: ...


class BaseProcessor(ABC):
    """
    Abstract base class for all text processors.
    
    Provides common functionality for batch processing, logging,
    and error handling.
    """
    
    def __init__(self, config: ConfigProtocol, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.batch_size = config.batch_size
        
    @abstractmethod
    def process(self, text: str, context: Optional[str] = None) -> tuple[str, str]:
        """Process text and return (processed_text, feedback)."""
        pass
    
    def validate_input(self, *inputs: str) -> bool:
        """Validate input parameters."""
        for inp in inputs:
            if not inp or not inp.strip():
                self.logger.warning("Empty or invalid input detected")
                return False
        return True
    
    def create_batches(self, items: List[str]) -> List[List[str]]:
        """Create batches from a list of items."""
        return [items[i:i + self.batch_size] for i in range(0, len(items), self.batch_size)]
    
    def preprocess_text(self, text: str) -> List[str]:
        """Preprocess text into a list of clean lines."""
        if not text:
            return []
        return [line.strip() for line in text.splitlines() if line.strip()]


class BaseExtractor(ABC):
    """
    Abstract base class for data extractors.
    
    Provides common functionality for file handling and data extraction.
    """
    
    def __init__(self, source_path: str, logger: Optional[logging.Logger] = None):
        self.source_path = Path(source_path)
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._validate_source()
    
    def _validate_source(self):
        """Validate the source file exists."""
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source file not found: {self.source_path}")
    
    @abstractmethod
    def extract(self) -> Dict[str, Any]:
        """Extract data from the source."""
        pass
    
    def save_results(self, data: Dict[str, Any], output_path: str) -> str:
        """Save extraction results to a file."""
        import json
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Results saved to: {output_file}")
        return str(output_file)


class BasePipeline(ABC):
    """
    Abstract base class for processing pipelines.
    
    Provides common functionality for pipeline orchestration.
    """
    
    def __init__(self, config: ConfigProtocol, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.results: Dict[str, Any] = {}
    
    @abstractmethod
    async def run(self) -> Dict[str, Any]:
        """Run the complete pipeline."""
        pass
    
    def log_stage(self, stage_name: str, success: bool = True, **kwargs):
        """Log pipeline stage completion."""
        status = "✅" if success else "❌"
        self.logger.info(f"{status} {stage_name}")
        
        for key, value in kwargs.items():
            self.logger.info(f"   {key}: {value}")
    
    def save_pipeline_results(self, output_dir: str = "data/processed") -> str:
        """Save pipeline results to JSON file."""
        import json
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        output_file = output_path / f"{self.__class__.__name__.lower()}_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Pipeline results saved to: {output_file}")
        return str(output_file)


class ProcessingError(Exception):
    """Base exception for processing errors."""
    pass


class ValidationError(ProcessingError):
    """Exception for validation errors."""
    pass


class ExtractionError(ProcessingError):
    """Exception for extraction errors."""
    pass


class PipelineError(ProcessingError):
    """Exception for pipeline errors."""
    pass