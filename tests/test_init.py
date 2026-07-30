import importlib
import warnings

import pytest

import azure.durable_functions as df


def create_function_app(tmp_path, requirement, legacy=True):
    (tmp_path / "host.json").write_text("{}")
    (tmp_path / "requirements.txt").write_text(requirement)

    if legacy:
        function_dir = tmp_path / "MyFunction"
        function_dir.mkdir()
        (function_dir / "function.json").write_text("{}")
    else:
        (tmp_path / "function_app.py").write_text("")


@pytest.mark.parametrize(
    "requirement",
    [
        "azure-functions-durable",
        "azure-functions-durable>=1.2",
        "azure-functions-durable<2.1",
        "azure-functions-durable<=2",
        "azure-functions-durable==2.*",
        "azure-functions-durable~=2.0",
        (
            'azure-functions-durable<2 ; python_version < "3.9"\n'
            'azure-functions-durable ; python_version >= "3.9"'
        ),
    ],
)
def test_unpinned_v1_programming_model_warns(monkeypatch, tmp_path, requirement):
    create_function_app(tmp_path, requirement)

    monkeypatch.chdir(tmp_path)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(df)

    compatibility_warnings = [
        warning for warning in caught
        if warning.category is df.DurableFunctionsCompatibilityWarning
    ]

    assert len(compatibility_warnings) == 1
    assert "legacy Python v1 programming model" in str(
        compatibility_warnings[0].message
    )
    assert "azure-functions-durable<2" in str(
        compatibility_warnings[0].message
    )


@pytest.mark.parametrize(
    "requirement",
    [
        "azure-functions-durable<2",
        "azure-functions-durable>=1.2,<2",
        "azure-functions-durable==1.6.0",
        "azure-functions-durable==1.*",
        "azure-functions-durable~=1.6",
        "Azure.Functions_Durable >= 1.2, < 2  # remain on v1",
    ],
)
def test_pinned_v1_programming_model_does_not_warn(
    monkeypatch,
    tmp_path,
    requirement,
):
    create_function_app(tmp_path, requirement)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        df,
        "_uses_v1_programming_model",
        lambda app_root: pytest.fail("pinned apps should not scan functions"),
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        df.validate_v1_programming_model()

    assert caught == []


def test_v1_programming_model_warns_during_pytest(monkeypatch, tmp_path):
    create_function_app(tmp_path, "azure-functions-durable")

    monkeypatch.chdir(tmp_path)

    with pytest.warns(df.DurableFunctionsCompatibilityWarning):
        df.validate_v1_programming_model()


def test_undecodable_requirements_does_not_break_import(monkeypatch, tmp_path):
    create_function_app(tmp_path, "azure-functions-durable")
    (tmp_path / "requirements.txt").write_bytes(b"\xff")

    monkeypatch.chdir(tmp_path)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(df)

    assert any(
        warning.category is df.DurableFunctionsCompatibilityWarning
        for warning in caught
    )


def test_directory_without_host_json_does_not_warn(monkeypatch, tmp_path):
    function_dir = tmp_path / "MyFunction"
    function_dir.mkdir()
    (function_dir / "function.json").write_text("{}")

    monkeypatch.chdir(tmp_path)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        df.validate_v1_programming_model()

    assert caught == []


def test_v2_programming_model_does_not_warn(monkeypatch, tmp_path):
    create_function_app(tmp_path, "azure-functions-durable", legacy=False)

    monkeypatch.chdir(tmp_path)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(df)

    assert caught == []
