from cleo import Application

from opyapi.__version__ import __version__
from .generate_dto import GenerateDtoCommand

application = Application(
    name="opyapi",
    version=__version__,
)
application.add(GenerateDtoCommand())


def main() -> None:
    application.run()


if __name__ == "__main__":
    main()
