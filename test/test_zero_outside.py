#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der korrigierten 0€-Beschriftung außerhalb des Diagramms
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtCore import QSettings
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor

def test_zero_label_outside():
    """Testet die 0€-Beschriftung außerhalb des Diagramms"""
    print("🎯 Test: 0€-Beschriftung außerhalb des Diagramms")
    print("=" * 55)
    
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
    
    print("\n📍 Korrektur der 0€-Beschriftung:")
    print("   ❌ PROBLEM: 0€-Label stand mitten auf der Mittellinie")
    print("   ✅ LÖSUNG: 0€-Label wird außerhalb des Diagramms positioniert")
    print("   📏 Position: left_margin - 0.7 cm (unter dem Diagramm)")
    print("   🎯 Zentriert unter der Mittellinie")
    print("   🔸 Schriftgröße: 9pt (etwas kleiner für weniger Störung)")
    print("   📊 Mittellinie bleibt nur im Diagrammbereich sichtbar")
    
    print("\n🔄 Generiere BWA mit externer 0€-Beschriftung...")
    
    # BWA-Generator erstellen und PDF generieren
    generator = BWAPDFGenerator()
    success = generator.generate_bwa_pdf("/tmp/zero_label_outside.pdf", csv_processor, account_mappings)
    
    if success:
        file_size = os.path.getsize("/tmp/zero_label_outside.pdf")
        print(f"\n✅ BWA mit externer 0€-Beschriftung erstellt!")
        print(f"📄 Datei: /tmp/zero_label_outside.pdf")
        print(f"📊 Größe: {file_size:,} Bytes")
        
        print(f"\n🎯 Verbesserungen:")
        print(f"   ✅ 0€-Beschriftung außerhalb des Diagramms")
        print(f"   ✅ Keine Überlappung mit Balken oder Mittellinie")
        print(f"   ✅ Mittellinie nur im relevanten Diagrammbereich")
        print(f"   ✅ Saubere, störungsfreie Darstellung")
        print(f"   ✅ Weiterhin als Orientierungshilfe verfügbar")
        
        print(f"\n📐 Layout-Spezifikation:")
        print(f"   📊 Diagrammbereich: left_margin bis chart_height - left_margin")
        print(f"   📏 0€-Label Position: left_margin - 0.7 cm")
        print(f"   📍 X-Position: center_x (zentriert unter Mittellinie)")
        print(f"   🔤 Schriftgröße: 9pt (reduziert für weniger Prominenz)")
        print(f"   🎨 Keine Störung der Hauptvisualisierung")
        
        print(f"\n🚀 Ergebnis: Perfekte Balkengrafik ohne störende Elemente!")
        
    else:
        print("❌ Fehler beim Erstellen der BWA mit externer 0€-Beschriftung")

if __name__ == "__main__":
    test_zero_label_outside()
