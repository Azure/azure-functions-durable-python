#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.


class UsageTelemetry:
    """Handles telemetry logging for OpenAI Agents SDK integration usage."""

    # Class-level flag to ensure logging happens only once across all instances
    _usage_logged = False

    @classmethod
    def log_usage_once(cls):
        """Log OpenAI Agents SDK integration usage exactly once.

        Fails gracefully if metadata cannot be retrieved.
        """
        if cls._usage_logged:
            return

        # NOTE: Any log line beginning with the special prefix defined below will be
        # captured by the Azure Functions host as a Language Worker console log and
        # forwarded to internal telemetry pipelines.
        # Do not change this constant value without coordinating with the Functions
        # host team.
        LANGUAGE_WORKER_CONSOLE_LOG_PREFIX = "LanguageWorkerConsoleLog"

        package_versions = cls._collect_openai_agent_package_versions()
        msg = (
            f"{LANGUAGE_WORKER_CONSOLE_LOG_PREFIX}"  # Prefix captured by Azure Functions host
            "Detected OpenAI Agents SDK integration with Durable Functions. "
            f"Package versions: {package_versions}"
        )
        print(msg)

        cls._usage_logged = True

    @classmethod
    def _collect_openai_agent_package_versions(cls) -> str:
        """Collect versions of relevant packages for telemetry logging.

        Returns
        -------
        str
            Comma-separated list of name=version entries or "(unavailable)" if
            versions could not be determined.
        """
        try:
            try:
                from importlib import metadata  # Python 3.8+
            except ImportError:  # pragma: no cover - legacy fallback
                import importlib_metadata as metadata  # type: ignore

            package_names = [
                "azure-functions-durable",
                "openai",
                "openai-agents",
            ]

            versions = []
            for package_name in package_names:
                try:
                    ver = metadata.version(package_name)
                    versions.append(f"{package_name}={ver}")
                except Exception:  # noqa: BLE001 - swallow and continue
                    versions.append(f"{package_name}=(not installed)")

            return ", ".join(versions) if versions else "(unavailable)"
        except Exception:  # noqa: BLE001 - never let version gathering break user code
            return "(unavailable)"
