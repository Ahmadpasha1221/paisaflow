"""Main entry point for PaisaFlow desktop application."""

import sys
from pathlib import Path

# Add src to sys.path if not present
src_dir = Path(__file__).parent / "src"
if src_dir.exists() and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from paisaflow.bootstrap import run_app  # noqa: E402


def main() -> None:
    sys.exit(run_app())


if __name__ == "__main__":
    main()
