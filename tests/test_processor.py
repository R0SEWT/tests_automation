import pytest
from unittest.mock import Mock, patch
from src.redactionAssistant.processor import Processor, cps_with_exp, preprocess_exp_or_cps


class MockConfig:
    """Mock configuration class for testing"""
    def __init__(self):
        self.code_hu = "USRNM"


class TestProcessor:
    """Test suite for Processor class"""

    @pytest.fixture
    def mock_config(self):
        """Fixture for mock configuration"""
        return MockConfig()

    @pytest.fixture
    def mock_builder(self):
        """Fixture for mock builder"""
        builder = Mock()
        builder.corregir_ortografia.return_value = "USRNM001 Caso corregido\nOBS: Se corrigió ortografía\nUSRNM002 Caso corregido 2\nOBS: Se corrigió ortografía 2"
        builder.obtener_feedback.return_value = "Feedback de corrección"
        builder.corregir_expect_result.return_value = "ExpRes1: Resultado corregido\nOBS: Se mejoró redacción"
        return builder

    @pytest.fixture
    def processor(self, mock_config, mock_builder):
        """Fixture for Processor instance with mocked dependencies"""
        with patch('src.redactionAssistant.processor.b.Builder') as mock_builder_class:
            mock_builder_class.return_value = mock_builder
            with patch('src.redactionAssistant.processor.OpenAI'):
                return Processor(mock_config, "test_api_key")

    def test_init_success(self, mock_config):
        """Test successful initialization"""
        with patch('src.redactionAssistant.processor.b.Builder'):
            with patch('src.redactionAssistant.processor.OpenAI'):
                proc = Processor(mock_config, "test_key")
                assert proc.cfg == mock_config
                assert proc.batch_size == 20

    def test_init_no_api_key(self, mock_config):
        """Test initialization failure with no API key"""
        with pytest.raises(ValueError, match="API key is required"):
            Processor(mock_config, "")

    def test_init_openai_failure(self, mock_config):
        """Test initialization failure with OpenAI client error"""
        with patch('src.redactionAssistant.processor.OpenAI') as mock_openai:
            mock_openai.side_effect = Exception("Connection failed")
            with pytest.raises(Exception, match="Connection failed"):
                Processor(mock_config, "test_key")

    def test_cps_corregidas_happy_path(self, processor, mock_builder):
        """Test successful correction of test cases"""
        hu = "Como usuario quiero login"
        cps = "USRNM001 Validar login\nUSRNM002 Validar logout"

        result, feedback = processor.cps_corregidas(hu, cps)

        assert "USRNM001 Caso corregido" in result
        assert "USRNM002 Caso corregido 2" in result
        assert feedback == "Feedback de corrección"
        mock_builder.corregir_ortografia.assert_called()
        mock_builder.obtener_feedback.assert_called_once()

    def test_cps_corregidas_empty_inputs(self, processor):
        """Test handling of empty inputs"""
        result, feedback = processor.cps_corregidas("", "")
        assert result == ""
        assert feedback == ""

    def test_cps_corregidas_no_cases_found(self, processor, mock_builder):
        """Test when no corrected cases are found"""
        mock_builder.corregir_ortografia.return_value = "Some random text"

        result, feedback = processor.cps_corregidas("HU", "USRNM001 Test")

        assert result == ""
        assert feedback == ""

    def test_cps_corregidas_mismatch_count(self, processor, mock_builder):
        """Test when corrected cases count doesn't match original"""
        mock_builder.corregir_ortografia.return_value = "USRNM001 Corrected"  # Only one case

        result, feedback = processor.cps_corregidas("HU", "USRNM001 Test\nUSRNM002 Test2")

        assert result == ""
        assert feedback == ""

    def test_exp_corregidos_happy_path(self, processor, mock_builder):
        """Test successful correction of expected results"""
        hu = "Como usuario quiero login"
        cps = "USRNM001 Validar login\nUSRNM002 Validar logout"
        exp = "Sistema permite acceso\nSistema cierra sesión"

        result, feedback = processor.exp_corregidos(hu, cps, exp)

        assert "Resultado corregido" in result
        assert feedback == "Feedback de corrección"
        mock_builder.corregir_expect_result.assert_called()

    def test_exp_corregidos_empty_inputs(self, processor):
        """Test handling of empty inputs for expected results"""
        result, feedback = processor.exp_corregidos("", "", "")
        assert result == ""
        assert feedback == ""

    def test_exp_corregidos_mismatch_lines(self, processor):
        """Test when CPS and EXP have different line counts"""
        result, feedback = processor.exp_corregidos("HU", "One line\n\n", "Two\nLines\n")
        assert result == ""
        assert feedback == ""

    def test_exp_corregidos_no_results(self, processor, mock_builder):
        """Test when no corrected results are found"""
        mock_builder.corregir_expect_result.return_value = "Some random text"
        mock_builder.obtener_feedback.return_value = ""

        result, feedback = processor.exp_corregidos("HU", "USRNM001 Test", "Expected result")

        assert result == ""
        assert feedback == ""

    def test_exp_corregidos_handles_blank_lines_and_formats_batches(self, processor, mock_builder):
        """Test that blank lines are ignored and batches are sent as plain text"""
        hu = "Como usuario quiero login"
        cps = "USRNM001 Validar login\n\n   \nUSRNM002 Validar logout\n"
        exp = "\n Sistema permite acceso \n\nSistema cierra sesión  \n"

        result, feedback = processor.exp_corregidos(hu, cps, exp)

        assert "Resultado corregido" in result
        assert feedback == "Feedback de corrección"

        mock_builder.corregir_expect_result.assert_called_once()
        args, _ = mock_builder.corregir_expect_result.call_args
        sent_prompt = args[0]

        assert isinstance(sent_prompt, str)
        assert "[" not in sent_prompt and "]" not in sent_prompt
        assert "USRNM001 Validar login | Sistema permite acceso" in sent_prompt
        assert "USRNM002 Validar logout | Sistema cierra sesión" in sent_prompt


class TestHelperFunctions:
    """Test suite for helper functions"""

    def test_cps_with_exp_success(self):
        """Test successful combination of CPS and EXP"""
        cps = "USRNM001 Test 1\nUSRNM002 Test 2"
        exp = "Result 1\nResult 2"

        result = cps_with_exp(cps, exp)

        assert len(result) == 2
        assert "USRNM001 Test 1 | Result 1" in result[0]
        assert "USRNM002 Test 2 | Result 2" in result[1]

    def test_cps_with_exp_empty_inputs(self):
        """Test handling of empty inputs"""
        assert cps_with_exp("", "") == []
        assert cps_with_exp("test", "") == []
        assert cps_with_exp("", "test") == []

    def test_cps_with_exp_whitespace_handling(self):
        """Test proper whitespace handling"""
        cps = "  USRNM001 Test  \n\n  USRNM002 Test  "
        exp = "  Result 1  \n\n  Result 2  "

        result = cps_with_exp(cps, exp)

        assert len(result) == 2
        assert result[0] == "USRNM001 Test | Result 1"
        assert result[1] == "USRNM002 Test | Result 2"

    def test_preprocess_exp_or_cps_success(self):
        """Test successful preprocessing"""
        text = "  Line 1  \n\n  Line 2  \n  "

        result = preprocess_exp_or_cps(text)

        assert result == ["Line 1", "Line 2"]

    def test_preprocess_exp_or_cps_empty(self):
        """Test preprocessing with empty input"""
        assert preprocess_exp_or_cps("") == []
        assert preprocess_exp_or_cps("   \n\n   ") == []

    def test_preprocess_exp_or_cps_single_line(self):
        """Test preprocessing with single line"""
        result = preprocess_exp_or_cps("Single line")
        assert result == ["Single line"]