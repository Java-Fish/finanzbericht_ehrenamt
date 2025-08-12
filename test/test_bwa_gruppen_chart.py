#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der BWA-Gruppen-Balkengrafiken
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtCore import QSettings
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor

def test_bwa_gruppen_chart():
    """Testet die neuen BWA-Gruppen-Balkengrafiken"""
    print("🔄 Teste BWA-Gruppen-Balkengrafiken...")
    
    # CSV-Datei laden
    csv_file = "./testdata/Finanzübersicht_2024.csv"
    csv_processor = CSVProcessor()
    success = csv_processor.load_csv_file(csv_file)
    if not success:
        print(f"❌ Fehler beim Laden der CSV-Datei: {csv_file}")
        return
    
    # Settings vorbereiten
    settings = QSettings()
    
    # BWA-Mappings laden (die aus unserem CSV-Import)
    csv_bwa_file = "./testdata/bwa_gruppen_export.csv"
    if os.path.exists(csv_bwa_file):
        print(f"📂 Lade BWA-Mappings aus {csv_bwa_file}")
        with open(csv_bwa_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[1:]  # Header überspringen
            for line in lines:
                parts = line.strip().split(';')
                if len(parts) >= 3:
                    account = parts[0]
                    bwa_group = parts[2]
                    settings.setValue(f"account_mappings/{account}", bwa_group)
        print(f"✅ {len(lines)} BWA-Mappings geladen")
    
    # BWA-Generator erstellen
    generator = BWAPDFGenerator()
    
    # PDF generieren mit neuen BWA-Gruppen-Diagrammen
    print("📄 Generiere BWA mit BWA-Gruppen-Diagrammen...")
    success = generator.generate_bwa_pdf("/tmp/test_bwa_gruppen_chart.pdf", csv_processor)
    
    if success:
        # Dateigröße anzeigen
        file_size = os.path.getsize("/tmp/test_bwa_gruppen_chart.pdf")
        print(f"✅ BWA mit BWA-Gruppen-Diagrammen erfolgreich erstellt!")
        print(f"📄 Datei: /tmp/test_bwa_gruppen_chart.pdf")
        print(f"📊 Größe: {file_size:,} Bytes")
        
        # BWA-Gruppen anzeigen, die in den Diagrammen erscheinen sollten
        print("\n📊 BWA-Gruppen in den Diagrammen:")
        bwa_mappings = {}
        for account in csv_processor.df['Sachkontonr.'].unique():
            account_str = str(account)
            bwa_group = settings.value(f"account_mappings/{account_str}", "")
            if bwa_group and bwa_group != "":
                if bwa_group not in bwa_mappings:
                    bwa_mappings[bwa_group] = []
                bwa_mappings[bwa_group].append(account_str)
        
        for bwa_group, accounts in bwa_mappings.items():
            print(f"   📈 {bwa_group}: {len(accounts)} Konten")
        
        print(f"\n🎯 Insgesamt {len(bwa_mappings)} BWA-Gruppen werden in den Balkengrafiken angezeigt")
        
    else:
        print("❌ Fehler beim Erstellen der BWA")

if __name__ == "__main__":
    test_bwa_gruppen_chart()
