import pytest
from unittest.mock import patch, MagicMock
from src.redactionAssitant.main import main, process_flow


class TestMain:
    """Test suite for main module functions"""

    @patch('src.redactionAssitant.main.Config')
    @patch('src.redactionAssitant.main.get_data')
    @patch('src.redactionAssitant.main.Processor')
    @patch('src.redactionAssitant.main.save_data')
    @patch('src.redactionAssitant.main.logging')
    def test_process_flow_success(self, mock_logging, mock_save_data, mock_processor_class,
                                  mock_get_data, mock_config_class):
        """Test successful process flow"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        mock_get_data.return_value = ("HU text", "CPS text", "EXP text")

        mock_processor = MagicMock()
        mock_processor.cps_corregidas.return_value = ("corrected CPS", "CPS feedback")
        mock_processor.exp_corregidos.return_value = ("corrected EXP", "EXP feedback")
        mock_processor_class.return_value = mock_processor

        # Import and call the function
        from src.redactionAssitant.main import process_flow
        process_flow()

        # Verify calls
        mock_config_class.assert_called_once()
        mock_get_data.assert_called_once_with(mock_config)
        mock_processor_class.assert_called_once_with(mock_config, mock_config.API_KEY)
        mock_processor.cps_corregidas.assert_called_once_with("HU text", "CPS text")
        mock_processor.exp_corregidos.assert_called_once_with("HU text", "corrected CPS", "EXP text")
        mock_save_data.assert_called_once()

    @patch('src.redactionAssitant.main.Config')
    @patch('src.redactionAssitant.main.get_data')
    @patch('src.redactionAssitant.main.Processor')
    @patch('src.redactionAssitant.main.save_data')
    @patch('src.redactionAssitant.main.logging')
    def test_process_flow_with_exception(self, mock_logging, mock_save_data, mock_processor_class,
                                        mock_get_data, mock_config_class):
        """Test process flow with exception"""
        mock_config_class.side_effect = Exception("Config error")

        from src.redactionAssitant.main import process_flow

        with pytest.raises(Exception, match="Config error"):
            process_flow()

    @patch('sys.exit')
    @patch('src.redactionAssitant.main.process_flow')
    @patch('src.redactionAssitant.main.logging')
    def test_main_success(self, mock_logging, mock_process_flow, mock_exit):
        """Test successful main execution"""
        mock_process_flow.return_value = None

        result = main()

        mock_process_flow.assert_called_once()
        mock_logging.info.assert_called_with("Proceso finalizado con éxito.")
        mock_exit.assert_called_with(0)

    @patch('sys.exit')
    @patch('src.redactionAssitant.main.process_flow')
    @patch('src.redactionAssitant.main.logging')
    def test_main_with_exception(self, mock_logging, mock_process_flow, mock_exit):
        """Test main execution with exception"""
        mock_process_flow.side_effect = ValueError("Process error")

        result = main()

        mock_logging.exception.assert_called_with("Se produjo un error en el flujo principal.")
        mock_exit.assert_called_with(1)