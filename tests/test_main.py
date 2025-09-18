import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.redactionAssistant.main import main


class TestMain:
    """Test suite for main module functions"""

    @patch('src.redactionAssistant.main.Config')
    @patch('src.redactionAssistant.main.get_data')
    @patch('src.redactionAssistant.main.Processor')
    @patch('src.redactionAssistant.main.save_data')
    @patch('src.redactionAssistant.main.logging')
    def test_process_flow_success(self, mock_logging, mock_save_data, mock_processor_class,
                                  mock_get_data, mock_config_class):
        """Test successful process flow"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_config.all_output_paths.return_value = (Path("cps_out.txt"), Path("exp_out.txt"), Path("fb_out.txt"))

        mock_get_data.return_value = ("HU text", "CPS text", "EXP text")

        mock_processor = MagicMock()
        mock_processor.cps_corregidas.return_value = ("corrected CPS", "CPS feedback")
        mock_processor.exp_corregidos.return_value = ("corrected EXP", "EXP feedback")
        mock_processor_class.return_value = mock_processor

        # Import and call the function
        from src.redactionAssistant.main import process_flow
        process_flow()

        # Verify calls
        mock_config_class.assert_called_once()
        mock_get_data.assert_called_once_with(mock_config)
        mock_processor_class.assert_called_once_with(mock_config, mock_config.API_KEY)
        mock_processor.cps_corregidas.assert_called_once_with("HU text", "CPS text")
        mock_processor.exp_corregidos.assert_called_once_with("HU text", "corrected CPS", "EXP text")
        mock_save_data.assert_called_once_with(
            "corrected CPS",
            "corrected EXP",
            "CPS feedback\n\nEXP feedback",
            Path("cps_out.txt"),
            Path("exp_out.txt"),
            Path("fb_out.txt")
        )
        mock_logging.info.assert_called_with("Feedback resumido:\n%s", "CPS feedback\n\nEXP feedback")

    @patch('src.redactionAssistant.main.Config')
    @patch('src.redactionAssistant.main.get_data')
    @patch('src.redactionAssistant.main.Processor')
    @patch('src.redactionAssistant.main.save_data')
    @patch('src.redactionAssistant.main.logging')
    def test_process_flow_with_exception(self, mock_logging, mock_save_data, mock_processor_class,
                                        mock_get_data, mock_config_class):
        """Test process flow with exception"""
        mock_config_class.side_effect = Exception("Config error")

        from src.redactionAssistant.main import process_flow

        with pytest.raises(Exception, match="Config error"):
            process_flow()

    @patch('src.redactionAssistant.main.process_flow')
    @patch('src.redactionAssistant.main.logging')
    def test_main_success(self, mock_logging, mock_process_flow):
        """Test successful main execution"""
        mock_process_flow.return_value = None

        result = main()

        assert result == 0
        mock_process_flow.assert_called_once()
        mock_logging.info.assert_called_with("Proceso finalizado con éxito.")

    @patch('src.redactionAssistant.main.process_flow')
    @patch('src.redactionAssistant.main.logging')
    def test_main_with_exception(self, mock_logging, mock_process_flow):
        """Test main execution with exception"""
        mock_process_flow.side_effect = ValueError("Process error")

        result = main()

        assert result == 1
        mock_logging.exception.assert_called_with("Se produjo un error en el flujo principal.")