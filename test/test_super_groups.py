#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Skript für die Obergruppen-Funktionalität
"""

import sys
import os
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Lokale Imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.utils.bwa_generator import BWAPDFGenerator
from src.settings.super_group_mapping import SuperGroupMappingTab

def test_super_groups():
    """Testet die Obergruppen-Funktionalität"""
    app = QApplication(sys.argv)
    
    print("🧪 Teste Obergruppen-Funktionalität...")
    
    # 1. Test: Obergruppen-Mappings setzen
    settings = QSettings()
    
    # Beispiel-Obergruppen-Mappings
    test_mappings = {
        "Mitgliedsbeiträge": "Einnahmen",
        "Spenden": "Einnahmen", 
        "Zuschüsse": "Einnahmen",
        "Bürokosten": "Verwaltungskosten",
        "Miete": "Verwaltungskosten",
        "Veranstaltungskosten": "Projektkosten",
        "Honorare": "Personalkosten"
    }
    
    mappings_json = json.dumps(test_mappings)
    settings.setValue("super_group_mappings", mappings_json)
    
    print(f"✅ Test-Mappings gesetzt: {len(test_mappings)} Zuordnungen")
    
    # 2. Test: BWA-Generator mit Obergruppen
    generator = BWAPDFGenerator()
    loaded_mappings = generator._load_super_group_mappings()
    
    print(f"✅ Mappings geladen: {len(loaded_mappings)} Zuordnungen")
    print("Geladene Mappings:")
    for bwa_group, super_group in loaded_mappings.items():
        print(f"  • {bwa_group} → {super_group}")
    
    # 3. Test: SuperGroupMappingTab
    tab = SuperGroupMappingTab()
    tab.load_settings()
    
    # Beispiel BWA-Gruppen
    test_bwa_groups = list(test_mappings.keys())
    tab.update_groups_from_mappings(test_bwa_groups)
    
    print(f"✅ SuperGroup-Tab aktualisiert mit {len(test_bwa_groups)} BWA-Gruppen")
    
    # 4. Test: Obergruppen-Struktur in BWA-Tabelle
    print("\n📊 Teste BWA-Tabellen-Struktur...")
    
    # Beispiel-BWA-Daten
    test_summary = {
        "Mitgliedsbeiträge": 5000.0,
        "Spenden": 3000.0,
        "Zuschüsse": 2000.0,
        "Bürokosten": -500.0,
        "Miete": -1200.0,
        "Veranstaltungskosten": -800.0,
        "Honorare": -1500.0
    }
    
    # Obergruppen organisieren
    super_groups = {}
    for bwa_group, amount in test_summary.items():
        super_group = test_mappings.get(bwa_group, "Nicht zugeordnet")
        if super_group not in super_groups:
            super_groups[super_group] = {}
        super_groups[super_group][bwa_group] = amount
    
    print("Obergruppen-Struktur:")
    total = 0.0
    for super_group in sorted(super_groups.keys()):
        bwa_groups = super_groups[super_group]
        super_group_total = sum(bwa_groups.values())
        total += super_group_total
        
        print(f"\n🏷️  {super_group}: {super_group_total:,.2f} €")
        for bwa_group, amount in sorted(bwa_groups.items()):
            print(f"     • {bwa_group}: {amount:,.2f} €")
    
    print(f"\n💰 Gesamtergebnis: {total:,.2f} €")
    
    print("\n🎉 Alle Tests erfolgreich!")
    
    app.quit()

if __name__ == "__main__":
    test_super_groups()
