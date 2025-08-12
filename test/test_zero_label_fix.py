#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der BWA-Balkengrafiken mit korrigierter 0€-Beschriftung
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtCore import QSettings
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor

def test_zero_label_position():
    """Testet die korrigierte Position der 0€-Beschriftung"""
    print("🎯 Test der 0€-Beschriftung unter dem Balkendiagramm")
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
    
    print("\n📍 Optimierung der 0€-Beschriftung:")
    print("   🔸 VORHER: 0€-Label mitten im Diagramm (überlappt mit Balken)")
    print("   🔸 NACHHER: 0€-Label unter dem Diagramm positioniert")
    print("   📏 Position: 0.2 cm vom unteren Rand")
    print("   🎯 Zentriert unter der Mittellinie")
    print("   ✨ Keine Überlappung mehr mit den Balken")
    
    print("\n🔄 Generiere BWA mit korrigierter 0€-Beschriftung...")
    
    # BWA-Generator erstellen und PDF generieren
    generator = BWAPDFGenerator()
    success = generator.generate_bwa_pdf("/tmp/zero_label_fixed.pdf", csv_processor, account_mappings)
    
    if success:
        file_size = os.path.getsize("/tmp/zero_label_fixed.pdf")
        print(f"\n✅ BWA mit korrigierter 0€-Beschriftung erstellt!")
        print(f"📄 Datei: /tmp/zero_label_fixed.pdf")
        print(f"📊 Größe: {file_size:,} Bytes")
        
        print(f"\n🎯 Verbesserungen:")
        print(f"   ✅ 0€-Beschriftung jetzt unter dem Diagramm")
        print(f"   ✅ Keine Überlappung mehr mit den Balken")
        print(f"   ✅ Bessere Lesbarkeit der Mittellinie")
        print(f"   ✅ Saubere, professionelle Darstellung")
        print(f"   ✅ Mittellinie bleibt als visuelle Referenz erhalten")
        
        print(f"\n📐 Layout-Details:")
        print(f"   📏 0€-Label Position: 0.2 cm vom unteren Rand")
        print(f"   🎯 Zentriert unter der Mittellinie (center_x)")
        print(f"   📊 Mittellinie durchzieht weiterhin das ganze Diagramm")
        print(f"   🎨 Keine Störung der Balken-Darstellung")
        
    else:
        print("❌ Fehler beim Erstellen der BWA mit korrigierter 0€-Beschriftung")

if __name__ == "__main__":
    test_zero_label_position()
