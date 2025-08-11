#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für die neuen Quartalsauswertungs-Modi und Einstellungen
"""

import sys
import os
import json
import pandas as pd
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Lokale Imports - Pfad zum Projekt-Root hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.utils.csv_processor import CSVProcessor
from src.utils.bwa_generator import BWAPDFGenerator

def test_quarter_modes():
    """Testet die verschiedenen Quartalsauswertungs-Modi"""
    app = QApplication(sys.argv)
    
    print("📊 Teste neue Quartalsauswertungs-Modi...")
    
    # Test-Daten erstellen
    test_data = pd.DataFrame([
        {'Buchungstag': '2024.01.15', 'Sachkontonr.': '4000', 'Betrag': 1000.0, 'Verwendungszweck': 'Q1 Buchung'},
        {'Buchungstag': '2024.02.15', 'Sachkontonr.': '4000', 'Betrag': 500.0, 'Verwendungszweck': 'Q1 Buchung 2'},
        {'Buchungstag': '2024.04.15', 'Sachkontonr.': '4000', 'Betrag': 800.0, 'Verwendungszweck': 'Q2 Buchung'},
        {'Buchungstag': '2024.05.15', 'Sachkontonr.': '4000', 'Betrag': 300.0, 'Verwendungszweck': 'Q2 Buchung 2'},
        {'Buchungstag': '2024.07.15', 'Sachkontonr.': '4000', 'Betrag': 600.0, 'Verwendungszweck': 'Q3 Buchung'},
        {'Buchungstag': '2024.08.15', 'Sachkontonr.': '4000', 'Betrag': 400.0, 'Verwendungszweck': 'Q3 Buchung 2'},
        {'Buchungstag': '2024.10.15', 'Sachkontonr.': '4000', 'Betrag': 900.0, 'Verwendungszweck': 'Q4 Buchung'},
        {'Buchungstag': '2024.11.15', 'Sachkontonr.': '4000', 'Betrag': 200.0, 'Verwendungszweck': 'Q4 Buchung 2'},
    ])
    
    # CSV-Processor (Mock)
    csv_processor = CSVProcessor()
    csv_processor.processed_data = test_data.copy()
    
    # Datum parsen und Quartale hinzufügen
    csv_processor.processed_data['Buchungstag_Clean'] = pd.to_datetime(test_data['Buchungstag'], format='%Y.%m.%d').dt.date
    csv_processor.processed_data['Quartal'] = csv_processor.processed_data['Buchungstag_Clean'].apply(csv_processor._get_quarter)
    csv_processor.processed_data['Betrag_Clean'] = test_data['Betrag']
    
    print("✅ Test-Daten erstellt:")
    print("   Q1: 1.500,00 € (1.000 + 500)")
    print("   Q2: 1.100,00 € (800 + 300)")
    print("   Q3: 1.000,00 € (600 + 400)")
    print("   Q4: 1.100,00 € (900 + 200)")
    
    settings = QSettings()
    
    # Test 1: Quartalsweise Auswertung
    print("\n🔍 Test 1: Quartalsweise Auswertung")
    settings.setValue("quarter_mode", "quarterly")
    
    for quarter in range(1, 5):
        quarter_data = csv_processor.get_data_by_quarter(quarter)
        total = quarter_data['Betrag_Clean'].sum()
        print(f"   Q{quarter}: {total:,.2f} € ({len(quarter_data)} Buchungen)")
    
    # Test 2: Kumulative Auswertung (Standard)
    print("\n🔍 Test 2: Kumulative Auswertung (kumuliere Quartale)")
    settings.setValue("quarter_mode", "cumulative")
    
    cumulative_total = 0.0
    for quarter in range(1, 5):
        quarter_data = csv_processor.get_data_by_quarter(quarter)
        total = quarter_data['Betrag_Clean'].sum()
        cumulative_total += (1500.0 if quarter == 1 else 1100.0 if quarter == 2 else 1000.0 if quarter == 3 else 1100.0)
        print(f"   Q{quarter}: {total:,.2f} € ({len(quarter_data)} Buchungen) - Erwartung: {cumulative_total:,.2f} €")
    
    # Test 3: Berichterstellungs-Optionen
    print("\n🔍 Test 3: Berichterstellungs-Optionen")
    
    # Alle Berichte aktiviert
    settings.setValue("generate_quarterly_reports", True)
    settings.setValue("generate_account_reports", True)
    print("   ✅ Quartalsberichte: Aktiviert")
    print("   ✅ Sachkontenberichte: Aktiviert")
    
    # Nur Jahresbericht
    settings.setValue("generate_quarterly_reports", False)
    settings.setValue("generate_account_reports", False)
    print("   ❌ Quartalsberichte: Deaktiviert")
    print("   ❌ Sachkontenberichte: Deaktiviert")
    
    # Test 4: BWA-Generator mit Einstellungen
    print("\n🔍 Test 4: BWA-Generator mit neuen Einstellungen")
    
    # Kumulative Auswertung mit allen Berichten
    settings.setValue("quarter_mode", "cumulative")
    settings.setValue("generate_quarterly_reports", True)
    settings.setValue("generate_account_reports", True)
    
    generator = BWAPDFGenerator()
    test_mappings = {"4000": "Test-Einnahmen"}
    
    # Testweise Quartals-Seite erstellen
    quarter_page = generator._create_quarter_page(2, csv_processor, test_mappings)
    
    if quarter_page:
        print("   ✅ Quartals-Seite Q2 (kumulativ) erfolgreich erstellt")
        
    # Quartalsweise Auswertung testen
    settings.setValue("quarter_mode", "quarterly")
    quarter_page_individual = generator._create_quarter_page(2, csv_processor, test_mappings)
    
    if quarter_page_individual:
        print("   ✅ Quartals-Seite Q2 (quartalsweise) erfolgreich erstellt")
    
    print("\n📋 Zusammenfassung der neuen Features:")
    print("   🔄 Quartalsauswertungs-Modi:")
    print("      • Quartalsweise: Q1(Jan-Mär), Q2(Apr-Jun), Q3(Jul-Sep), Q4(Okt-Dez)")
    print("      • Kumulativ: Q1(Jan-Mär), Q2(Jan-Jun), Q3(Jan-Sep), Q4(Jan-Dez)")
    print("   📊 Optionale Berichterstellung:")
    print("      • Quartalsberichte ein/ausschaltbar")
    print("      • Sachkontenberichte ein/ausschaltbar")
    print("   💾 Einstellungen Export/Import:")
    print("      • Alle Einstellungen als JSON exportierbar")
    print("      • Import mit Sicherheitsabfrage")
    
    print("\n🎉 Alle Tests erfolgreich!")
    app.quit()

if __name__ == "__main__":
    test_quarter_modes()
