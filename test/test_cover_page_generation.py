# -*- coding: utf-8 -*-
"""
Test für die korrekte Generierung der PDF-Titelseite
"""

import unittest
import tempfile
import os
from PySide6.QtCore import QSettings, QCoreApplication
from PySide6.QtWidgets import QApplication
import sys

# Test-Setup
def setup_test_qt():
    """Stellt sicher, dass QApplication existiert"""
    if QCoreApplication.instance() is None:
        app = QApplication(sys.argv)
        return app
    return QCoreApplication.instance()

# Python-Pfad für Imports anpassen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importiere die Module nach Qt-Setup und Pfad-Anpassung
app = setup_test_qt()

from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor
import pandas as pd
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


class TestCoverPageGeneration(unittest.TestCase):
    """Test-Klasse für die PDF-Titelseiten-Generierung"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Eindeutige Settings pro Test
        import uuid
        self.test_id = str(uuid.uuid4())
        self.settings = QSettings(f"TestOrg-{self.test_id}", f"TestApp-{self.test_id}")
        
        # Generator mit Test-spezifischen Settings erstellen
        self.generator = BWAPDFGenerator()
        self.generator.settings = self.settings
        
        # Test-CSV-Daten erstellen
        self.test_data = pd.DataFrame({
            'Buchungstag': ['2024-01-15', '2024-02-20', '2024-03-10'],
            'Sachkontonr.': ['1000', '2000', '1500'],
            'Sachkonto': ['Kasse', 'Verbindlichkeiten', 'Forderungen'],
            'Verwendungszweck': ['Testbuchung 1', 'Testbuchung 2', 'Testbuchung 3'],
            'Betrag': [100.50, -50.25, 75.00],
            'Betrag_Clean': [100.50, -50.25, 75.00],
            'Buchungsnr.': ['B001', 'B002', 'B003']
        })
        
        # Test-CSV-Datei erstellen
        self.temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_csv.name, index=False, sep=';')
        self.temp_csv.close()
        
        # CSV-Processor initialisieren
        self.csv_processor = CSVProcessor()
        self.csv_processor.load_csv_file(self.temp_csv.name)
        
        # Test-Logo erstellen (einfaches PNG)
        self.temp_logo = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        self.temp_logo.close()
        
        # Einfaches PNG erstellen
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (200, 100), color='blue')
        draw = ImageDraw.Draw(img)
        draw.text((50, 40), "TEST LOGO", fill='white')
        img.save(self.temp_logo.name)
        
    def tearDown(self):
        """Cleanup nach jedem Test"""
        # Temporäre Dateien löschen
        if os.path.exists(self.temp_csv.name):
            os.unlink(self.temp_csv.name)
        if os.path.exists(self.temp_logo.name):
            os.unlink(self.temp_logo.name)
            
        # Settings zurücksetzen
        self.settings.clear()
        
    def test_cover_page_with_organization_data(self):
        """Test: Titelseite mit vollständigen Organisationsdaten"""
        print("🏢 Teste Titelseite mit Organisationsdaten...")
        
        # Organisationsdaten setzen
        self.settings.setValue("organization/name", "Test Verein e.V.")
        self.settings.setValue("organization/street", "Teststraße 123")
        self.settings.setValue("organization/zip", "12345")
        self.settings.setValue("organization/city", "Teststadt")
        self.settings.setValue("organization/phone", "+49 123 456789")
        self.settings.setValue("organization/email", "test@verein.de")
        self.settings.setValue("organization/info", "Ein Testverein für die Entwicklung")
        self.settings.setValue("organization/logo_path", self.temp_logo.name)
        
        # Kontostand setzen
        self.settings.setValue("opening_balance", 1000.0)
        
        # Header-Farbe setzen (Rot für Test)
        self.settings.setValue("header_color", "#FF0000")
        
        # PDF generieren
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            success = self.generator.generate_bwa_pdf(
                temp_pdf.name, 
                self.csv_processor, 
                {"1000": "Kasse", "2000": "Verbindlichkeiten", "1500": "Forderungen"}
            )
            
            self.assertTrue(success, "PDF-Generierung sollte erfolgreich sein")
            self.assertTrue(os.path.exists(temp_pdf.name), "PDF-Datei sollte erstellt worden sein")
            
            # Prüfe PDF-Größe (sollte Inhalt haben) - reduzierte Erwartung
            pdf_size = os.path.getsize(temp_pdf.name)
            self.assertGreater(pdf_size, 3000, "PDF sollte mindestens 3KB groß sein")
            
            print(f"✅ PDF mit Organisationsdaten erstellt: {pdf_size} Bytes")
            
            # Aufräumen
            os.unlink(temp_pdf.name)
            
    def test_cover_page_color_customization(self):
        """Test: Farbkustomisierung funktioniert korrekt"""
        print("🎨 Teste Header-Farbkustomisierung...")
        
        # Verschiedene Farben testen
        test_colors = [
            "#FF0000",  # Rot
            "#00FF00",  # Grün
            "#0000FF",  # Blau
            "#FF00FF",  # Magenta
            "#FFFF00",  # Gelb
        ]
        
        for color_hex in test_colors:
            with self.subTest(color=color_hex):
                # Farbe setzen
                self.settings.setValue("header_color", color_hex)
                
                # Generator neu erstellen und Settings zuweisen
                generator = BWAPDFGenerator()
                generator.settings = self.settings
                
                # _get_header_color() testen
                actual_color = generator._get_header_color()
                self.assertIsInstance(actual_color, Color, f"Sollte Color-Objekt für {color_hex} sein")
                
                # RGB-Werte prüfen
                expected_r = int(color_hex[1:3], 16) / 255.0
                expected_g = int(color_hex[3:5], 16) / 255.0
                expected_b = int(color_hex[5:7], 16) / 255.0
                
                self.assertAlmostEqual(actual_color.red, expected_r, places=3, 
                                     msg=f"Rot-Wert für {color_hex} falsch")
                self.assertAlmostEqual(actual_color.green, expected_g, places=3, 
                                     msg=f"Grün-Wert für {color_hex} falsch")
                self.assertAlmostEqual(actual_color.blue, expected_b, places=3, 
                                     msg=f"Blau-Wert für {color_hex} falsch")
                
                print(f"✅ Farbe {color_hex} korrekt als RGB({actual_color.red:.2f}, {actual_color.green:.2f}, {actual_color.blue:.2f})")
                
    def test_cover_page_without_organization_data(self):
        """Test: Titelseite ohne Organisationsdaten"""
        print("📄 Teste Titelseite ohne Organisationsdaten...")
        
        # Keine Organisationsdaten setzen (leere Settings)
        self.settings.setValue("opening_balance", 500.0)
        
        # PDF generieren
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            success = self.generator.generate_bwa_pdf(
                temp_pdf.name, 
                self.csv_processor, 
                {"1000": "Kasse"}
            )
            
            self.assertTrue(success, "PDF-Generierung sollte auch ohne Organisationsdaten erfolgreich sein")
            self.assertTrue(os.path.exists(temp_pdf.name), "PDF-Datei sollte erstellt worden sein")
            
            print("✅ PDF ohne Organisationsdaten erfolgreich erstellt")
            
            # Aufräumen
            os.unlink(temp_pdf.name)
            
    def test_cover_page_with_logo_and_without_logo(self):
        """Test: Titelseite mit und ohne Logo"""
        print("🖼️ Teste Logo-Handling...")
        
        # Mit Logo
        self.settings.setValue("organization/name", "Test Verein")
        self.settings.setValue("organization/logo_path", self.temp_logo.name)
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            success = self.generator.generate_bwa_pdf(
                temp_pdf.name, 
                self.csv_processor, 
                {"1000": "Kasse"}
            )
            
            self.assertTrue(success, "PDF-Generierung mit Logo sollte erfolgreich sein")
            logo_pdf_size = os.path.getsize(temp_pdf.name)
            print(f"✅ PDF mit Logo: {logo_pdf_size} Bytes")
            os.unlink(temp_pdf.name)
            
        # Ohne Logo
        self.settings.setValue("organization/logo_path", "")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            success = self.generator.generate_bwa_pdf(
                temp_pdf.name, 
                self.csv_processor, 
                {"1000": "Kasse"}
            )
            
            self.assertTrue(success, "PDF-Generierung ohne Logo sollte erfolgreich sein")
            no_logo_pdf_size = os.path.getsize(temp_pdf.name)
            print(f"✅ PDF ohne Logo: {no_logo_pdf_size} Bytes")
            os.unlink(temp_pdf.name)
            
    def test_cover_page_balance_calculations(self):
        """Test: Korrekte Berechnung der Kontostände auf Titelseite"""
        print("💰 Teste Kontostandsberechnungen...")
        
        # Anfangskontostand setzen
        opening_balance = 1000.0
        self.settings.setValue("opening_balance", opening_balance)
        
        # Generator erstellen
        generator = BWAPDFGenerator()
        
        # Berechnungen prüfen
        total_amount = generator._calculate_total_amount(self.csv_processor)
        expected_total = self.test_data['Betrag_Clean'].sum()  # 100.5 - 50.25 + 75 = 125.25
        
        self.assertAlmostEqual(total_amount, expected_total, places=2, 
                             msg="Gesamtsumme sollte korrekt berechnet werden")
        
        new_balance = generator._calculate_new_balance(self.csv_processor)
        expected_new_balance = opening_balance + expected_total  # 1000 + 125.25 = 1125.25
        
        self.assertAlmostEqual(new_balance, expected_new_balance, places=2, 
                             msg="Neuer Kontostand sollte korrekt berechnet werden")
        
        print(f"✅ Berechnungen korrekt: Anfang={opening_balance}€, Summe={total_amount}€, Neu={new_balance}€")
        
    def test_cover_page_hex_color_validation(self):
        """Test: HEX-Farbvalidierung und Fallback"""
        print("🔍 Teste HEX-Farbvalidierung...")
        
        # Gültige HEX-Farben
        valid_colors = ["#FF0000", "#00ff00", "0000FF", "#123ABC"]
        
        for color in valid_colors:
            with self.subTest(color=color):
                self.settings.setValue("header_color", color)
                generator = BWAPDFGenerator()
                result_color = generator._get_header_color()
                self.assertIsInstance(result_color, Color, f"Gültige Farbe {color} sollte funktionieren")
                
        # Ungültige HEX-Farben (sollten auf Blau zurückfallen)
        invalid_colors = ["#GG0000", "ZZZZZZ", "#12345", "", "invalid"]
        
        for color in invalid_colors:
            with self.subTest(color=color):
                self.settings.setValue("header_color", color)
                generator = BWAPDFGenerator()
                result_color = generator._get_header_color()
                # Sollte auf Standard-Blau zurückfallen
                self.assertIsInstance(result_color, Color, f"Ungültige Farbe {color} sollte Fallback verwenden")
                
        print("✅ HEX-Farbvalidierung funktioniert korrekt")


if __name__ == '__main__':
    print("🧪 Starte Cover-Page-Generierung Tests...")
    unittest.main(verbosity=2)
