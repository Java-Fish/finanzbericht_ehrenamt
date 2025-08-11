#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimaler CI Build-Script für GitHub Actions.
Ziele:
- Plattform erkennen
- PyInstaller Build durchführen (onefile wo sinnvoll)
- macOS zusätzlich .pkg Versuch + .tar.gz Archiv
- Windows: .exe
- Linux: Binary
- Keine E-Mails / keine externen Benachrichtigungen

Verwendung (in GitHub Action):
  python ci_build.py

Optionale Umgebungsvariablen:
  APP_VERSION  -> überschreibt Versionsnummer (sonst aus pyproject.toml oder default 0.0.0)
"""
from __future__ import annotations

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import re

ROOT = Path(__file__).parent
BUILD = ROOT / "build"
APP_NAME = "Finanzauswertung_Ehrenamt"  # Für Executables (keine Leerzeichen)
DISPLAY_NAME = "Finanzauswertung Ehrenamt"


def log(msg: str):
    print(msg, flush=True)


def read_version() -> str:
    v = os.environ.get("APP_VERSION")
    if v:
        return v
    pyproject = ROOT / "pyproject.toml"
    if pyproject.exists():
        m = re.search(r"^version\s*=\s*\"([^\"]+)\"", pyproject.read_text(encoding="utf-8"), re.MULTILINE)
        if m:
            return m.group(1)
    return "0.0.0"


def ensure_clean_build():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True, exist_ok=True)


def data_arg(src_folder: str, dest_name: str) -> str:
    sep = ";" if platform.system() == "Windows" else ":"
    return f"{ROOT / src_folder}{sep}{dest_name}"


def base_pyinstaller_cmd() -> list[str]:
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--distpath", str(BUILD),
        "--workpath", str(BUILD / "temp"),
        "--specpath", str(BUILD / "temp"),
        "--add-data", data_arg("resources", "resources"),
        "--add-data", data_arg("src", "src"),
        "--hidden-import", "PySide6",
        "--hidden-import", "pandas",
        "--hidden-import", "openpyxl",
        "--hidden-import", "chardet",
    ]
    return cmd


def build_windows():
    log("🪟 Windows Build")
    cmd = base_pyinstaller_cmd() + [
        "--onefile",
        "--noconsole",
        "--icon", str(ROOT / "resources" / "icons" / "app_icon.ico"),
        "main.py",
    ]
    return run(cmd, "Windows .exe")


def build_linux():
    log("🐧 Linux Build")
    cmd = base_pyinstaller_cmd() + [
        "--onefile",
        "--icon", str(ROOT / "resources" / "icons" / "app_icon.png"),
        "main.py",
    ]
    return run(cmd, "Linux Binary")


def build_macos():
    log("🍎 macOS Build (.app + .pkg)")
    cmd = base_pyinstaller_cmd() + [
        "--onedir",
        "--windowed",
    ]
    icns = ROOT / "resources" / "icons" / "app_icon.icns"
    if icns.exists():
        cmd += ["--icon", str(icns)]
    else:
        png = ROOT / "resources" / "icons" / "app_icon.png"
        if png.exists():
            cmd += ["--icon", str(png)]
    cmd += ["main.py"]
    if not run(cmd, ".app onedir Basis"):
        return False
    app_dir = BUILD / APP_NAME
    if not app_dir.exists():
        log("❌ Erwarteter App-Ordner nicht gefunden")
        return False
    archive = BUILD / f"{APP_NAME}.tar.gz"
    subprocess.run(["tar", "-czf", str(archive), APP_NAME], cwd=BUILD, check=False)
    pkg_target = BUILD / f"{APP_NAME}.pkg"
    pkgbuild = shutil.which("pkgbuild")
    if pkgbuild:
        identifier = "org.ehrenamt.finanzauswertung"
        try:
            subprocess.run([
                pkgbuild,
                "--root", str(app_dir),
                "--identifier", identifier,
                "--version", read_version(),
                str(pkg_target)
            ], check=True)
        except subprocess.CalledProcessError as e:
            log(f"⚠️ pkgbuild fehlgeschlagen: {e}")
    else:
        log("ℹ️ pkgbuild nicht verfügbar – nur .tar.gz erstellt")
    return True


def run(cmd: list[str], label: str) -> bool:
    log("📦 " + label + ": " + " ".join(cmd))
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode == 0:
        log(f"✅ {label} erfolgreich")
        return True
    log(f"❌ {label} fehlgeschlagen")
    log(result.stdout)
    log(result.stderr)
    return False


def main() -> int:
    ensure_clean_build()
    sys_platform = platform.system()
    ok = False
    if sys_platform == "Windows":
        ok = build_windows()
    elif sys_platform == "Linux":
        ok = build_linux()
    elif sys_platform == "Darwin":
        ok = build_macos()
    else:
        log(f"❌ Nicht unterstützte Plattform: {sys_platform}")
        return 1

    if ok:
        log("\n🔍 Build Dateien:")
        for p in BUILD.glob("**/*"):
            if p.is_file():
                log(f"  • {p.relative_to(BUILD)} ({p.stat().st_size} B)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
