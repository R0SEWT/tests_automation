import pytest
from unittest.mock import Mock, patch, MagicMock
from src.redactionAssistant.builder import Builder


class TestBuilder:
    """Test suite for Builder class"""

    @pytest.fixture
    def mock_client(self):
        """Fixture for mock OpenAI client"""
        client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Mocked response content"
        client.chat.completions.create.return_value = mock_response
        return client

    @pytest.fixture
    def builder(self, mock_client):
        """Fixture for Builder instance"""
        return Builder(mock_client)

    def test_init(self, mock_client):
        """Test Builder initialization"""
        builder = Builder(mock_client)
        assert builder.client == mock_client
        assert builder.model == "deepseek-chat"

    def test_corregir_ortografia_success(self, builder, mock_client):
        """Test successful orthography correction"""
        hu = "Como usuario quiero login"
        cps = ["USRNM001 Validar login", "USRNM002 Validar logout"]

        result = builder.corregir_ortografia(hu, cps)

        assert result == "Mocked response content"
        mock_client.chat.completions.create.assert_called_once()

        # Verify the call arguments
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "deepseek-chat"
        assert len(call_args[1]["messages"]) == 2
        assert "Eres un experto en pruebas de software" in call_args[1]["messages"][0]["content"]
        assert hu in call_args[1]["messages"][1]["content"]
        assert "USRNM001 Validar login" in call_args[1]["messages"][1]["content"]

    def test_corregir_ortografia_empty_inputs(self, builder, mock_client, caplog):
        """Test orthography correction with empty inputs"""
        with caplog.at_level("WARNING"):
            result = builder.corregir_ortografia("", [])

        assert "Historia de usuario o casos de prueba vacíos" in caplog.text
        mock_client.chat.completions.create.assert_called_once()

    def test_corregir_ortografia_api_error(self, builder, mock_client):
        """Test orthography correction with API error"""
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        result = builder.corregir_ortografia("HU", ["Test case"])

        assert "Error al corregir ortografía: API Error" in result

    def test_obtener_feedback_success(self, builder, mock_client):
        """Test successful feedback generation"""
        obs_text = "OBS1: Se corrigió ortografía\nOBS2: Se mejoró redacción"

        result = builder.obtener_feedback(obs_text)

        assert result == "Mocked response content"
        mock_client.chat.completions.create.assert_called_once()

        # Verify the call arguments
        call_args = mock_client.chat.completions.create.call_args
        assert "feedback claro y conciso" in call_args[1]["messages"][0]["content"]
        assert obs_text in call_args[1]["messages"][1]["content"]

    def test_obtener_feedback_api_error(self, builder, mock_client):
        """Test feedback generation with API error"""
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        result = builder.obtener_feedback("Some observations")

        assert "Error: API Error" in result

    def test_corregir_expect_result_success(self, builder, mock_client):
        """Test successful expected result correction"""
        cps_exp_text = "USRNM001 Test | Expected result"

        result = builder.corregir_expect_result(cps_exp_text)

        assert result == "Mocked response content"
        mock_client.chat.completions.create.assert_called_once()

        # Verify the call arguments
        call_args = mock_client.chat.completions.create.call_args
        assert "corregir la ortografía y mejorar la redacción" in call_args[1]["messages"][0]["content"]
        assert cps_exp_text in call_args[1]["messages"][1]["content"]
        assert "ExpRes1:" in call_args[1]["messages"][2]["content"]

    def test_corregir_expect_result_api_error(self, builder, mock_client):
        """Test expected result correction with API error"""
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        result = builder.corregir_expect_result("Test data")

        assert "Error: API Error" in result

    def test_prompt_construction_ortografia(self, builder, mock_client):
        """Test that orthography correction prompt is constructed correctly"""
        hu = "Test HU"
        cps = ["Test CP1", "Test CP2"]

        builder.corregir_ortografia(hu, cps)

        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][1]["content"]

        # Verify key elements in prompt
        assert "Eres un experto en QA" in prompt
        assert "Historia de Usuario:" in prompt
        assert hu in prompt
        assert "Casos de prueba:" in prompt
        assert "Test CP1" in prompt
        assert "Test CP2" in prompt
        assert "Fin de instrucción" in prompt

    def test_prompt_construction_feedback(self, builder, mock_client):
        """Test that feedback prompt is constructed correctly"""
        obs = "Test observations"

        builder.obtener_feedback(obs)

        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][1]["content"]

        # Verify key elements in prompt
        assert "observaciones de corrección:" in prompt
        assert obs in prompt
        assert "texto plano" in prompt

    def test_prompt_construction_expect_result(self, builder, mock_client):
        """Test that expected result correction prompt is constructed correctly"""
        data = "Test data"

        builder.corregir_expect_result(data)

        call_args = mock_client.chat.completions.create.call_args
        system_prompt = call_args[1]["messages"][0]["content"]
        user_prompt1 = call_args[1]["messages"][1]["content"]
        user_prompt2 = call_args[1]["messages"][2]["content"]

        # Verify key elements in prompts
        assert "corregir la ortografía y mejorar la redacción" in system_prompt
        assert data in user_prompt1
        assert "ExpRes1:" in user_prompt2
        assert "OBS:" in user_prompt2
        assert "tiempo presente" in user_prompt2

    def test_corregir_expect_result_accepts_list_without_python_syntax(self, builder, mock_client):
        """Ensure list inputs are transformed into clean multiline prompts"""
        data = ["CP1 | Exp1", "CP2 | Exp2"]

        builder.corregir_expect_result(data)

        call_args = mock_client.chat.completions.create.call_args
        user_prompt = call_args[1]["messages"][1]["content"]

        assert "[" not in user_prompt and "]" not in user_prompt
        assert "CP1 | Exp1" in user_prompt
        assert "CP2 | Exp2" in user_prompt
        assert "CP1 | Exp1\nCP2 | Exp2" in user_prompt

    @pytest.mark.parametrize("method_name,expected_log_message", [
        ("corregir_ortografia", "Error al llamar a la API"),
        ("obtener_feedback", "Error al obtener feedback"),
        ("corregir_expect_result", "Error al corregir expected results"),
    ])
    def test_error_logging(self, builder, mock_client, caplog, method_name, expected_log_message):
        """Test that errors are properly logged"""
        mock_client.chat.completions.create.side_effect = Exception("Test error")

        with caplog.at_level("ERROR"):
            if method_name == "corregir_ortografia":
                builder.corregir_ortografia("HU", ["Test"])
            elif method_name == "obtener_feedback":
                builder.obtener_feedback("Test")
            elif method_name == "corregir_expect_result":
                builder.corregir_expect_result("Test")

        assert expected_log_message in caplog.text
        assert "Test error" in caplog.text