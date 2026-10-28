"""Linux packaging script building a production standalone archive for PaisaFlow."""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path


def get_version(project_root: Path) -> str:
    init_py = project_root / "src" / "paisaflow" / "__init__.py"
    if init_py.exists():
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_py.read_text(encoding="utf-8"))
        if match:
            return match.group(1)
    return "0.1.0"


def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def build() -> int:
    project_root = Path(__file__).parent.parent.resolve()
    version = get_version(project_root)
    main_script = project_root / "main.py"
    qml_dir = project_root / "src" / "paisaflow" / "presentation" / "qml"
    assets_dir = project_root / "assets"
    icons_dir = assets_dir / "icons"

    print("==================================================")
    print(f"Building PaisaFlow Desktop Application v{version} (Linux x64)")
    print("==================================================")
    print(f"Project root: {project_root}")
    print(f"Main entry:   {main_script}")

    # 1. Ensure icons are generated
    gen_script = project_root / "scripts" / "generate_icons.py"
    if gen_script.exists():
        print("\n[Step 1/5] Generating platform icons...")
        subprocess.run([sys.executable, str(gen_script)], cwd=str(project_root), check=True)

    # 2. Compile Qt resources
    print("\n[Step 2/5] Compiling Qt resources (resources.qrc)...")
    qrc_file = qml_dir / "resources.qrc"
    qrc_py = qml_dir / "resources_rc.py"
    try:
        subprocess.run(["pyside6-rcc", str(qrc_file), "-o", str(qrc_py)], check=True)
        print(f"Compiled resources to: {qrc_py}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.run([sys.executable, "-m", "PySide6.scripts.rcc", str(qrc_file), "-o", str(qrc_py)], check=True)
            print(f"Compiled resources via module to: {qrc_py}")
        except Exception as e:
            print(f"Warning: RCC compilation encountered: {e}. Using existing resources_rc.py if present.")

    # 3. PyInstaller bundle
    print("\n[Step 3/5] Running PyInstaller standalone build...")
    icon_png = icons_dir / "brand.png"
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name=PaisaFlow",
        "--windowed",
        f"--add-data={qml_dir}{os.pathsep}paisaflow/presentation/qml",
        f"--add-data={icons_dir}{os.pathsep}assets/icons",
        "--hidden-import=PySide6.QtQuick",
        "--hidden-import=PySide6.QtQml",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtQuickControls2",
        "--hidden-import=sqlalchemy",
        "--hidden-import=sqlalchemy.dialects.sqlite",
        "--hidden-import=alembic",
        "--hidden-import=pydantic",
        str(main_script),
    ]
    if icon_png.exists():
        cmd.append(f"--icon={icon_png}")

    result = subprocess.run(cmd, cwd=str(project_root))
    if result.returncode != 0:
        print(f"\nPyInstaller build failed with exit code: {result.returncode}", file=sys.stderr)
        return result.returncode

    dist_app_dir = project_root / "dist" / "PaisaFlow"
    exe_path = dist_app_dir / "PaisaFlow"
    if not exe_path.exists():
        print(f"Error: Expected executable not found at {exe_path}", file=sys.stderr)
        return 1

    # Ensure executable bit
    try:
        exe_path.chmod(0o755)
    except Exception:
        pass

    # Add .desktop entry and README to package
    desktop_file = dist_app_dir / "paisaflow.desktop"
    desktop_file.write_text(
        f"""[Desktop Entry]
Name=PaisaFlow
Comment=Personal finance, made clear. Offline-first desktop money manager.
Exec=PaisaFlow
Icon=paisaflow
Terminal=false
Type=Application
Categories=Office;Finance;
Version={version}
""",
        encoding="utf-8",
    )

    readme_file = dist_app_dir / "README.txt"
    readme_file.write_text(
        f"""PaisaFlow v{version} — Linux x64 Standalone Package
==================================================

Prerequisites:
  - 64-bit Linux distribution (Ubuntu 20.04+, Debian 11+, Fedora 36+, Arch Linux)
  - Wayland or X11 desktop environment
  - Standard GLIBC >= 2.31 and libGL / libxcb installed

To run PaisaFlow:
  ./PaisaFlow

User Data Directory:
  All SQLite databases, backups, and logs are stored under:
  ~/.local/share/paisaflow/

To override data directory:
  PAISAFLOW_DATA_DIR=/path/to/data ./PaisaFlow
""",
        encoding="utf-8",
    )

    # 4. Create tar.gz distribution archive
    print("\n[Step 4/5] Packaging tar.gz distribution archive...")
    tar_filename = f"PaisaFlow-{version}-linux-x64.tar.gz"
    tar_path = project_root / "dist" / tar_filename

    if tar_path.exists():
        tar_path.unlink()

    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(dist_app_dir, arcname="PaisaFlow")

    tar_size_mb = tar_path.stat().st_size / (1024 * 1024)
    print(f"Created archive: {tar_path} ({tar_size_mb:.2f} MB)")

    # 5. Generate SHA-256 checksum
    print("\n[Step 5/5] Generating SHA-256 checksum...")
    sha256_hash = compute_sha256(tar_path)
    sha_file = project_root / "dist" / f"{tar_filename}.sha256"
    sha_file.write_text(f"{sha256_hash}  {tar_filename}\n", encoding="utf-8")
    print(f"SHA-256: {sha256_hash}")
    print(f"Checksum written to: {sha_file}")

    print("\n==================================================")
    print("Linux Build Summary:")
    print(f"  Version:   {version}")
    print(f"  Directory: {dist_app_dir}")
    print(f"  Artifact:  {tar_path} ({tar_size_mb:.2f} MB)")
    print(f"  SHA-256:   {sha256_hash}")
    print("==================================================")
    return 0


if __name__ == "__main__":
    sys.exit(build())
