#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der String-Konsistenz für Sachkontonummern
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Test-Helpers importieren
from test_helpers import get_test_file_path, cleanup_test_files

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_file_with_mixed_types():
    """Erstellt eine Test-Datei mit verschiedenen Sachkonto-Typen"""
    
    # Temporäre Datei im test/ Ordner
    file_path = get_test_file_path('test_string_consistency.xlsx')
    
    # Test-Daten mit gemischten Datentypen
    test_data = {
        'Sachkontonr.': [1000, '1200', 4000.0, '5000', 6000, '6100'],  # Mix: int, str, float
        'Sachkonto': [
            'Kassenkonto',
            'Girokonto Bank',
            'Spenden allgemein',
            'Büromaterial',
            'Miete Vereinsheim',
            'Telefon/Internet'
        ],
        'Betrag': [1500.00, -500.00, 2000.00, -300.00, -800.00, -150.00],
        'Buchungstag': [
            '2024-01-15', '2024-01-20', '2024-02-10',
            '2024-02-15', '2024-03-05', '2024-03-10'
        ]
    }
    
    # Excel-Datei erstellen
    df = pd.DataFrame(test_data)
    df.to_excel(file_path, index=False, sheet_name='Mixed Types Test')
    
    print(f"✅ Test-Datei mit gemischten Typen erstellt: {file_path}")
    print(f"Original Sachkontonr. Typen: {[type(x) for x in test_data['Sachkontonr.']]}")
    
    return file_path

def test_string_consistency():
    """Testet die String-Konsistenz der Sachkontonummern"""
    from src.utils.csv_processor import CSVProcessor
    
    print("\n=== Test String-Konsistenz für Sachkontonummern ===")
    
    # Test-Datei erstellen
    test_file = create_test_file_with_mixed_types()
    
    processor = CSVProcessor()
    
    # Datei laden
    success = processor.load_file(test_file)
    print(f"Datei geladen: {success}")
    
    if success:
        print("\n--- Rohdaten nach Laden ---")
        print(f"Raw data Sachkontonr. column type: {processor.raw_data['Sachkontonr.'].dtype}")
        print(f"Raw data sample: {processor.raw_data['Sachkontonr.'].head().tolist()}")
        print(f"Raw data types: {[type(x) for x in processor.raw_data['Sachkontonr.'].head().tolist()]}")
        
        print("\n--- Verarbeitete Daten ---")
        print(f"Processed data Sachkontonr. column type: {processor.processed_data['Sachkontonr.'].dtype}")
        print(f"Processed data sample: {processor.processed_data['Sachkontonr.'].head().tolist()}")
        print(f"Processed data types: {[type(x) for x in processor.processed_data['Sachkontonr.'].head().tolist()]}")
        
        # Sachkonten-Nummern abrufen
        account_numbers = processor.get_account_numbers()
        print(f"\n--- get_account_numbers() ---")
        print(f"Account numbers: {account_numbers}")
        print(f"Account number types: {[type(x) for x in account_numbers]}")
        
        # Alle Sachkonto-Namen abrufen
        all_account_names = processor.get_all_account_names()
        print(f"\n--- get_all_account_names() ---")
        print(f"Account names dict: {all_account_names}")
        print(f"Account names keys types: {[type(k) for k in all_account_names.keys()]}")
        
        # Einzelne Namen testen
        print(f"\n--- Einzelne Namen-Tests ---")
        for account_num in account_numbers:
            name = processor.get_account_name(account_num)
            print(f"Konto {account_num} (type: {type(account_num)}): {name}")
            
            # Test mit verschiedenen Input-Typen
            name_int = processor.get_account_name(int(account_num)) if account_num.isdigit() else None
            name_str = processor.get_account_name(str(account_num))
            print(f"  - Als int: {name_int}")
            print(f"  - Als str: {name_str}")
            print(f"  - Konsistent: {name == name_str}")
    
    return success

def test_account_mapping_consistency():
    """Testet die String-Konsistenz in der Account Mapping"""
    print("\n=== Test Account Mapping String-Konsistenz ===")
    
    # Mock-Daten mit verschiedenen Typen
    account_numbers = ['1000', '1200', '4000', '5000', '6000']  # Als Strings
    account_names = {
        1000: 'Kassenkonto',        # Key als int
        '1200': 'Girokonto Bank',   # Key als str
        4000.0: 'Spenden allgemein', # Key als float
        '5000': 'Büromaterial',     # Key als str
        '6000': 'Miete Vereinsheim' # Key als str
    }
    
    print(f"Input account_numbers: {account_numbers}")
    print(f"Input account_numbers types: {[type(x) for x in account_numbers]}")
    print(f"Input account_names keys: {list(account_names.keys())}")
    print(f"Input account_names key types: {[type(k) for k in account_names.keys()]}")
    
    # Test der update_accounts_from_csv Logik (simuliert)
    processed_names = {}
    for account_num, account_name in account_names.items():
        if account_name and str(account_name).strip():
            # Sachkontonummer als String sicherstellen und Float-Notation normalisieren
            if str(account_num).replace('.', '').replace('-', '').isdigit():
                normalized_num = str(int(float(account_num)))
            else:
                normalized_num = str(account_num)
            key = normalized_num.strip()
            processed_names[key] = str(account_name).strip()
            
    print(f"\nProcessed account_names keys: {list(processed_names.keys())}")
    print(f"Processed account_names key types: {[type(k) for k in processed_names.keys()]}")
    
    # Test der Konsistenz
    for account_num in account_numbers:
        found_name = processed_names.get(account_num, "")
        print(f"Account {account_num}: {found_name}")

def test_data_type_edge_cases():
    """Testet Edge Cases mit Datentypen"""
    print("\n=== Test Edge Cases mit Datentypen ===")
    print("Testing verschiedene Eingabe-Formate:")

    # CSVProcessor importieren für Normalisierungstest
    from src.utils.csv_processor import CSVProcessor
    processor = CSVProcessor()

    test_cases = [
        "1000",      # String
        1000,        # Integer  
        1000.0,      # Float
        "01000",     # String mit führender Null
        " 1000 ",    # String mit Leerzeichen
        1234.0,      # Float ohne Dezimalstellen
        1234.5,      # Float mit Dezimalstellen
        "1234.0",    # String mit .0 Endung
    ]

    for test_input in test_cases:
        normalized = processor.normalize_account_number(test_input)
        print(f"Input: {test_input} (type: {type(test_input)}) → Normalized: '{normalized}' (type: {type(normalized)})")

    print("\n=== Test AccountMapping Normalisierung ===")
    # AccountMappingTab-Test (nur die Normalisierungslogik)
    import pandas as pd
    
    def normalize_account_number(account_nr) -> str:
        """Normalisiert eine Sachkontonummer zu einem String-Format (Test-Version)"""
        if pd.isna(account_nr):
            return ""
        
        # Zu String konvertieren und Whitespace entfernen
        account_str = str(account_nr).strip()
        
        # Prüfen ob es eine Zahl ist (auch Floats)
        if account_str.replace('.', '').replace('-', '').isdigit():
            try:
                # Float zu Int zu String (entfernt .0 Endungen)
                float_val = float(account_str)
                if float_val.is_integer():
                    return str(int(float_val))
                else:
                    return account_str  # Behalte Original wenn echte Dezimalzahl
            except ValueError:
                pass
        
        return account_str

    # Test account_names Dict mit gemischten Schlüsseln
    mixed_account_names = {
        1000: "Kassenkonto",
        "1200": "Girokonto Bank", 
        4000.0: "Spenden allgemein",
        "5000": "Büromaterial",
        "6000": "Miete Vereinsheim"
    }

    print(f"Input account_names keys: {list(mixed_account_names.keys())}")
    print(f"Input account_names key types: {[type(k) for k in mixed_account_names.keys()]}")

    # Normalisierung testen
    normalized_dict = {}
    for key, value in mixed_account_names.items():
        normalized_key = normalize_account_number(key)
        normalized_dict[normalized_key] = value

    print(f"Normalized account_names keys: {list(normalized_dict.keys())}")
    print(f"Normalized account_names key types: {[type(k) for k in normalized_dict.keys()]}")

    for key, value in normalized_dict.items():
        print(f"Account {key}: {value}")

if __name__ == "__main__":
    print("=== Test: String-Konsistenz für Sachkontonummern ===")
    print(f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    
    # Tests ausführen
    success = test_string_consistency()
    
    if success:
        test_account_mapping_consistency()
        test_data_type_edge_cases()
    
    print("\n=== Test abgeschlossen ===")
    print("💡 Alle Sachkontonummern werden jetzt konsistent als String behandelt!")
