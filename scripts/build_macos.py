"""macOS packaging script building a production standalone application bundle for PaisaFlow."""

import hashlib
import os
import platform
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
    arch = platform.machine() or "x86_64"
    if arch.lower() in ("arm64", "aarch64"):
        arch_label = "arm64"
    else:
        arch_label = "x86_64"

    main_script = project_root / "main.py"
    qml_dir = project_root / "src" / "paisaflow" / "presentation" / "qml"
    assets_dir = project_root / "assets"
    icons_dir = assets_dir / "icons"
    brand_icns = icons_dir / "brand.icns"

    print("==================================================")
    print(f"Building PaisaFlow Desktop Application v{version} (macOS {arch_label})")
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
    print("\n[Step 3/5] Running PyInstaller macOS app bundle build...")
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
        "--osx-bundle-identifier=com.paisaflow.desktop",
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
    if brand_icns.exists():
        cmd.append(f"--icon={brand_icns}")

    result = subprocess.run(cmd, cwd=str(project_root))
    if result.returncode != 0:
        print(f"\nPyInstaller build failed with exit code: {result.returncode}", file=sys.stderr)
        return result.returncode

    app_bundle = project_root / "dist" / "PaisaFlow.app"
    if not app_bundle.exists():
        # Might be in dist/PaisaFlow/ if not generated directly at dist/
        alt_bundle = project_root / "dist" / "PaisaFlow" / "PaisaFlow.app"
        if alt_bundle.exists():
            app_bundle = alt_bundle
        else:
            print(f"Error: Expected .app bundle not found at {app_bundle}", file=sys.stderr)
            return 1

    print(f"\nApp bundle generated: {app_bundle}")

    # 4. Create ZIP distribution archive
    print("\n[Step 4/5] Packaging ZIP distribution archive...")
    zip_filename = f"PaisaFlow-{version}-macos-{arch_label}.zip"
    zip_path = project_root / "dist" / zip_filename

    if zip_path.exists():
        zip_path.unlink()

    # Use ditto or zip to preserve symlinks and permissions on macOS
    try:
        subprocess.run(
            ["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(app_bundle), str(zip_path)],
            check=True,
        )
    except Exception:
        # Fallback to python zipfile
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for file in app_bundle.rglob("*"):
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
    print("macOS Build Summary:")
    print(f"  Version:   {version}")
    print(f"  Bundle:    {app_bundle}")
    print(f"  Artifact:  {zip_path} ({zip_size_mb:.2f} MB)")
    print(f"  SHA-256:   {sha256_hash}")
    print("==================================================")
    return 0


if __name__ == "__main__":
    sys.exit(build())
