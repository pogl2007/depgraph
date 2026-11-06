import pytest

from config import DEFAULT_DEPTH, MAX_NAME_LENGTH, MIN_DEPTH, Config
from errors import ConfigError
from main import EXIT_ERROR, EXIT_OK, main

URL = "https://api.nuget.org/v3-flatcontainer/"
PACKAGE = "Serilog"
VERSION = "3.1.1"
CUSTOM_DEPTH = 5
BAD_DEPTH = MIN_DEPTH - 1
NEGATIVE_DEPTH = -1
LONG_NAME = "A" * (MAX_NAME_LENGTH + 1)
ERRORS_AT_ONCE = 3


def make(**changes):
    params = {"package": PACKAGE, "repo": URL, "version": VERSION,
              "max_depth": DEFAULT_DEPTH, "test_mode": False}
    params.update(changes)
    return Config(**params)


def test_from_args():
    config = Config.from_args([
        "--package", PACKAGE, "--repo", URL,
        "--version", VERSION, "--max-depth", str(CUSTOM_DEPTH),
    ])
    assert config.package == PACKAGE
    assert config.repo == URL
    assert config.version == VERSION
    assert config.max_depth == CUSTOM_DEPTH
    assert config.test_mode is False


def test_default_depth():
    config = Config.from_args(
        ["--package", PACKAGE, "--repo", URL, "--version", VERSION])
    assert config.max_depth == DEFAULT_DEPTH


def test_show(capsys):
    make().show()
    assert capsys.readouterr().out == (
        f"package={PACKAGE}\n"
        f"repo={URL}\n"
        "test_mode=False\n"
        f"version={VERSION}\n"
        f"max_depth={DEFAULT_DEPTH}\n"
    )


def test_valid_config():
    make().validate()


def test_valid_test_mode(tmp_path):
    path = tmp_path / "graph.txt"
    path.write_text("A: B\n", encoding="utf-8")
    make(repo=str(path), test_mode=True).validate()


@pytest.mark.parametrize("changes, message", [
    ({"package": ""}, "не может быть пустым"),
    ({"package": "bad name"}, "недопустимое имя пакета"),
    ({"package": LONG_NAME}, "слишком длинное"),
    ({"repo": "ftp://example.com"}, "должен начинаться с http"),
    ({"repo": "no_such.txt", "test_mode": True}, "не найден"),
    ({"version": "abc"}, "неверный формат версии"),
    ({"version": "1"}, "неверный формат версии"),
    ({"max_depth": BAD_DEPTH}, f"не меньше {MIN_DEPTH}"),
])
def test_invalid(changes, message):
    with pytest.raises(ConfigError, match=message):
        make(**changes).validate()


def test_all_errors_at_once():
    config = make(package="", version="x", max_depth=NEGATIVE_DEPTH)
    with pytest.raises(ConfigError) as info:
        config.validate()
    assert len(str(info.value).splitlines()) == ERRORS_AT_ONCE


def test_depth_not_number():
    with pytest.raises(SystemExit):
        Config.from_args(["--package", PACKAGE, "--repo", URL,
                          "--version", VERSION, "--max-depth", "abc"])


def test_missing_required():
    with pytest.raises(SystemExit):
        Config.from_args(["--package", PACKAGE])


def test_main_exit_codes(capsys):
    good = ["--package", PACKAGE, "--repo", URL, "--version", VERSION]
    bad = ["--package", PACKAGE, "--repo", "x", "--version", VERSION]
    assert main(good) == EXIT_OK
    assert main(bad) == EXIT_ERROR
    assert "Ошибка" in capsys.readouterr().out
