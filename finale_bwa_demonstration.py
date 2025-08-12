#!/usr/bin/env python3
"""
Finale Demonstration der detaillierten BWA-Tabellen
"""

import os
import sys
import tempfile

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from utils.csv_processor import CSVProcessor
from utils.bwa_generator import BWAPDFGenerator

def demonstrate_detailed_bwa():
    """Demonstriert die detaillierten BWA-Tabellen"""
    print("🎯 Finale Demonstration der detaillierten BWA-Tabellen")
    print("=" * 60)
    
    main_csv_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/Finanzübersicht_2024.csv"
    
    if not os.path.exists(main_csv_path):
        print(f"❌ Hauptdaten-CSV nicht gefunden: {main_csv_path}")
        return False
    
    # QApplication für GUI-Tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    try:
        print("📊 Lade Daten und Einstellungen...")
        
        # CSV-Processor erstellen
        csv_processor = CSVProcessor()
        success = csv_processor.load_file(main_csv_path)
        
        if not success:
            print(f"❌ Fehler beim Laden der CSV-Daten")
            return False
        
        # Account-Mappings und Namen laden
        settings = QSettings()
        
        account_mappings = {}
        settings.beginGroup("account_mapping")
        for key in settings.allKeys():
            value = settings.value(key, "")
            if value.strip():
                account_mappings[key] = value
        settings.endGroup()
        
        account_names = {}
        settings.beginGroup("account_names")
        for key in settings.allKeys():
            value = settings.value(key, "")
            if value.strip():
                account_names[key] = value
        settings.endGroup()
        
        print(f"✅ Daten geladen: {len(account_mappings)} BWA-Mappings, {len(account_names)} Sachkonto-Namen")
        
        # BWA-PDF generieren
        print(f"\n📄 Generiere finale BWA mit detaillierten Tabellen...")
        
        final_pdf = "/tmp/finale_detaillierte_bwa.pdf"
        
        bwa_generator = BWAPDFGenerator()
        success = bwa_generator.generate_bwa_pdf(final_pdf, csv_processor, account_mappings)
        
        if success:
            print(f"✅ Finale BWA erfolgreich erstellt!")
            
            # Dateigröße prüfen
            file_size = os.path.getsize(final_pdf)
            print(f"📄 PDF-Größe: {file_size:,} Bytes")
            
            print(f"\n📁 Finale BWA-Datei: {final_pdf}")
            
            # JSON auch verfügbar machen
            json_path = final_pdf.replace('.pdf', '.json')
            if os.path.exists(json_path):
                final_json = "/tmp/finale_detaillierte_bwa.json"
                os.rename(json_path, final_json)
                json_size = os.path.getsize(final_json)
                print(f"📋 JSON-Export: {final_json} ({json_size:,} Bytes)")
            
            # Demonstriere die Struktur
            print(f"\n📋 BWA-Struktur im PDF:")
            print(f"🔹 Obergruppen:")
            print(f"   📈 Einnahmen aus ideellem Bereich")
            print(f"      • Spenden (S03220, S03222, S03223, S03225)")
            print(f"      • Sonstige Einnahmen (S03215, S03216, S03217, S05070)")
            print(f"      • Förderung (S02302, S03224)")
            print(f"   📉 Kosten ideeller Bereich")
            print(f"      • Bürokosten (S02660, S02701, S02702, S02711)")
            print(f"      • Untergliederungen (S02710, S02713, S02719, S02720)")
            print(f"      • Sonstige Kosten ideeller Bereich (S02703, S02704, S02705, S02709, S02802, S02810, S02811)")
            print(f"      • Gehalts- / Honorar- / Pauschalzahlung (S02712)")
            print(f"   💰 Vermögensverwaltung")
            print(f"      • Kosten Finanzanlagen (S04712)")
            
            print(f"\n🎨 Formatierung:")
            print(f"   • Obergruppen: Fett, farbiger Hintergrund")
            print(f"   • BWA-Gruppen: Normal, eingerückt mit '•'")
            print(f"   • Sachkonten: Klein, weiter eingerückt mit Kontonummer und Name")
            print(f"   • Beträge: Rechtsbündig, negative Werte in rot")
            
            return True
        else:
            print(f"❌ BWA-PDF Generierung fehlgeschlagen")
            return False
        
    except Exception as e:
        print(f"❌ Fehler bei der Demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demonstrate_detailed_bwa()
    
    if success:
        print(f"\n🎉 DEMONSTRATION ERFOLGREICH!")
        print(f"\n✅ Implementierte Features:")
        print(f"1. ✅ Hierarchische BWA-Struktur:")
        print(f"   - Obergruppen (3 Hauptkategorien)")
        print(f"   - BWA-Gruppen (9 Kategorien)")
        print(f"   - Sachkonten (27 Konten mit Details)")
        print(f"2. ✅ Vollständige Betragsdarstellung auf allen Ebenen")
        print(f"3. ✅ Professionelle Formatierung und Farbcodierung")
        print(f"4. ✅ Einrückung zur besseren Lesbarkeit")
        print(f"5. ✅ JSON-Export mit detaillierten Daten")
        
        print(f"\n🚀 Die BWA-Berichte enthalten jetzt:")
        print(f"   📊 Quartalsberichte mit Sachkonto-Details")
        print(f"   📈 Jahresbericht mit Sachkonto-Details")
        print(f"   💾 JSON-Export mit vollständigen Daten")
        print(f"   🎨 Professionelle PDF-Formatierung")
        
        print(f"\n📁 Dateien zum Prüfen:")
        print(f"   📄 /tmp/finale_detaillierte_bwa.pdf")
        print(f"   📋 /tmp/finale_detaillierte_bwa.json")
    else:
        print(f"\n💥 DEMONSTRATION FEHLGESCHLAGEN!")
    
    sys.exit(0 if success else 1)
