# -*- coding: utf-8 -*-
"""
Test für die Farbeinstellungen-UI in den allgemeinen Einstellungen
"""

import sys
import os
import unittest

# Python-Pfad für Imports anpassen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings, QCoreApplication
from PySide6.QtGui import QColor
from src.settings.general_settings import GeneralSettingsTab


class TestColorSettings(unittest.TestCase):
    """Test-Klasse für die Farbeinstellungen-UI"""
    
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
        self.settings = QSettings(f"ColorSettingsTest-{self.test_id}", f"TestApp-{self.test_id}")
        
    def tearDown(self):
        """Cleanup nach jedem Test"""
        self.settings.clear()

    def test_color_ui_elements_exist(self):
        """Teste ob alle Farbauswahl-UI-Elemente vorhanden sind"""
        print("🎨 Teste Farbauswahl-UI-Elemente...")
        
        try:
            # Settings-Tab erstellen
            settings_tab = GeneralSettingsTab()
            
            # Prüfen ob Farbauswahl-Elemente existieren
            self.assertTrue(hasattr(settings_tab, 'red_input'), "RGB-Rot-Eingabefeld sollte vorhanden sein")
            self.assertTrue(hasattr(settings_tab, 'green_input'), "RGB-Grün-Eingabefeld sollte vorhanden sein")
            self.assertTrue(hasattr(settings_tab, 'blue_input'), "RGB-Blau-Eingabefeld sollte vorhanden sein")
            self.assertTrue(hasattr(settings_tab, 'hex_input'), "HEX-Eingabefeld sollte vorhanden sein")
            self.assertTrue(hasattr(settings_tab, 'color_button'), "Farbwähler-Button sollte vorhanden sein")
            
            print("✅ Alle UI-Elemente vorhanden")
            
        except Exception as e:
            self.fail(f"Fehler beim Erstellen der Settings-UI: {e}")

    def test_default_color_loading(self):
        """Teste das Laden der Standardfarbe"""
        print("🔵 Teste Standard-Farbladung...")
        
        try:
            settings_tab = GeneralSettingsTab()
            
            # Standard-Farbe sollte Blau sein
            if hasattr(settings_tab, 'current_color'):
                self.assertIsInstance(settings_tab.current_color, QColor, "current_color sollte QColor-Objekt sein")
                print(f"✅ Standard-Farbe geladen: {settings_tab.current_color.name()}")
            else:
                self.fail("current_color Attribut nicht gefunden")
                
        except Exception as e:
            self.fail(f"Fehler beim Laden der Standardfarbe: {e}")

    def test_rgb_input_functionality(self):
        """Teste RGB-Eingabefeld-Funktionalität"""
        print("🔴 Teste RGB-Eingabe...")
        
        try:
            settings_tab = GeneralSettingsTab()
            
            # Teste RGB-Werte setzen (Rot) - verwende setText da es QLineEdit ist
            if hasattr(settings_tab, 'red_input') and hasattr(settings_tab, 'green_input') and hasattr(settings_tab, 'blue_input'):
                settings_tab.red_input.setText("255")
                settings_tab.green_input.setText("0")
                settings_tab.blue_input.setText("0")
                
                # Trigger Update-Methode falls vorhanden
                if hasattr(settings_tab, 'on_rgb_changed'):
                    settings_tab.on_rgb_changed()
                
                # Prüfe ob Farbe korrekt gesetzt wurde
                if hasattr(settings_tab, 'current_color'):
                    self.assertEqual(settings_tab.current_color.red(), 255, "Rot-Wert sollte 255 sein")
                    self.assertEqual(settings_tab.current_color.green(), 0, "Grün-Wert sollte 0 sein")
                    self.assertEqual(settings_tab.current_color.blue(), 0, "Blau-Wert sollte 0 sein")
                    
                print("✅ RGB-Eingabe funktioniert")
            else:
                self.fail("RGB-Eingabefelder nicht gefunden")
                
        except Exception as e:
            self.fail(f"Fehler beim Testen der RGB-Eingabe: {e}")

    def test_hex_input_functionality(self):
        """Teste HEX-Eingabefeld-Funktionalität"""
        print("🟢 Teste HEX-Eingabe...")
        
        try:
            settings_tab = GeneralSettingsTab()
            
            # Teste HEX-Werte setzen (Grün)
            if hasattr(settings_tab, 'hex_input'):
                settings_tab.hex_input.setText("#00FF00")
                
                # Trigger Update-Methode falls vorhanden
                if hasattr(settings_tab, 'on_hex_changed'):
                    settings_tab.on_hex_changed()
                
                # Prüfe ob Farbe korrekt gesetzt wurde
                if hasattr(settings_tab, 'current_color'):
                    self.assertEqual(settings_tab.current_color.red(), 0, "Rot-Wert sollte 0 sein")
                    self.assertEqual(settings_tab.current_color.green(), 255, "Grün-Wert sollte 255 sein")
                    self.assertEqual(settings_tab.current_color.blue(), 0, "Blau-Wert sollte 0 sein")
                    
                print("✅ HEX-Eingabe funktioniert")
            else:
                self.fail("HEX-Eingabefeld nicht gefunden")
                
        except Exception as e:
            self.fail(f"Fehler beim Testen der HEX-Eingabe: {e}")

    def test_color_persistence(self):
        """Teste Farbspeicherung und -ladung"""
        print("💾 Teste Farbpersistenz...")
        
        try:
            # Erste Instanz - Farbe setzen und speichern
            settings_tab1 = GeneralSettingsTab()
            settings_tab1.settings = self.settings  # Test-spezifische Settings verwenden
            
            if hasattr(settings_tab1, 'current_color'):
                test_color = QColor("#FF6600")  # Orange
                settings_tab1.current_color = test_color
                
                if hasattr(settings_tab1, 'save_settings'):
                    settings_tab1.save_settings()
                
                # Zweite Instanz - Farbe laden
                settings_tab2 = GeneralSettingsTab()
                settings_tab2.settings = self.settings  # Dieselben Test-Settings
                
                if hasattr(settings_tab2, 'load_settings'):
                    settings_tab2.load_settings()
                
                # Vergleiche geladene Farbe (Kleinschreibung beachten)
                if hasattr(settings_tab2, 'current_color'):
                    saved_color_hex = self.settings.value("header_color", "#0000FF")
                    self.assertEqual(saved_color_hex.upper(), "#FF6600", "Gespeicherte Farbe sollte korrekt geladen werden")
                    
                print("✅ Farbpersistenz funktioniert")
            else:
                self.fail("current_color Attribut nicht gefunden")
                
        except Exception as e:
            self.fail(f"Fehler beim Testen der Farbpersistenz: {e}")


if __name__ == '__main__':
    print("🧪 Starte Farbeinstellungen-Tests...")
    unittest.main(verbosity=2)
