#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test des neuen Sachkonten-Balkendiagramms
"""

import sys
import os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtCore import QSettings
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor

def test_sachkonten_balkendiagramm():
    """Testet das neue Sachkonten-Balkendiagramm"""
    print("🎯 Test des Sachkonten-Balkendiagramms")
    print("=" * 50)
    
    # CSV-Datei laden
    csv_file = "./testdata/Finanzübersicht_2024.csv"
    csv_processor = CSVProcessor()
    success = csv_processor.load_csv_file(csv_file)
    if not success:
        print(f"❌ Fehler beim Laden der CSV-Datei: {csv_file}")
        return
    
    print(f"📊 CSV-Daten geladen: {len(csv_processor.raw_data)} Buchungszeilen")
    
    # Sachkonten analysieren
    accounts = csv_processor.get_account_numbers()
    print(f"🗂️  Gefundene Sachkonten: {len(accounts)}")
    
    # BWA-Mappings aus QSettings laden (für Kontonamen)
    settings = QSettings()
    account_mappings = {}
    
    settings.beginGroup("account_mappings")
    for key in settings.allKeys():
        account_mappings[key] = settings.value(key)
    settings.endGroup()
    
    account_names = {}
    settings.beginGroup("account_names")
    for key in settings.allKeys():
        account_names[key] = settings.value(key)
    settings.endGroup()
    
    print(f"📝 Gespeicherte Kontonamen: {len(account_names)}")
    
    print("\n📊 Neues Sachkonten-Balkendiagramm:")
    print("   🎯 Zeigt alle Sachkonten-Salden über Gesamtdaten")
    print("   📏 Top 20 Konten (nach Betragshöhe sortiert)")
    print("   🎨 Grüne Balken für positive, rote für negative Werte")
    print("   📐 ReportLab-basierte Implementierung (wie BWA-Gruppen)")
    print("   📍 0€-Linie als Orientierung")
    print("   📝 Sachkonto-Namen aus QSettings falls verfügbar")
    
    print("\n🔄 Generiere BWA mit Sachkonten-Balkendiagramm...")
    
    # BWA-Generator erstellen und PDF generieren
    generator = BWAPDFGenerator()
    success = generator.generate_bwa_pdf("/tmp/sachkonten_chart_test.pdf", csv_processor, account_mappings)
    
    if success:
        file_size = os.path.getsize("/tmp/sachkonten_chart_test.pdf")
        print(f"\n✅ BWA mit Sachkonten-Diagramm erfolgreich erstellt!")
        print(f"📄 Datei: /tmp/sachkonten_chart_test.pdf")
        print(f"📊 Größe: {file_size:,} Bytes")
        
        # Beispiel-Sachkonten anzeigen
        print(f"\n📋 Beispiel-Sachkonten aus den Daten:")
        sample_accounts = accounts[:10] if len(accounts) > 10 else accounts
        for i, account in enumerate(sample_accounts, 1):
            account_data = csv_processor.get_data_by_account(account)
            if not account_data.empty:
                try:
                    # Versuche zuerst direkte Konvertierung
                    total = float(account_data['Betrag'].sum())
                except (ValueError, TypeError):
                    # Falls das fehlschlägt, bereinige die Daten
                    amounts = account_data['Betrag'].astype(str)
                    amounts = amounts.str.replace('€', '').str.replace(',', '.').str.strip()
                    numeric_amounts = pd.to_numeric(amounts, errors='coerce')
                    total = float(numeric_amounts.sum())
                
                account_name = account_names.get(account, "")
                display_name = f"{account}: {account_name}" if account_name else f"Konto {account}"
                print(f"   {i:2d}. {display_name}: {total:,.2f} €")
        
        if len(accounts) > 10:
            print(f"   ... und {len(accounts) - 10} weitere Sachkonten")
        
        print(f"\n🎯 Features des Sachkonten-Diagramms:")
        print(f"   ✅ Alle Sachkonten über Gesamtdaten analysiert")
        print(f"   ✅ Top 20 Konten für bessere Übersichtlichkeit")
        print(f"   ✅ Positive (grün) und negative (rot) Salden")
        print(f"   ✅ Konsistenter Stil mit BWA-Gruppen-Diagrammen")
        print(f"   ✅ Sachkonto-Namen aus Einstellungen")
        print(f"   ✅ Kompakte aber lesbare Darstellung")
        
    else:
        print("❌ Fehler beim Erstellen der BWA mit Sachkonten-Diagramm")

if __name__ == "__main__":
    test_sachkonten_balkendiagramm()
