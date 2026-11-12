import pytest

from errors import RepositoryError
from graph import Graph, LocalRepository, NuGetSource, lowest_version
from main import EXIT_ERROR, EXIT_OK, main
from nuget import Dependency

DEEP = 10
ONE_LEVEL = 1
TWO_LEVELS = 2


class FakeSource:

    def __init__(self, packages):
        self.packages = packages

    def dependencies(self, node):
        return self.packages.get(node, [])


class FakeRepository:

    def __init__(self):
        self.calls = 0

    def direct_dependencies(self, package, version):
        self.calls += 1
        return [Dependency("System.Memory", "[4.5.5, 5.0)")]


def build(packages, depth=DEEP):
    return Graph(FakeSource(packages), depth).build("A")


@pytest.mark.parametrize("spec, version", [
    ("4.5.0", "4.5.0"),
    ("1.0", "1.0.0"),
    ("[1.0, 2.0)", "1.0.0"),
    ("(4.3.0, )", "4.3.0"),
    ("4.3.0.0", "4.3.0"),
    ("1.2.3.4", "1.2.3.4"),
    ("8.0.0-Preview.1", "8.0.0-preview.1"),
])
def test_lowest_version(spec, version):
    assert lowest_version(spec) == version


def test_bad_version():
    with pytest.raises(RepositoryError, match="непонятная версия"):
        lowest_version("*")


def test_transitive():
    graph = build({"A": ["B", "C"], "B": ["D"], "C": ["D"]})
    assert graph.edges == {"A": ["B", "C"], "B": ["D"], "D": [],
                           "C": ["D"]}
    assert graph.cycles == []


def test_max_depth():
    graph = build({"A": ["B"], "B": ["C"], "C": ["D"]}, TWO_LEVELS)
    assert list(graph.edges) == ["A", "B", "C"]
    assert graph.edges["C"] == []


def test_short_path_is_expanded_again():
    graph = build({"A": ["B", "C"], "B": ["C"], "C": ["D"]}, TWO_LEVELS)
    assert graph.levels["C"] == ONE_LEVEL
    assert graph.edges["C"] == ["D"]


def test_cycle():
    graph = build({"A": ["B"], "B": ["C"], "C": ["A"]})
    assert graph.cycles == [("A", "B", "C", "A")]


def test_self_cycle():
    assert build({"A": ["A"]}).cycles == [("A", "A")]


def test_nuget_source_cache():
    repository = FakeRepository()
    source = NuGetSource(repository)
    node = source.start("Serilog", "3.1.1")
    assert source.dependencies(node) == ["System.Memory 4.5.5"]
    source.dependencies(node)
    assert repository.calls == ONE_LEVEL


def test_local_repository(tmp_path):
    path = tmp_path / "repo.txt"
    path.write_text("A: B C\n\nB:\n", encoding="utf-8")
    repository = LocalRepository(str(path))
    assert repository.start("A", "1.0") == "A"
    assert repository.dependencies("A") == ["B", "C"]
    assert repository.dependencies("C") == []


@pytest.mark.parametrize("text", ["A -> B\n", "A: b\n", "a: B\n"])
def test_local_repository_bad_line(tmp_path, text):
    path = tmp_path / "repo.txt"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(RepositoryError, match="строка 1"):
        LocalRepository(str(path))


def test_local_repository_unknown_package(tmp_path):
    path = tmp_path / "repo.txt"
    path.write_text("A:\n", encoding="utf-8")
    with pytest.raises(RepositoryError, match="нет в тестовом"):
        LocalRepository(str(path)).start("Z", "1.0")


def test_main_test_mode(capsys):
    code = main(["--package", "A", "--repo", "test_repos/cycle.txt",
                 "--test-mode", "--version", "1.0", "--max-depth",
                 str(DEEP)])
    assert code == EXIT_OK
    out = capsys.readouterr().out
    assert "  C: A, D\n" in out
    assert "Циклическая зависимость: A -> B -> C -> A" in out


def test_main_broken_repository(capsys):
    code = main(["--package", "A", "--repo", "test_repos/broken.txt",
                 "--test-mode", "--version", "1.0"])
    assert code == EXIT_ERROR
    assert "строка 2" in capsys.readouterr().out
