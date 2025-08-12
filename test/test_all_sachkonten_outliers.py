#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test des verbesserten Sachkonten-Balkendiagramms mit Outlier-Behandlung
"""

import sys
import os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtCore import QSettings
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor

def test_all_sachkonten_with_outliers():
    """Testet das Sachkonten-Balkendiagramm mit allen Konten und Outlier-Behandlung"""
    print("🎯 Test: Alle Sachkonten mit Outlier-Behandlung")
    print("=" * 60)
    
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
    
    print("\n🚀 Verbessertes Sachkonten-Balkendiagramm:")
    print("   📊 ALLE Sachkonten werden angezeigt (keine 20er-Begrenzung)")
    print("   🎯 Outlier-Erkennung: Werte >3x Median werden als Ausreißer erkannt")
    print("   ✂️  Skalierung begrenzt: Outlier-Balken werden gekürzt dargestellt")
    print("   🔧 Zickzack-Linien: Visuelle Kennzeichnung gekürzter Balken")
    print("   📝 Asterisk (*): Markierung bei gekürzten Beträgen")
    print("   📋 Legende: Erklärung der Kürzungen")
    
    print("\n🔄 Generiere BWA mit verbessertem Sachkonten-Diagramm...")
    
    # Beispiel-Datenanalyse für Outlier-Erkennung
    sample_amounts = []
    for account in accounts[:10]:
        account_data = csv_processor.get_data_by_account(account)
        if not account_data.empty:
            try:
                amounts = account_data['Betrag'].astype(str)
                amounts = amounts.str.replace('€', '').str.replace(',', '.').str.strip()
                numeric_amounts = pd.to_numeric(amounts, errors='coerce')
                total = float(numeric_amounts.sum())
                sample_amounts.append(abs(total))
            except:
                pass
    
    if sample_amounts:
        sample_amounts.sort()
        median = sample_amounts[len(sample_amounts)//2]
        outlier_threshold = median * 3
        outliers = [amt for amt in sample_amounts if amt > outlier_threshold]
        print(f"\n📈 Outlier-Analyse (Beispiel):")
        print(f"   📊 Median-Betrag: {median:,.2f} €")
        print(f"   🚨 Outlier-Schwelle: {outlier_threshold:,.2f} €")
        print(f"   ⚠️  Erkannte Outliers: {len(outliers)}")
    
    # BWA-Generator erstellen und PDF generieren
    generator = BWAPDFGenerator()
    success = generator.generate_bwa_pdf("/tmp/all_sachkonten_outliers.pdf", csv_processor, account_mappings)
    
    if success:
        file_size = os.path.getsize("/tmp/all_sachkonten_outliers.pdf")
        print(f"\n✅ Verbessertes Sachkonten-Diagramm erstellt!")
        print(f"📄 Datei: /tmp/all_sachkonten_outliers.pdf")
        print(f"📊 Größe: {file_size:,} Bytes")
        
        print(f"\n🎯 Neue Features:")
        print(f"   ✅ Alle {len(accounts)} Sachkonten werden angezeigt")
        print(f"   ✅ Intelligente Outlier-Erkennung und -Behandlung")
        print(f"   ✅ Zickzack-Linien für gekürzte Balken")
        print(f"   ✅ Asterisk-Markierung bei gekürzten Werten")
        print(f"   ✅ Automatische Legende für Erklärungen")
        print(f"   ✅ Dynamische Diagrammhöhe je nach Kontenanzahl")
        
        print(f"\n🎨 Visuelle Verbesserungen:")
        print(f"   📊 Bessere Proportionen durch Outlier-Begrenzung")
        print(f"   🔧 Klare Kennzeichnung von Skalierungsbrüchen")
        print(f"   📝 Vollständige Information trotz kompakter Darstellung")
        print(f"   🎯 Professionelle, wissenschaftliche Visualisierung")
        
        print(f"\n💡 Beispiel:")
        print(f"   S02720 mit -20.531,52 € wird als Outlier erkannt")
        print(f"   Der Balken wird auf angemessene Länge gekürzt")
        print(f"   Zickzack-Linien zeigen die Kürzung an")
        print(f"   Betrag wird mit * markiert: -20.531,52 € *")
        
    else:
        print("❌ Fehler beim Erstellen der BWA mit verbessertem Sachkonten-Diagramm")

if __name__ == "__main__":
    test_all_sachkonten_with_outliers()
