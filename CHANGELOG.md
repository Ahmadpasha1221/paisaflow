# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-10-28

### Added
- **Multi-Platform Production Packaging**:
  - Windows standalone distribution (`PaisaFlow-0.1.0-windows-x64.zip`) with embedded icon and windowed execution.
  - Linux standalone distribution (`PaisaFlow-0.1.0-linux-x64.tar.gz`) with freedesktop `.desktop` launcher and documentation.
  - macOS application bundle (`PaisaFlow-0.1.0-macos-<arch>.zip`) with embedded `.icns` bundle.
- **Brand Assets & Icon Integration**:
  - Generated multi-resolution Windows icon (`brand.ico`) covering 16x16, 24x24, 32x32, 48x48, 64x64, 128x128, and 256x256 resolutions from master `brand.png`.
  - Generated macOS Apple Icon Image (`brand.icns`) with Retina up to 1024x1024.
  - Generated standard Linux hicolor desktop icons from 16x16 to 512x512.
  - Automated icon generator script `scripts/generate_icons.py`.
- **Windows Taskbar Identity & AppUserModelID**:
  - Explicit Windows AppUserModelID registration (`PaisaFlow.Flowline.Desktop.0.1.0`) preventing grouping under the generic Python executable.
- **Diagnostic Logging**:
  - Structured file logging to `%LOCALAPPDATA%\PaisaFlow\logs\paisaflow.log` (Windows), `~/.local/share/paisaflow/logs/` (Linux), and `~/Library/Application Support/PaisaFlow/logs/` (macOS).
  - Clear exception capture and diagnostic traces on startup failures.
- **Cross-Platform Data Paths**:
  - Implemented standard XDG data directory resolution for Linux, Application Support for macOS, and LOCALAPPDATA for Windows, with `PAISAFLOW_DATA_DIR` environment override.
- **GitHub Actions CI/CD Release Pipeline**:
  - Automated multi-platform workflow (`.github/workflows/release.yml`) testing, building, packaging, and publishing versioned GitHub Releases on `v*` tags with SHA-256 checksums.

### Fixed
- Fixed Windows taskbar icon showing the generic Python logo when running via `python main.py` or development environments.
- Fixed `TopBar is not a type` startup crash by registering missing component files in `resources.qrc`.
- Fixed `Splash.qml` null-reference warnings and startup geometry crashes.
- Fixed PySide6 6.12+ QQuickItem active focus and wrapMode property test conversion issues.

---

### Security & Privacy Invariants
- 100% offline-first operations: zero telemetry, zero analytics, zero external network requests.
- Strict double-entry ledger bookkeeping with integer minor units (Paise).
- User data directories remain strictly decoupled from application binaries across upgrades.
