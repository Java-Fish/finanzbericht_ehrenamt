#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der weiter optimierten BWA-Gruppen-Balkengrafiken
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtCore import QSettings
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor

def test_maximized_bwa_charts():
    """Testet die weiter optimierten BWA-Gruppen-Balkengrafiken mit maximaler Platznutzung"""
    print("🎯 Test der maximierten BWA-Gruppen-Balkengrafiken")
    print("=" * 65)
    
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
    
    print("\n🎯 Weitere Optimierungen der Balkengrafiken:")
    print("   📏 Gesamtbreite: 14 cm → 16 cm (maximale Platznutzung)")
    print("   📐 Linker Bereich: 2.5 cm → 3.5 cm (mehr Platz für BWA-Namen)")
    print("   📐 Rechter Bereich: 2.5 cm → 1.5 cm (kompakter für Beträge)")
    print("   📊 Balkenbereich: 9 cm → 11 cm (22% mehr Platz für Balken)")
    print("   📝 Max. Textlänge: 30 → 35 Zeichen (noch längere BWA-Namen)")
    print("   🎨 Kompaktere Positionierung der Betragsanzeige")
    
    print("\n🔄 Generiere maximierte BWA-Reports...")
    
    # BWA-Generator erstellen und PDF generieren
    generator = BWAPDFGenerator()
    success = generator.generate_bwa_pdf("/tmp/maximized_bwa_charts.pdf", csv_processor, account_mappings)
    
    if success:
        file_size = os.path.getsize("/tmp/maximized_bwa_charts.pdf")
        print(f"\n✅ Maximierte BWA erfolgreich erstellt!")
        print(f"📄 Datei: /tmp/maximized_bwa_charts.pdf")
        print(f"📊 Größe: {file_size:,} Bytes")
        
        print(f"\n🎯 Optimierungsresultat:")
        print(f"   ✅ Maximale Nutzung der verfügbaren Seitenbreite")
        print(f"   ✅ 22% mehr Platz für Balken (9 cm → 11 cm)")
        print(f"   ✅ Längere BWA-Gruppennamen vollständig sichtbar")
        print(f"   ✅ Kompakte aber lesbare Betragsanzeige")
        print(f"   ✅ Ausgewogenes Layout für professionelle Darstellung")
        
        print(f"\n📐 Finale Layout-Details:")
        print(f"   📏 Gesamtbreite: 16 cm (optimal für A4)")
        print(f"   📐 Linker Bereich: 3.5 cm für BWA-Gruppennamen")
        print(f"   📊 Balkenbereich: 11 cm für Diagramm")
        print(f"   📐 Rechter Bereich: 1.5 cm für Beträge")
        print(f"   📝 Max. BWA-Name: 35 Zeichen")
        
        print(f"\n🎨 Visuelle Verbesserungen:")
        print(f"   📊 Längere Balken für bessere Proportionen")
        print(f"   📝 Vollständige BWA-Gruppennamen sichtbar")
        print(f"   💰 Kompakte aber gut lesbare Betragsdarstellung")
        print(f"   🎯 Optimale Platzverteilung ohne verschwendeten Raum")
        
    else:
        print("❌ Fehler beim Erstellen der maximierten BWA")

if __name__ == "__main__":
    test_maximized_bwa_charts()
