"""Windows packaging script building a production standalone executable for PaisaFlow."""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import zipfile
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
    brand_ico = icons_dir / "brand.ico"
    brand_png = icons_dir / "brand.png"

    print("==================================================")
    print(f"Building PaisaFlow Desktop Application v{version} (Windows x64)")
    print("==================================================")
    print(f"Project root: {project_root}")
    print(f"Main entry:   {main_script}")

    # 1. Ensure icons are generated
    if not brand_ico.exists():
        print("\n[Step 1/5] Generating platform icons...")
        gen_script = project_root / "scripts" / "generate_icons.py"
        res = subprocess.run([sys.executable, str(gen_script)], cwd=str(project_root))
        if res.returncode != 0:
            print("Icon generation failed!", file=sys.stderr)
            return res.returncode
    else:
        print("\n[Step 1/5] Platform icons verified.")

    # 2. Compile Qt resources
    print("\n[Step 2/5] Compiling Qt resources (resources.qrc)...")
    qrc_file = qml_dir / "resources.qrc"
    qrc_py = qml_dir / "resources_rc.py"
    rcc_cmd = ["pyside6-rcc", str(qrc_file), "-o", str(qrc_py)]
    try:
        subprocess.run(rcc_cmd, check=True)
        print(f"Compiled resources to: {qrc_py}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.run([sys.executable, "-m", "PySide6.scripts.rcc", str(qrc_file), "-o", str(qrc_py)], check=True)
            print(f"Compiled resources via module to: {qrc_py}")
        except Exception as e:
            print(f"Warning: RCC compilation encountered: {e}. Using existing resources_rc.py if present.")

    # 3. PyInstaller bundle
    print("\n[Step 3/5] Running PyInstaller standalone build...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name=PaisaFlow",
        "--windowed",  # No console window in production release
        f"--icon={brand_ico}",
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

    result = subprocess.run(cmd, cwd=str(project_root))
    if result.returncode != 0:
        print(f"\nPyInstaller build failed with exit code: {result.returncode}", file=sys.stderr)
        return result.returncode

    dist_app_dir = project_root / "dist" / "PaisaFlow"
    exe_path = dist_app_dir / "PaisaFlow.exe"
    if not exe_path.exists():
        print(f"Error: Expected executable not found at {exe_path}", file=sys.stderr)
        return 1

    print(f"\nPyInstaller build completed successfully: {exe_path}")

    # 4. Create ZIP distribution archive
    print("\n[Step 4/5] Packaging distribution archive...")
    zip_filename = f"PaisaFlow-{version}-windows-x64.zip"
    zip_path = project_root / "dist" / zip_filename

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for file in dist_app_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(project_root / "dist")
                zipf.write(file, arcname)

    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"Created archive: {zip_path} ({zip_size_mb:.2f} MB)")

    # 5. Generate SHA-256 checksum
    print("\n[Step 5/5] Generating SHA-256 checksum...")
    sha256_hash = compute_sha256(zip_path)
    sha_file = project_root / "dist" / f"{zip_filename}.sha256"
    sha_file.write_text(f"{sha256_hash}  {zip_filename}\n", encoding="utf-8")
    print(f"SHA-256: {sha256_hash}")
    print(f"Checksum written to: {sha_file}")

    print("\n==================================================")
    print("Windows Build Summary:")
    print(f"  Version:   {version}")
    print(f"  Directory: {dist_app_dir}")
    print(f"  Artifact:  {zip_path} ({zip_size_mb:.2f} MB)")
    print(f"  SHA-256:   {sha256_hash}")
    print("==================================================")
    return 0


if __name__ == "__main__":
    sys.exit(build())
