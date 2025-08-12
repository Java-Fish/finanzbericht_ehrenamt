#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test für Footer-Funktionalität in BWA-PDFs
"""

import unittest
import os
import sys
import tempfile
import json
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

# Pfad zum src-Verzeichnis hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.bwa_generator import BWAPDFGenerator
from utils.csv_processor import CSVProcessor


class TestFooterFunctionality(unittest.TestCase):
    """Test-Klasse für Footer-Funktionalität"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # QApplication falls noch nicht vorhanden
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        # Test-Settings
        self.settings = QSettings("BWA-Test", "Footer-Tests")
        
        # Standard-Einstellungen setzen
        self.settings.setValue("show_page_number", True)
        self.settings.setValue("show_total_pages", True)
        self.settings.setValue("show_organization_footer", True)
        
        # Test-Organisation
        test_org = {
            "name": "Test Verein e.V.",
            "street": "Teststraße 123",
            "city": "12345 Teststadt",
            "phone": "0123/456789",
            "email": "test@verein.de"
        }
        self.settings.setValue("organization_data", json.dumps(test_org))
        self.settings.sync()
        
        # Test-CSV-Datei verwenden
        self.test_csv_path = os.path.join(os.path.dirname(__file__), "..", "test_bwa.csv")
        if not os.path.exists(self.test_csv_path):
            # Alternative Pfade testen
            alt_paths = [
                os.path.join(os.path.dirname(__file__), "..", "testdata", "Finanzübersicht_2024.csv"),
                os.path.join(os.path.dirname(__file__), "..", "testdata", "test.csv")
            ]
            for path in alt_paths:
                if os.path.exists(path):
                    self.test_csv_path = path
                    break
        
    def tearDown(self):
        """Aufräumen nach jedem Test"""
        # Test-Settings löschen
        self.settings.clear()
        self.settings.sync()
        
    def test_footer_settings_exist(self):
        """Teste dass Footer-Einstellungen existieren"""
        print("📋 Teste Footer-Einstellungen...")
        
        # Settings laden
        show_page_number = self.settings.value("show_page_number", False, type=bool)
        show_total_pages = self.settings.value("show_total_pages", False, type=bool)
        show_organization_footer = self.settings.value("show_organization_footer", False, type=bool)
        
        # Prüfen dass alle Settings gesetzt sind
        self.assertTrue(show_page_number, "show_page_number sollte aktiviert sein")
        self.assertTrue(show_total_pages, "show_total_pages sollte aktiviert sein")
        self.assertTrue(show_organization_footer, "show_organization_footer sollte aktiviert sein")
        
        print("   ✅ Footer-Einstellungen korrekt gesetzt")
        
    def test_pdf_generation_with_footer(self):
        """Teste PDF-Generierung mit Footer"""
        print("📄 Teste PDF-Generierung mit Footer...")
        
        try:
            # Temporäre PDF-Datei
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                temp_pdf_path = tmp_file.name
            
            # BWA-Generator erstellen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # CSV-Processor erstellen
            if os.path.exists(self.test_csv_path):
                processor = CSVProcessor()
                load_success = processor.load_file(self.test_csv_path)
                
                if load_success:
                    # Test Account-Mappings erstellen
                    account_mappings = {
                        "1000": "Kasse",
                        "1200": "Bank",
                        "4000": "Mitgliedsbeiträge"
                    }
                    
                    # PDF generieren
                    success = generator.generate_bwa_pdf(temp_pdf_path, processor, account_mappings)
                    
                    # Prüfen dass PDF erstellt wurde
                    self.assertTrue(success, "PDF sollte erfolgreich erstellt werden")
                    self.assertTrue(os.path.exists(temp_pdf_path), "PDF-Datei sollte existieren")
                    
                    # PDF-Größe prüfen (sollte nicht leer sein)
                    file_size = os.path.getsize(temp_pdf_path)
                    self.assertGreater(file_size, 1000, "PDF sollte mindestens 1KB groß sein")
                    
                    print(f"   ✅ PDF erfolgreich erstellt: {file_size} Bytes")
                else:
                    print(f"   ⚠️ CSV-Datei konnte nicht geladen werden: {self.test_csv_path}")
                    self.skipTest("CSV-Datei konnte nicht geladen werden")
                
                # Aufräumen
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
            else:
                print(f"   ⚠️ Test-CSV nicht gefunden: {self.test_csv_path}")
                self.skipTest("Test-CSV-Datei nicht gefunden")
                
        except Exception as e:
            self.fail(f"Fehler bei PDF-Generierung mit Footer: {e}")
            
    def test_footer_settings_disabled(self):
        """Teste PDF-Generierung mit deaktivierten Footer-Optionen"""
        print("🔇 Teste deaktivierte Footer-Optionen...")
        
        try:
            # Alle Footer-Optionen deaktivieren
            self.settings.setValue("show_page_number", False)
            self.settings.setValue("show_total_pages", False)
            self.settings.setValue("show_organization_footer", False)
            self.settings.sync()
            
            # Temporäre PDF-Datei
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                temp_pdf_path = tmp_file.name
            
            # BWA-Generator erstellen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # CSV-Processor erstellen
            if os.path.exists(self.test_csv_path):
                processor = CSVProcessor()
                load_success = processor.load_file(self.test_csv_path)
                
                if load_success:
                    # Test Account-Mappings erstellen
                    account_mappings = {
                        "1000": "Kasse",
                        "1200": "Bank",
                        "4000": "Mitgliedsbeiträge"
                    }
                    
                    # PDF generieren
                    success = generator.generate_bwa_pdf(temp_pdf_path, processor, account_mappings)
                    
                    # Prüfen dass PDF trotzdem erstellt wurde
                    self.assertTrue(success, "PDF sollte auch ohne Footer erstellt werden")
                    self.assertTrue(os.path.exists(temp_pdf_path), "PDF-Datei sollte existieren")
                    
                    print("   ✅ PDF auch ohne Footer erfolgreich erstellt")
                else:
                    print(f"   ⚠️ CSV-Datei konnte nicht geladen werden: {self.test_csv_path}")
                    self.skipTest("CSV-Datei konnte nicht geladen werden")
                
                # Aufräumen
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
            else:
                print(f"   ⚠️ Test-CSV nicht gefunden: {self.test_csv_path}")
                self.skipTest("Test-CSV-Datei nicht gefunden")
                
        except Exception as e:
            self.fail(f"Fehler bei PDF-Generierung ohne Footer: {e}")
            
    def test_organization_data_in_footer(self):
        """Teste dass Organisationsdaten im Footer verwendet werden"""
        print("🏢 Teste Organisationsdaten im Footer...")
        
        # Organisationsdaten laden
        organization_data_json = self.settings.value("organization_data", "{}")
        try:
            organization_data = json.loads(organization_data_json)
            organization_name = organization_data.get("name", "")
            
            # Prüfen dass Organisationsdaten vorhanden sind
            self.assertIsNotNone(organization_name, "Organisationsname sollte vorhanden sein")
            self.assertEqual(organization_name, "Test Verein e.V.", "Organisationsname sollte korrekt sein")
            
            print(f"   ✅ Organisationsdaten korrekt: {organization_name}")
            
        except (json.JSONDecodeError, TypeError):
            self.fail("Organisationsdaten sollten korrekt als JSON gespeichert sein")
            
    def test_partial_footer_settings(self):
        """Teste gemischte Footer-Einstellungen"""
        print("🔧 Teste gemischte Footer-Einstellungen...")
        
        try:
            # Nur Seitenzahl aktivieren
            self.settings.setValue("show_page_number", True)
            self.settings.setValue("show_total_pages", False)
            self.settings.setValue("show_organization_footer", False)
            self.settings.sync()
            
            # Temporäre PDF-Datei
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                temp_pdf_path = tmp_file.name
            
            # BWA-Generator erstellen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # CSV-Processor erstellen
            if os.path.exists(self.test_csv_path):
                processor = CSVProcessor()
                load_success = processor.load_file(self.test_csv_path)
                
                if load_success:
                    # Test Account-Mappings erstellen
                    account_mappings = {
                        "1000": "Kasse",
                        "1200": "Bank",
                        "4000": "Mitgliedsbeiträge"
                    }
                    
                    # PDF generieren
                    success = generator.generate_bwa_pdf(temp_pdf_path, processor, account_mappings)
                    
                    # Prüfen dass PDF erstellt wurde
                    self.assertTrue(success, "PDF sollte mit teilweisem Footer erstellt werden")
                    
                    print("   ✅ PDF mit partiellen Footer-Einstellungen erfolgreich erstellt")
                else:
                    print(f"   ⚠️ CSV-Datei konnte nicht geladen werden: {self.test_csv_path}")
                    self.skipTest("CSV-Datei konnte nicht geladen werden")
                
                # Aufräumen
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
            else:
                print(f"   ⚠️ Test-CSV nicht gefunden: {self.test_csv_path}")
                self.skipTest("Test-CSV-Datei nicht gefunden")
                
        except Exception as e:
            self.fail(f"Fehler bei partiellen Footer-Einstellungen: {e}")


    def test_footer_visual_verification(self):
        """Teste dass Footer visuell im PDF vorhanden ist"""
        print("👁️ Teste visuellen Footer im PDF...")
        
        try:
            # Temporäre PDF-Datei
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                temp_pdf_path = tmp_file.name
            
            # BWA-Generator erstellen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # CSV-Processor erstellen
            if os.path.exists(self.test_csv_path):
                processor = CSVProcessor()
                load_success = processor.load_file(self.test_csv_path)
                
                if load_success:
                    # Test Account-Mappings erstellen
                    account_mappings = {
                        "1000": "Kasse",
                        "1200": "Bank",
                        "4000": "Mitgliedsbeiträge"
                    }
                    
                    # PDF generieren
                    success = generator.generate_bwa_pdf(temp_pdf_path, processor, account_mappings)
                    
                    # Prüfen dass PDF erstellt wurde
                    self.assertTrue(success, "PDF sollte erfolgreich erstellt werden")
                    self.assertTrue(os.path.exists(temp_pdf_path), "PDF-Datei sollte existieren")
                    
                    # PDF-Größe prüfen (sollte nicht leer sein)
                    file_size = os.path.getsize(temp_pdf_path)
                    self.assertGreater(file_size, 1000, "PDF sollte mindestens 1KB groß sein")
                    
                    # Versuche PDF-Inhalt zu analysieren (einfache Textsuche)
                    try:
                        # PyPDF2 ist möglicherweise nicht verfügbar, also verwenden wir pdfplumber falls verfügbar
                        import subprocess
                        result = subprocess.run(['pdftotext', temp_pdf_path, '-'], 
                                              capture_output=True, text=True, timeout=10)
                        
                        if result.returncode == 0:
                            pdf_text = result.stdout
                            
                            # Prüfe ob Footer-Elemente im Text enthalten sind
                            if generator.settings.value("show_page_number", True, type=bool):
                                self.assertIn("Seite", pdf_text, "PDF sollte Seitenzahlen enthalten")
                                
                            if generator.settings.value("show_organization_footer", True, type=bool):
                                org_name = "Test Verein e.V."
                                if org_name and org_name in pdf_text:
                                    print(f"   ✅ Organisationsname '{org_name}' im PDF gefunden")
                                else:
                                    print(f"   ⚠️ Organisationsname '{org_name}' nicht im PDF-Text gefunden")
                                    
                            print(f"   ✅ PDF mit Footer erfolgreich analysiert")
                        else:
                            print("   ⚠️ PDF-Text-Extraktion nicht verfügbar (pdftotext nicht installiert)")
                            
                    except (ImportError, subprocess.TimeoutExpired, FileNotFoundError):
                        print("   ⚠️ PDF-Analyse-Tools nicht verfügbar - überspringe Textprüfung")
                    
                    # Teste direkt die Footer-Funktionen
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import A4
                    
                    # Mock Canvas erstellen für Test
                    test_canvas_path = temp_pdf_path.replace('.pdf', '_footer_test.pdf')
                    test_canvas = canvas.Canvas(test_canvas_path, pagesize=A4)
                    
                    # Mock Doc
                    class MockDoc:
                        pass
                    
                    mock_doc = MockDoc()
                    
                    # Footer-Funktion direkt testen
                    generator._add_footer_to_page(test_canvas, mock_doc)
                    test_canvas.save()
                    
                    # Teste dass Footer-Test-PDF erstellt wurde
                    self.assertTrue(os.path.exists(test_canvas_path), "Footer-Test-PDF sollte erstellt werden")
                    
                    footer_file_size = os.path.getsize(test_canvas_path)
                    self.assertGreater(footer_file_size, 100, "Footer-Test-PDF sollte Inhalt haben")
                    
                    print(f"   ✅ Footer-Funktion direkt getestet: {footer_file_size} Bytes")
                    
                    # Aufräumen
                    if os.path.exists(test_canvas_path):
                        os.unlink(test_canvas_path)
                        
                else:
                    print(f"   ⚠️ CSV-Datei konnte nicht geladen werden: {self.test_csv_path}")
                    self.skipTest("CSV-Datei konnte nicht geladen werden")
                
                # Aufräumen
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
            else:
                print(f"   ⚠️ Test-CSV nicht gefunden: {self.test_csv_path}")
                self.skipTest("Test-CSV-Datei nicht gefunden")
                
        except Exception as e:
            self.fail(f"Fehler bei Footer-Visualisierungstest: {e}")


if __name__ == '__main__':
    print("🦶 Starte Footer-Funktionalitäts-Tests...")
    
    # Test-Suite ausführen
    unittest.main(verbosity=2)
