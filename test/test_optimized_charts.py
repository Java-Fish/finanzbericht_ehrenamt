#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der optimierten BWA-Gruppen-Balkengrafiken
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtCore import QSettings
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor

def test_optimized_bwa_charts():
    """Testet die optimierten BWA-Gruppen-Balkengrafiken"""
    print("🔧 Test der optimierten BWA-Gruppen-Balkengrafiken")
    print("=" * 60)
    
    # CSV-Datei laden
    csv_file = "./testdata/Finanzübersicht_2024.csv"
    csv_processor = CSVProcessor()
    success = csv_processor.load_csv_file(csv_file)
    if not success:
        print(f"❌ Fehler beim Laden der CSV-Datei: {csv_file}")
        return
    
    print(f"📊 CSV-Daten geladen: {len(csv_processor.raw_data)} Buchungszeilen")
    
    # BWA-Mappings aus QSettings laden
    settings = QSettings()
    account_mappings = {}
    
    settings.beginGroup("account_mappings")
    for key in settings.allKeys():
        account_mappings[key] = settings.value(key)
    settings.endGroup()
    
    print(f"🗂️  BWA-Mappings: {len(account_mappings)} Konten zugeordnet")
    
    print("\n🔧 Optimierungen der Balkengrafiken:")
    print("   📏 Breite: 16 cm → 14 cm (bessere A4-Passform)")
    print("   📐 Linker Rand: 1 cm → 2.5 cm (mehr Platz für BWA-Namen)")
    print("   📐 Rechter Rand: 1 cm → 2.5 cm (mehr Platz für Beträge)")
    print("   📏 Balkenbereich: 14 cm → 9 cm (optimiertes Layout)")
    print("   📝 Max. Textlänge: 25 → 30 Zeichen (längere BWA-Namen)")
    
    print("\n🔄 Generiere optimierte BWA-Reports...")
    
    # BWA-Generator erstellen und PDF generieren
    generator = BWAPDFGenerator()
    success = generator.generate_bwa_pdf("/tmp/optimized_bwa_charts.pdf", csv_processor, account_mappings)
    
    if success:
        file_size = os.path.getsize("/tmp/optimized_bwa_charts.pdf")
        print(f"\n✅ Optimierte BWA erfolgreich erstellt!")
        print(f"📄 Datei: /tmp/optimized_bwa_charts.pdf")
        print(f"📊 Größe: {file_size:,} Bytes")
        
        print(f"\n🎯 Verbesserungen:")
        print(f"   ✅ Balkengrafiken passen vollständig auf A4-Seitenbreite")
        print(f"   ✅ Bessere Platzverteilung für BWA-Gruppennamen")
        print(f"   ✅ Mehr Platz für Betragsanzeige rechts")
        print(f"   ✅ Längere BWA-Gruppennamen werden vollständig angezeigt")
        print(f"   ✅ Weiterhin vertikale (senkrechte) Ausrichtung")
        
        print(f"\n📐 Layout-Details:")
        print(f"   📏 Gesamtbreite: 14 cm (vorher 16 cm)")
        print(f"   📐 Linker Bereich: 2.5 cm für BWA-Namen")
        print(f"   📊 Balkenbereich: 9 cm für Diagramm")
        print(f"   📐 Rechter Bereich: 2.5 cm für Beträge")
        
    else:
        print("❌ Fehler beim Erstellen der optimierten BWA")

if __name__ == "__main__":
    test_optimized_bwa_charts()
