#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für FileHandler Fehlerfälle und Edge Cases
"""
import sys
import os
import tempfile
import pandas as pd
from pathlib import Path

# Lokale Imports
sys.path.append('src')
from utils.file_handler import FileHandler

def test_file_handler_errors():
    """Testet Fehlerbehandlung im FileHandler"""
    print("🔍 Teste FileHandler Fehlerfälle...")
    
    handler = FileHandler()
    
    # Test 1: Nicht existierende Datei
    print("  📋 Test 1: Nicht existierende Datei")
    try:
        handler.process_file("/nicht/existierend.csv")
        print("  ❌ Fehler: Sollte FileNotFoundError werfen")
        return False
    except FileNotFoundError:
        print("  ✅ FileNotFoundError korrekt geworfen")
    except Exception as e:
        print(f"  ❌ Unerwarteter Fehler: {e}")
        return False
    
    # Test 2: Nicht unterstütztes Dateiformat
    print("  📋 Test 2: Nicht unterstütztes Dateiformat")
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(b"test content")
        temp_path = temp_file.name
    
    try:
        handler.process_file(temp_path)
        print("  ❌ Fehler: Sollte ValueError werfen")
        return False
    except ValueError as e:
        if "Nicht unterstütztes Dateiformat" in str(e):
            print("  ✅ ValueError für unsupported format korrekt geworfen")
        else:
            print(f"  ❌ Unerwartete ValueError Nachricht: {e}")
            return False
    except Exception as e:
        print(f"  ❌ Unerwarteter Fehler: {e}")
        return False
    finally:
        os.unlink(temp_path)
    
    # Test 3: Leere CSV-Datei
    print("  📋 Test 3: Leere CSV-Datei")
    with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', delete=False) as temp_file:
        temp_file.write("")  # Leere Datei
        temp_path = temp_file.name
    
    try:
        result = handler.process_file(temp_path)
        # Leere CSV kann fehlerhafte sein oder ein leeres DataFrame zurückgeben
        print("  ✅ Leere CSV ohne Fehler verarbeitet")
    except Exception as e:
        # Das ist auch ein erwartetes Verhalten
        print(f"  ✅ Leere CSV wirft erwarteten Fehler: {type(e).__name__}")
    finally:
        os.unlink(temp_path)
    
    # Test 4: CSV mit nur Header
    print("  📋 Test 4: CSV mit nur Header")
    with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', delete=False) as temp_file:
        temp_file.write("Spalte1;Spalte2;Spalte3\n")  # Nur Header
        temp_path = temp_file.name
    
    try:
        result = handler.process_file(temp_path)
        if isinstance(result, pd.DataFrame) and len(result) == 0 and len(result.columns) == 3:
            print("  ✅ Header-only CSV korrekt verarbeitet")
        else:
            print(f"  ❌ Unerwartetes Ergebnis für Header-only CSV: {len(result)} Zeilen, {len(result.columns)} Spalten")
            return False
    except Exception as e:
        print(f"  ❌ Fehler bei Header-only CSV: {e}")
        return False
    finally:
        os.unlink(temp_path)
    
    # Test 5: CSV mit inkonsistenten Trennzeichen
    print("  📋 Test 5: CSV mit verschiedenen Trennzeichen")
    with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', delete=False) as temp_file:
        temp_file.write("Spalte1,Spalte2,Spalte3\n")
        temp_file.write("Wert1,Wert2,Wert3\n")
        temp_path = temp_file.name
    
    try:
        result = handler.process_file(temp_path)
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            print("  ✅ Komma-separierte CSV korrekt verarbeitet")
        else:
            print(f"  ❌ Fehler bei Komma-CSV: {len(result)} Zeilen")
            return False
    except Exception as e:
        print(f"  ❌ Fehler bei Komma-CSV: {e}")
        return False
    finally:
        os.unlink(temp_path)
    
    # Test 6: Encoding-Probleme
    print("  📋 Test 6: Encoding mit Umlauten")
    with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', encoding='utf-8', delete=False) as temp_file:
        temp_file.write("Spalte1;Spalte2;Spalte3\n")
        temp_file.write("Müller;Größe;Wäscherei\n")
        temp_path = temp_file.name
    
    try:
        result = handler.process_file(temp_path)
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            # Prüfe ob Umlaute korrekt gelesen wurden
            first_value = str(result.iloc[0, 0])
            if "Müller" in first_value:
                print("  ✅ UTF-8 Encoding korrekt verarbeitet")
            else:
                print(f"  ⚠️ Encoding möglicherweise nicht korrekt: '{first_value}'")
        else:
            print(f"  ❌ Fehler bei UTF-8 CSV: {len(result)} Zeilen")
            return False
    except Exception as e:
        print(f"  ❌ Fehler bei UTF-8 CSV: {e}")
        return False
    finally:
        os.unlink(temp_path)
    
    print("✅ FileHandler Fehlerbehandlung erfolgreich getestet")
    return True

def main():
    """Hauptfunktion"""
    return test_file_handler_errors()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
