#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der Sachkonto-Namen Funktionalität
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Test-Helpers importieren
from test_helpers import get_test_file_path, cleanup_test_files

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_file_with_account_names():
    """Erstellt eine Test-Excel-Datei mit Sachkonto-Namen"""
    
    # Temporäre Datei im test/ Ordner
    file_path = get_test_file_path('test_account_names.xlsx')
    
    # Test-Daten mit Sachkonto-Namen
    test_data = {
        'Sachkontonr.': ['1000', '1200', '4000', '5000', '6000', '6100', '1000', '4000'],
        'Sachkonto': [
            'Kassenkonto',
            'Girokonto Bank',
            'Spenden allgemein',
            'Büromaterial',
            'Miete Vereinsheim',
            'Telefon/Internet',
            'Kassenkonto',  # Doppelt um zu testen
            'Spenden allgemein'  # Doppelt um zu testen
        ],
        'Betrag': [1500.00, -500.00, 2000.00, -300.00, -800.00, -150.00, 500.00, 1200.00],
        'Buchungstag': [
            '2024-01-15', '2024-01-20', '2024-02-10', 
            '2024-02-15', '2024-03-05', '2024-03-10',
            '2024-04-05', '2024-04-12'
        ],
        'Beschreibung': [
            'Eröffnungsbilanz', 'Bankgebühren', 'Mitgliederspende',
            'Büromaterial Einkauf', 'Monatsmiete', 'Telefonrechnung',
            'Bareinzahlung', 'Spende Sommerfest'
        ]
    }
    
    # Excel-Datei erstellen
    df = pd.DataFrame(test_data)
    df.to_excel(file_path, index=False, sheet_name='BWA Daten mit Namen')
    
    print(f"✅ Test-Datei mit Sachkonto-Namen erstellt: {file_path}")
    print(f"Sachkonten: {df['Sachkontonr.'].unique()}")
    print(f"Namen: {df['Sachkonto'].unique()}")
    
    return file_path

def test_csv_processor_with_names():
    """Testet den CSVProcessor mit Sachkonto-Namen"""
    from src.utils.csv_processor import CSVProcessor
    
    print("\n=== Test CSVProcessor mit Sachkonto-Namen ===")
    
    # Test-Datei erstellen
    test_file = create_test_file_with_account_names()
    
    processor = CSVProcessor()
    
    # Datei laden
    success = processor.load_file(test_file)
    print(f"Datei geladen: {success}")
    
    if success:
        # Sachkonten-Nummern abrufen
        account_numbers = processor.get_account_numbers()
        print(f"Gefundene Sachkonten: {account_numbers}")
        
        # Alle Sachkonto-Namen abrufen
        all_account_names = processor.get_all_account_names()
        print(f"Sachkonto-Namen: {all_account_names}")
        
        # Einzelne Namen testen
        for account_num in account_numbers:
            name = processor.get_account_name(account_num)
            print(f"Konto {account_num}: {name}")
    
    return success

def test_account_mapping_ui():
    """Testet die Account Mapping UI (nur Datenstrukturen)"""
    from src.settings.account_mapping import AccountMappingTab
    
    print("\n=== Test Account Mapping Datenstrukturen ===")
    
    # Mock-Daten
    account_numbers = ['1000', '1200', '4000', '5000', '6000']
    account_names = {
        '1000': 'Kassenkonto',
        '1200': 'Girokonto Bank',
        '4000': 'Spenden allgemein',
        '5000': 'Büromaterial',
        '6000': 'Miete Vereinsheim'
    }
    
    # Test ohne UI erstellen (schwierig ohne Qt-App)
    print(f"Account Numbers: {account_numbers}")
    print(f"Account Names: {account_names}")
    
    # Simuliere die Logik der update_account_item_display
    for account_num in account_numbers:
        account_name = account_names.get(account_num, "")
        group_name = ""  # Keine Gruppe zugeordnet
        
        display_text = account_num
        if account_name:
            display_text += f" - {account_name}"
        if group_name:
            display_text += f" → {group_name}"
            
        print(f"Display: {display_text}")

def test_data_processing():
    """Testet die Datenverarbeitung mit verschiedenen Spalten-Namen"""
    print("\n=== Test verschiedene Spalten-Namen ===")
    
    # Test verschiedene Bezeichnungen für Sachkonto-Namen
    test_variations = [
        {
            'Sachkontonr.': ['1000', '2000'],
            'Sachkonto': ['Kasse', 'Bank'],  # Standard-Name
            'Betrag': [100, -50],
            'Buchungstag': ['2024-01-01', '2024-01-02']
        },
        {
            'Sachkontonr.': ['3000', '4000'],
            'Sachkontobezeichnung': ['Spenden', 'Kosten'],  # Alternative
            'Betrag': [200, -75],
            'Buchungstag': ['2024-01-03', '2024-01-04']
        },
        {
            'Sachkontonr.': ['5000', '6000'],
            'Kontobezeichnung': ['Miete', 'Telefon'],  # Weitere Alternative
            'Betrag': [-300, -50],
            'Buchungstag': ['2024-01-05', '2024-01-06']
        }
    ]
    
    from src.utils.csv_processor import CSVProcessor
    
    for i, test_data in enumerate(test_variations, 1):
        print(f"\n--- Test {i}: {list(test_data.keys())} ---")
        
        # Temporäre Excel-Datei erstellen
        temp_file = f'/Users/nabu/git/finanzauswertungEhrenamt/test_variation_{i}.xlsx'
        df = pd.DataFrame(test_data)
        df.to_excel(temp_file, index=False)
        
        # Mit CSVProcessor testen
        processor = CSVProcessor()
        success = processor.load_file(temp_file)
        
        if success:
            account_numbers = processor.get_account_numbers()
            account_names = processor.get_all_account_names()
            print(f"Konten: {account_numbers}")
            print(f"Namen: {account_names}")
        else:
            print("Fehler beim Laden")
        
        # Temporäre Datei löschen
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    print("=== Test: Sachkonto-Namen Funktionalität ===")
    print(f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    
    # Tests ausführen
    success = test_csv_processor_with_names()
    
    if success:
        test_account_mapping_ui()
        test_data_processing()
    
    print("\n=== Test abgeschlossen ===")
    print("💡 Starten Sie die Anwendung und importieren Sie test_account_names.xlsx")
    print("   um die Sachkonto-Namen in der BWA-Gruppen-Zuordnung zu sehen!")
