import nox

CFS_PYPI_INDEX = (
    "https://pkgs.dev.azure.com/azfunc/public/"
    "_packaging/upstream-public/pypi/simple/"
)

# Mirror the supported range exercised by CI (.github/workflows/validate.yml).
# nox automatically skips interpreters that aren't installed locally.
SUPPORTED_PYTHONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]

# Lint and autopep run on a single canonical version: on Python 3.12+ the PEP
# 701 f-string tokenization changes cause pycodestyle false positives, so CI
# lints only on 3.10 and we match that here.
CANONICAL_PYTHON = "3.10"


def use_cfs(session):
    session.env["PIP_INDEX_URL"] = CFS_PYPI_INDEX
    session.env.pop("PIP_EXTRA_INDEX_URL", None)


@nox.session(python=SUPPORTED_PYTHONS)
def tests(session):
    use_cfs(session)
    # same as pip install -r -requirements.txt
    session.install("-r", "requirements.txt")
    session.install("pytest")
    session.run("pytest", "-v", "tests")


@nox.session(python=CANONICAL_PYTHON)
def lint(session):
    use_cfs(session)
    session.install("flake8")
    session.install("flake8-docstrings")
    session.run("flake8", "./azure/")

@nox.session(python=SUPPORTED_PYTHONS)
def typecheck(session):
    use_cfs(session)
    session.install("-r", "requirements.txt")
    session.install("mypy")
    session.run("mypy", "./azure/")

@nox.session(python=CANONICAL_PYTHON)
def autopep(session):
    use_cfs(session)
    session.install("-r", "requirements.txt")
    session.run("autopep8", "--in-place --aggressive --aggressive --recursive \"./azure/\"")
