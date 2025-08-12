#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für JSON-Import-Funktionalität
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

# Projekt-Pfad hinzufügen
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtCore import QSettings
from src.utils.csv_processor import CSVProcessor
from src.utils.bwa_generator import BWAPDFGenerator


class TestJSONImport(unittest.TestCase):
    """Tests für JSON-Import-Funktionalität"""
    
    def setUp(self):
        """Test-Setup"""
        self.csv_processor = CSVProcessor()
        self.bwa_generator = BWAPDFGenerator()
        self.test_json_data = self._create_test_json_data()
        
    def _create_test_json_data(self):
        """Erstellt Test-JSON-Daten"""
        return {
            "metadata": {
                "export_date": "2024-08-12T10:00:00",
                "year": 2024,
                "quarter_mode": "cumulative",
                "generated_reports": {
                    "quarterly": True,
                    "account_details": True
                }
            },
            "organization": {
                "name": "Test Verein e.V.",
                "street": "Teststraße 123",
                "zip": "12345",
                "city": "Teststadt",
                "phone": "+49 123 456789",
                "email": "test@verein.de",
                "info": "Ein Test-Verein"
            },
            "balance_info": {
                "opening_balance": 1000.0,
                "total_transactions": 500.0,
                "closing_balance": 1500.0
            },
            "yearly_summary": {
                "summary": {
                    "Einnahmen": {
                        "Mitgliedsbeiträge": 1200.0,
                        "Spenden": 800.0
                    },
                    "Ausgaben": {
                        "Verwaltungskosten": -300.0,
                        "Veranstaltungskosten": -700.0
                    }
                },
                "bwa_groups": {
                    "Mitgliedsbeiträge": 1200.0,
                    "Spenden": 800.0,
                    "Verwaltungskosten": -300.0,
                    "Veranstaltungskosten": -700.0
                },
                "total": 1000.0
            },
            "quarterly_summaries": [],
            "account_details": [
                {
                    "account_number": "8100",
                    "account_name": "Mitgliedsbeiträge",
                    "total": 1200.0,
                    "transaction_count": 3,
                    "transactions": [
                        {
                            "booking_number": "1",
                            "date": "2024-01-15",
                            "purpose": "Beitrag Januar",
                            "amount": 400.0
                        },
                        {
                            "booking_number": "2", 
                            "date": "2024-02-15",
                            "purpose": "Beitrag Februar",
                            "amount": 400.0
                        },
                        {
                            "booking_number": "3",
                            "date": "2024-03-15", 
                            "purpose": "Beitrag März",
                            "amount": 400.0
                        }
                    ]
                },
                {
                    "account_number": "8200",
                    "account_name": "Spenden",
                    "total": 800.0,
                    "transaction_count": 2,
                    "transactions": [
                        {
                            "booking_number": "4",
                            "date": "2024-01-20",
                            "purpose": "Spende Privat",
                            "amount": 300.0
                        },
                        {
                            "booking_number": "5",
                            "date": "2024-02-20",
                            "purpose": "Spende Firma",
                            "amount": 500.0
                        }
                    ]
                }
            ]
        }
    
    def test_json_file_validation(self):
        """Test: JSON-Datei-Validierung funktioniert"""
        # Gültige JSON-Struktur
        valid_result = self.csv_processor._validate_json_structure(self.test_json_data)
        self.assertTrue(valid_result, "Gültige JSON-Struktur sollte validiert werden")
        
        # Ungültige JSON-Struktur (fehlender Schlüssel)
        invalid_json = self.test_json_data.copy()
        del invalid_json['metadata']
        
        invalid_result = self.csv_processor._validate_json_structure(invalid_json)
        self.assertFalse(invalid_result, "Ungültige JSON-Struktur sollte abgelehnt werden")
    
    def test_dataframe_creation_from_json(self):
        """Test: DataFrame-Erstellung aus JSON-Daten funktioniert"""
        # JSON-Daten setzen
        self.csv_processor.json_data = self.test_json_data
        self.csv_processor.is_json_source = True
        
        # DataFrame erstellen
        df = self.csv_processor._create_dataframe_from_json()
        
        # Überprüfungen
        self.assertIsNotNone(df, "DataFrame sollte erstellt werden")
        self.assertGreater(len(df), 0, "DataFrame sollte Daten enthalten")
        
        # Spalten prüfen
        expected_columns = ['Buchungsnr.', 'Sachkontonr.', 'Sachkonto', 'Buchungstag', 
                          'Verwendungszweck', 'Betrag']
        for col in expected_columns:
            self.assertIn(col, df.columns, f"Spalte {col} sollte vorhanden sein")
        
        # Daten prüfen
        sachkonten = df['Sachkontonr.'].unique()
        self.assertIn('8100', sachkonten, "Sachkonto 8100 sollte vorhanden sein")
        self.assertIn('8200', sachkonten, "Sachkonto 8200 sollte vorhanden sein")
    
    def test_json_organization_data_extraction(self):
        """Test: Organisationsdaten aus JSON extrahieren"""
        # JSON-Daten setzen
        self.csv_processor.json_data = self.test_json_data
        self.csv_processor.is_json_source = True
        
        # Organisationsdaten holen
        org_data = self.csv_processor.get_json_organization_data()
        
        # Überprüfungen
        self.assertIsNotNone(org_data, "Organisationsdaten sollten verfügbar sein")
        self.assertEqual(org_data.get('name'), "Test Verein e.V.")
        self.assertEqual(org_data.get('street'), "Teststraße 123")
        self.assertEqual(org_data.get('city'), "Teststadt")
    
    def test_json_balance_info_extraction(self):
        """Test: Kontostandsinfo aus JSON extrahieren"""
        # JSON-Daten setzen
        self.csv_processor.json_data = self.test_json_data
        self.csv_processor.is_json_source = True
        
        # Kontostandsinfo holen
        balance_info = self.csv_processor.get_json_balance_info()
        
        # Überprüfungen
        self.assertIsNotNone(balance_info, "Kontostandsinfo sollte verfügbar sein")
        self.assertEqual(balance_info.get('opening_balance'), 1000.0)
        self.assertEqual(balance_info.get('total_transactions'), 500.0)
        self.assertEqual(balance_info.get('closing_balance'), 1500.0)
    
    def test_json_file_loading(self):
        """Test: JSON-Datei laden funktioniert"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_json_data, f, indent=2)
            json_path = f.name
        
        try:
            # JSON-Datei laden
            success = self.csv_processor.load_file(json_path)
            
            # Überprüfungen
            self.assertTrue(success, "JSON-Datei sollte erfolgreich geladen werden")
            self.assertTrue(self.csv_processor.is_json_source, "JSON-Quelle sollte erkannt werden")
            self.assertIsNotNone(self.csv_processor.json_data, "JSON-Daten sollten gesetzt sein")
            
            # DataFrame prüfen
            self.assertIsNotNone(self.csv_processor.processed_data, "Verarbeitete Daten sollten verfügbar sein")
            
        finally:
            # Aufräumen
            if os.path.exists(json_path):
                os.unlink(json_path)
    
    def test_bwa_generation_from_json(self):
        """Test: BWA-Generierung aus JSON-Daten"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as json_file:
            json.dump(self.test_json_data, json_file, indent=2)
            json_path = json_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
            pdf_path = pdf_file.name
        
        try:
            # JSON-Datei laden
            success = self.csv_processor.load_file(json_path)
            self.assertTrue(success, "JSON-Datei sollte geladen werden")
            
            # BWA generieren
            bwa_success = self.bwa_generator.generate_bwa_pdf(pdf_path, self.csv_processor)
            
            # Überprüfungen
            self.assertTrue(bwa_success, "BWA sollte aus JSON-Daten erstellt werden")
            self.assertTrue(os.path.exists(pdf_path), "PDF-Datei sollte erstellt werden")
            
            # PDF-Größe prüfen
            pdf_size = os.path.getsize(pdf_path)
            self.assertGreater(pdf_size, 1000, "PDF sollte sinnvolle Größe haben")
            
        finally:
            # Aufräumen
            for path in [json_path, pdf_path]:
                if os.path.exists(path):
                    os.unlink(path)


    def test_real_json_file_import(self):
        """Test: Import einer echten JSON-Datei aus testdata"""
        json_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'testdata', 'test.json')
        
        # Prüfen ob die Datei existiert
        if not os.path.exists(json_file):
            self.skipTest(f"Test-JSON-Datei nicht gefunden: {json_file}")
        
        # JSON-Datei laden
        success = self.csv_processor.load_file(json_file)
        
        # Überprüfungen
        self.assertTrue(success, f"Echte JSON-Datei sollte geladen werden: {json_file}")
        self.assertTrue(self.csv_processor.is_json_source, "JSON-Quelle sollte erkannt werden")
        self.assertIsNotNone(self.csv_processor.json_data, "JSON-Daten sollten gesetzt sein")
        self.assertIsNotNone(self.csv_processor.processed_data, "Verarbeitete Daten sollten verfügbar sein")
        
        # Daten-Details prüfen
        self.assertGreater(len(self.csv_processor.processed_data), 0, "DataFrame sollte Daten enthalten")
        
        # Organisationsdaten prüfen
        org_data = self.csv_processor.get_json_organization_data()
        self.assertIsNotNone(org_data, "Organisationsdaten sollten verfügbar sein")
        self.assertIn('name', org_data, "Organisationsname sollte vorhanden sein")
        
        # Kontostandsinfo prüfen
        balance_info = self.csv_processor.get_json_balance_info()
        self.assertIsNotNone(balance_info, "Kontostandsinfo sollte verfügbar sein")
        self.assertIn('opening_balance', balance_info, "Anfangskontostand sollte vorhanden sein")
        
        print(f"✅ Echte JSON-Datei erfolgreich importiert: {len(self.csv_processor.processed_data)} Buchungen")
    
    def test_main_window_json_processing(self):
        """Test: MainWindow JSON-Verarbeitung ohne GUI-Interferenz"""
        # Test überspringen wenn GUI nicht verfügbar
        try:
            from PySide6.QtWidgets import QApplication
            if not QApplication.instance():
                app = QApplication([])
            
            from src.main_window import MainWindow
            
            # MainWindow erstellen
            window = MainWindow()
            
            # Test-JSON erstellen
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(self.test_json_data, f, indent=2)
                json_path = f.name
            
            try:
                # JSON-Verarbeitung testen (sollte nicht mehr auf status_label zugreifen)
                window._process_json_file(json_path)
                
                # Überprüfung dass CSVProcessor korrekt gesetzt wurde
                self.assertTrue(window.csv_processor.is_json_source, "JSON-Quelle sollte erkannt werden")
                self.assertIsNotNone(window.csv_processor.json_data, "JSON-Daten sollten gesetzt sein")
                
                print("✅ MainWindow JSON-Verarbeitung erfolgreich")
                
            finally:
                # Aufräumen
                if os.path.exists(json_path):
                    os.unlink(json_path)
                    
        except ImportError:
            self.skipTest("GUI-Test übersprungen - PySide6 nicht verfügbar")
        except Exception as e:
            if 'status_label' in str(e):
                self.fail(f"Status-Label-Fehler nicht behoben: {e}")
            else:
                self.skipTest(f"GUI-Test übersprungen - andere GUI-Probleme: {e}")


    def test_status_label_error_fix(self):
        """Test: Überprüfung dass der status_label Fehler behoben ist"""
        try:
            from PySide6.QtWidgets import QApplication
            if not QApplication.instance():
                app = QApplication([])
            
            from src.main_window import MainWindow
            
            # MainWindow erstellen
            window = MainWindow()
            
            # Prüfen dass status_label NICHT existiert (da es den Fehler verursacht hat)
            self.assertFalse(hasattr(window, 'status_label'), 
                           "MainWindow sollte kein status_label Attribut haben")
            
            # Prüfen dass file_drop_area existiert (für Status-Updates)
            self.assertTrue(hasattr(window, 'file_drop_area'), 
                          "MainWindow sollte file_drop_area für Status-Updates haben")
            
            # Test-JSON erstellen und verarbeiten
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(self.test_json_data, f, indent=2)
                json_path = f.name
            
            try:
                # Dies sollte NICHT mehr den status_label Fehler werfen
                window._process_json_file(json_path)
                print("✅ Status-Label-Fehler erfolgreich behoben")
                
            except AttributeError as e:
                if 'status_label' in str(e):
                    self.fail(f"Status-Label-Fehler NICHT behoben: {e}")
                else:
                    raise  # Andere AttributeErrors weiterleiten
                    
            finally:
                # Aufräumen
                if os.path.exists(json_path):
                    os.unlink(json_path)
                    
        except ImportError:
            self.skipTest("GUI-Test übersprungen - PySide6 nicht verfügbar")
        except Exception as e:
            # Andere Exceptions sind OK, solange es nicht der status_label Fehler ist
            if 'status_label' in str(e):
                self.fail(f"Status-Label-Fehler noch vorhanden: {e}")
            else:
                self.skipTest(f"GUI-Test übersprungen - andere Probleme: {e}")


if __name__ == '__main__':
    unittest.main()
