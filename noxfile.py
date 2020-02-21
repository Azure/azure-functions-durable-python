import nox

@nox.session(python="3.7")
def tests(session):
    # same as pip install -r -requirements.txt
    session.install("-r", "requirements.txt")
    session.install("pytest")
    session.run("pytest")

