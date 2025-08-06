#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo für BWA-PDF mit Obergruppen
"""

import sys
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Lokale Imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.bwa_generator import BWAPDFGenerator

def create_demo_pdf():
    """Erstellt ein Demo-BWA-PDF mit Obergruppen"""
    app = QApplication(sys.argv)
    
    print("📄 Erstelle Demo-BWA-PDF mit Obergruppen...")
    
    # Obergruppen-Mappings setzen
    settings = QSettings()
    super_group_mappings = {
        "Mitgliedsbeiträge": "Einnahmen",
        "Spenden": "Einnahmen", 
        "Zuschüsse": "Einnahmen",
        "Projektförderung": "Einnahmen",
        "Bürokosten": "Verwaltungskosten",
        "Miete": "Verwaltungskosten",
        "Telefon": "Verwaltungskosten",
        "Internet": "Verwaltungskosten",
        "Veranstaltungskosten": "Projektkosten",
        "Material": "Projektkosten",
        "Werbung": "Projektkosten",
        "Honorare": "Personalkosten",
        "Reisekosten": "Sonstige Kosten",
        "Versicherungen": "Sonstige Kosten"
    }
    
    mappings_json = json.dumps(super_group_mappings)
    settings.setValue("super_group_mappings", mappings_json)
    
    print(f"✅ Obergruppen-Mappings gesetzt: {len(super_group_mappings)} Zuordnungen")
    
    # BWA-Generator
    generator = BWAPDFGenerator()
    
    # Demo-Daten für BWA-Tabelle
    demo_summary = {
        "Mitgliedsbeiträge": 8500.0,
        "Spenden": 4200.0,
        "Zuschüsse": 3000.0,
        "Projektförderung": 5500.0,
        "Bürokosten": -850.0,
        "Miete": -1200.0,
        "Telefon": -120.0,
        "Internet": -80.0,
        "Veranstaltungskosten": -2400.0,
        "Material": -1100.0,
        "Werbung": -450.0,
        "Honorare": -3200.0,
        "Reisekosten": -320.0,
        "Versicherungen": -280.0
    }
    
    # BWA-Tabelle erstellen
    table = generator._create_bwa_table(demo_summary, "Demo")
    
    if table:
        print("✅ BWA-Tabelle mit Obergruppen erfolgreich erstellt!")
        
        # Berechnung der Obergruppen-Summen
        loaded_mappings = generator._load_super_group_mappings()
        super_groups = {}
        
        for bwa_group, amount in demo_summary.items():
            super_group = loaded_mappings.get(bwa_group, "Nicht zugeordnet")
            if super_group not in super_groups:
                super_groups[super_group] = 0.0
            super_groups[super_group] += amount
        
        print("\n📊 Obergruppen-Übersicht:")
        total = 0.0
        for super_group in sorted(super_groups.keys()):
            amount = super_groups[super_group]
            total += amount
            print(f"  🏷️  {super_group}: {amount:+,.2f} €")
        
        print(f"\n💰 Gesamtergebnis: {total:+,.2f} €")
        
        # Detailaufstellung
        print("\n📋 Detailaufstellung:")
        for super_group in sorted(super_groups.keys()):
            print(f"\n🏷️  {super_group}:")
            for bwa_group, amount in demo_summary.items():
                if loaded_mappings.get(bwa_group) == super_group:
                    print(f"     • {bwa_group}: {amount:+,.2f} €")
    
    else:
        print("❌ Fehler beim Erstellen der BWA-Tabelle")
    
    print("\n🎉 Demo abgeschlossen!")
    app.quit()

if __name__ == "__main__":
    create_demo_pdf()
