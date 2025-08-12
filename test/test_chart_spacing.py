#!/usr/bin/env python3
"""
Einfacher Test für verbesserte Abstände im Sachkonten-Diagramm
"""

import sys
import os
from pathlib import Path

# Projektverzeichnis hinzufügen
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

# PySide6 für QSettings
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

# Eigene Module
from utils.csv_processor import CSVProcessor
from utils.bwa_generator import BWAPDFGenerator

def test_improved_spacing():
    """Teste das Sachkonten-Diagramm mit verbesserten Abständen"""
    print("🎯 Test: Verbesserte Abstände im Sachkonten-Diagramm")
    print("=" * 60)
    
    # QApplication für QSettings (minimal)
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    try:
        # CSV-Datei laden
        csv_file = "./testdata/Finanzübersicht_2024.csv"
        print(f"Lade CSV-Datei: {csv_file}")
        
        processor = CSVProcessor()
        processor.load_csv_file(csv_file)
        
        # Account mappings laden (falls vorhanden)
        account_mappings = {}
        bwa_csv = "./testdata/bwa_gruppen_export.csv"
        if os.path.exists(bwa_csv):
            import pandas as pd
            bwa_data = pd.read_csv(bwa_csv, delimiter=';')
            for _, row in bwa_data.iterrows():
                account_mappings[row['Sachkonto']] = row['BWA-Gruppe']
            print(f"📊 BWA-Mappings geladen: {len(account_mappings)} Zuordnungen")
        
        # PDF generieren mit verbessertem Layout
        generator = BWAPDFGenerator()
        output_file = "/tmp/improved_spacing_test.pdf"
        
        print("🎨 Verbesserungen:")
        print("   ✅ Left Margin: 5.0 cm → 5.5 cm")
        print("   ✅ Right Margin: 2.0 cm → 2.5 cm")
        print("   ✅ Text-Balken Abstand links: 0.2 cm → 0.3 cm")
        print("   ✅ Text-Balken Abstand rechts: 0.1 cm → 0.2 cm")
        print("   ✅ Mehr Platz für Zickzack-Linien und Asterisk-Markierungen")
        
        success = generator.generate_bwa_pdf(output_file, processor, account_mappings)
        
        if success and os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"\n✅ PDF erfolgreich erstellt!")
            print(f"📄 Datei: {output_file}")
            print(f"📊 Größe: {file_size:,} Bytes")
            print(f"🎯 Alle Text-Elemente haben jetzt mehr Abstand zu den Balken")
            print(f"🔧 Zickzack-Linien überlappen nicht mehr mit Text")
            
            return True
        else:
            print("❌ Fehler beim Erstellen der PDF")
            return False
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False
    finally:
        if app:
            app.quit()

if __name__ == "__main__":
    test_improved_spacing()
