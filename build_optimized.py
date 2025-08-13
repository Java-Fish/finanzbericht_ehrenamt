#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimierter Build mit maximaler Größenreduzierung
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent

def optimized_macos_build():
    """Erstellt einen stark optimierten macOS Build"""
    print("🍎 Optimierter macOS Build (minimale Größe)")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "Finanzauswertung_Ehrenamt_mini",
        "--onefile",
        "--windowed", 
        "--strip",                     # Debug-Symbole entfernen
        "--optimize", "2",             # Maximale Python-Optimierung
        "--noupx",                     # UPX deaktivieren (kann Probleme verursachen)
        
        # Viele unnötige Module ausschließen
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib", 
        "--exclude-module", "numpy.testing",
        "--exclude-module", "setuptools",
        "--exclude-module", "distutils",
        "--exclude-module", "unittest",
        "--exclude-module", "test",
        "--exclude-module", "tests", 
        "--exclude-module", "pytest",
        "--exclude-module", "IPython",
        "--exclude-module", "jupyter",
        "--exclude-module", "scipy",
        "--exclude-module", "tornado", 
        "--exclude-module", "zmq",
        "--exclude-module", "sqlite3",
        "--exclude-module", "xmlrpc",
        "--exclude-module", "urllib3",
        "--exclude-module", "requests",
        "--exclude-module", "certifi",
        "--exclude-module", "email",
        "--exclude-module", "multiprocessing",
        "--exclude-module", "concurrent.futures",
        
        # Nur erforderliche Daten einbeziehen
        "--add-data", "resources:resources",
        "--add-data", "src:src",
        
        # Minimal erforderliche Hidden-Imports
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PySide6.QtGui", 
        "--hidden-import", "pandas",
        "--hidden-import", "openpyxl",
        "--hidden-import", "chardet",
        "--hidden-import", "fitz",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "odf.opendocument",
        
        # Icon
        "--icon", "resources/icons/app_icon.icns",
        
        # Hauptdatei
        "main.py"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Optimierter Build erfolgreich")
        return True
    else:
        print("❌ Build fehlgeschlagen:")
        print(result.stderr)
        return False

if __name__ == "__main__":
    if optimized_macos_build():
        # Größe prüfen
        import os
        app_path = ROOT / "dist" / "Finanzauswertung_Ehrenamt_mini"
        if app_path.exists():
            size_mb = os.path.getsize(app_path) / (1024 * 1024)
            print(f"📊 Binary-Größe: {size_mb:.1f} MB")
        
        app_bundle = ROOT / "dist" / "Finanzauswertung_Ehrenamt_mini.app"
        if app_bundle.exists():
            # App-Bundle-Größe berechnen
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(app_bundle):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            size_mb = total_size / (1024 * 1024)
            print(f"📊 App-Bundle-Größe: {size_mb:.1f} MB")
    else:
        sys.exit(1)
