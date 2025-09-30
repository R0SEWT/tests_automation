"""
Centralized utilities for the HU processing system.

This module provides common utility functions that are used across
different components of the system.
"""

import logging
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import islice
import asyncio


class FileManager:
    """Utility class for file operations."""
    
    @staticmethod
    def read_text_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """Read text file content safely."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        try:
            return path.read_text(encoding=encoding).strip()
        except Exception as e:
            raise IOError(f"Error reading file {path}: {e}")
    
    @staticmethod
    def write_text_file(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
        """Write text file content safely."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            path.write_text(content, encoding=encoding)
        except Exception as e:
            raise IOError(f"Error writing file {path}: {e}")
    
    @staticmethod
    def read_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Read JSON file content safely."""
        try:
            content = FileManager.read_text_file(file_path)
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {file_path}: {e}")
    
    @staticmethod
    def write_json_file(file_path: Union[str, Path], data: Dict[str, Any], indent: int = 2) -> None:
        """Write JSON file content safely."""
        content = json.dumps(data, ensure_ascii=False, indent=indent)
        FileManager.write_text_file(file_path, content)


class TextProcessor:
    """Utility class for text processing operations."""
    
    @staticmethod
    def clean_lines(text: str) -> List[str]:
        """Clean and split text into non-empty lines."""
        if not text:
            return []
        return [line.strip() for line in text.splitlines() if line.strip()]
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text."""
        return re.sub(r'\s+', ' ', text.strip())
    
    @staticmethod
    def extract_pattern(text: str, pattern: str, group: int = 0) -> Optional[str]:
        """Extract pattern from text using regex."""
        match = re.search(pattern, text)
        return match.group(group) if match else None
    
    @staticmethod
    def find_matching_column(columns: List[str], patterns: List[str]) -> Optional[str]:
        """Find matching column name using pattern list."""
        lower_columns = [col.lower() for col in columns]
        
        for pattern in patterns:
            for i, col in enumerate(lower_columns):
                if pattern.lower() in col:
                    return columns[i]
        return None


class BatchProcessor:
    """Utility class for batch processing operations."""
    
    @staticmethod
    def create_batches(items: List[Any], batch_size: int) -> List[List[Any]]:
        """Create batches from a list of items."""
        if batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    @staticmethod
    def process_batches(
        items: List[Any],
        processor_func: Callable,
        batch_size: int = 10,
        max_workers: int = 4
    ) -> List[Any]:
        """Process items in batches using ThreadPoolExecutor."""
        batches = BatchProcessor.create_batches(items, batch_size)
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_batch = {
                executor.submit(processor_func, batch): batch 
                for batch in batches
            }
            
            for future in as_completed(future_to_batch):
                try:
                    batch_result = future.result()
                    if isinstance(batch_result, str):
                        results.extend(batch_result.splitlines())
                    elif isinstance(batch_result, list):
                        results.extend(batch_result)
                    else:
                        results.append(batch_result)
                except Exception as e:
                    logging.error(f"Error processing batch: {e}")
                    raise
        
        return results
    
    @staticmethod
    async def async_process_batches(
        items: List[Any],
        processor_func: Callable,
        batch_size: int = 10,
        max_concurrent: int = 4
    ) -> List[Any]:
        """Process items in batches asynchronously."""
        batches = BatchProcessor.create_batches(items, batch_size)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_batch_with_semaphore(batch):
            async with semaphore:
                return await processor_func(batch)
        
        tasks = [process_batch_with_semaphore(batch) for batch in batches]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logging.error(f"Error processing batch: {batch_result}")
                raise batch_result
            elif isinstance(batch_result, str):
                results.extend(batch_result.splitlines())
            elif isinstance(batch_result, list):
                results.extend(batch_result)
            else:
                results.append(batch_result)
        
        return results


class Validator:
    """Utility class for validation operations."""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate that required fields are present and non-empty."""
        errors = []
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
                errors.append(f"Empty required field: {field}")
        return errors
    
    @staticmethod
    def validate_file_exists(file_path: Union[str, Path]) -> bool:
        """Validate that a file exists."""
        return Path(file_path).exists()
    
    @staticmethod
    def validate_directory_writable(dir_path: Union[str, Path]) -> bool:
        """Validate that a directory is writable."""
        path = Path(dir_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            test_file = path / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False


class Logger:
    """Utility class for logging configuration."""
    
    @staticmethod
    def setup_logger(
        name: str,
        level: int = logging.INFO,
        format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ) -> logging.Logger:
        """Set up a logger with consistent formatting."""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(format_string))
            logger.addHandler(handler)
        
        return logger
    
    @staticmethod
    def log_performance(func: Callable) -> Callable:
        """Decorator to log function performance."""
        import time
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{func.__name__} completed in {execution_time:.2f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
                raise
        
        return wrapper


class DataFormatter:
    """Utility class for data formatting operations."""
    
    @staticmethod
    def format_hu_data(hu_code: str, title: str, description: str) -> str:
        """Format HU data for processing."""
        if title:
            return f"[{hu_code}] {title}\n\n{description}"
        return f"[{hu_code}] {description}"
    
    @staticmethod
    def format_test_case(hu_code: str, tc_id: str, description: str) -> str:
        """Format test case for processing."""
        return f"{hu_code}-{tc_id} {description}"
    
    @staticmethod
    def format_expected_result(hu_code: str, tc_id: str, expected: str) -> str:
        """Format expected result for processing."""
        return f"{hu_code}-{tc_id} {expected}"
    
    @staticmethod
    def parse_correction_output(output: str, separator: str = "OBS") -> tuple[List[str], List[str]]:
        """Parse AI correction output into observations and corrected text."""
        lines = output.splitlines()
        observations = []
        corrected = []
        
        for line in lines:
            if line.startswith(separator):
                observations.append(line)
            else:
                corrected.append(line)
        
        return observations, corrected


class PerformanceMonitor:
    """Utility class for performance monitoring."""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        import time
        self.metrics[operation] = {'start': time.time()}
    
    def end_timer(self, operation: str):
        """End timing an operation."""
        import time
        if operation in self.metrics and 'start' in self.metrics[operation]:
            self.metrics[operation]['duration'] = time.time() - self.metrics[operation]['start']
    
    def get_metrics(self) -> Dict[str, float]:
        """Get performance metrics."""
        return {op: data.get('duration', 0) for op, data in self.metrics.items()}
    
    def log_metrics(self, logger: logging.Logger):
        """Log performance metrics."""
        for operation, duration in self.get_metrics().items():
            logger.info(f"Performance - {operation}: {duration:.2f}s")