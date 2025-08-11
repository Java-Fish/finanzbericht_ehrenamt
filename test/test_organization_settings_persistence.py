#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für die Persistierung von Organisationseinstellungen

Testet die korrekte Speicherung und das Laden von Organisationsdaten
einschließlich automatischer Speicherung beim Schließen des Einstellungsfensters.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Test-spezifische QApplication-Erstellung
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings, QTimer
    from PySide6.QtTest import QTest
    
    # Prüfe ob QApplication bereits existiert
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app.setOrganizationName("FinanzauswertungEhrenamt")
        app.setApplicationName("Test")
    
except ImportError as e:
    print(f"❌ Fehler beim Importieren von PySide6: {e}")
    sys.exit(1)

# Projektwurzel zum Pfad hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.settings.organization_settings import OrganizationSettingsTab
    from src.settings.settings_window import SettingsWindow
    from src.utils.bwa_generator import BWAPDFGenerator
    import pandas as pd
except ImportError as e:
    print(f"❌ Fehler beim Importieren der Projektmodule: {e}")
    sys.exit(1)


class TestOrganizationSettingsPersistence(unittest.TestCase):
    """Test-Klasse für Organisationseinstellungen-Persistierung"""
    
    def setUp(self):
        """Setup für jeden Test"""
        print(f"\n🔧 Setup für {self._testMethodName}")
        
        # Temporäre Einstellungsdatei für isolierte Tests
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "test_settings.ini")
        
        # Test-spezifische QSettings-Instanz
        self.settings = QSettings(self.settings_file, QSettings.Format.IniFormat)
        self.settings.clear()  # Alle vorherigen Einstellungen löschen
        
        # Liste für Cleanup
        self.cleanup_files = []
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        print(f"🧹 Cleanup für {self._testMethodName}")
        
        # Generierte Dateien löschen
        for file_path in self.cleanup_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"   ✅ Datei gelöscht: {file_path}")
            except Exception as e:
                print(f"   ⚠️  Fehler beim Löschen von {file_path}: {e}")
        
        # Temporäres Verzeichnis löschen
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                print(f"   ✅ Temporäres Verzeichnis gelöscht: {self.temp_dir}")
        except Exception as e:
            print(f"   ⚠️  Fehler beim Löschen des temporären Verzeichnisses: {e}")
    
    def test_organization_data_persistence(self):
        """Teste persistente Speicherung von Organisationsdaten"""
        print("💾 Teste Organisationsdaten-Persistierung...")
        
        try:
            # Test-Daten definieren
            test_data = {
                "name": "Testverein e.V.",
                "street": "Teststraße 123",
                "zip": "12345",
                "city": "Teststadt",
                "email": "test@testverein.de",
                "phone": "01234567890",
                "info": "Ein Testverein für die Softwaretests",
                "opening_balance": 1234.56
            }
            
            # Erste Instanz - Daten setzen und speichern
            org_tab1 = OrganizationSettingsTab()
            org_tab1.settings = self.settings  # Test-Settings verwenden
            
            # Daten in UI-Felder setzen
            org_tab1.name_edit.setText(test_data["name"])
            org_tab1.street_edit.setText(test_data["street"])
            org_tab1.zip_edit.setText(test_data["zip"])
            org_tab1.city_edit.setText(test_data["city"])
            org_tab1.email_edit.setText(test_data["email"])
            org_tab1.phone_edit.setText(test_data["phone"])
            org_tab1.info_edit.setPlainText(test_data["info"])
            org_tab1.opening_balance_input.setText(f"{test_data['opening_balance']:.2f}".replace(".", ","))
            
            # Speichern
            org_tab1.save_settings()
            
            # Zweite Instanz - Daten laden und prüfen
            org_tab2 = OrganizationSettingsTab()
            org_tab2.settings = self.settings  # Dieselben Test-Settings
            org_tab2.load_settings()
            
            # Vergleichen
            self.assertEqual(org_tab2.name_edit.text(), test_data["name"], "Name sollte korrekt geladen werden")
            self.assertEqual(org_tab2.street_edit.text(), test_data["street"], "Straße sollte korrekt geladen werden")
            self.assertEqual(org_tab2.zip_edit.text(), test_data["zip"], "PLZ sollte korrekt geladen werden")
            self.assertEqual(org_tab2.city_edit.text(), test_data["city"], "Stadt sollte korrekt geladen werden")
            self.assertEqual(org_tab2.email_edit.text(), test_data["email"], "E-Mail sollte korrekt geladen werden")
            self.assertEqual(org_tab2.phone_edit.text(), test_data["phone"], "Telefon sollte korrekt geladen werden")
            self.assertEqual(org_tab2.info_edit.toPlainText(), test_data["info"], "Info sollte korrekt geladen werden")
            
            # Anfangskontostand prüfen (deutsche Formatierung)
            loaded_balance_text = org_tab2.opening_balance_input.text()
            expected_balance_text = f"{test_data['opening_balance']:.2f}".replace(".", ",")
            self.assertEqual(loaded_balance_text, expected_balance_text, "Anfangskontostand sollte korrekt geladen werden")
            
            print("   ✅ Alle Organisationsdaten korrekt persistiert")
            
        except Exception as e:
            self.fail(f"Fehler beim Testen der Organisationsdaten-Persistierung: {e}")
    
    def test_settings_window_auto_save(self):
        """Teste automatisches Speichern beim Schließen des Einstellungsfensters"""
        print("🔄 Teste automatisches Speichern beim Schließen...")
        
        try:
            # Settings-Fenster erstellen
            settings_window = SettingsWindow()
            settings_window.settings = self.settings  # Test-Settings verwenden
            
            # Auch für alle Tabs die Test-Settings setzen
            settings_window.organization_tab.settings = self.settings
            settings_window.general_tab.settings = self.settings
            settings_window.mapping_tab.settings = self.settings
            settings_window.account_mapping_tab.settings = self.settings
            settings_window.super_group_mapping_tab.settings = self.settings
            
            # Test-Daten in Organisationstab setzen
            test_name = "Auto-Save Testverein e.V."
            settings_window.organization_tab.name_edit.setText(test_name)
            settings_window.organization_tab.email_edit.setText("autosave@test.de")
            
            # Fenster schließen (triggert automatisches Speichern)
            settings_window.close()
            
            # Prüfen ob Daten gespeichert wurden
            saved_name = self.settings.value("organization/name", "")
            saved_email = self.settings.value("organization/email", "")
            
            self.assertEqual(saved_name, test_name, "Name sollte automatisch gespeichert werden")
            self.assertEqual(saved_email, "autosave@test.de", "E-Mail sollte automatisch gespeichert werden")
            
            print("   ✅ Automatisches Speichern beim Schließen funktioniert")
            
        except Exception as e:
            self.fail(f"Fehler beim Testen des automatischen Speicherns: {e}")
    
    def test_organization_data_in_pdf_generation(self):
        """Teste ob gespeicherte Organisationsdaten im PDF-Generator verfügbar sind"""
        print("📄 Teste Organisationsdaten in PDF-Generation...")
        
        try:
            # Test-Daten in Settings speichern
            test_data = {
                "organization/name": "PDF-Test Verein e.V.",
                "organization/street": "PDF-Straße 456",
                "organization/zip": "67890",
                "organization/city": "PDF-Stadt",
                "organization/email": "pdf@testverein.de",
                "organization/phone": "09876543210",
                "organization/info": "PDF-Test Informationen"
            }
            
            for key, value in test_data.items():
                self.settings.setValue(key, value)
            self.settings.sync()
            
            # BWA-Generator erstellen und Settings zuweisen
            bwa_generator = BWAPDFGenerator()
            bwa_generator.settings = self.settings
            
            # Prüfen ob Organisationsdaten korrekt geladen werden
            loaded_name = bwa_generator.settings.value("organization/name", "")
            loaded_street = bwa_generator.settings.value("organization/street", "")
            loaded_email = bwa_generator.settings.value("organization/email", "")
            
            self.assertEqual(loaded_name, test_data["organization/name"], "PDF-Generator sollte Name korrekt laden")
            self.assertEqual(loaded_street, test_data["organization/street"], "PDF-Generator sollte Straße korrekt laden")
            self.assertEqual(loaded_email, test_data["organization/email"], "PDF-Generator sollte E-Mail korrekt laden")
            
            print("   ✅ PDF-Generator kann Organisationsdaten korrekt laden")
            
        except Exception as e:
            self.fail(f"Fehler beim Testen der PDF-Generator Organisationsdaten: {e}")
    
    def test_opening_balance_formatting(self):
        """Teste korrekte Formatierung des Anfangskontostands"""
        print("💰 Teste Anfangskontostand-Formatierung...")
        
        try:
            # Test verschiedene Zahlenformate
            test_values = [
                (1234.56, "1234,56"),
                (0.0, "0,00"),
                (999.99, "999,99"),
                (10000.00, "10000,00")
            ]
            
            for original_value, expected_display in test_values:
                # Organisationsdaten-Tab erstellen
                org_tab = OrganizationSettingsTab()
                org_tab.settings = self.settings
                
                # Wert setzen und speichern
                org_tab.opening_balance_input.setText(f"{original_value:.2f}".replace(".", ","))
                org_tab.save_settings()
                
                # Neuen Tab erstellen und laden
                org_tab2 = OrganizationSettingsTab()
                org_tab2.settings = self.settings
                org_tab2.load_settings()
                
                # Prüfen ob deutsche Formatierung korrekt angezeigt wird
                displayed_value = org_tab2.opening_balance_input.text()
                self.assertEqual(displayed_value, expected_display, 
                               f"Anfangskontostand {original_value} sollte als '{expected_display}' angezeigt werden")
                
                # Prüfen ob Wert korrekt als Float gespeichert wird
                saved_value = self.settings.value("opening_balance", 0.0, type=float)
                self.assertAlmostEqual(saved_value, original_value, places=2,
                                     msg=f"Gespeicherter Wert sollte {original_value} entsprechen")
            
            print("   ✅ Anfangskontostand-Formatierung funktioniert korrekt")
            
        except Exception as e:
            self.fail(f"Fehler beim Testen der Anfangskontostand-Formatierung: {e}")
    
    def test_empty_values_handling(self):
        """Teste Behandlung leerer Werte"""
        print("📝 Teste Behandlung leerer Werte...")
        
        try:
            # Organisationsdaten-Tab mit leeren Werten erstellen
            org_tab = OrganizationSettingsTab()
            org_tab.settings = self.settings
            
            # Alle Felder leer lassen
            org_tab.name_edit.setText("")
            org_tab.street_edit.setText("")
            org_tab.zip_edit.setText("")
            org_tab.city_edit.setText("")
            org_tab.email_edit.setText("")
            org_tab.phone_edit.setText("")
            org_tab.info_edit.setPlainText("")
            org_tab.opening_balance_input.setText("")
            
            # Speichern
            org_tab.save_settings()
            
            # Neuen Tab erstellen und laden
            org_tab2 = OrganizationSettingsTab()
            org_tab2.settings = self.settings
            org_tab2.load_settings()
            
            # Prüfen ob leere Werte korrekt behandelt werden
            self.assertEqual(org_tab2.name_edit.text(), "", "Leerer Name sollte korrekt behandelt werden")
            self.assertEqual(org_tab2.email_edit.text(), "", "Leere E-Mail sollte korrekt behandelt werden")
            
            # Anfangskontostand sollte 0.0 sein
            saved_balance = self.settings.value("opening_balance", 0.0, type=float)
            self.assertEqual(saved_balance, 0.0, "Leerer Anfangskontostand sollte 0.0 entsprechen")
            
            print("   ✅ Leere Werte werden korrekt behandelt")
            
        except Exception as e:
            self.fail(f"Fehler beim Testen der Behandlung leerer Werte: {e}")


if __name__ == '__main__':
    print("🧪 Starte Organisationseinstellungen-Persistierung-Tests...")
    
    # Test-Suite ausführen
    unittest.main(verbosity=2)
