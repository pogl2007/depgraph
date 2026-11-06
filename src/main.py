import sys

from config import Config
from errors import ConfigError

EXIT_OK = 0
EXIT_ERROR = 1


def main(argv=None):
    config = Config.from_args(argv)
    config.show()
    try:
        config.validate()
    except ConfigError as err:
        print(err)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
