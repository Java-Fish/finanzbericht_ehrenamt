#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für BWA-PDF-Export - Erweiterte Tests für Spalten-Konsistenz
"""

import sys
import os
import tempfile
import json
import pandas as pd
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Lokale Imports - Pfad zum Projekt-Root hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor
from test_helpers import TestFileManager


def test_pdf_cover_page_with_organization():
    """Testet die Deckblatt-Generierung mit Organisationsdaten"""
    print("📄 Teste PDF-Deckblatt mit Organisationsdaten...")
    
    file_manager = TestFileManager()
    
    try:
        # Test-Organisationsdaten in Settings speichern
        settings = QSettings()
        settings.setValue("organization/name", "Musterverein e.V.")
        settings.setValue("organization/street", "Musterstraße 123")
        settings.setValue("organization/zip", "12345")
        settings.setValue("organization/city", "Musterstadt")
        settings.setValue("organization/phone", "+49 123 456789")
        settings.setValue("organization/email", "info@musterverein.de")
        settings.setValue("organization/info", "Ein Verein für alle Fälle")
        settings.setValue("opening_balance", 1000.0)
        
        # Test-CSV-Daten erstellen
        test_csv_content = """Sachkontonr.;Betrag;Buchungstag;Beschreibung;Verwendungszweck
4000;1.500,00;2024-01-15;Mitgliedsbeiträge;Jahresbeitrag Müller
4100;500,00;2024-02-10;Spenden;Spende Schmidt"""
        
        test_csv_path = file_manager.get_temp_file_path('test_org.csv')
        with open(test_csv_path, 'w', encoding='utf-8') as f:
            f.write(test_csv_content)
        
        # CSV-Processor und BWA-Generator
        csv_processor = CSVProcessor()
        success_load = csv_processor.load_file(test_csv_path)
        
        if not success_load:
            print("❌ CSV-Datei konnte nicht geladen werden")
            return False
        
        generator = BWAPDFGenerator()
        
        # Test der Deckblatt-Erstellung
        cover_elements = generator._create_cover_page(csv_processor)
        
        if not cover_elements:
            print("❌ Deckblatt-Elemente konnten nicht erstellt werden")
            return False
            
        print(f"✅ Deckblatt erstellt mit {len(cover_elements)} Elementen")
        
        # Test der vollständigen PDF-Generierung mit Organisationsdaten
        output_pdf = file_manager.get_temp_file_path('test_org_output.pdf')
        account_mappings = {
            "4000": "Mitgliedsbeiträge",
            "4100": "Spenden"
        }
        
        # Settings für minimale PDF-Generierung (nur Deckblatt und Jahr)
        settings.setValue("generate_quarterly_reports", False)
        settings.setValue("generate_account_reports", False)
        settings.setValue("generate_chart_report", False)
        
        success = generator.generate_bwa_pdf(output_pdf, csv_processor, account_mappings)
        
        if success and os.path.exists(output_pdf):
            file_size = os.path.getsize(output_pdf)
            print(f"✅ PDF mit Organisationsdaten erstellt!")
            print(f"   📄 Größe: {file_size:,} Bytes")
            
            if file_size > 2000:
                print("✅ PDF hat angemessene Größe für Organisationsdaten")
            else:
                print("⚠️ PDF kleiner als erwartet")
                
        else:
            print("❌ PDF-Generierung mit Organisationsdaten fehlgeschlagen")
            return False
        
        # Settings zurücksetzen
        settings.remove("organization/name")
        settings.remove("organization/street")
        settings.remove("organization/zip")
        settings.remove("organization/city")
        settings.remove("organization/phone")
        settings.remove("organization/email")
        settings.remove("organization/info")
        settings.remove("generate_quarterly_reports")
        settings.remove("generate_account_reports")
        settings.remove("generate_chart_report")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Organisationsdaten-Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export_consistency():
    """Testet die Konsistenz zwischen Betrag und Betrag_Clean Spalten beim PDF-Export"""
    print("📊 Teste PDF-Export mit Spalten-Konsistenz...")
    
    file_manager = TestFileManager()
    
    try:
        # Test-CSV-Daten mit verschiedenen Betragsformaten erstellen
        test_csv_content = """Sachkontonr.;Betrag;Buchungstag;Beschreibung;Verwendungszweck
4000;1.500,00;2024-01-15;Mitgliedsbeiträge;Jahresbeitrag Müller
4100;2000.50;2024-02-10;Spenden;Spende Schmidt
6300;-450,00;2024-01-20;Bürokosten;Büromaterial
6400;-800.75;2024-03-05;Miete;Monatsmiete März
8100;-320,50;2024-04-15;Veranstaltungskosten;Catering Event
4000;500,00;2024-05-10;Mitgliedsbeiträge;Nachzahlung"""
        
        # Test-CSV-Datei erstellen
        test_csv_path = file_manager.get_temp_file_path('test_consistency.csv')
        with open(test_csv_path, 'w', encoding='utf-8') as f:
            f.write(test_csv_content)
        
        # CSV-Processor initialisieren und Datei laden
        csv_processor = CSVProcessor()
        success_load = csv_processor.load_file(test_csv_path)
        
        if not success_load:
            print("❌ CSV-Datei konnte nicht geladen werden")
            return False
        
        # Test 1: Prüfe ob Betrag_Clean Spalte erstellt wurde
        processed_data = csv_processor.processed_data
        if processed_data is None or processed_data.empty:
            print("❌ Keine verarbeiteten Daten verfügbar")
            return False
            
        if 'Betrag_Clean' not in processed_data.columns:
            print("❌ Betrag_Clean Spalte wurde nicht erstellt")
            return False
        
        print("✅ Betrag_Clean Spalte vorhanden")
        
        # Test 2: Prüfe Datentypen und Werte
        betrag_clean_series = processed_data['Betrag_Clean']
        if not betrag_clean_series.dtype in ['float64', 'float32']:
            print(f"❌ Betrag_Clean hat falschen Datentyp: {betrag_clean_series.dtype}")
            return False
            
        print("✅ Betrag_Clean hat korrekten Datentyp (float)")
        
        # Test 3: BWA-Generator Methoden testen
        generator = BWAPDFGenerator()
        
        # Test _calculate_total_amount
        total_amount = generator._calculate_total_amount(csv_processor)
        print(f"ℹ️ Gesamtsumme berechnet: {total_amount:.2f}")
        
        # Test Quartals-Berechnung
        quarter_data = csv_processor.get_data_by_quarter(1)
        if not quarter_data.empty:
            if 'Betrag_Clean' not in quarter_data.columns:
                print("❌ Betrag_Clean fehlt in Quartalsdaten")
                return False
            
            quarter_total = quarter_data['Betrag_Clean'].sum()
            print(f"✅ Q1 Summe berechnet: {quarter_total:.2f}")
        else:
            print("⚠️ Keine Daten für Q1 verfügbar")
        
        # Test 4: Account-Mappings vorbereiten
        account_mappings = {
            "4000": "Mitgliedsbeiträge",
            "4100": "Spenden",
            "6300": "Bürokosten", 
            "6400": "Miete",
            "8100": "Veranstaltungskosten"
        }
        
        # Test 5: BWA-Zusammenfassung erstellen
        if not quarter_data.empty:
            summary = generator._create_quarter_summary(quarter_data, account_mappings)
            if summary:
                print(f"✅ BWA-Zusammenfassung erstellt: {len(summary)} Gruppen")
                
                # Prüfe ob alle Beträge gültig sind
                for group, amount in summary.items():
                    if not isinstance(amount, (int, float)):
                        print(f"❌ Ungültiger Betrag in Gruppe {group}: {amount}")
                        return False
                print("✅ Alle Beträge in Zusammenfassung sind gültig")
            else:
                print("❌ BWA-Zusammenfassung konnte nicht erstellt werden")
                return False
        
        # Test 6: Vollständige PDF-Generierung
        output_pdf = file_manager.get_temp_file_path('test_output.pdf')
        
        print("🔄 Generiere komplettes PDF...")
        success = generator.generate_bwa_pdf(output_pdf, csv_processor, account_mappings)
        
        if success and os.path.exists(output_pdf):
            file_size = os.path.getsize(output_pdf)
            print(f"✅ PDF erfolgreich erstellt!")
            print(f"   📄 Größe: {file_size:,} Bytes")
            
            # Test 7: PDF-Inhalt validieren (falls möglich)
            if file_size > 1000:  # Mindestgröße für gültiges PDF
                print("✅ PDF hat realistische Größe")
            else:
                print("⚠️ PDF sehr klein - möglicherweise leer")
                
        else:
            print("❌ PDF-Generierung fehlgeschlagen")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim PDF-Export-Test: {e}")
        import traceback
        print("\n🔍 Vollständiger Traceback:")
        traceback.print_exc()
        return False


def main():
    """Hauptfunktion für alle PDF-Export-Tests"""
    print("🚀 BWA-PDF-Export Tests")
    print("=" * 50)
    
    # QApplication für GUI-Tests
    app = QApplication(sys.argv)
    
    try:
        # Test 1: Spalten-Konsistenz
        success1 = test_pdf_export_consistency()
        
        print("\n" + "=" * 30)
        
        # Test 2: Deckblatt mit Organisationsdaten
        success2 = test_pdf_cover_page_with_organization()
        
        print("\n" + "=" * 50)
        print("📊 Test-Zusammenfassung:")
        print(f"   PDF-Export (Konsistenz): {'✅' if success1 else '❌'}")
        print(f"   PDF-Deckblatt (Organisation): {'✅' if success2 else '❌'}")
        
        overall_success = success1 and success2
        
        if overall_success:
            print("\n🎉 Alle PDF-Export-Tests erfolgreich!")
            return True
        else:
            print("\n💥 Ein oder mehrere PDF-Export-Tests fehlgeschlagen!")
            return False
            
    finally:
        app.quit()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)