# -*- coding: utf-8 -*-
"""
Test für PDF-Generierung mit vollständigen Organisationsdaten
Umfassender Integrationstest für Layout und Organisationsinformationen
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


class TestOrganizationPDF(unittest.TestCase):
    """Test-Klasse für PDF-Generierung mit Organisationsdaten"""
    
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
        self.settings = QSettings(f"OrganizationTest-{self.test_id}", f"TestApp-{self.test_id}")
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

    def test_pdf_with_complete_organization_data(self):
        """Teste PDF mit vollständigen Organisationsdaten und Farbkustomisierung"""
        print("🏢 Teste PDF mit vollständigen Organisationsdaten...")
        
        # Vollständige Organisationsdaten und grüne Farbe
        self.settings.setValue("header_color", "#00AA00")  # Grün
        self.settings.setValue("organization/name", "Ehrenamt Testverein e.V.")
        self.settings.setValue("organization/street", "Musterstraße 42")
        self.settings.setValue("organization/zip", "12345")
        self.settings.setValue("organization/city", "Musterstadt")
        self.settings.setValue("organization/phone", "+49 123 456789")
        self.settings.setValue("organization/email", "kontakt@testverein.de")
        self.settings.setValue("organization/info", "Ein gemeinnütziger Verein für Test und Entwicklung")
        self.settings.setValue("opening_balance", 2500.75)
        
        # Umfangreichere Test-CSV-Daten
        test_data = pd.DataFrame({
            'Buchungstag': ['2024-01-15', '2024-02-20', '2024-03-10', '2024-04-05', '2024-05-12'],
            'Sachkontonr.': ['1000', '2000', '1500', '4000', '8000'],
            'Sachkonto': ['Kasse', 'Verbindlichkeiten', 'Forderungen', 'Einnahmen', 'Ausgaben'],
            'Verwendungszweck': ['Beitrag Mitglied A', 'Rechnungszahlung', 'Spende erhalten', 'Veranstaltungserlös', 'Materialkosten'],
            'Betrag': [50.00, -75.50, 100.00, 250.00, -45.25],
            'Betrag_Clean': [50.00, -75.50, 100.00, 250.00, -45.25],
            'Buchungsnr.': ['B001', 'B002', 'B003', 'B004', 'B005']
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
            
            # PDF-Generator mit vollständigen Settings
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Farbtest
            color = generator._get_header_color()
            self.assertAlmostEqual(color.green, 0.67, places=1, msg="Grün-Wert sollte ~0.67 sein")
            print(f"✅ Geladene Farbe: RGB({color.red:.2f}, {color.green:.2f}, {color.blue:.2f})")
            
            # Kontostandsberechnungen prüfen
            total_amount = generator._calculate_total_amount(csv_processor)
            opening_balance = generator._get_opening_balance()
            new_balance = generator._calculate_new_balance(csv_processor)
            
            expected_total = sum([50.00, -75.50, 100.00, 250.00, -45.25])  # = 279.25
            expected_new_balance = 2500.75 + expected_total  # = 2780.0
            
            self.assertAlmostEqual(total_amount, expected_total, places=2, 
                                 msg="Gesamtsumme sollte korrekt berechnet werden")
            self.assertAlmostEqual(new_balance, expected_new_balance, places=2,
                                 msg="Neuer Kontostand sollte korrekt berechnet werden")
            
            print(f"💰 Anfangskontostand: {opening_balance}€")
            print(f"💰 Summe Buchungen: {total_amount}€")
            print(f"💰 Neuer Kontostand: {new_balance}€")
            
            # PDF generieren
            pdf_path = os.path.join(os.path.dirname(__file__), "test_organization_complete.pdf")
            self.generated_files.append(pdf_path)
            
            pdf_success = generator.generate_bwa_pdf(
                pdf_path,
                csv_processor,
                {
                    "1000": "Barmittel und Bankguthaben",
                    "2000": "Verbindlichkeiten aus Lieferungen",
                    "1500": "Forderungen aus Mitgliedsbeiträgen",
                    "4000": "Mitgliedsbeiträge und Spenden", 
                    "8000": "Sonstige betriebliche Aufwendungen"
                }
            )
            
            self.assertTrue(pdf_success, "PDF-Generierung sollte erfolgreich sein")
            self.assertTrue(os.path.exists(pdf_path), "PDF-Datei sollte existieren")
            
            pdf_size = os.path.getsize(pdf_path)
            self.assertGreater(pdf_size, 3500, "PDF mit Organisationsdaten sollte mindestens 3.5KB groß sein")
            
            print(f"✅ PDF erfolgreich erstellt: {pdf_size} Bytes")
            
        except Exception as e:
            self.fail(f"Unerwarteter Fehler: {e}")

    def test_pdf_with_minimal_organization_data(self):
        """Teste PDF mit minimalen Organisationsdaten"""
        print("� Teste PDF mit minimalen Organisationsdaten...")
        
        # Nur Name und blaue Standardfarbe
        self.settings.setValue("organization/name", "Minimal Verein")
        self.settings.setValue("opening_balance", 1000.0)
        # header_color wird nicht gesetzt -> Standardblau
        
        # Minimale Test-Daten
        test_data = pd.DataFrame({
            'Buchungstag': ['2024-07-01'],
            'Sachkontonr.': ['1000'],
            'Sachkonto': ['Kasse'],
            'Verwendungszweck': ['Minimale Buchung'],
            'Betrag': [42.0],
            'Betrag_Clean': [42.0],
            'Buchungsnr.': ['M001']
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
            
            # Sollte Standardfarbe (Blau) verwenden
            color = generator._get_header_color()
            self.assertAlmostEqual(color.blue, 1.0, places=2, msg="Standardfarbe sollte blau sein")
            
            # PDF generieren
            pdf_path = os.path.join(os.path.dirname(__file__), "test_organization_minimal.pdf")
            self.generated_files.append(pdf_path)
            
            pdf_success = generator.generate_bwa_pdf(
                pdf_path,
                csv_processor,
                {"1000": "Kasse"}
            )
            
            self.assertTrue(pdf_success, "PDF-Generierung sollte erfolgreich sein")
            self.assertTrue(os.path.exists(pdf_path), "PDF-Datei sollte existieren")
            
            print(f"✅ Minimale PDF erfolgreich erstellt")
            
        except Exception as e:
            self.fail(f"Unerwarteter Fehler: {e}")


if __name__ == '__main__':
    print("🧪 Starte Organisationsdaten-Tests...")
    unittest.main(verbosity=2)
