# -*- coding: utf-8 -*-
"""
Test für PDF-Generierung mit angepasster Überschriftenfarbe
Fokussiert auf Farbvalidierung in generierten PDFs
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
from reportlab.lib.colors import Color


class TestPDFColorApplication(unittest.TestCase):
    """Test-Klasse für PDF-Farbenanwendung"""
    
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
        self.settings = QSettings(f"PDFColorTest-{self.test_id}", f"TestApp-{self.test_id}")
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

    def test_pdf_with_red_headers(self):
        """Teste PDF-Generierung mit roten Überschriften"""
        print("🔴 Teste PDF mit roten Überschriften...")
        
        # Rote Überschriftenfarbe setzen
        self.settings.setValue("header_color", "#FF0000")
        self.settings.setValue("organization/name", "Rot-Test Verein e.V.")
        self.settings.setValue("opening_balance", 1000.0)
        
        # Test-CSV erstellen
        test_csv_content = """Buchungstag;Sachkontonr.;Sachkonto;Verwendungszweck;Betrag;Betrag_Clean;Buchungsnr.
2025-01-15;4000;Mitgliedsbeiträge;Test-Beitrag;500.00;500.00;R001
2025-02-10;4100;Spenden;Test-Spende;300.00;300.00;R002"""
        
        # Temporäre CSV-Datei
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_csv:
            temp_csv.write(test_csv_content)
            temp_csv_path = temp_csv.name
        
        self.generated_files.append(temp_csv_path)
        
        try:
            # CSV verarbeiten
            csv_processor = CSVProcessor()
            success = csv_processor.load_csv_file(temp_csv_path)
            self.assertTrue(success, "CSV sollte erfolgreich geladen werden")
            
            # BWA-Generator testen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Farbvalidierung
            header_color = generator._get_header_color()
            self.assertIsInstance(header_color, Color, "Header-Farbe sollte Color-Objekt sein")
            self.assertAlmostEqual(header_color.red, 1.0, places=2, msg="Rot-Wert sollte 1.0 sein")
            self.assertAlmostEqual(header_color.green, 0.0, places=2, msg="Grün-Wert sollte 0.0 sein")
            self.assertAlmostEqual(header_color.blue, 0.0, places=2, msg="Blau-Wert sollte 0.0 sein")
            
            print(f"✅ Überschriftenfarbe geladen: RGB({header_color.red:.2f}, {header_color.green:.2f}, {header_color.blue:.2f})")
            
            # PDF-Pfad
            pdf_path = os.path.join(os.path.dirname(__file__), "test_red_headers.pdf")
            self.generated_files.append(pdf_path)
            
            # PDF generieren
            account_mappings = {
                "4000": "Mitgliedsbeiträge und Aufnahmegebühren",
                "4100": "Spenden und Zuschüsse"
            }
            
            pdf_success = generator.generate_bwa_pdf(pdf_path, csv_processor, account_mappings)
            self.assertTrue(pdf_success, "PDF mit roten Überschriften sollte erfolgreich erstellt werden")
            self.assertTrue(os.path.exists(pdf_path), "PDF-Datei sollte existieren")
            
            # PDF-Größe prüfen
            pdf_size = os.path.getsize(pdf_path)
            self.assertGreater(pdf_size, 2500, "PDF sollte mindestens 2.5KB groß sein")
            
            print(f"✅ PDF mit roten Überschriften erstellt: {pdf_size} Bytes")
            
        except Exception as e:
            self.fail(f"Unerwarteter Fehler bei rotem PDF: {e}")

    def test_pdf_with_blue_headers(self):
        """Teste PDF-Generierung mit blauen Überschriften (Standard)"""
        print("🔵 Teste PDF mit blauen Standard-Überschriften...")
        
        # Keine header_color setzen -> sollte Standard-Blau verwenden
        self.settings.setValue("organization/name", "Blau-Test Verein e.V.")
        self.settings.setValue("opening_balance", 2000.0)
        
        # Test-CSV erstellen
        test_csv_content = """Buchungstag;Sachkontonr.;Sachkonto;Verwendungszweck;Betrag;Betrag_Clean;Buchungsnr.
2025-03-01;1000;Kasse;Eingang;750.00;750.00;B001"""
        
        # Temporäre CSV-Datei
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_csv:
            temp_csv.write(test_csv_content)
            temp_csv_path = temp_csv.name
        
        self.generated_files.append(temp_csv_path)
        
        try:
            # CSV verarbeiten
            csv_processor = CSVProcessor()
            success = csv_processor.load_csv_file(temp_csv_path)
            self.assertTrue(success, "CSV sollte erfolgreich geladen werden")
            
            # BWA-Generator
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Standard-Farbe sollte Blau sein
            header_color = generator._get_header_color()
            self.assertIsInstance(header_color, Color, "Header-Farbe sollte Color-Objekt sein")
            self.assertAlmostEqual(header_color.blue, 1.0, places=2, msg="Standard-Farbe sollte blau sein")
            
            print(f"✅ Standard-Farbe (Blau) geladen: RGB({header_color.red:.2f}, {header_color.green:.2f}, {header_color.blue:.2f})")
            
            # PDF-Pfad
            pdf_path = os.path.join(os.path.dirname(__file__), "test_blue_headers.pdf")
            self.generated_files.append(pdf_path)
            
            # PDF generieren
            pdf_success = generator.generate_bwa_pdf(
                pdf_path, 
                csv_processor, 
                {"1000": "Barmittel und Kasse"}
            )
            
            self.assertTrue(pdf_success, "PDF mit blauen Überschriften sollte erfolgreich erstellt werden")
            self.assertTrue(os.path.exists(pdf_path), "PDF-Datei sollte existieren")
            
            print(f"✅ PDF mit blauen Standard-Überschriften erstellt")
            
        except Exception as e:
            self.fail(f"Unerwarteter Fehler bei blauem PDF: {e}")

    def test_pdf_with_multiple_colors(self):
        """Teste PDF-Generierung mit verschiedenen Farben nacheinander"""
        print("🌈 Teste PDF mit verschiedenen Farben...")
        
        test_colors = [
            ("#FF0000", "Rot"),
            ("#00FF00", "Grün"), 
            ("#0000FF", "Blau"),
            ("#FFFF00", "Gelb"),
            ("#FF00FF", "Magenta")
        ]
        
        # Test-CSV erstellen
        test_csv_content = """Buchungstag;Sachkontonr.;Sachkonto;Verwendungszweck;Betrag;Betrag_Clean;Buchungsnr.
2025-05-01;1000;Kasse;Farbtest;100.00;100.00;C001"""
        
        for i, (hex_color, color_name) in enumerate(test_colors):
            with self.subTest(color=hex_color, name=color_name):
                # Farbe setzen
                self.settings.setValue("header_color", hex_color)
                self.settings.setValue("organization/name", f"{color_name}-Test Verein")
                
                # Temporäre CSV-Datei
                with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_csv:
                    temp_csv.write(test_csv_content)
                    temp_csv_path = temp_csv.name
                
                self.generated_files.append(temp_csv_path)
                
                try:
                    # CSV verarbeiten
                    csv_processor = CSVProcessor()
                    success = csv_processor.load_csv_file(temp_csv_path)
                    self.assertTrue(success, f"CSV für {color_name} sollte geladen werden")
                    
                    # BWA-Generator
                    generator = BWAPDFGenerator()
                    generator.settings = self.settings
                    
                    # Farbvalidierung
                    header_color = generator._get_header_color()
                    self.assertIsInstance(header_color, Color, f"Farbe für {color_name} sollte Color-Objekt sein")
                    
                    # PDF-Pfad
                    pdf_path = os.path.join(os.path.dirname(__file__), f"test_{color_name.lower()}_color.pdf")
                    self.generated_files.append(pdf_path)
                    
                    # PDF generieren
                    pdf_success = generator.generate_bwa_pdf(
                        pdf_path, 
                        csv_processor, 
                        {"1000": "Kasse"}
                    )
                    
                    self.assertTrue(pdf_success, f"PDF für {color_name} sollte erfolgreich erstellt werden")
                    self.assertTrue(os.path.exists(pdf_path), f"PDF-Datei für {color_name} sollte existieren")
                    
                    print(f"✅ {color_name}-PDF erfolgreich erstellt")
                    
                except Exception as e:
                    self.fail(f"Fehler bei {color_name}-PDF: {e}")


if __name__ == '__main__':
    print("🧪 Starte PDF-Farbanwendungs-Tests...")
    unittest.main(verbosity=2)
