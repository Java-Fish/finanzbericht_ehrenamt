#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der Excel/ODS Blatt-Auswahl Funktionalität
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Test-Helpers importieren
from test_helpers import get_test_file_path, cleanup_test_files

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_excel_file():
    """Erstellt eine Test-Excel-Datei mit mehreren Blättern"""
    
    # Temporäre Datei im test/ Ordner
    file_path = get_test_file_path('test_multi_sheet.xlsx')
    
    # Test-Daten für BWA
    bwa_data = {
        'Sachkontonr.': ['1000', '1200', '4000', '5000', '6000'],
        'Betrag': [1500.00, -500.00, 2000.00, -300.00, -800.00],
        'Buchungstag': ['2024-01-15', '2024-01-20', '2024-02-10', '2024-02-15', '2024-03-05'],
        'Beschreibung': ['Eröffnung', 'Bankgebühren', 'Spende', 'Büromaterial', 'Miete']
    }
    
    # Dummy-Daten für andere Blätter
    other_data1 = {
        'Mitglied': ['Max Mustermann', 'Anna Schmidt', 'Peter Weber'],
        'Beitrag': [50.00, 75.00, 60.00],
        'Status': ['Aktiv', 'Aktiv', 'Inaktiv']
    }
    
    other_data2 = {
        'Veranstaltung': ['Sommerfest', 'Weihnachtsfeier', 'Jahreshauptversammlung'],
        'Datum': ['2024-06-15', '2024-12-20', '2024-03-10'],
        'Kosten': [500.00, 800.00, 200.00]
    }
    
    # Excel-Datei mit mehreren Blättern erstellen
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        pd.DataFrame(bwa_data).to_excel(writer, sheet_name='BWA Daten', index=False)
        pd.DataFrame(other_data1).to_excel(writer, sheet_name='Mitgliederliste', index=False)
        pd.DataFrame(other_data2).to_excel(writer, sheet_name='Veranstaltungen', index=False)
    
    print(f"✅ Test-Excel-Datei erstellt: {file_path}")
    return file_path

def create_test_ods_file():
    """Erstellt eine Test-ODS-Datei mit mehreren Blättern"""
    
    # Test-Daten für BWA
    bwa_data = {
        'Sachkontonr.': ['2000', '2100', '8000', '6100', '7000'],
        'Betrag': [2500.00, -200.00, 1500.00, -450.00, -600.00],
        'Buchungstag': ['2024-04-15', '2024-04-20', '2024-05-10', '2024-05-15', '2024-06-05'],
        'Beschreibung': ['Spende groß', 'Porto', 'Förderung', 'Telefon', 'Versicherung']
    }
    
    # Dummy-Daten für andere Blätter
    inventory_data = {
        'Gegenstand': ['Laptop', 'Drucker', 'Beamer'],
        'Anschaffungsdatum': ['2023-01-15', '2023-05-20', '2023-08-10'],
        'Wert': [800.00, 150.00, 300.00]
    }
    
    # ODS-Datei mit mehreren Blättern erstellen
    file_path = get_test_file_path('test_multi_sheet.ods')
    
    try:
        # ODS mit pandas erstellen (benötigt odfpy)
        with pd.ExcelWriter(file_path, engine='odf') as writer:
            pd.DataFrame(bwa_data).to_excel(writer, sheet_name='Finanzdaten', index=False)
            pd.DataFrame(inventory_data).to_excel(writer, sheet_name='Inventar', index=False)
        
        print(f"✅ Test-ODS-Datei erstellt: {file_path}")
        return file_path
        
    except ImportError:
        print("⚠️ ODS-Test übersprungen - odfpy nicht installiert")
        return None

def test_file_handler():
    """Testet den FileHandler mit den Multi-Sheet-Dateien"""
    from src.utils.file_handler import FileHandler
    
    handler = FileHandler()
    
    # Test Excel-Datei
    excel_file = create_test_excel_file()
    print(f"\n=== Test Excel-Datei: {os.path.basename(excel_file)} ===")
    
    # Blatt-Namen testen
    sheet_names = handler.get_sheet_names(excel_file)
    print(f"Arbeitsblätter: {sheet_names}")
    
    # Mehrere Blätter prüfen
    has_multiple = handler.has_multiple_sheets(excel_file)
    print(f"Hat mehrere Blätter: {has_multiple}")
    
    # Verschiedene Blätter laden
    for sheet_name in sheet_names:
        print(f"\n--- Blatt: {sheet_name} ---")
        try:
            df = handler.process_file(excel_file, sheet_name)
            print(f"Spalten: {list(df.columns)}")
            print(f"Erste Zeile: {df.iloc[0].to_dict() if not df.empty else 'Leer'}")
        except Exception as e:
            print(f"Fehler: {e}")
    
    # Test ODS-Datei
    ods_file = create_test_ods_file()
    if ods_file:
        print(f"\n=== Test ODS-Datei: {os.path.basename(ods_file)} ===")
        
        try:
            sheet_names = handler.get_sheet_names(ods_file)
            print(f"Arbeitsblätter: {sheet_names}")
            
            has_multiple = handler.has_multiple_sheets(ods_file)
            print(f"Hat mehrere Blätter: {has_multiple}")
            
            # Erstes Blatt laden
            if sheet_names:
                df = handler.process_file(ods_file, sheet_names[0])
                print(f"Spalten: {list(df.columns)}")
                print(f"Erste Zeile: {df.iloc[0].to_dict() if not df.empty else 'Leer'}")
                
        except Exception as e:
            print(f"ODS-Fehler: {e}")

def test_csv_processor():
    """Testet den CSVProcessor mit den neuen Methoden"""
    from src.utils.csv_processor import CSVProcessor
    
    processor = CSVProcessor()
    
    # Test mit Excel-Datei
    excel_file = '/Users/nabu/git/finanzauswertungEhrenamt/test_multi_sheet.xlsx'
    if os.path.exists(excel_file):
        print(f"\n=== Test CSVProcessor mit Excel ===")
        
        # Blätter prüfen
        has_multiple = processor.has_multiple_sheets(excel_file)
        print(f"Hat mehrere Blätter: {has_multiple}")
        
        if has_multiple:
            sheet_names = processor.get_sheet_names(excel_file)
            print(f"Verfügbare Blätter: {sheet_names}")
            
            # BWA-Daten-Blatt laden
            if 'BWA Daten' in sheet_names:
                success = processor.load_file(excel_file, 'BWA Daten')
                print(f"BWA Daten geladen: {success}")
                
                if success:
                    account_numbers = processor.get_account_numbers()
                    print(f"Gefundene Sachkonten: {account_numbers}")

if __name__ == "__main__":
    print("=== Test: Excel/ODS Blatt-Auswahl ===")
    print(f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    
    test_file_handler()
    test_csv_processor()
    
    print("\n=== Test abgeschlossen ===")
    print("💡 Starten Sie nun die Anwendung und testen Sie den Import der Multi-Sheet-Dateien!")
