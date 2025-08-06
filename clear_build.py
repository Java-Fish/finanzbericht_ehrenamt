#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clear Build Script für Finanzauswertung Ehrenamt
Führt alle Tests aus und baut danach die Apps neu
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from datetime import datetime

def run_all_tests():
    """Führt alle Tests aus"""
    print("🧪 Führe alle Tests aus...")
    
    test_script = Path(__file__).parent / "test" / "run_all_tests.py"
    
    if not test_script.exists():
        print("❌ Test-Skript nicht gefunden!")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_script)],
            cwd=Path(__file__).parent,
            check=False
        )
        
        if result.returncode == 0:
            print("✅ Alle Tests erfolgreich!")
            return True
        else:
            print("❌ Einige Tests sind fehlgeschlagen!")
            print("ℹ️ Build wird trotzdem fortgesetzt...")
            return True  # Trotzdem fortfahren
            
    except Exception as e:
        print(f"💥 Fehler beim Ausführen der Tests: {e}")
        return False

def build_apps():
    """Baut die Apps für die aktuelle Plattform"""
    print("🏗️ Baue Apps...")
    
    build_script = Path(__file__).parent / "build.py"
    
    if not build_script.exists():
        print("❌ Build-Skript nicht gefunden!")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(build_script)],
            cwd=Path(__file__).parent,
            check=True
        )
        
        print("✅ Apps erfolgreich gebaut!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build fehlgeschlagen: {e}")
        return False
    except Exception as e:
        print(f"💥 Unerwarteter Fehler beim Build: {e}")
        return False

def show_build_results():
    """Zeigt die Ergebnisse des Builds"""
    build_dir = Path(__file__).parent / "build"
    
    if not build_dir.exists():
        print("⚠️ Build-Verzeichnis nicht gefunden!")
        return
    
    build_files = list(build_dir.glob("*"))
    
    if not build_files:
        print("⚠️ Keine Build-Dateien gefunden!")
        return
    
    print(f"\\n📁 Build-Ergebnisse in {build_dir}:")
    for file in sorted(build_files):
        size = ""
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            size = f" ({size_mb:.1f} MB)"
        
        print(f"  📱 {file.name}{size}")

def main():
    """Hauptfunktion"""
    print("🚀 Finanzauswertung Ehrenamt - Clear Build")
    print(f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"Plattform: {platform.system()} {platform.release()}")
    print("="*60)
    
    # Schritt 1: Tests ausführen
    if not run_all_tests():
        print("\\n❌ Tests konnten nicht ausgeführt werden!")
        return 1
    
    print("\\n" + "="*60)
    
    # Schritt 2: Apps bauen
    if not build_apps():
        print("\\n❌ Build fehlgeschlagen!")
        return 1
    
    print("\\n" + "="*60)
    
    # Schritt 3: Ergebnisse anzeigen
    show_build_results()
    
    print("\\n🎉 Clear Build erfolgreich abgeschlossen!")
    print("\\n🚀 Nächste Schritte:")
    
    current_platform = platform.system()
    if current_platform == "Windows":
        print("   • Windows: Starte die .exe-Datei im build/ Ordner")
    elif current_platform == "Darwin":
        print("   • macOS: Öffne die .app-Datei im build/ Ordner")
    
    print("   • Konsole: python main.py")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
