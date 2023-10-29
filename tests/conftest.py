import pytest

pytest_plugins = ["pytester"]


@pytest.fixture
def tmphome(tmpdir, monkeypatch):
    monkeypatch.setenv("HOME", str(tmpdir))
    monkeypatch.setenv("USERPROFILE", str(tmpdir))

    with tmpdir.as_cwd():
        yield tmpdir
