import nox

@nox.session(python=["3.7","3.8"])
def tests(session):
    # same as pip install -r -requirements.txt
    session.install("-r", "requirements.txt")
    session.install("pytest")
    session.run("pytest", "-v", "tests")


@nox.session(python=["3.7", "3.8"])
def lint(session):
    session.install("flake8")
    session.install("flake8-docstrings")
    session.run("flake8", "./azure/")

@nox.session(python=["3.7", "3.8"])
def typecheck(session):
    session.install("-r", "requirements.txt")
    session.install("mypy")
    session.run("mypy", "./azure/")

@nox.session(python=["3.7", "3.8"])
def autopep(session):
    session.install("-r", "requirements.txt")
    session.run("autopep8", "--in-place --aggressive --aggressive --recursive \"./azure/\"")