#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Hilfsfunktionen für temporäre Dateien
"""

import os
import tempfile
import atexit
from pathlib import Path
from typing import List

class TestFileManager:
    """Verwaltet temporäre Test-Dateien im test/ Ordner"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.temp_files: List[Path] = []
        
        # Automatische Aufräumung beim Beenden registrieren
        atexit.register(self.cleanup_all)
    
    def get_temp_file_path(self, filename: str) -> str:
        """Gibt einen Pfad für eine temporäre Datei im test/ Ordner zurück"""
        temp_path = self.test_dir / filename
        self.temp_files.append(temp_path)
        return str(temp_path)
    
    def cleanup_all(self):
        """Löscht alle temporären Test-Dateien"""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    print(f"🗑️ Temporäre Datei gelöscht: {temp_file.name}")
            except Exception as e:
                print(f"⚠️ Konnte temporäre Datei nicht löschen: {temp_file} - {e}")
    
    def cleanup_file(self, file_path: str):
        """Löscht eine spezifische temporäre Datei"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                print(f"🗑️ Temporäre Datei gelöscht: {path.name}")
                # Aus der Liste entfernen
                if path in self.temp_files:
                    self.temp_files.remove(path)
        except Exception as e:
            print(f"⚠️ Konnte temporäre Datei nicht löschen: {file_path} - {e}")

# Globale Instanz für alle Tests
test_file_manager = TestFileManager()

def get_test_file_path(filename: str) -> str:
    """Einfache Funktion um einen Test-Dateipfad zu bekommen"""
    return test_file_manager.get_temp_file_path(filename)

def cleanup_test_files():
    """Räumt alle Test-Dateien auf"""
    test_file_manager.cleanup_all()
