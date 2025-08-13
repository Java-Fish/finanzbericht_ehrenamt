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
        "--distpath", str(BUILD),  # Direkt in build/ statt build/dist/
        "--workpath", str(BUILD / "temp"),
        "--specpath", str(BUILD / "temp"),
        "--add-data", data_arg("resources", "resources"),
        "--add-data", data_arg("src", "src"),
        # Optimierungen für kleinere Builds
        "--strip",                    # Debugging-Symbole entfernen
        "--optimize", "2",            # Python-Bytecode optimieren
        "--noupx",                   # UPX deaktivieren für Stabilität
        "--exclude-module", "tkinter", # Tkinter ausschließen
        "--exclude-module", "matplotlib", # Matplotlib ausschließen
        "--exclude-module", "numpy.testing", # Testing-Module ausschließen
        "--exclude-module", "PIL.ImageQt", # Nicht benötigte PIL-Module
        "--exclude-module", "setuptools", # Setup-Tools ausschließen
        "--exclude-module", "distutils", # Distutils ausschließen
        "--exclude-module", "unittest", # Unit-Test-Framework
        "--exclude-module", "test", # Test-Module
        "--exclude-module", "tests", # Test-Module
        "--exclude-module", "pytest", # Pytest
        "--exclude-module", "sqlite3", # SQLite
        "--exclude-module", "urllib3", # HTTP-Library
        "--exclude-module", "requests", # HTTP-Library
        "--exclude-module", "email", # Email-Module
        # Erforderliche Imports (spezifisch statt pauschal)
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtWidgets", 
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "pandas",
        "--hidden-import", "openpyxl",
        "--hidden-import", "chardet",
        "--hidden-import", "fitz",      # PyMuPDF
        "--hidden-import", "PIL.Image", # Spezifische PIL-Module
        "--hidden-import", "odf.opendocument", # Spezifische ODF-Module
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
    version = read_version()
    
    # Versuche erst onefile für kompakte Binary
    cmd = base_pyinstaller_cmd() + [
        "--onefile",
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
    
    if not run(cmd, ".app onefile Build"):
        # Fallback zu onedir falls onefile fehlschlägt
        log("⚠️ onefile fehlgeschlagen, versuche onedir Fallback")
        cmd_onedir = base_pyinstaller_cmd() + [
            "--onedir",
            "--windowed",
        ]
        if icns.exists():
            cmd_onedir += ["--icon", str(icns)]
        elif png.exists():
            cmd_onedir += ["--icon", str(png)]
        cmd_onedir += ["main.py"]
        
        if not run(cmd_onedir, ".app onedir Fallback"):
            return False
    
    # Versionierte Namen für finale Artefakte
    app_bundle = BUILD / f"{APP_NAME}.app"
    versioned_app = BUILD / f"{APP_NAME}-{version}.app"
    
    # Binary (onefile) falls vorhanden
    binary = BUILD / APP_NAME
    versioned_binary = BUILD / f"{APP_NAME}-{version}"
    
    # Umbenennungen für versionierte Artefakte
    if binary.exists():
        try:
            if versioned_binary.exists():
                versioned_binary.unlink()
            binary.rename(versioned_binary)
            versioned_binary.chmod(0o755)
            log(f"🔖 Versioniertes Binary: {versioned_binary.name}")
        except Exception as e:
            log(f"⚠️ Konnte Binary nicht umbenennen: {e}")
    
    if app_bundle.exists():
        try:
            if versioned_app.exists():
                shutil.rmtree(versioned_app)
            app_bundle.rename(versioned_app)
            log(f"🔖 Versionierte App: {versioned_app.name}")
            app_bundle = versioned_app  # Für .pkg-Erstellung verwenden
        except Exception as e:
            log(f"⚠️ Konnte App nicht umbenennen: {e}")
            return False
    
    # .pkg erstellen falls App-Bundle vorhanden
    if app_bundle.exists():
        pkg_name = f"{APP_NAME}-{version}.pkg"
        pkg_path = BUILD / pkg_name
        try:
            if pkg_path.exists():
                pkg_path.unlink()
            
            # .pkg mit Staging-Verzeichnis erstellen
            staging_dir = BUILD / "_pkg_staging"
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
            
            apps_dir = staging_dir / "Applications"
            apps_dir.mkdir(parents=True)
            
            # .app in das Staging-Verzeichnis kopieren
            staging_app = apps_dir / app_bundle.name
            shutil.copytree(app_bundle, staging_app)
            
            if pkg_path.exists():
                pkg_path.unlink()
            
            pkg_cmd = [
                "pkgbuild",
                "--root", str(staging_dir),
                "--install-location", "/",
                "--identifier", f"com.ehrenamt.{APP_NAME.lower()}",
                "--version", version,
                str(pkg_path)
            ]
            
            if run_command(pkg_cmd, f".pkg Installer ({pkg_name})"):
                log(f"🔖 Versioniertes Paket: {pkg_name}")
            else:
                log("⚠️ .pkg Erstellung fehlgeschlagen, aber .app ist verfügbar")
            
            # Staging-Verzeichnis aufräumen
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
        except Exception as e:
            log(f"⚠️ .pkg Erstellung fehlgeschlagen: {e}")
    
    return True


def run_command(cmd: list[str], label: str) -> bool:
    """Führt einen Systembefehl aus"""
    log(f"🔨 {label}: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, check=True)
        log(f"✅ {label} erfolgreich")
        return True
    except subprocess.CalledProcessError as e:
        log(f"❌ {label} fehlgeschlagen")
        if e.stdout:
            log(e.stdout)
        if e.stderr:
            log(e.stderr)
        return False
    except Exception as e:
        log(f"❌ {label} Fehler: {e}")
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
    """Führt einen Befehl aus und gibt True zurück wenn erfolgreich"""
    log("📦 " + label + ": " + " ".join(cmd))
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode == 0:
        log(f"✅ {label} erfolgreich")
        return True
    log(f"❌ {label} fehlgeschlagen")
    if result.stdout.strip():
        log(result.stdout)
    if result.stderr.strip():
        log(result.stderr)
    return False


def cleanup_build_artifacts():
    """Entfernt temporäre Build-Ordner nach erfolgreichem Build"""
    log("\n🧹 Cleanup: Entferne temporäre Build-Ordner...")
    
    # Temporäre PyInstaller-Ordner entfernen
    temp_dirs = [
        BUILD / "temp", 
        BUILD / APP_NAME,  # onedir-Ordner falls vorhanden
        BUILD / "_pkg_staging",  # Staging-Ordner für .pkg
        BUILD / "dist",
        BUILD / "build",
        ROOT / "dist",
        ROOT / "build" / "dist",
        ROOT / APP_NAME,
    ]
    
    for temp_dir in temp_dirs:
        if temp_dir.exists() and temp_dir.is_dir():
            try:
                shutil.rmtree(temp_dir)
                log(f"✅ Entfernt: {temp_dir.name}")
            except Exception as e:
                log(f"⚠️ Konnte {temp_dir} nicht entfernen: {e}")
    
    # .spec Dateien aufräumen
    for spec_file in ROOT.glob("*.spec"):
        if spec_file.name != "app.spec":  # Originale .spec behalten
            try:
                spec_file.unlink()
                log(f"✅ Entfernt: {spec_file.name}")
            except Exception as e:
                log(f"⚠️ Konnte {spec_file} nicht entfernen: {e}")


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
        cleanup_build_artifacts()  # Cleanup nach erfolgreichem Build
        log("\n🎉 Build erfolgreich abgeschlossen!")
        log("\n� Finale Build-Artefakte in /build:")
        for p in sorted(BUILD.glob("*")):
            if p.is_file():
                size_mb = p.stat().st_size / (1024 * 1024)
                log(f"  • {p.name} ({size_mb:.1f} MB)")
        return 0
    
    log("❌ Build fehlgeschlagen")
    return 1


if __name__ == "__main__":
    sys.exit(main())
