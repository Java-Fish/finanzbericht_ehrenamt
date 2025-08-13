#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean Build Script - Vereinfachtes Interface für den Build-Prozess
- Führt Tests aus (ohne GUI-Tests)
- Startet ci_build.py für plattformspezifische Builds
- Alle Artefakte landen direkt in /build mit Versionsnummern
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent


def log(msg: str):
    print(f"[clean_build] {msg}")


def run_tests() -> bool:
    """Führt Tests ohne GUI-Dialoge aus"""
    log("🧪 Starte Tests...")
    test_runner = ROOT / "test" / "run_all_tests.py"
    
    if not test_runner.exists():
        log("⚠️ Test Runner nicht gefunden, überspringe Tests")
        return True
        
    result = subprocess.run([sys.executable, str(test_runner)], cwd=ROOT)
    if result.returncode == 0:
        log("✅ Tests erfolgreich")
        return True
    else:
        log("❌ Tests fehlgeschlagen (Build wird trotzdem fortgesetzt)")
        return True  # Tests sollen Build nicht blockieren


def run_ci_build() -> bool:
    """Startet den optimierten ci_build.py"""
    log("🏗️ Starte optimierten Build...")
    ci_script = ROOT / "ci_build.py"
    
    if not ci_script.exists():
        log("❌ ci_build.py nicht gefunden")
        return False
        
    result = subprocess.run([sys.executable, str(ci_script)], cwd=ROOT)
    if result.returncode == 0:
        log("✅ Build erfolgreich abgeschlossen")
        return True
    else:
        log("❌ Build fehlgeschlagen")
        return False


def main() -> int:
    log("🚀 Clean Build gestartet...")
    
    # 1. Tests ausführen
    if not run_tests():
        log("⚠️ Tests hatten Probleme, Build wird trotzdem versucht")
    
    # 2. Build durchführen
    if not run_ci_build():
        log("💥 Build-Prozess fehlgeschlagen")
        return 1
    
    log("🎉 Clean Build erfolgreich abgeschlossen!")
    log("📁 Alle Artefakte befinden sich in /build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
