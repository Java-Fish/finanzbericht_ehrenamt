#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup-Script für Build-Artefakte
Entfernt temporäre Ordner und alte Build-Reste
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent

def cleanup_build():
    """Entfernt alle temporären Build-Ordner und Dateien"""
    print("🧹 Cleanup: Entferne Build-Artefakte...")
    
    # Ordner zum Entfernen
    dirs_to_remove = [
        ROOT / "build",
        ROOT / "dist",
        ROOT / "Finanzauswertung_Ehrenamt",  # PyInstaller onedir Ordner
        ROOT / "temp",
        ROOT / "__pycache__",
        ROOT / ".pytest_cache",
    ]
    
    # Dateien zum Entfernen (PyInstaller Specs)
    files_to_remove = [
        ROOT / "Finanzauswertung_Ehrenamt.spec",
        ROOT / "Finanzauswertung_Ehrenamt_optimized.spec",
    ]
    
    removed_count = 0
    
    # Ordner entfernen
    for dir_path in dirs_to_remove:
        if dir_path.exists() and dir_path.is_dir():
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Entfernt: {dir_path.name}/")
                removed_count += 1
            except Exception as e:
                print(f"⚠️ Konnte {dir_path.name}/ nicht entfernen: {e}")
    
    # Dateien entfernen
    for file_path in files_to_remove:
        if file_path.exists() and file_path.is_file():
            try:
                file_path.unlink()
                print(f"✅ Entfernt: {file_path.name}")
                removed_count += 1
            except Exception as e:
                print(f"⚠️ Konnte {file_path.name} nicht entfernen: {e}")
    
    # Cache-Ordner in Test-Verzeichnis
    test_cache = ROOT / "test" / "__pycache__"
    if test_cache.exists():
        try:
            shutil.rmtree(test_cache)
            print(f"✅ Entfernt: test/__pycache__/")
            removed_count += 1
        except Exception as e:
            print(f"⚠️ Konnte test/__pycache__/ nicht entfernen: {e}")
    
    # Src Cache-Ordner
    src_cache = ROOT / "src" / "__pycache__"
    if src_cache.exists():
        try:
            shutil.rmtree(src_cache)
            print(f"✅ Entfernt: src/__pycache__/")
            removed_count += 1
        except Exception as e:
            print(f"⚠️ Konnte src/__pycache__/ nicht entfernen: {e}")
    
    if removed_count == 0:
        print("ℹ️ Keine Build-Artefakte gefunden.")
    else:
        print(f"\n🎉 Cleanup abgeschlossen: {removed_count} Elemente entfernt.")

if __name__ == "__main__":
    cleanup_build()
