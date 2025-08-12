#!/usr/bin/env python3
"""
Finaler automatisierter JSON Roundtrip Test
Kann als Regression-Test für zukünftige Entwicklung verwendet werden
"""

import os
import sys
import json
import tempfile
from PySide6.QtCore import QSettings

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from utils.csv_processor import CSVProcessor

class JSONRoundtripTest:
    """Automatisierter Test für JSON Import/Export Funktionalität"""
    
    def __init__(self):
        self.test_results = {
            'csv_loading': False,
            'json_export': False, 
            'json_import': False,
            'data_integrity': False,
            'overall': False
        }
        
    def setup_test_environment(self):
        """Konfiguriert Test-Umgebung"""
        settings = QSettings()
        
        # Basis-Einstellungen für Tests
        test_settings = {
            "organization/name": "Test Organization",
            "organization/street": "Test Street 123",
            "organization/zip": "12345",
            "organization/city": "Test City",
            "opening_balance": 1000.0,
            "json_export": True
        }
        
        for key, value in test_settings.items():
            settings.setValue(key, value)
        
        # Account-Mappings
        mappings = {
            "S03220": "Donations General",
            "S03223": "Donations Projects", 
            "S03215": "Organization Income",
            "S03216": "Membership Fees",
            "S02660": "Rent and Utilities",
            "S02720": "Project Expenses",
            "S02702": "IT and Communication",
            "S02701": "Office Supplies",
            "S02703": "Travel Costs",
            "S02705": "Events",
            "S02710": "Youth Work",
            "S02711": "Administration",
            "S02712": "Volunteer Compensation",
            "S02802": "Gifts",
            "S02811": "Marketing",
            "S04712": "Bank Fees"
        }
        
        settings.setValue("account_mappings", json.dumps(mappings))
        return True
    
    def test_csv_loading(self, csv_path):
        """Test CSV-Loading"""
        try:
            processor = CSVProcessor()
            success = processor.load_file(csv_path)
            
            if success and processor.processed_data is not None:
                entry_count = len(processor.processed_data)
                print(f"✅ CSV Loading: {entry_count} Einträge geladen")
                self.test_results['csv_loading'] = True
                return processor
            else:
                print("❌ CSV Loading fehlgeschlagen")
                return None
                
        except Exception as e:
            print(f"❌ CSV Loading Fehler: {e}")
            return None
    
    def create_test_json(self, processor, json_path):
        """Erstellt Test-JSON aus CSV-Daten"""
        try:
            settings = QSettings()
            
            # Gruppiere Transaktionen nach Sachkonto
            accounts_data = {}
            
            for _, row in processor.processed_data.iterrows():
                account_nr = row.get('Sachkontonr.', '')
                account_name = row.get('Sachkonto', '')
                
                if account_nr not in accounts_data:
                    accounts_data[account_nr] = {
                        'account_number': account_nr,
                        'account_name': account_name,
                        'transactions': []
                    }
                
                transaction = {
                    'booking_number': row.get('Buchungsnr.', ''),
                    'date': row.get('Buchungstag', ''),
                    'purpose': row.get('Verwendungszweck', ''),
                    'amount': row.get('Betrag', ''),
                    'amount_clean': row.get('Betrag_Clean', 0.0),
                    'quarter': row.get('Quartal', 1)
                }
                
                accounts_data[account_nr]['transactions'].append(transaction)
            
            json_data = {
                "metadata": {
                    "created_at": "2024-08-12T12:00:00",
                    "version": "1.0",
                    "source_file": "automated_test",
                    "test_mode": True
                },
                "organization": {
                    "name": settings.value("organization/name", ""),
                    "street": settings.value("organization/street", ""),
                    "zip": settings.value("organization/zip", ""),
                    "city": settings.value("organization/city", ""),
                    "phone": settings.value("organization/phone", ""),
                    "email": settings.value("organization/email", ""),
                    "info": settings.value("organization/info", "")
                },
                "balance_info": {
                    "opening_balance": settings.value("opening_balance", 0.0, type=float),
                    "period": "2024"
                },
                "account_mappings": {
                    "S03220": "Donations General",
                    "S03223": "Donations Projects", 
                    "S03215": "Organization Income",
                    "S03216": "Membership Fees",
                    "S02660": "Rent and Utilities",
                    "S02720": "Project Expenses",
                    "S02702": "IT and Communication",
                    "S02701": "Office Supplies",
                    "S02703": "Travel Costs",
                    "S02705": "Events",
                    "S02710": "Youth Work",
                    "S02711": "Administration",
                    "S02712": "Volunteer Compensation",
                    "S02802": "Gifts",
                    "S02811": "Marketing",
                    "S04712": "Bank Fees"
                },
                "super_group_mappings": {
                    "Donations General": "Income",
                    "Donations Projects": "Income",
                    "Organization Income": "Income", 
                    "Membership Fees": "Income",
                    "Rent and Utilities": "Expenses",
                    "Project Expenses": "Expenses",
                    "IT and Communication": "Expenses",
                    "Office Supplies": "Expenses",
                    "Travel Costs": "Expenses",
                    "Events": "Expenses",
                    "Youth Work": "Expenses",
                    "Administration": "Expenses",
                    "Volunteer Compensation": "Expenses",
                    "Gifts": "Expenses",
                    "Marketing": "Expenses",
                    "Bank Fees": "Expenses"
                },
                "account_details": list(accounts_data.values())
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ JSON Export: {len(accounts_data)} Konten, {os.path.getsize(json_path)} Bytes")
            self.test_results['json_export'] = True
            return True
            
        except Exception as e:
            print(f"❌ JSON Export Fehler: {e}")
            return False
    
    def test_json_import(self, json_path):
        """Test JSON-Import"""
        try:
            processor = CSVProcessor()
            success = processor.load_file(json_path)
            
            if success and processor.processed_data is not None:
                entry_count = len(processor.processed_data)
                print(f"✅ JSON Import: {entry_count} Einträge importiert")
                self.test_results['json_import'] = True
                return processor
            else:
                print("❌ JSON Import fehlgeschlagen")
                return None
                
        except Exception as e:
            print(f"❌ JSON Import Fehler: {e}")
            return None
    
    def test_data_integrity(self, original_processor, imported_processor):
        """Test Datenintegrität nach Roundtrip"""
        try:
            # Anzahl Einträge
            count_original = len(original_processor.processed_data)
            count_imported = len(imported_processor.processed_data)
            
            if count_original != count_imported:
                print(f"❌ Datenintegrität: Anzahl Einträge {count_original} → {count_imported}")
                return False
            
            # Beträge-Summe (falls verfügbar)
            if 'Betrag_Clean' in original_processor.processed_data.columns and 'Betrag_Clean' in imported_processor.processed_data.columns:
                sum_original = original_processor.processed_data['Betrag_Clean'].sum()
                sum_imported = imported_processor.processed_data['Betrag_Clean'].sum()
                
                if abs(sum_original - sum_imported) > 0.01:
                    print(f"❌ Datenintegrität: Beträge {sum_original:.2f} → {sum_imported:.2f}")
                    return False
                
                print(f"✅ Datenintegrität: {count_original} Einträge, {sum_original:.2f} € Summe")
            else:
                print(f"✅ Datenintegrität: {count_original} Einträge")
            
            self.test_results['data_integrity'] = True
            return True
            
        except Exception as e:
            print(f"❌ Datenintegrität Fehler: {e}")
            return False
    
    def run_complete_test(self, csv_path=None):
        """Führt kompletten Test aus"""
        print("🧪 JSON Roundtrip Regression Test")
        print("=" * 50)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Test-Umgebung Setup fehlgeschlagen")
            return False
        
        # Standard-CSV falls nicht angegeben
        if csv_path is None:
            csv_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/test_anonymous.csv"
        
        if not os.path.exists(csv_path):
            print(f"❌ Test-CSV nicht gefunden: {csv_path}")
            return False
        
        # Test-Verzeichnis
        test_dir = "/tmp/json_roundtrip_regression_test"
        os.makedirs(test_dir, exist_ok=True)
        json_path = os.path.join(test_dir, "test_export.json")
        
        try:
            # 1. CSV Loading
            print("\n📊 Test 1: CSV Loading...")
            original_processor = self.test_csv_loading(csv_path)
            if not original_processor:
                return False
            
            # 2. JSON Export
            print("\n📤 Test 2: JSON Export...")
            if not self.create_test_json(original_processor, json_path):
                return False
            
            # 3. JSON Import
            print("\n📥 Test 3: JSON Import...")
            imported_processor = self.test_json_import(json_path)
            if not imported_processor:
                return False
            
            # 4. Datenintegrität
            print("\n🔍 Test 4: Datenintegrität...")
            if not self.test_data_integrity(original_processor, imported_processor):
                return False
            
            # Gesamtergebnis
            all_tests_passed = all([
                self.test_results['csv_loading'],
                self.test_results['json_export'], 
                self.test_results['json_import'],
                self.test_results['data_integrity']
            ])
            self.test_results['overall'] = all_tests_passed
            
            print("\n📊 Test-Ergebnisse:")
            print("=" * 30)
            for test_name, result in self.test_results.items():
                status = "✅" if result else "❌"
                print(f"{status} {test_name.replace('_', ' ').title()}")
            
            if self.test_results['overall']:
                print("\n🎉 Alle Tests erfolgreich!")
                print("📋 JSON Roundtrip funktioniert korrekt")
                return True
            else:
                print("\n💥 Tests fehlgeschlagen!")
                return False
            
        except Exception as e:
            print(f"❌ Unerwarteter Test-Fehler: {e}")
            return False
            
        finally:
            print(f"\n🗂️ Test-Dateien: {test_dir}")

def main():
    """Hauptfunktion"""
    test = JSONRoundtripTest()
    
    # CSV-Pfad aus Kommandozeile oder Standard
    csv_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    success = test.run_complete_test(csv_path)
    
    print(f"\n{'🎯 REGRESSION TEST: BESTANDEN' if success else '💥 REGRESSION TEST: FEHLGESCHLAGEN'}")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
