import sys

from config import Config
from errors import ConfigError, RepositoryError
from nuget import NuGetRepository

EXIT_OK = 0
EXIT_ERROR = 1


def load_dependencies(config):
    if config.test_mode:
        raise RepositoryError(
            "Ошибка: тестовый репозиторий будет поддержан на этапе 3")
    repository = NuGetRepository(config.repo)
    return repository.direct_dependencies(config.package, config.version)


def print_dependencies(config, dependencies):
    print(f"Прямые зависимости {config.package} {config.version}:")
    if not dependencies:
        print("  нет")
        return
    for dependency in dependencies:
        print(f"  {dependency}")
    print(f"Всего: {len(dependencies)}")


def main(argv=None):
    config = Config.from_args(argv)
    try:
        config.validate()
        dependencies = load_dependencies(config)
    except (ConfigError, RepositoryError) as err:
        print(err)
        return EXIT_ERROR
    print_dependencies(config, dependencies)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
