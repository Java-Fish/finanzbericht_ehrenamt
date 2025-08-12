#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstration der BWA-Gruppen-Balkengrafiken
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtCore import QSettings
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor

def demonstrate_bwa_group_charts():
    """Demonstriert die neuen BWA-Gruppen-Balkengrafiken"""
    print("🎯 Demonstration: BWA-Gruppen-Balkengrafiken")
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
    
    # BWA-Gruppen auflisten
    bwa_groups = set(account_mappings.values())
    print(f"📈 BWA-Gruppen ({len(bwa_groups)}):")
    for i, group in enumerate(sorted(bwa_groups), 1):
        accounts_in_group = [k for k, v in account_mappings.items() if v == group]
        print(f"   {i:2d}. {group} ({len(accounts_in_group)} Konten)")
    
    print("\n🔄 Generiere BWA-Report mit BWA-Gruppen-Diagrammen...")
    print("   ✨ NEU: Balkengrafiken zeigen BWA-Gruppen statt Obergruppen")
    
    # BWA-Generator erstellen und PDF generieren
    generator = BWAPDFGenerator()
    success = generator.generate_bwa_pdf("/tmp/bwa_gruppen_demo.pdf", csv_processor, account_mappings)
    
    if success:
        file_size = os.path.getsize("/tmp/bwa_gruppen_demo.pdf")
        print(f"\n✅ BWA-Report erfolgreich erstellt!")
        print(f"📄 Datei: /tmp/bwa_gruppen_demo.pdf")
        print(f"📊 Größe: {file_size:,} Bytes")
        
        print(f"\n🎨 Was hat sich geändert:")
        print(f"   🔸 VORHER: Balkengrafiken zeigten 3 Obergruppen")
        print(f"   🔸 NACHHER: Balkengrafiken zeigen {len(bwa_groups)} BWA-Gruppen")
        print(f"   🔸 Titel geändert: 'Obergruppen-Übersicht' → 'BWA-Gruppen-Übersicht'")
        print(f"   🔸 Detailliertere Aufschlüsselung der Finanzdaten")
        
        print(f"\n📋 BWA-Report Inhalt:")
        print(f"   📈 Quartalsberichte mit BWA-Gruppen-Diagrammen")
        print(f"   📊 Jahresbericht mit BWA-Gruppen-Diagrammen")
        print(f"   🗂️  Detaillierte Hierarchie: Obergruppen → BWA-Gruppen → Sachkonten")
        print(f"   🎨 Professionelle Farbcodierung und Einrückung")
        
        print(f"\n🎯 ERFOLGREICH: BWA-Gruppen-Balkengrafiken implementiert!")
        
    else:
        print("❌ Fehler beim Erstellen der BWA")

if __name__ == "__main__":
    demonstrate_bwa_group_charts()
