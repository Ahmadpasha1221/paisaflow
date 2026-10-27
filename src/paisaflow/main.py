"""Package main entry point."""

import sys

from paisaflow.bootstrap import run_app


def main() -> None:
    sys.exit(run_app())


if __name__ == "__main__":
    main()
