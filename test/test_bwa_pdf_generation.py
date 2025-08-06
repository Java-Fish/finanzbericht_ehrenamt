#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für BWA-PDF-Generierung
"""

import sys
import os
import tempfile
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Lokale Imports
sys.path.append('src')
from utils.bwa_generator import BWAPDFGenerator
from utils.csv_processor import CSVProcessor
from test_helpers import TestFileManager

def test_bwa_pdf_generation():
    """Testet die komplette BWA-PDF-Generierung"""
    print("📄 Teste BWA-PDF-Generierung...")
    
    app = QApplication(sys.argv)
    file_manager = TestFileManager()
    
    try:
        # Test-CSV-Daten erstellen
        test_csv_content = """Sachkontonr.;Betrag;Buchungstag;Beschreibung
4000;1500.00;2024-01-15;Mitgliedsbeiträge
4100;2000.50;2024-02-10;Spenden
6300;-450.00;2024-01-20;Bürokosten
6400;-800.75;2024-03-05;Miete
8100;-320.50;2024-02-15;Veranstaltungskosten"""
        
        # Test-CSV-Datei erstellen
        test_csv_path = file_manager.get_temp_file_path('test_data.csv')
        with open(test_csv_path, 'w', encoding='utf-8') as f:
            f.write(test_csv_content)
        
        # Test-Mappings für Obergruppen setzen
        settings = QSettings()
        super_group_mappings = {
            "Mitgliedsbeiträge": "Einnahmen",
            "Spenden": "Einnahmen", 
            "Bürokosten": "Verwaltungskosten",
            "Miete": "Verwaltungskosten",
            "Veranstaltungskosten": "Projektkosten"
        }
        settings.setValue("super_group_mappings", json.dumps(super_group_mappings))
        
        # BWA-Gruppierungen setzen
        account_mappings = {
            "4000": "Mitgliedsbeiträge",
            "4100": "Spenden",
            "6300": "Bürokosten", 
            "6400": "Miete",
            "8100": "Veranstaltungskosten"
        }
        
        # CSV-Processor initialisieren
        csv_processor = CSVProcessor()
        success_load = csv_processor.load_file(test_csv_path)
        
        if not success_load:
            print("❌ CSV-Datei konnte nicht geladen werden")
            return False
        
        # BWA-Generator initialisieren
        generator = BWAPDFGenerator()
        
        # PDF-Ausgabepfad
        output_pdf = file_manager.get_temp_file_path('test_bwa.pdf')
        
        # PDF generieren
        print("🔄 Generiere BWA-PDF...")
        success = generator.generate_bwa_pdf(output_pdf, csv_processor, account_mappings)
        
        if success and os.path.exists(output_pdf):
            file_size = os.path.getsize(output_pdf)
            print(f"✅ BWA-PDF erfolgreich erstellt!")
            print(f"   📄 Pfad: {output_pdf}")
            print(f"   📊 Größe: {file_size:,} Bytes")
            
            # Test der wichtigsten Komponenten
            print("\n🔍 Teste einzelne Komponenten...")
            
            # Test Obergruppen-Mappings
            loaded_mappings = generator._load_super_group_mappings()
            if loaded_mappings:
                print(f"✅ Obergruppen-Mappings geladen: {len(loaded_mappings)} Zuordnungen")
            else:
                print("❌ Obergruppen-Mappings konnten nicht geladen werden")
            
            # Test BWA-Tabelle
            quarter_data = csv_processor.get_data_by_quarter(1)
            if not quarter_data.empty:
                summary = generator._create_quarter_summary(quarter_data, account_mappings)
                table = generator._create_bwa_table(summary, "Q1")
                if table:
                    print("✅ BWA-Tabelle erfolgreich erstellt")
                else:
                    print("❌ BWA-Tabelle konnte nicht erstellt werden")
            else:
                print("⚠️ Keine Daten für Q1 verfügbar")
            
            return True
        else:
            print("❌ BWA-PDF-Generierung fehlgeschlagen")
            return False
            
    except Exception as e:
        print(f"❌ Fehler bei BWA-PDF-Test: {e}")
        import traceback
        print("\n🔍 Vollständiger Traceback:")
        traceback.print_exc()
        return False
    finally:
        app.quit()

if __name__ == "__main__":
    success = test_bwa_pdf_generation()
    if success:
        print("\n🎉 BWA-PDF-Test erfolgreich!")
    else:
        print("\n💥 BWA-PDF-Test fehlgeschlagen!")
        sys.exit(1)
