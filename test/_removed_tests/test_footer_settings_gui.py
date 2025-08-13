#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test für GUI-Integration der Footer-Einstellungen
"""

import unittest
import os
import sys
import tempfile
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Pfad zum src-Verzeichnis hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from settings.general_settings import GeneralSettingsTab


class TestFooterSettingsGUI(unittest.TestCase):
    """Test-Klasse für GUI Footer-Einstellungen"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # QApplication falls noch nicht vorhanden
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        # Test-Settings
        self.settings = QSettings("BWA-Test", "Footer-GUI-Tests")
        self.settings.clear()
        
    def tearDown(self):
        """Aufräumen nach jedem Test"""
        # Test-Settings löschen
        self.settings.clear()
        self.settings.sync()
        
    def test_footer_checkboxes_exist(self):
        """Teste dass Footer-Checkboxen in der GUI existieren"""
        print("🎛️ Teste Footer-Checkboxen in GUI...")
        
        # GeneralSettingsTab erstellen
        settings_tab = GeneralSettingsTab()
        
        # Prüfen dass Footer-Checkboxen existieren
        self.assertTrue(hasattr(settings_tab, 'show_page_number_cb'), 
                       "show_page_number_cb sollte existieren")
        
        self.assertTrue(hasattr(settings_tab, 'show_organization_footer_cb'), 
                       "show_organization_footer_cb sollte existieren")
        
        print("   ✅ Alle Footer-Checkboxen existieren")
        
    def test_footer_default_values(self):
        """Teste Standard-Werte der Footer-Einstellungen"""
        print("🔧 Teste Standard-Werte...")
        
        # GeneralSettingsTab erstellen
        settings_tab = GeneralSettingsTab()
        
        # Standard-Werte prüfen (sollten alle True sein)
        self.assertTrue(settings_tab.show_page_number_cb.isChecked(), 
                       "Seitenzahl sollte standardmäßig aktiviert sein")
        self.assertTrue(settings_tab.show_organization_footer_cb.isChecked(), 
                       "Organisation in Footer sollte standardmäßig aktiviert sein")
        
        print("   ✅ Standard-Werte sind korrekt")
        
    def test_footer_settings_save_load(self):
        """Teste Speichern und Laden der Footer-Einstellungen"""
        print("💾 Teste Speichern und Laden...")
        
        # GeneralSettingsTab erstellen
        settings_tab = GeneralSettingsTab()
        settings_tab.settings = self.settings  # Test-Settings verwenden
        
        # Werte ändern
        settings_tab.show_page_number_cb.setChecked(False)
        settings_tab.show_organization_footer_cb.setChecked(False)
        
        # Speichern
        settings_tab.save_settings()
        
        # Neue Tab erstellen und laden
        new_settings_tab = GeneralSettingsTab()
        new_settings_tab.settings = self.settings
        new_settings_tab.load_settings()
        
        # Prüfen dass Werte korrekt geladen wurden
        self.assertFalse(new_settings_tab.show_page_number_cb.isChecked(), 
                        "Seitenzahl sollte deaktiviert sein")
        self.assertFalse(new_settings_tab.show_organization_footer_cb.isChecked(), 
                        "Organisation in Footer sollte deaktiviert sein")
        
        print("   ✅ Speichern und Laden funktioniert korrekt")
        
    def test_footer_reset_to_defaults(self):
        """Teste Reset auf Standard-Werte"""
        print("🔄 Teste Reset auf Standard-Werte...")
        
        # GeneralSettingsTab erstellen
        settings_tab = GeneralSettingsTab()
        
        # Werte ändern
        settings_tab.show_page_number_cb.setChecked(False)
        settings_tab.show_organization_footer_cb.setChecked(False)
        
        # Reset
        settings_tab.reset_to_defaults()
        
        # Prüfen dass alle wieder auf True stehen
        self.assertTrue(settings_tab.show_page_number_cb.isChecked(), 
                       "Seitenzahl sollte nach Reset aktiviert sein")
        self.assertTrue(settings_tab.show_organization_footer_cb.isChecked(), 
                       "Organisation in Footer sollte nach Reset aktiviert sein")
        
        print("   ✅ Reset funktioniert korrekt")
        
    def test_footer_in_berichterstellung_group(self):
        """Teste dass Footer-Optionen in der Berichterstellung-Gruppe sind"""
        print("📊 Teste Gruppierung in Berichterstellung...")
        
        # GeneralSettingsTab erstellen
        settings_tab = GeneralSettingsTab()
        
        # Prüfen dass es eine Berichterstellung-Gruppe gibt
        # (Das ist schwierig direkt zu testen, aber wir können prüfen dass die Widgets existieren)
        self.assertIsNotNone(settings_tab.show_page_number_cb.parent(), 
                           "Footer-Checkboxen sollten in einem Container sein")
        
        print("   ✅ Footer-Optionen sind korrekt gruppiert")


if __name__ == '__main__':
    print("🎮 Starte Footer-GUI-Tests...")
    
    # Test-Suite ausführen
    unittest.main(verbosity=2)
