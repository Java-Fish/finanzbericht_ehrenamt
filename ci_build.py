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
VERSION_FILE = ROOT / "version"


def log(msg: str):
    print(msg, flush=True)


def read_version() -> str:
    # Priorität: ENV > version Datei > pyproject.toml > fallback
    v = os.environ.get("APP_VERSION")
    if v:
        return v.strip()
    if VERSION_FILE.exists():
        content = VERSION_FILE.read_text(encoding="utf-8").strip()
        if content:
            return content
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
    "--hidden-import", "fitz",      # PyMuPDF
    "--hidden-import", "PIL",       # Pillow
    "--hidden-import", "odf",       # odfpy
    ]
    return cmd


def build_windows():
    log("🪟 Windows Build")
    icon_path = ROOT / "resources" / "icons" / "app_icon.ico"
    cmd = base_pyinstaller_cmd() + ["--onefile", "--noconsole"]
    if icon_path.exists():
        cmd += ["--icon", str(icon_path)]
    cmd += ["main.py"]
    if run(cmd, "Windows .exe (onefile)"):
        # Versioniertes Umbenennen
        exe = BUILD / f"{APP_NAME}.exe"
        if exe.exists():
            versioned = BUILD / f"{APP_NAME}-{read_version()}.exe"
            try:
                if versioned.exists():
                    versioned.unlink()
                exe.rename(versioned)
                log(f"🔖 Versioniertes Artefakt: {versioned.name}")
            except Exception as e:
                log(f"⚠️ Konnte {exe.name} nicht umbenennen: {e}")
        return True
    log("⚠️ Onefile Build fehlgeschlagen – versuche onedir Fallback")
    fallback_cmd = base_pyinstaller_cmd() + ["--onedir", "--noconsole"]
    if icon_path.exists():
        fallback_cmd += ["--icon", str(icon_path)]
    fallback_cmd += ["main.py"]
    if run(fallback_cmd, "Windows onedir Fallback"):
        # Kopiere exe aus onedir
        inner = BUILD / APP_NAME / f"{APP_NAME}.exe"
        if inner.exists():
            target = BUILD / f"{APP_NAME}-{read_version()}.exe"
            shutil.copy2(inner, target)
            log(f"🔖 Versioniertes Artefakt: {target.name}")
        return True
    return False


def build_linux():
    log("🐧 Linux Build")
    icon_path = ROOT / "resources" / "icons" / "app_icon.png"
    cmd = base_pyinstaller_cmd() + ["--onefile"]
    if icon_path.exists():
        cmd += ["--icon", str(icon_path)]
    cmd += ["main.py"]
    if run(cmd, "Linux Binary (onefile)"):
        bin_path = BUILD / APP_NAME
        if bin_path.exists():
            versioned = BUILD / f"{APP_NAME}-{read_version()}"
            try:
                if versioned.exists():
                    versioned.unlink()
                bin_path.rename(versioned)
                versioned.chmod(0o755)
                log(f"🔖 Versioniertes Artefakt: {versioned.name}")
            except Exception as e:
                log(f"⚠️ Umbenennung fehlgeschlagen: {e}")
        return True
    log("⚠️ Onefile Build fehlgeschlagen – versuche onedir Fallback")
    fallback_cmd = base_pyinstaller_cmd() + ["--onedir"]
    if icon_path.exists():
        fallback_cmd += ["--icon", str(icon_path)]
    fallback_cmd += ["main.py"]
    if run(fallback_cmd, "Linux onedir Fallback"):
        inner = BUILD / APP_NAME / APP_NAME
        if inner.exists():
            target = BUILD / f"{APP_NAME}-{read_version()}"
            shutil.copy2(inner, target)
            target.chmod(0o755)
            log(f"🔖 Versioniertes Artefakt: {target.name}")
        return True
    return False


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

    # PyInstaller erzeugt i.d.R. ein .app Bundle: NAME.app
    app_bundle = BUILD / f"{APP_NAME}.app"
    alt_dir = BUILD / APP_NAME  # fallback (falls kein .app erstellt wurde)

    if not app_bundle.exists():
        if alt_dir.exists() and alt_dir.is_dir():
            # Manuell .app Struktur erstellen
            log("ℹ️ Erzeuge .app Bundle aus Ordner-Struktur")
            manual_bundle = BUILD / f"{APP_NAME}.app"
            contents = manual_bundle / "Contents"
            macos_dir = contents / "MacOS"
            resources_dir = contents / "Resources"
            for d in (manual_bundle, contents, macos_dir, resources_dir):
                d.mkdir(exist_ok=True)
            # Kopiere alles hinein
            for item in alt_dir.iterdir():
                target = macos_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target)
            # einfache Info.plist
            plist = contents / "Info.plist"
            plist.write_text(f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\"><dict><key>CFBundleExecutable</key><string>{APP_NAME}</string></dict></plist>""", encoding="utf-8")
            app_bundle = manual_bundle
        else:
            log("❌ Weder .app Bundle noch Alternative gefunden")
            return False

    version = read_version()
    # Archiv (.tar.gz) des .app Bundles
    archive = BUILD / f"{APP_NAME}-{version}.tar.gz"
    subprocess.run(["tar", "-czf", str(archive), app_bundle.name], cwd=BUILD, check=False)

    # .pkg erstellen (Staging unter Applications)
    pkgbuild = shutil.which("pkgbuild")
    pkg_target = BUILD / f"{APP_NAME}-{version}.pkg"
    if pkgbuild:
        staging = BUILD / "_pkgroot"
        apps_dir = staging / "Applications"
        apps_dir.mkdir(parents=True, exist_ok=True)
        # Kopiere/Sync .app in Staging
        dest_app = apps_dir / app_bundle.name
        if dest_app.exists():
            shutil.rmtree(dest_app)
        shutil.copytree(app_bundle, dest_app, dirs_exist_ok=True)
        identifier = "org.ehrenamt.finanzauswertung"
        try:
            subprocess.run([
                pkgbuild,
                "--root", str(staging),
                "--install-location", "/",
                "--identifier", identifier,
                "--version", read_version(),
                str(pkg_target)
            ], check=True)
        except subprocess.CalledProcessError as e:
            log(f"⚠️ pkgbuild fehlgeschlagen: {e}")
        finally:
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
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
