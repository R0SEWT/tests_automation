import pytest
from unittest.mock import patch, MagicMock
from src.redactionAssitant.config import Config


class TestConfig:
    """Test suite for Config class"""

    @patch.dict('os.environ', {'DS_API_KEY': 'test_api_key'})
    def test_init_success(self):
        """Test successful configuration initialization"""
        config = Config()
        assert config.API_KEY == 'test_api_key'
        assert config.code_hu == 'USRNM'

    @patch.dict('os.environ', {}, clear=True)
    def test_init_no_api_key(self):
        """Test initialization failure when API key is missing"""
        with pytest.raises(ValueError, match="DS_API_KEY no encontrada"):
            Config()

    @patch.dict('os.environ', {'DS_API_KEY': 'test_api_key'})
    def test_input_path(self):
        """Test input path generation"""
        config = Config()
        path = config.input_path('hus')
        assert str(path).endswith('data/raw/UserStory.txt')

    @patch.dict('os.environ', {'DS_API_KEY': 'test_api_key'})
    def test_input_path_invalid_key(self):
        """Test input path with invalid key"""
        config = Config()
        with pytest.raises(ValueError, match="Clave 'invalid' no válida"):
            config.input_path('invalid')

    @patch.dict('os.environ', {'DS_API_KEY': 'test_api_key'})
    def test_output_path(self):
        """Test output path generation"""
        config = Config()
        path = config.output_path('cps')
        assert str(path).endswith('data/processed/TestCases.txt')

    @patch.dict('os.environ', {'DS_API_KEY': 'test_api_key'})
    def test_output_path_invalid_key(self):
        """Test output path with invalid key"""
        config = Config()
        with pytest.raises(ValueError, match="Clave 'invalid' no válida"):
            config.output_path('invalid')

    @patch.dict('os.environ', {'DS_API_KEY': 'test_api_key'})
    def test_all_output_paths(self):
        """Test all output paths tuple"""
        config = Config()
        cps_path, exp_path, fb_path = config.all_output_paths()

        assert str(cps_path).endswith('data/processed/TestCases.txt')
        assert str(exp_path).endswith('data/processed/expectedResults.txt')
        assert str(fb_path).endswith('data/processed/feedback.txt')