#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests für JSON-Export-Funktionalität
"""

import unittest
import tempfile
import os
import sys
import json
from unittest.mock import Mock, patch

# Pfad zur src-Verzeichnis hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtCore import QSettings
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor


class TestJSONExport(unittest.TestCase):
    """Tests für JSON-Export-Funktionalität"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Standard QSettings verwenden (die der BWAPDFGenerator auch verwendet)
        self.test_settings = QSettings()
        
        # Test-Einstellungen setzen
        self.test_settings.setValue('json_export', True)
        self.test_settings.setValue('generate_quarterly_reports', True)
        self.test_settings.setValue('generate_account_reports', False)  # Für Test-Performance
        self.test_settings.setValue('organization/name', 'Test JSON Verein e.V.')
        self.test_settings.setValue('organization/street', 'Teststraße 123')
        self.test_settings.setValue('organization/city', 'Teststadt')
        self.test_settings.setValue('opening_balance', 1000.0)
        self.test_settings.sync()
        
    def tearDown(self):
        """Cleanup nach jedem Test"""
        # Nur Test-spezifische Werte zurücksetzen
        self.test_settings.setValue('json_export', False)
        self.test_settings.sync()
        
    def test_json_export_setting_exists(self):
        """Test: JSON-Export-Einstellung existiert und funktioniert"""
        # Überspringe GUI-Test - wird in anderen GUI-Tests abgedeckt
        self.skipTest("GUI-Test übersprungen - wird separat getestet")
        
    def test_json_export_settings_save_load(self):
        """Test: JSON-Export-Einstellung wird korrekt gespeichert und geladen"""
        # Überspringe GUI-Test - wird in anderen GUI-Tests abgedeckt
        self.skipTest("GUI-Test übersprungen - wird separat getestet")
        
    @patch('src.utils.csv_processor.CSVProcessor')
    def test_json_file_creation(self, mock_csv_processor):
        """Test: JSON-Datei wird erstellt wenn Option aktiviert ist"""
        # Mock CSV-Processor Setup
        mock_processor = Mock()
        mock_processor.get_year_data.return_value = Mock()
        mock_processor.get_year_data.return_value.empty = True
        mock_processor.get_data_by_quarter.return_value = Mock()
        mock_processor.get_data_by_quarter.return_value.empty = True
        mock_processor.get_account_numbers.return_value = []
        mock_csv_processor.return_value = mock_processor
        
        # Temporäre Dateien
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            pdf_path = tmp_pdf.name
        
        json_path = pdf_path.rsplit('.', 1)[0] + '.json'
        
        try:
            # BWA-Generator mit Test-Einstellungen (verwendet Standard QSettings)
            generator = BWAPDFGenerator()
            
            # PDF generieren (mit JSON-Export)
            success = generator.generate_bwa_pdf(pdf_path, mock_processor, {})
            
            # Verifizieren dass beide Dateien existieren
            self.assertTrue(success, "PDF-Generierung sollte erfolgreich sein")
            self.assertTrue(os.path.exists(pdf_path), "PDF-Datei sollte existieren")
            self.assertTrue(os.path.exists(json_path), "JSON-Datei sollte erstellt werden")
            
        finally:
            # Aufräumen
            for file_path in [pdf_path, json_path]:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
    @patch('src.utils.csv_processor.CSVProcessor')
    def test_json_file_not_created_when_disabled(self, mock_csv_processor):
        """Test: JSON-Datei wird NICHT erstellt wenn Option deaktiviert ist"""
        # JSON-Export deaktivieren
        self.test_settings.setValue('json_export', False)
        self.test_settings.sync()
        
        # Mock CSV-Processor Setup
        mock_processor = Mock()
        mock_processor.get_year_data.return_value = Mock()
        mock_processor.get_year_data.return_value.empty = True
        mock_processor.get_data_by_quarter.return_value = Mock()
        mock_processor.get_data_by_quarter.return_value.empty = True
        mock_processor.get_account_numbers.return_value = []
        mock_csv_processor.return_value = mock_processor
        
        # Temporäre Dateien
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            pdf_path = tmp_pdf.name
        
        json_path = pdf_path.rsplit('.', 1)[0] + '.json'
        
        try:
            # BWA-Generator mit Test-Einstellungen (verwendet Standard QSettings)
            generator = BWAPDFGenerator()
            
            # PDF generieren (ohne JSON-Export)
            success = generator.generate_bwa_pdf(pdf_path, mock_processor, {})
            
            # Verifizieren dass nur PDF existiert
            self.assertTrue(success, "PDF-Generierung sollte erfolgreich sein")
            self.assertTrue(os.path.exists(pdf_path), "PDF-Datei sollte existieren")
            self.assertFalse(os.path.exists(json_path), "JSON-Datei sollte NICHT erstellt werden")
            
        finally:
            # Aufräumen
            for file_path in [pdf_path, json_path]:
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def test_json_content_structure(self):
        """Test: JSON-Datei hat korrekte Datenstruktur"""
        # Test mit echten CSV-Daten
        if os.path.exists('testdata/Finanzübersicht_2024.csv'):
            # CSV-Prozessor mit echten Daten
            csv_proc = CSVProcessor()
            success = csv_proc.load_file('testdata/Finanzübersicht_2024.csv')
            
            if success:
                # Temporäre Dateien
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                    pdf_path = tmp_pdf.name
                
                json_path = pdf_path.rsplit('.', 1)[0] + '.json'
                
                try:
                    # BWA-Generator mit Test-Einstellungen (verwendet Standard QSettings)
                    generator = BWAPDFGenerator()
                    
                    # PDF+JSON generieren
                    pdf_success = generator.generate_bwa_pdf(pdf_path, csv_proc, {})
                    
                    self.assertTrue(pdf_success, "PDF-Generierung sollte erfolgreich sein")
                    self.assertTrue(os.path.exists(json_path), "JSON-Datei sollte existieren")
                    
                    # JSON-Inhalt prüfen
                    with open(json_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    # Struktur-Tests
                    self.assertIn('metadata', json_data, "metadata sollte vorhanden sein")
                    self.assertIn('organization', json_data, "organization sollte vorhanden sein")
                    self.assertIn('balance_info', json_data, "balance_info sollte vorhanden sein")
                    self.assertIn('yearly_summary', json_data, "yearly_summary sollte vorhanden sein")
                    self.assertIn('quarterly_summaries', json_data, "quarterly_summaries sollte vorhanden sein")
                    
                    # Metadata-Tests
                    metadata = json_data['metadata']
                    self.assertIn('export_date', metadata, "export_date sollte vorhanden sein")
                    self.assertIn('year', metadata, "year sollte vorhanden sein")
                    
                    # Organisation-Tests
                    org = json_data['organization']
                    self.assertEqual(org['name'], 'Test JSON Verein e.V.', "Organisationsname sollte korrekt sein")
                    
                    # Balance-Tests
                    balance = json_data['balance_info']
                    self.assertIn('opening_balance', balance, "opening_balance sollte vorhanden sein")
                    self.assertIn('total_transactions', balance, "total_transactions sollte vorhanden sein")
                    self.assertIn('closing_balance', balance, "closing_balance sollte vorhanden sein")
                    
                finally:
                    # Aufräumen
                    for file_path in [pdf_path, json_path]:
                        if os.path.exists(file_path):
                            os.remove(file_path)
            else:
                self.skipTest("CSV-Testdaten konnten nicht geladen werden")
        else:
            self.skipTest("CSV-Testdaten nicht verfügbar")
    
    def test_json_export_helper_methods(self):
        """Test: JSON-Export-Hilfsmethoden funktionieren korrekt"""
        generator = BWAPDFGenerator()
        
        # Organization Data Test
        org_data = generator._get_organization_data()
        self.assertIsInstance(org_data, dict, "Organization data sollte dict sein")
        self.assertEqual(org_data['name'], 'Test JSON Verein e.V.', "Name sollte korrekt sein")
        
        # Balance Info Test (mit Mock CSV-Processor)
        mock_processor = Mock()
        mock_processor.get_year_data.return_value = Mock()
        mock_processor.get_year_data.return_value.empty = True
        
        balance_info = generator._get_balance_info(mock_processor)
        self.assertIsInstance(balance_info, dict, "Balance info sollte dict sein")
        self.assertIn('opening_balance', balance_info, "opening_balance sollte vorhanden sein")
        self.assertEqual(balance_info['opening_balance'], 1000.0, "Opening balance sollte 1000.0 sein")


if __name__ == '__main__':
    unittest.main()
