# -*- coding: utf-8 -*-
"""
Test der PDF-Generierung mit benutzerdefinierten Farben
Integrationstest für die Header-Farb-Funktionalität
"""

import sys
import os
import tempfile
import unittest

# Python-Pfad für Imports anpassen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings, QCoreApplication
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor
import pandas as pd


class TestColorIntegration(unittest.TestCase):
    """Test-Klasse für die Farbintegration in PDF-Generierung"""
    
    @classmethod
    def setUpClass(cls):
        """Setup für die Test-Klasse"""
        if QCoreApplication.instance() is None:
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QCoreApplication.instance()
    
    def setUp(self):
        """Setup für jeden Test"""
        import uuid
        self.test_id = str(uuid.uuid4())
        self.settings = QSettings(f"ColorIntegrationTest-{self.test_id}", f"TestApp-{self.test_id}")
        self.generated_files = []  # Liste der zu löschenden Dateien
        
    def tearDown(self):
        """Cleanup nach jedem Test"""
        # Alle generierten Dateien löschen
        for file_path in self.generated_files:
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except OSError:
                    pass  # Ignoriere Fehler beim Löschen
        
        # Settings zurücksetzen
        self.settings.clear()

    def test_pdf_with_custom_red_color(self):
        """Teste PDF-Generierung mit roter Überschriftenfarbe"""
        print("🎨 Teste PDF-Generierung mit roter Farbe...")
        
        # Test-Settings mit roter Farbe
        self.settings.setValue("header_color", "#FF0000")  # Rot
        self.settings.setValue("organization/name", "Test Verein e.V.")
        self.settings.setValue("organization/street", "Teststraße 123")
        self.settings.setValue("organization/city", "Teststadt")
        self.settings.setValue("opening_balance", 1000.0)
        
        # Test-CSV-Daten erstellen
        test_data = pd.DataFrame({
            'Buchungstag': ['2024-01-15', '2024-02-20', '2024-03-10'],
            'Sachkontonr.': ['1000', '2000', '1500'],
            'Sachkonto': ['Kasse', 'Verbindlichkeiten', 'Forderungen'],
            'Verwendungszweck': ['Testbuchung 1', 'Testbuchung 2', 'Testbuchung 3'],
            'Betrag': [100.50, -50.25, 75.00],
            'Betrag_Clean': [100.50, -50.25, 75.00],
            'Buchungsnr.': ['B001', 'B002', 'B003']
        })
        
        # Temporäre CSV-Datei
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_csv:
            test_data.to_csv(temp_csv.name, index=False, sep=';')
            temp_csv_path = temp_csv.name
        
        self.generated_files.append(temp_csv_path)
        
        try:
            # CSV-Processor
            csv_processor = CSVProcessor()
            success = csv_processor.load_csv_file(temp_csv_path)
            self.assertTrue(success, "CSV-Datei sollte erfolgreich geladen werden")
            
            # PDF-Generator mit benutzerdefinierten Settings
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Farbtest
            color = generator._get_header_color()
            self.assertAlmostEqual(color.red, 1.0, places=2, msg="Rot-Wert sollte 1.0 sein")
            self.assertAlmostEqual(color.green, 0.0, places=2, msg="Grün-Wert sollte 0.0 sein")
            self.assertAlmostEqual(color.blue, 0.0, places=2, msg="Blau-Wert sollte 0.0 sein")
            
            print(f"✅ Geladene Farbe: RGB({color.red:.2f}, {color.green:.2f}, {color.blue:.2f})")
            
            # PDF generieren
            pdf_path = os.path.join(os.path.dirname(__file__), "test_custom_red_color.pdf")
            self.generated_files.append(pdf_path)
            
            pdf_success = generator.generate_bwa_pdf(
                pdf_path,
                csv_processor,
                {"1000": "Kasse", "2000": "Verbindlichkeiten", "1500": "Forderungen"}
            )
            
            self.assertTrue(pdf_success, "PDF-Generierung sollte erfolgreich sein")
            self.assertTrue(os.path.exists(pdf_path), "PDF-Datei sollte existieren")
            
            pdf_size = os.path.getsize(pdf_path)
            self.assertGreater(pdf_size, 3000, "PDF sollte mindestens 3KB groß sein")
            
            print(f"✅ PDF erfolgreich erstellt: {pdf_size} Bytes")
            
        except Exception as e:
            self.fail(f"Unerwarteter Fehler: {e}")

    def test_pdf_with_custom_green_color(self):
        """Teste PDF-Generierung mit grüner Überschriftenfarbe"""
        print("🌿 Teste PDF-Generierung mit grüner Farbe...")
        
        # Test-Settings mit grüner Farbe
        self.settings.setValue("header_color", "#00AA00")  # Grün
        self.settings.setValue("organization/name", "Grüner Test Verein")
        self.settings.setValue("opening_balance", 500.0)
        
        # Einfache Test-Daten
        test_data = pd.DataFrame({
            'Buchungstag': ['2024-06-15'],
            'Sachkontonr.': ['1000'],
            'Sachkonto': ['Kasse'],
            'Verwendungszweck': ['Grüne Testbuchung'],
            'Betrag': [200.0],
            'Betrag_Clean': [200.0],
            'Buchungsnr.': ['G001']
        })
        
        # Temporäre CSV-Datei
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_csv:
            test_data.to_csv(temp_csv.name, index=False, sep=';')
            temp_csv_path = temp_csv.name
        
        self.generated_files.append(temp_csv_path)
        
        try:
            # CSV-Processor
            csv_processor = CSVProcessor()
            success = csv_processor.load_csv_file(temp_csv_path)
            self.assertTrue(success, "CSV-Datei sollte erfolgreich geladen werden")
            
            # PDF-Generator
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Farbtest - Grün (0x00AA00 = RGB(0, 170, 0))
            color = generator._get_header_color()
            self.assertAlmostEqual(color.red, 0.0, places=2, msg="Rot-Wert sollte 0.0 sein")
            self.assertAlmostEqual(color.green, 0.67, places=1, msg="Grün-Wert sollte ~0.67 sein (170/255)")
            self.assertAlmostEqual(color.blue, 0.0, places=2, msg="Blau-Wert sollte 0.0 sein")
            
            print(f"✅ Geladene Farbe: RGB({color.red:.2f}, {color.green:.2f}, {color.blue:.2f})")
            
            # PDF generieren
            pdf_path = os.path.join(os.path.dirname(__file__), "test_custom_green_color.pdf")
            self.generated_files.append(pdf_path)
            
            pdf_success = generator.generate_bwa_pdf(
                pdf_path,
                csv_processor,
                {"1000": "Kasse"}
            )
            
            self.assertTrue(pdf_success, "PDF-Generierung sollte erfolgreich sein")
            self.assertTrue(os.path.exists(pdf_path), "PDF-Datei sollte existieren")
            
            print(f"✅ Grüne PDF erfolgreich erstellt")
            
        except Exception as e:
            self.fail(f"Unerwarteter Fehler: {e}")


if __name__ == '__main__':
    print("🧪 Starte Farbintegrations-Tests...")
    unittest.main(verbosity=2)
