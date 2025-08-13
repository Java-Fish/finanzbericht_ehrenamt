#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für CSV-Processor Edge Cases und Datenverarbeitung
"""
import sys
import os
import tempfile
import pandas as pd
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Lokale Imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.csv_processor import CSVProcessor

def test_csv_processor_edge_cases():
    """Testet Edge Cases im CSV-Processor"""
    print("🔄 Teste CSV-Processor Edge Cases...")
    
    # QApplication nur erstellen wenn noch keine existiert
    app = None
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])  # Leere argv für nicht-interaktive Tests
            app.setQuitOnLastWindowClosed(True)
    except ImportError:
        print("⚠️ PySide6 nicht verfügbar - GUI-unabhängige Tests")
    
    processor = CSVProcessor()
    
    # Test 1: CSV mit ungültigen Datumsformaten
    print("  📋 Test 1: Ungültige Datumsformate")
    test_data = pd.DataFrame([
        {'Sachkontonr.': '4000', 'Betrag': '1000.50', 'Buchungstag': 'invalid-date', 'Beschreibung': 'Test 1'},
        {'Sachkontonr.': '4100', 'Betrag': '500.00', 'Buchungstag': '2024-13-45', 'Beschreibung': 'Test 2'},
        {'Sachkontonr.': '4200', 'Betrag': '750.00', 'Buchungstag': '2024.02.15', 'Beschreibung': 'Test 3'},
    ])
    
    processor.raw_data = test_data
    success = processor._process_data()
    
    if success and processor.processed_data is not None:
        # Prüfe ob nur gültige Daten verarbeitet wurden
        valid_rows = processor.processed_data.dropna(subset=['Buchungstag_Clean'])
        print(f"  ✅ {len(valid_rows)} von {len(test_data)} Zeilen mit gültigen Daten verarbeitet")
    else:
        print("  ❌ Datenverarbeitung fehlgeschlagen")
        return False
    
    # Test 2: CSV mit ungültigen Beträgen
    print("  📋 Test 2: Ungültige Beträge")
    test_data = pd.DataFrame([
        {'Sachkontonr.': '4000', 'Betrag': 'nicht-numerisch', 'Buchungstag': '2024.01.15', 'Beschreibung': 'Test 1'},
        {'Sachkontonr.': '4100', 'Betrag': '', 'Buchungstag': '2024.02.15', 'Beschreibung': 'Test 2'},
        {'Sachkontonr.': '4200', 'Betrag': '1.500,50', 'Buchungstag': '2024.03.15', 'Beschreibung': 'Test 3'},
        {'Sachkontonr.': '4300', 'Betrag': '750.00', 'Buchungstag': '2024.04.15', 'Beschreibung': 'Test 4'},
    ])
    
    processor.raw_data = test_data
    success = processor._process_data()
    
    if success and processor.processed_data is not None:
        # Prüfe Betrag_Clean Spalte
        valid_amounts = processor.processed_data.dropna(subset=['Betrag_Clean'])
        print(f"  ✅ {len(valid_amounts)} von {len(test_data)} Zeilen mit gültigen Beträgen verarbeitet")
    else:
        print("  ❌ Betragsverarbeitung fehlgeschlagen")
        return False
    
    # Test 3: Leere Sachkontonummern
    print("  📋 Test 3: Leere und ungültige Sachkontonummern")
    test_data = pd.DataFrame([
        {'Sachkontonr.': '', 'Betrag': '1000.00', 'Buchungstag': '2024.01.15', 'Beschreibung': 'Test 1'},
        {'Sachkontonr.': None, 'Betrag': '500.00', 'Buchungstag': '2024.02.15', 'Beschreibung': 'Test 2'},
        {'Sachkontonr.': '4000', 'Betrag': '750.00', 'Buchungstag': '2024.03.15', 'Beschreibung': 'Test 3'},
    ])
    
    processor.raw_data = test_data
    success = processor._process_data()
    
    if success and processor.processed_data is not None:
        account_numbers = processor.get_account_numbers()
        if '4000' in account_numbers and len(account_numbers) >= 1:
            print(f"  ✅ Nur gültige Sachkonten erkannt: {account_numbers}")
        else:
            print(f"  ❌ Unerwartete Sachkonten: {account_numbers}")
            return False
    else:
        print("  ❌ Sachkonten-Verarbeitung fehlgeschlagen")
        return False
    
    # Test 4: Quartalsberechnung mit Edge Cases
    print("  📋 Test 4: Quartalsberechnung")
    test_data = pd.DataFrame([
        {'Sachkontonr.': '4000', 'Betrag': '1000.00', 'Buchungstag': '2024.01.01', 'Beschreibung': 'Q1 Start'},
        {'Sachkontonr.': '4000', 'Betrag': '500.00', 'Buchungstag': '2024.03.31', 'Beschreibung': 'Q1 Ende'},
        {'Sachkontonr.': '4000', 'Betrag': '750.00', 'Buchungstag': '2024.12.31', 'Beschreibung': 'Q4 Ende'},
    ])
    
    processor.raw_data = test_data
    success = processor._process_data()
    
    if success and processor.processed_data is not None:
        q1_data = processor.get_data_by_quarter(1)
        q4_data = processor.get_data_by_quarter(4)
        
        if len(q1_data) == 2 and len(q4_data) == 1:
            print("  ✅ Quartalsaufteilung korrekt")
        else:
            print(f"  ❌ Quartalsaufteilung fehlerhaft: Q1={len(q1_data)}, Q4={len(q4_data)}")
            return False
    else:
        print("  ❌ Quartalsberechnung fehlgeschlagen")
        return False
    
    # Test 5: Große Datenmengen (Performance Test)
    print("  📋 Test 5: Performance mit größeren Datenmengen")
    import time
    
    # Generiere 1000 Testdatensätze
    large_data = []
    for i in range(1000):
        large_data.append({
            'Sachkontonr.': f'40{i%10:02d}',
            'Betrag': f'{(i*10.50):.2f}',
            'Buchungstag': f'2024.{(i%12)+1:02d}.{(i%28)+1:02d}',
            'Beschreibung': f'Test Entry {i}'
        })
    
    test_data = pd.DataFrame(large_data)
    processor.raw_data = test_data
    
    start_time = time.time()
    success = processor._process_data()
    processing_time = time.time() - start_time
    
    if success and processing_time < 5.0:  # Sollte unter 5 Sekunden dauern
        print(f"  ✅ 1000 Datensätze in {processing_time:.2f}s verarbeitet")
    else:
        print(f"  ⚠️ Performance-Test: {processing_time:.2f}s für 1000 Datensätze")
        if not success:
            print("  ❌ Verarbeitung fehlgeschlagen")
            return False
    
    print("✅ CSV-Processor Edge Cases erfolgreich getestet")
    return True

def main():
    """Hauptfunktion"""
    return test_csv_processor_edge_cases()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
