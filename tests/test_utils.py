import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from src.redactionAssitant.utils import get_data, save_data, procesar_en_batches


class TestUtils:
    """Test suite for utility functions"""

    @patch('src.redactionAssitant.utils.Path')
    def test_get_data_success(self, mock_path_class):
        """Test successful data loading"""
        # Mock paths
        mock_hus_path = MagicMock()
        mock_cps_path = MagicMock()
        mock_exp_path = MagicMock()

        mock_hus_path.exists.return_value = True
        mock_cps_path.exists.return_value = True
        mock_exp_path.exists.return_value = True

        mock_hus_path.read_text.return_value = "Historia de usuario\n"
        mock_cps_path.read_text.return_value = "Caso de prueba 1\nCaso de prueba 2\n"
        mock_exp_path.read_text.return_value = "Resultado esperado 1\nResultado esperado 2\n"

        # Mock the input_path method calls
        mock_config = MagicMock()
        mock_config.input_path.side_effect = [mock_hus_path, mock_cps_path, mock_exp_path]

        hus, cps, exp = get_data(mock_config)

        assert hus == "Historia de usuario"
        assert cps == "Caso de prueba 1\nCaso de prueba 2"
        assert exp == "Resultado esperado 1\nResultado esperado 2"

    @patch('src.redactionAssitant.utils.Path')
    def test_get_data_file_not_found(self, mock_path_class):
        """Test file not found error"""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path

        mock_config = MagicMock()
        mock_config.input_path.return_value = mock_path

        with pytest.raises(FileNotFoundError, match="Archivo HUS no encontrado"):
            get_data(mock_config)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_data_success(self, mock_file):
        """Test successful data saving"""
        save_data("cps data", "exp data", "feedback data", "cps_path", "exp_path", "fb_path")

        # Verify all files were opened and written correctly
        assert mock_file.call_count == 3

        # Check that write was called for each file
        calls = mock_file().write.call_args_list
        assert calls[0][0][0] == "cps data"
        assert calls[1][0][0] == "exp data"
        assert calls[2][0][0] == "feedback data"

    @patch('builtins.open', new_callable=mock_open)
    def test_save_data_with_exception(self, mock_file):
        """Test save data with file write error"""
        mock_file.side_effect = IOError("Write error")

        with pytest.raises(IOError, match="Write error"):
            save_data("data", "data", "data", "path1", "path2", "path3")

    def test_procesar_en_batches_success(self):
        """Test successful batch processing"""
        def mock_processor(batch):
            return "\n".join([f"processed_{item}" for item in batch])

        items = ["item1", "item2", "item3", "item4", "item5"]
        result = procesar_en_batches(items, mock_processor, batch_size=2)

        expected = ["processed_item1", "processed_item2", "processed_item3", "processed_item4", "processed_item5"]
        assert result == expected

    def test_procesar_en_batches_empty_list(self):
        """Test batch processing with empty list"""
        def mock_processor(batch):
            return [f"processed_{item}" for item in batch]

        result = procesar_en_batches([], mock_processor, batch_size=2)
        assert result == []

    def test_procesar_en_batches_single_batch(self):
        """Test batch processing with single batch"""
        def mock_processor(batch):
            return "\n".join([f"processed_{item}" for item in batch])

        items = ["item1", "item2"]
        result = procesar_en_batches(items, mock_processor, batch_size=5)

        expected = ["processed_item1", "processed_item2"]
        assert result == expected

    def test_procesar_en_batches_invalid_batch_size(self):
        """Test batch processing with invalid batch size"""
        def mock_processor(batch):
            return [f"processed_{item}" for item in batch]

        with pytest.raises(ValueError, match="batch_size debe ser mayor que 0"):
            procesar_en_batches(["item1"], mock_processor, batch_size=0)

    def test_procesar_en_batches_processor_exception(self):
        """Test batch processing with processor exception"""
        def failing_processor(batch):
            raise ValueError("Processor failed")

        items = ["item1", "item2"]

        with pytest.raises(ValueError, match="Processor failed"):
            procesar_en_batches(items, failing_processor, batch_size=2)