"""Base module for the Python Durable functions.

Exposes the different API components intended for public consumption
"""
from .orchestrator import Orchestrator
from .entity import Entity
from .models.utils.entity_utils import EntityId
from .models.DurableOrchestrationClient import DurableOrchestrationClient
from .models.OrchestrationRuntimeStatus import OrchestrationRuntimeStatus
from .models.DurableOrchestrationContext import DurableOrchestrationContext
from .models.DurableEntityContext import DurableEntityContext
from .models.RetryOptions import RetryOptions
from .models.TokenSource import ManagedIdentityTokenSource
import json
import logging
import os
from pathlib import Path
import re
import sys
import warnings


_LOGGER = logging.getLogger(__name__)
_DURABLE_REQUIREMENT = re.compile(
    r"^azure[-_.]functions[-_.]durable(?:\[[^\]]+\])?\s*"
    r"(?P<specifier>(?:===|~=|==|!=|<=|>=|<|>).*)?$",
    re.IGNORECASE,
)
_VERSION_SPECIFIER = re.compile(
    r"(===|~=|==|<=|>=|!=|<|>)\s*([^,\s]+)"
)


class DurableFunctionsCompatibilityWarning(UserWarning):
    """Warn about application configurations incompatible with future releases."""


def validate_extension_bundles():
    """Raise a warning if host.json contains bundle-range V1.

    Effects
    ------
        Warning: Warning prompting the user to update to bundles V2
    """
    # No need to validate if we're running tests
    if "pytest" in sys.modules:
        return

    host_path = "host.json"
    bundles_key = "extensionBundle"
    version_key = "version"
    host_file = Path(host_path)

    if not host_file.exists():
        # If it doesn't exist, we ignore it
        return

    with open(host_path) as f:
        host_settings = json.loads(f.read())
        try:
            version_range = host_settings[bundles_key][version_key]
        except Exception:
            # If bundle info is not available, we ignore it.
            # For example: it's possible the user is using a manual extension install
            return
        # We do a best-effort attempt to detect bundles V1
        # This is the string hard-coded into the bundles V1 template in VSCode
        if version_range == "[1.*, 2.0.0)":
            message = "Your application is currently configured to use Extension Bundles V1."\
                " Durable Functions for Python works best with Bundles V2,"\
                " which provides additional features like Durable Entities, better performance,"\
                " and is actively being developed."\
                " Please update to Bundles V2 in your `host.json`."\
                " You can set extensionBundles version to be: [2.*, 3.0.0)"
            warnings.warn(message)


def _find_function_app_root():
    """Find the function app root without searching parent directories."""
    candidates = []
    script_root = os.environ.get("AzureWebJobsScriptRoot")
    if script_root:
        candidates.append(Path(script_root))
    candidates.append(Path.cwd())

    for candidate in candidates:
        if (candidate / "host.json").is_file():
            return candidate
    return None


def _release_parts(version):
    """Return the numeric release prefix of a version specifier."""
    match = re.match(r"^v?(\d+(?:\.\d+)*)", version)
    if match is None:
        return ()
    return tuple(int(part) for part in match.group(1).split("."))


def _specifier_excludes_v2(specifier):
    """Return whether a requirement specifier demonstrably excludes version 2."""
    for operator, version in _VERSION_SPECIFIER.findall(specifier):
        release = _release_parts(version)
        if not release:
            continue

        if operator in ("==", "===") and release[0] < 2:
            return True
        if operator == "~=" and release[0] < 2:
            return True
        if operator == "<":
            if release[0] < 2:
                return True
            if release[0] == 2 and all(part == 0 for part in release[1:]):
                return True
        if operator == "<=" and release[0] < 2:
            return True

    return False


def _requirements_exclude_v2(app_root):
    """Return whether requirements.txt demonstrably restricts the SDK below 2."""
    requirements_path = app_root / "requirements.txt"
    try:
        requirements = requirements_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    except (OSError, UnicodeError):
        _LOGGER.debug(
            "Unable to inspect %s for an azure-functions-durable version constraint.",
            requirements_path,
            exc_info=True,
        )
        return False

    for raw_line in requirements.splitlines():
        line = re.sub(r"\s+#.*$", "", raw_line).strip()
        # Evaluating PEP 508 markers requires packaging. Ignore conditional
        # pins rather than incorrectly treating a non-applicable pin as safe.
        if ";" in line:
            continue
        match = _DURABLE_REQUIREMENT.match(line)
        if match and _specifier_excludes_v2(match.group("specifier") or ""):
            return True
    return False


def _uses_v1_programming_model(app_root):
    """Return whether a direct child contains legacy function metadata."""
    try:
        with os.scandir(app_root) as entries:
            return any(
                entry.is_dir() and Path(entry.path, "function.json").is_file()
                for entry in entries
            )
    except OSError:
        _LOGGER.debug(
            "Unable to inspect %s for legacy function metadata.",
            app_root,
            exc_info=True,
        )
        return False


def validate_v1_programming_model():
    """Warn users of the unsupported functions.json programming model."""
    app_root = _find_function_app_root()
    if app_root is None or _requirements_exclude_v2(app_root):
        return

    if _uses_v1_programming_model(app_root):
        message = (
            "Your application uses the legacy Python v1 programming model, "
            "which relies on function.json files. This programming model is "
            "not supported by azure-functions-durable 2.x. Migrate to the "
            "Python v2 programming model before upgrading, or pin "
            "`azure-functions-durable<2` in your requirements.txt file."
        )
        warnings.warn(
            message,
            DurableFunctionsCompatibilityWarning,
            stacklevel=2,
        )


# Validate that users are not in extension bundles V1
validate_extension_bundles()

# Warn users whose applications will not be compatible with version 2.x
validate_v1_programming_model()

__all__ = [
    'Orchestrator',
    'Entity',
    'EntityId',
    'DurableOrchestrationClient',
    'DurableEntityContext',
    'DurableOrchestrationContext',
    'DurableFunctionsCompatibilityWarning',
    'ManagedIdentityTokenSource',
    'OrchestrationRuntimeStatus',
    'RetryOptions'
]

try:
    # disabling linter on this line because it fails to recognize the conditional export
    from .decorators.durable_app import (DFApp, Blueprint) # noqa
    __all__.append('DFApp')
    __all__.append('Blueprint')
except ModuleNotFoundError:
    pass

# Import OpenAI Agents integration (optional dependency)
try:
    from . import openai_agents # noqa
    __all__.append('openai_agents')
except ImportError:
    # OpenAI agents integration requires additional dependencies
    pass
