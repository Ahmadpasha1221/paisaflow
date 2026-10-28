"""Generate platform-specific icon assets from the master brand.png.

Source of truth:
  assets/icons/brand.png

Outputs:
  - Windows: assets/icons/brand.ico (16, 24, 32, 48, 64, 128, 256)
  - macOS:   assets/icons/brand.icns (16, 32, 64, 128, 256, 512, 1024)
  - Linux:   assets/icons/hicolor/<size>x<size>/apps/paisaflow.png (standard freedesktop sizes)
"""

import sys
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets" / "icons"
SOURCE_IMAGE = ASSETS_DIR / "brand.png"


def generate_icons() -> int:
    if not SOURCE_IMAGE.exists():
        print(f"Error: Source image not found at {SOURCE_IMAGE}", file=sys.stderr)
        return 1

    print(f"Loading master brand asset: {SOURCE_IMAGE}")
    with Image.open(SOURCE_IMAGE) as img:
        img = img.convert("RGBA")
        print(f"Master dimensions: {img.size}, mode: {img.mode}")

        # 1. Windows Multi-Resolution ICO
        ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        ico_path = ASSETS_DIR / "brand.ico"
        img.save(ico_path, format="ICO", sizes=ico_sizes)
        print(f"Generated Windows multi-res ICO: {ico_path} (sizes: {[s[0] for s in ico_sizes]})")

        # 2. macOS ICNS
        icns_path = ASSETS_DIR / "brand.icns"
        img.save(icns_path, format="ICNS")
        print(f"Generated macOS ICNS: {icns_path}")

        # 3. Linux Freedesktop Hicolor Icons
        linux_sizes = [16, 24, 32, 48, 64, 128, 256, 512]
        for size in linux_sizes:
            hicolor_dir = ASSETS_DIR / "hicolor" / f"{size}x{size}" / "apps"
            hicolor_dir.mkdir(parents=True, exist_ok=True)
            out_file = hicolor_dir / "paisaflow.png"
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(out_file, format="PNG")
            # Also save flat reference size
            flat_file = ASSETS_DIR / f"brand_{size}x{size}.png"
            resized.save(flat_file, format="PNG")

        print(f"Generated Linux desktop icon hierarchy under {ASSETS_DIR / 'hicolor'}")

    print("All platform icon assets successfully generated.")
    return 0


if __name__ == "__main__":
    sys.exit(generate_icons())
