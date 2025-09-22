#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest.mock


class TestUsageTelemetry:
    """Test cases for the UsageTelemetry class."""

    def test_log_usage_once_logs_message_on_first_call(self, capsys):
        """Test that log_usage_once logs the telemetry message."""
        # Reset any previous state by creating a fresh import
        import importlib
        from azure.durable_functions.openai_agents import usage_telemetry
        importlib.reload(usage_telemetry)
        UsageTelemetryFresh = usage_telemetry.UsageTelemetry

        def mock_version(package_name):
            if package_name == "azure-functions-durable":
                return "1.3.4"
            elif package_name == "openai":
                return "1.98.0"
            elif package_name == "openai-agents":
                return "0.2.5"
            return "unknown"

        with unittest.mock.patch('importlib.metadata.version', side_effect=mock_version):
            UsageTelemetryFresh.log_usage_once()

            captured = capsys.readouterr()
            assert captured.out.startswith("LanguageWorkerConsoleLog")
            assert "Detected OpenAI Agents SDK integration with Durable Functions." in captured.out
            assert "azure-functions-durable=1.3.4" in captured.out
            assert "openai=1.98.0" in captured.out
            assert "openai-agents=0.2.5" in captured.out

    def test_log_usage_handles_package_version_errors(self, capsys):
        """Test that log_usage_once handles package version lookup errors gracefully."""
        # Reset any previous state by creating a fresh import
        import importlib
        from azure.durable_functions.openai_agents import usage_telemetry
        importlib.reload(usage_telemetry)
        UsageTelemetryFresh = usage_telemetry.UsageTelemetry

        # Test with mixed success/failure scenario: some packages work, others fail
        def mock_version(package_name):
            if package_name == "azure-functions-durable":
                return "1.3.4"
            elif package_name == "openai":
                raise Exception("Package not found")
            elif package_name == "openai-agents":
                return "0.2.5"
            return "unknown"

        with unittest.mock.patch('importlib.metadata.version', side_effect=mock_version):
            UsageTelemetryFresh.log_usage_once()

            captured = capsys.readouterr()
            assert captured.out.startswith("LanguageWorkerConsoleLog")
            assert "Detected OpenAI Agents SDK integration with Durable Functions." in captured.out
            # Should handle errors gracefully: successful packages show versions, failed ones show "(not installed)"
            assert "azure-functions-durable=1.3.4" in captured.out
            assert "openai=(not installed)" in captured.out
            assert "openai-agents=0.2.5" in captured.out

    def test_log_usage_works_with_real_packages(self, capsys):
        """Test that log_usage_once works with real package versions."""
        # Reset any previous state by creating a fresh import
        import importlib
        from azure.durable_functions.openai_agents import usage_telemetry
        importlib.reload(usage_telemetry)
        UsageTelemetryFresh = usage_telemetry.UsageTelemetry

        # Test without mocking to see the real behavior
        UsageTelemetryFresh.log_usage_once()

        captured = capsys.readouterr()
        assert captured.out.startswith("LanguageWorkerConsoleLog")
        assert "Detected OpenAI Agents SDK integration with Durable Functions." in captured.out
        # Should contain some version information or (unavailable)
        assert ("azure-functions-durable=" in captured.out or "(unavailable)" in captured.out)

    def test_log_usage_once_is_idempotent(self, capsys):
        """Test that multiple calls to log_usage_once only log once."""
        # Reset any previous state by creating a fresh import
        import importlib
        from azure.durable_functions.openai_agents import usage_telemetry
        importlib.reload(usage_telemetry)
        UsageTelemetryFresh = usage_telemetry.UsageTelemetry

        with unittest.mock.patch('importlib.metadata.version', return_value="1.0.0"):
            # Call multiple times
            UsageTelemetryFresh.log_usage_once()
            UsageTelemetryFresh.log_usage_once()
            UsageTelemetryFresh.log_usage_once()

            captured = capsys.readouterr()
            # Should only see one log message despite multiple calls
            log_count = captured.out.count("LanguageWorkerConsoleLogDetected OpenAI Agents SDK integration")
            assert log_count == 1