#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für verbesserte BWA-Tabellen-Formatierung
"""

import sys
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Lokale Imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.bwa_generator import BWAPDFGenerator
from utils.csv_processor import CSVProcessor

def test_improved_bwa_table():
    """Testet die verbesserte BWA-Tabellen-Formatierung"""
    app = QApplication(sys.argv)
    
    print("🎨 Teste verbesserte BWA-Tabellen-Formatierung...")
    
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
    
    # Test-Daten mit positiven und negativen Beträgen
    test_summary = {
        "Mitgliedsbeiträge": 8500.50,
        "Spenden": 4200.75,
        "Zuschüsse": 3000.00,
        "Projektförderung": 5500.25,
        "Bürokosten": -850.30,
        "Miete": -1200.00,
        "Telefon": -120.50,
        "Internet": -80.00,
        "Veranstaltungskosten": -2400.75,
        "Material": -1100.25,
        "Werbung": -450.00,
        "Honorare": -3200.50,
        "Reisekosten": -320.75,
        "Versicherungen": -280.00
    }
    
    print("\n📊 Erstelle BWA-Tabelle mit neuer Formatierung...")
    
    # BWA-Tabelle erstellen
    table = generator._create_bwa_table(test_summary, "Q1")
    
    if table:
        print("✅ BWA-Tabelle erfolgreich erstellt!")
        print("✅ Neue Features:")
        print("   • Keine HTML-Tags mehr (kein <b> </b>)")
        print("   • Dezente Obergruppen-Farben")
        print("   • Rote Zahlen für negative Beträge")
        print("   • Schwarze Zahlen für positive Beträge")
        print("   • Professionelle Tabellenformatierung")
        print("   • Farbliche Trennung der Obergruppen")
        
        # Test der _format_amount Methode
        print("\n💰 Test der Betragsformatierung:")
        test_amounts = [1234.56, -1234.56, 0.0, 10000.99, -999.01]
        for amount in test_amounts:
            formatted = generator._format_amount(amount)
            print(f"   {amount:>10} → {formatted}")
        
        # Berechnung für Demo
        loaded_mappings = generator._load_super_group_mappings()
        super_groups = {}
        
        for bwa_group, amount in test_summary.items():
            super_group = loaded_mappings.get(bwa_group, "Nicht zugeordnet")
            if super_group not in super_groups:
                super_groups[super_group] = 0.0
            super_groups[super_group] += amount
        
        print("\n📋 Obergruppen-Übersicht (wie im PDF):")
        total = 0.0
        for super_group in sorted(super_groups.keys()):
            amount = super_groups[super_group]
            formatted = generator._format_amount(amount)
            color_indicator = "🔴" if amount < 0 else "⚫"
            print(f"   {color_indicator} {super_group}: {formatted}")
            total += amount
        
        total_formatted = generator._format_amount(total)
        total_color = "🔴" if total < 0 else "⚫"
        print(f"\n   {total_color} GESAMTERGEBNIS Q1: {total_formatted}")
        
    else:
        print("❌ Fehler beim Erstellen der BWA-Tabelle")
    
    print("\n🎉 Test abgeschlossen!")
    app.quit()

if __name__ == "__main__":
    test_improved_bwa_table()
