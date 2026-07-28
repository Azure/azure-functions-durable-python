import importlib
import sys
import warnings

import azure.durable_functions as df


def test_v1_programming_model_warns(monkeypatch, tmp_path):
    function_dir = tmp_path / "MyFunction"
    function_dir.mkdir()
    (function_dir / "function.json").write_text("{}")

    monkeypatch.chdir(tmp_path)
    monkeypatch.delitem(sys.modules, "pytest")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(df)

    assert len(caught) == 1
    assert "legacy Python v1 programming model" in str(caught[0].message)
    assert "azure-functions-durable<2" in str(caught[0].message)


def test_v2_programming_model_does_not_warn(monkeypatch, tmp_path):
    (tmp_path / "function_app.py").write_text("")

    monkeypatch.chdir(tmp_path)
    monkeypatch.delitem(sys.modules, "pytest")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(df)

    assert caught == []
