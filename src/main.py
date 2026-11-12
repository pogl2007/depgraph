import sys

from config import Config
from errors import ConfigError, RepositoryError
from graph import Graph, LocalRepository, NuGetSource
from nuget import NuGetRepository

EXIT_OK = 0
EXIT_ERROR = 1


def make_source(config):
    if config.test_mode:
        return LocalRepository(config.repo)
    return NuGetSource(NuGetRepository(config.repo))


def build_graph(config):
    source = make_source(config)
    root = source.start(config.package, config.version)
    return Graph(source, config.max_depth).build(root)


def print_graph(config, graph):
    print(f"Граф зависимостей {graph.root} (глубина {config.max_depth}):")
    for node, children in graph.edges.items():
        print(f"  {node}: {', '.join(children) or 'нет'}")
    print(f"Всего пакетов: {len(graph.edges)}")
    for cycle in graph.cycles:
        print(f"Циклическая зависимость: {' -> '.join(cycle)}")


def main(argv=None):
    config = Config.from_args(argv)
    try:
        config.validate()
        graph = build_graph(config)
    except (ConfigError, RepositoryError) as err:
        print(err)
        return EXIT_ERROR
    print_graph(config, graph)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
