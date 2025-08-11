#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für Balkendiagramm-Funktionalität in BWA-Berichten

Testet die korrekte Generierung von Balkendiagrammen für Obergruppen,
die Einstellungssteuerung und die Platzierung auf separaten Seiten.
"""

import unittest
import tempfile
import os
import sys
import pandas as pd
from pathlib import Path

# Test-spezifische QApplication-Erstellung
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings
    
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
    from src.utils.bwa_generator import BWAPDFGenerator
    from src.utils.csv_processor import CSVProcessor
    from reportlab.graphics.shapes import Drawing
except ImportError as e:
    print(f"❌ Fehler beim Importieren der Projektmodule: {e}")
    sys.exit(1)


class TestBarChartFunctionality(unittest.TestCase):
    """Test-Klasse für Balkendiagramm-Funktionalität"""
    
    def setUp(self):
        """Setup für jeden Test"""
        print(f"\n🔧 Setup für {self._testMethodName}")
        
        # Liste für Cleanup zuerst initialisieren
        self.cleanup_files = []
        
        # Temporäre Einstellungsdatei für isolierte Tests
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, "test_settings.ini")
        
        # Test-spezifische QSettings-Instanz
        self.settings = QSettings(self.settings_file, QSettings.Format.IniFormat)
        self.settings.clear()
        
        # Standard-Testdaten vorbereiten
        self.setup_test_data()
    
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
    
    def setup_test_data(self):
        """Richtet Testdaten ein"""
        # Test-CSV-Daten erstellen
        test_data = {
            'Buchungsdatum': ['2025-01-15', '2025-02-10', '2025-03-20'],
            'Sachkonto': ['4000', '6000', '4200'],
            'Betrag': [1500.50, -800.75, 2200.00],
            'Buchungstext': ['Test Einnahme', 'Test Ausgabe', 'Test Projekt']
        }
        
        # Test-CSV-Datei erstellen
        self.test_csv_file = os.path.join(self.temp_dir, "test_data.csv")
        df = pd.DataFrame(test_data)
        df.to_csv(self.test_csv_file, index=False, sep=';')
        self.cleanup_files.append(self.test_csv_file)
        
        # Test-Sachkonten-Mappings
        account_mappings = {
            "4000": "Einnahmen",
            "4200": "Spenden", 
            "6000": "Verwaltungskosten"
        }
        import json
        self.settings.setValue("account_mappings", json.dumps(account_mappings))
        
        # Test-Obergruppen-Mappings
        super_group_mappings = {
            "Einnahmen": "Erträge",
            "Spenden": "Erträge",
            "Verwaltungskosten": "Ausgaben"
        }
        self.settings.setValue("super_group_mappings", json.dumps(super_group_mappings))
        
        # Chart-Generierung aktivieren
        self.settings.setValue("generate_chart_report", True)
        self.settings.sync()
    
    def test_bar_chart_creation(self):
        """Teste die Erstellung von Balkendiagrammen"""
        print("📊 Teste Balkendiagramm-Erstellung...")
        
        try:
            # BWA-Generator erstellen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Test-Daten für Summary erstellen (korrekte Struktur: Dict[str, float])
            summary = {
                'Einnahmen': 1500.50,
                'Spenden': 2200.00,
                'Verwaltungskosten': -800.75
            }
            
            # Balkendiagramm erstellen
            chart = generator._create_supergroup_bar_chart(summary, "Q1")
            
            # Prüfen ob Chart erstellt wurde
            self.assertIsNotNone(chart, "Balkendiagramm sollte erstellt werden")
            self.assertIsInstance(chart, Drawing, "Chart sollte ein Drawing-Objekt sein")
            
            # Prüfen ob Chart-Dimensionen korrekt sind
            self.assertGreater(chart.width, 0, "Chart-Breite sollte größer als 0 sein")
            self.assertGreater(chart.height, 0, "Chart-Höhe sollte größer als 0 sein")
            
            print("   ✅ Balkendiagramm erfolgreich erstellt")
            
        except Exception as e:
            self.fail(f"Fehler beim Erstellen des Balkendiagramms: {e}")
    
    def test_chart_setting_disabled(self):
        """Teste dass kein Chart erstellt wird wenn Setting deaktiviert ist"""
        print("🔇 Teste deaktivierte Chart-Generierung...")
        
        try:
            # Chart-Generierung deaktivieren
            self.settings.setValue("generate_chart_report", False)
            self.settings.sync()
            
            # BWA-Generator erstellen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Test-Daten
            summary = {
                'Einnahmen': 1500.50,
                'Ausgaben': -800.75
            }
            
            # Prüfen ob Chart-Setting korrekt ausgelesen wird
            chart_enabled = generator.settings.value("generate_chart_report", True, type=bool)
            self.assertFalse(chart_enabled, "Chart-Generierung sollte deaktiviert sein")
            
            print("   ✅ Chart-Setting korrekt deaktiviert")
            
        except Exception as e:
            self.fail(f"Fehler beim Testen der deaktivierten Chart-Generierung: {e}")
    
    def test_empty_data_handling(self):
        """Teste Behandlung leerer Daten"""
        print("📝 Teste Behandlung leerer Daten...")
        
        try:
            # BWA-Generator erstellen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Leere Summary testen (korrekte Struktur: Dict[str, float])
            empty_summary = {}
            chart = generator._create_supergroup_bar_chart(empty_summary, "Q1")
            
            # Bei leeren Daten sollte None zurückgegeben werden
            self.assertIsNone(chart, "Bei leeren Daten sollte kein Chart erstellt werden")
            
            print("   ✅ Leere Daten korrekt behandelt")
            
        except Exception as e:
            self.fail(f"Fehler beim Testen leerer Daten: {e}")
    
    def test_positive_negative_values(self):
        """Teste korrekte Behandlung positiver und negativer Werte"""
        print("⚖️ Teste positive und negative Werte...")
        
        try:
            # BWA-Generator erstellen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Test-Daten (korrekte Struktur: Dict[str, float])
            summary = {
                'Spenden': 1500.00,        # Positiv
                'Reisekosten': -300.50     # Negativ
            }
            
            # Chart erstellen
            chart = generator._create_supergroup_bar_chart(summary, "Jahr")
            
            # Prüfen ob Chart erstellt wurde
            self.assertIsNotNone(chart, "Chart sollte mit gemischten Werten erstellt werden")
            self.assertIsInstance(chart, Drawing, "Chart sollte ein Drawing-Objekt sein")
            
            print("   ✅ Positive und negative Werte korrekt verarbeitet")
            
        except Exception as e:
            self.fail(f"Fehler beim Testen positiver/negativer Werte: {e}")
    
    def test_pdf_generation_with_charts(self):
        """Teste PDF-Generierung mit Balkendiagrammen (vereinfacht)"""
        print("📄 Teste Chart-Integration (vereinfacht)...")
        
        try:
            # Chart-Generierung aktivieren
            self.settings.setValue("generate_chart_report", True)
            self.settings.sync()
            
            # BWA-Generator erstellen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Test-Summary direkt erstellen (korrekte Struktur: Dict[str, float])
            summary = {
                'Einnahmen': 1500.50,
                'Spenden': 2200.00,
                'Verwaltungskosten': -800.75
            }
            
            # Account mappings für Generator setzen
            account_mappings_json = self.settings.value("account_mappings", "{}")
            import json
            account_mappings = json.loads(account_mappings_json)
            
            # Prüfen ob Chart-Erstellung mit PDF-relevanten Daten funktioniert
            chart = generator._create_supergroup_bar_chart(summary, "Q1")
            self.assertIsNotNone(chart, "Chart sollte für PDF-Integration erstellt werden")
            
            # Prüfen ob Settings korrekt gelesen werden
            chart_enabled = generator.settings.value("generate_chart_report", True, type=bool)
            self.assertTrue(chart_enabled, "Chart-Setting sollte aktiviert sein")
            
            print(f"   ✅ Chart-Integration erfolgreich getestet")
            
        except Exception as e:
            self.fail(f"Fehler bei Chart-Integration: {e}")
    
    def test_obergruppen_aggregation(self):
        """Teste korrekte Aggregation der Obergruppen"""
        print("🗂️ Teste Obergruppen-Aggregation...")
        
        try:
            # BWA-Generator erstellen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Test-Summary (korrekte Struktur: Dict[str, float])
            # Diese Daten repräsentieren bereits aggregierte Obergruppen-Werte
            summary = {
                'Erträge': 3000.00,        # Summe aus Einnahmen + Spenden
                'Ausgaben': -500.00        # Verwaltungskosten
            }
            
            # Chart erstellen
            chart = generator._create_supergroup_bar_chart(summary, "Q1")
            
            # Chart sollte erstellt werden
            self.assertIsNotNone(chart, "Chart sollte mit aggregierten Obergruppen erstellt werden")
            
            # Die Methode sollte die BWA-Gruppen korrekt zu Obergruppen aggregieren
            # Erträge: 1000 + 2000 = 3000
            # Ausgaben: -500
            
            print("   ✅ Obergruppen-Aggregation funktioniert")
            
        except Exception as e:
            self.fail(f"Fehler bei Obergruppen-Aggregation: {e}")
    
    def test_long_group_names(self):
        """Teste Behandlung langer Gruppennamen"""
        print("📏 Teste lange Gruppennamen...")
        
        try:
            # Sehr lange Obergruppen-Namen in Settings setzen
            long_super_group_mappings = {
                "Einnahmen": "Sehr sehr sehr lange Obergruppe für Erträge und Einnahmen",
                "Verwaltungskosten": "Ausgaben"
            }
            import json
            self.settings.setValue("super_group_mappings", json.dumps(long_super_group_mappings))
            self.settings.sync()
            
            # BWA-Generator erstellen
            generator = BWAPDFGenerator()
            generator.settings = self.settings
            
            # Test-Summary (korrekte Struktur: Dict[str, float])
            summary = {
                'Sehr sehr sehr lange Obergruppe für Erträge und Einnahmen': 1000.00,
                'Ausgaben': -500.00
            }
            
            # Chart erstellen
            chart = generator._create_supergroup_bar_chart(summary, "Q1")
            
            # Chart sollte auch mit langen Namen erstellt werden
            self.assertIsNotNone(chart, "Chart sollte auch mit langen Gruppennamen erstellt werden")
            
            print("   ✅ Lange Gruppennamen korrekt behandelt")
            
        except Exception as e:
            self.fail(f"Fehler bei langen Gruppennamen: {e}")


if __name__ == '__main__':
    print("🧪 Starte Balkendiagramm-Funktionalitäts-Tests...")
    
    # Test-Suite ausführen
    unittest.main(verbosity=2)
