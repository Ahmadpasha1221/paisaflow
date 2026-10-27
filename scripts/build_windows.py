"""Windows packaging script building a standalone executable for PaisaFlow."""

import os
import subprocess
import sys
from pathlib import Path


def build() -> int:
    project_root = Path(__file__).parent.parent.resolve()
    main_script = project_root / "main.py"
    qml_dir = project_root / "src" / "paisaflow" / "presentation" / "qml"

    print("==================================================")
    print("Building PaisaFlow Desktop Application for Windows")
    print("==================================================")
    print(f"Project root: {project_root}")
    print(f"Main entry:   {main_script}")
    print(f"QML assets:   {qml_dir}")

    # PyInstaller arguments
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name=PaisaFlow",
        "--windowed",  # No console window in production release
        f"--add-data={qml_dir}{os.pathsep}paisaflow/presentation/qml",
        "--hidden-import=PySide6.QtQuick",
        "--hidden-import=PySide6.QtQml",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=sqlalchemy",
        "--hidden-import=sqlalchemy.dialects.sqlite",
        "--hidden-import=alembic",
        "--hidden-import=pydantic",
        str(main_script),
    ]

    print("\nRunning build command:")
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=str(project_root))
    if result.returncode == 0:
        dist_path = project_root / "dist" / "PaisaFlow"
        print("\nBuild successful!")
        print(f"Distribution package located at: {dist_path}")
    else:
        print("\nBuild failed with exit code:", result.returncode, file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
