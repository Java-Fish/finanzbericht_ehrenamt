# -*- coding: utf-8 -*-
"""
Test für PDF-Generierung mit Deckblatt-Demo
Demonstriert verbessertes PDF-Layout mit Organisationsdaten
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


class TestCoverPageDemo(unittest.TestCase):
    """Test-Klasse für das verbesserte PDF-Deckblatt"""
    
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
        self.settings = QSettings(f"CoverPageDemo-{self.test_id}", f"TestApp-{self.test_id}")
        self.generated_files = []
        
    def tearDown(self):
        """Cleanup nach jedem Test"""
        # Alle generierten Dateien löschen
        for file_path in self.generated_files:
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except OSError:
                    pass
        
        self.settings.clear()

    def test_demo_pdf_creation(self):
        """Teste Erstellung eines Demo-PDFs mit realistischen Vereinsdaten"""
        print("📄 Teste Demo-PDF mit verbessertem Deckblatt...")
        
        # Test-Organisationsdaten setzen
        self.settings.setValue("organization/name", "Musterverein e.V.")
        self.settings.setValue("organization/street", "Vereinsstraße 42")
        self.settings.setValue("organization/zip", "12345")
        self.settings.setValue("organization/city", "Musterstadt")
        self.settings.setValue("organization/phone", "+49 (0) 123 456789")
        self.settings.setValue("organization/email", "kontakt@musterverein.de")
        self.settings.setValue("organization/info", "Gemeinnütziger Verein für Bildung und Kultur")
        self.settings.setValue("opening_balance", 5000.0)
        
        # PDF-Einstellungen für kompaktes Demo
        self.settings.setValue("generate_quarterly_reports", False)
        self.settings.setValue("generate_account_reports", False)
        self.settings.setValue("generate_chart_report", False)
        
        # Test-CSV-Daten mit realistischen Vereinsdaten
        demo_csv_content = """Buchungstag;Sachkontonr.;Sachkonto;Verwendungszweck;Betrag;Betrag_Clean;Buchungsnr.
2025-01-15;4000;Mitgliedsbeiträge;Jahresbeitrag 2025;1200.00;1200.00;MB001
2025-02-01;4000;Mitgliedsbeiträge;Nachzahlungen;850.00;850.00;MB002
2025-01-20;4100;Spenden;Neujahrssammlung;2500.50;2500.50;SP001
2025-03-15;4100;Spenden;Frühjahrsbasar;1750.00;1750.00;SP002
2025-01-25;6300;Bürokosten;Büromaterial Januar;-125.80;-125.80;BK001
2025-02-28;6300;Bürokosten;Porto und Telefon;-89.50;-89.50;BK002
2025-01-31;6400;Miete;Vereinsheim Januar;-450.00;-450.00;MK001
2025-02-28;6400;Miete;Vereinsheim Februar;-450.00;-450.00;MK002"""
        
        # Temporäre CSV-Datei erstellen
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_csv:
            temp_csv.write(demo_csv_content)
            temp_csv_path = temp_csv.name
        
        self.generated_files.append(temp_csv_path)
        
        try:
            # CSV-Processor
            csv_processor = CSVProcessor()
            success = csv_processor.load_csv_file(temp_csv_path)
            self.assertTrue(success, "CSV-Datei sollte erfolgreich geladen werden")
            
            # BWA-Generator mit Demo-Settings
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # PDF-Pfad
            pdf_path = os.path.join(os.path.dirname(__file__), "demo_cover_page.pdf")
            self.generated_files.append(pdf_path)
            
            # PDF generieren
            pdf_success = generator.generate_bwa_pdf(
                pdf_path,
                csv_processor,
                {
                    "4000": "Mitgliedsbeiträge und Aufnahmegebühren",
                    "4100": "Spenden und Zuschüsse",
                    "6300": "Büro- und Verwaltungskosten",
                    "6400": "Miete und Nebenkosten"
                }
            )
            
            self.assertTrue(pdf_success, "Demo-PDF sollte erfolgreich erstellt werden")
            self.assertTrue(os.path.exists(pdf_path), "Demo-PDF-Datei sollte existieren")
            
            # PDF-Größe prüfen
            pdf_size = os.path.getsize(pdf_path)
            self.assertGreater(pdf_size, 3000, "Demo-PDF sollte mindestens 3KB groß sein")
            
            print(f"✅ Demo-PDF erfolgreich erstellt: {pdf_size} Bytes")
            
            # Kontostandsberechnungen validieren
            total_amount = generator._calculate_total_amount(csv_processor)
            expected_total = (1200.00 + 850.00 + 2500.50 + 1750.00 - 125.80 - 89.50 - 450.00 - 450.00)  # 5185.20
            
            self.assertAlmostEqual(total_amount, expected_total, places=2, 
                                 msg="Gesamtsumme sollte korrekt berechnet werden")
            
            print(f"💰 Berechnungen validiert: {total_amount:.2f}€")
            
        except Exception as e:
            self.fail(f"Unerwarteter Fehler bei Demo-PDF-Erstellung: {e}")

    def test_demo_pdf_with_custom_colors(self):
        """Teste Demo-PDF mit benutzerdefinierten Farben"""
        print("🎨 Teste Demo-PDF mit benutzerdefinierten Farben...")
        
        # Organisationsdaten und benutzerdefinierte Farbe
        self.settings.setValue("organization/name", "Farbverein e.V.")
        self.settings.setValue("organization/city", "Farbstadt")
        self.settings.setValue("opening_balance", 3000.0)
        self.settings.setValue("header_color", "#800080")  # Lila
        
        # Einfache Test-Daten
        simple_csv_content = """Buchungstag;Sachkontonr.;Sachkonto;Verwendungszweck;Betrag;Betrag_Clean;Buchungsnr.
2025-04-01;1000;Kasse;Test-Einnahme;500.00;500.00;T001
2025-04-15;2000;Ausgaben;Test-Ausgabe;-200.00;-200.00;T002"""
        
        # Temporäre CSV-Datei
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_csv:
            temp_csv.write(simple_csv_content)
            temp_csv_path = temp_csv.name
        
        self.generated_files.append(temp_csv_path)
        
        try:
            # CSV-Processor
            csv_processor = CSVProcessor()
            success = csv_processor.load_csv_file(temp_csv_path)
            self.assertTrue(success, "CSV-Datei sollte erfolgreich geladen werden")
            
            # BWA-Generator
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Farbtest
            color = generator._get_header_color()
            self.assertAlmostEqual(color.red, 0.5, places=1, msg="Lila sollte Rot-Wert ~0.5 haben")
            self.assertAlmostEqual(color.green, 0.0, places=2, msg="Lila sollte Grün-Wert 0.0 haben")
            self.assertAlmostEqual(color.blue, 0.5, places=1, msg="Lila sollte Blau-Wert ~0.5 haben")
            
            # PDF-Pfad
            pdf_path = os.path.join(os.path.dirname(__file__), "demo_colored_cover.pdf")
            self.generated_files.append(pdf_path)
            
            # PDF generieren
            pdf_success = generator.generate_bwa_pdf(
                pdf_path,
                csv_processor,
                {"1000": "Kasse", "2000": "Ausgaben"}
            )
            
            self.assertTrue(pdf_success, "Farbiges Demo-PDF sollte erfolgreich erstellt werden")
            self.assertTrue(os.path.exists(pdf_path), "Farbiges Demo-PDF sollte existieren")
            
            print(f"✅ Farbiges Demo-PDF mit Lila-Überschriften erstellt")
            
        except Exception as e:
            self.fail(f"Unerwarteter Fehler bei farbigem Demo-PDF: {e}")


if __name__ == '__main__':
    print("🧪 Starte Cover-Page-Demo-Tests...")
    unittest.main(verbosity=2)
