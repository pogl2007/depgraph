import re

from errors import RepositoryError

PACKAGE_LINE = re.compile(r"([A-Z]+):((\s+[A-Z]+)*)\s*")
VERSION_NUMBER = re.compile(r"\d+(\.\d+)*(-[0-9A-Za-z.-]+)?")
MIN_PARTS = 3


def lowest_version(spec):
    found = VERSION_NUMBER.search(spec)
    if not found:
        raise RepositoryError(f"Ошибка: непонятная версия зависимости {spec}")
    numbers, dash, label = found.group().partition("-")
    parts = numbers.split(".")
    while len(parts) < MIN_PARTS:
        parts.append("0")
    if len(parts) > MIN_PARTS and parts[-1] == "0":
        parts = parts[:MIN_PARTS]
    return ".".join(parts) + dash + label.lower()


class LocalRepository:

    def __init__(self, path):
        try:
            with open(path, encoding="utf-8") as file:
                lines = file.read().splitlines()
        except (OSError, UnicodeDecodeError) as err:
            raise RepositoryError(
                f"Ошибка: не удалось прочитать файл {path}") from err
        self.packages = {}
        for number, line in enumerate(lines, start=1):
            if line.strip():
                self.parse_line(number, line)

    def parse_line(self, number, line):
        match = PACKAGE_LINE.fullmatch(line.strip())
        if not match:
            raise RepositoryError(
                f"Ошибка: строка {number} тестового репозитория "
                f"имеет неверный формат: {line}")
        self.packages[match.group(1)] = match.group(2).split()

    def start(self, package, version):
        if package not in self.packages:
            raise RepositoryError(
                f"Ошибка: пакета {package} нет в тестовом репозитории")
        return package

    def dependencies(self, node):
        return self.packages.get(node, [])


class NuGetSource:

    def __init__(self, repository):
        self.repository = repository
        self.cache = {}

    def start(self, package, version):
        return f"{package} {version}"

    def dependencies(self, node):
        if node not in self.cache:
            package, version = node.split(" ")
            found = self.repository.direct_dependencies(package, version)
            self.cache[node] = [
                f"{item.name} {lowest_version(item.version)}"
                for item in found]
        return self.cache[node]


class Graph:

    def __init__(self, source, max_depth):
        self.source = source
        self.max_depth = max_depth
        self.root = None
        self.edges = {}
        self.levels = {}
        self.cycles = []

    def build(self, root):
        self.root = root
        self.walk(root, 0, ())
        return self

    def walk(self, node, level, stack):
        if node in stack:
            cycle = stack[stack.index(node):] + (node,)
            if cycle not in self.cycles:
                self.cycles.append(cycle)
            return
        if node in self.levels and self.levels[node] <= level:
            return
        self.levels[node] = level
        self.edges[node] = []
        if level >= self.max_depth:
            return
        for child in self.source.dependencies(node):
            self.edges[node].append(child)
            self.walk(child, level + 1, stack + (node,))
