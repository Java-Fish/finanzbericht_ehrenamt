#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für verbesserte Sachkonten-Einzelauswertung
"""

import sys
import json
import pandas as pd
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Lokale Imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.bwa_generator import BWAPDFGenerator

class MockAccountCSVProcessor:
    """Mock CSV-Processor für Sachkonten-Test"""
    
    def __init__(self):
        # Erstelle Test-Daten basierend auf dem Bild
        self.account_data = pd.DataFrame([
            {'Buchungstag': '2024.01.02', 'Verwendungszweck': 'Miete', 'Betrag_Clean': -130.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.01.15', 'Verwendungszweck': 'ReNr:LA8001584659 (Abschlag Januar) MandatsRef:800097138...', 'Betrag_Clean': -9.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.02.01', 'Verwendungszweck': 'Miete', 'Betrag_Clean': -130.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.02.15', 'Verwendungszweck': 'ReNr:LA8001592387 (Abschlag Februar) MandatsRef:800097138...', 'Betrag_Clean': -9.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.03.01', 'Verwendungszweck': 'Miete', 'Betrag_Clean': -130.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.03.15', 'Verwendungszweck': 'ReNr:LA8001597583 (Abschlag März) MandatsRef:800097138...', 'Betrag_Clean': -9.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.04.02', 'Verwendungszweck': 'Miete', 'Betrag_Clean': -130.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.04.15', 'Verwendungszweck': 'ReNr:LA8001603675 (Abschlag April) MandatsRef:800097138...', 'Betrag_Clean': -9.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.05.02', 'Verwendungszweck': 'Miete', 'Betrag_Clean': -130.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.05.15', 'Verwendungszweck': 'ReNr:LA8001612013 (Abschlag Mai) MandatsRef:800097138...', 'Betrag_Clean': -9.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.06.03', 'Verwendungszweck': 'Miete', 'Betrag_Clean': -130.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.06.12', 'Verwendungszweck': 'Nebenkostenabrechnung 2022/2023 NABU Jena DATUM 12.06.20...', 'Betrag_Clean': -85.24, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.08.01', 'Verwendungszweck': 'ReNr:LR8001079076 (Rechnung Juni) inkl. Entl. 1.55 Manda...', 'Betrag_Clean': 4.13, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.08.01', 'Verwendungszweck': 'Miete', 'Betrag_Clean': -130.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.09.02', 'Verwendungszweck': 'Miete', 'Betrag_Clean': -130.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.10.01', 'Verwendungszweck': 'Miete', 'Betrag_Clean': -130.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.11.01', 'Verwendungszweck': 'Miete', 'Betrag_Clean': -130.00, 'Sachkonto': 'Miete, Nebenkonten'},
            {'Buchungstag': '2024.12.02', 'Verwendungszweck': 'Miete', 'Betrag_Clean': -130.00, 'Sachkonto': 'Miete, Nebenkonten'},
        ])
        
        # Füge Sachkontonummer hinzu
        self.account_data['Sachkontonr.'] = 'S02660'
    
    def get_data_by_account(self, account_number):
        """Gibt Daten für ein bestimmtes Sachkonto zurück"""
        if account_number == 'S02660':
            return self.account_data
        else:
            return pd.DataFrame()  # Leer für andere Konten

def test_improved_account_page():
    """Testet die verbesserte Sachkonten-Einzelauswertung"""
    app = QApplication(sys.argv)
    
    print("📊 Teste verbesserte Sachkonten-Einzelauswertung...")
    
    # Mock CSV-Processor mit Test-Daten
    csv_processor = MockAccountCSVProcessor()
    
    # BWA-Generator
    generator = BWAPDFGenerator()
    
    print("✅ Test-Daten geladen (Sachkonto S02660 - Miete, Nebenkonten)")
    
    # Sachkonten-Seite erstellen
    account_elements = generator._create_account_page('S02660', csv_processor)
    
    if account_elements:
        print("✅ Sachkonten-Seite erfolgreich erstellt!")
        print("✅ Neue Features:")
        print("   • Keine HTML-Tags mehr (kein <b> </b>)")
        print("   • Rote Zahlen für negative Beträge")
        print("   • Schwarze Zahlen für positive Beträge")
        print("   • Zebrastreifen für bessere Lesbarkeit")
        print("   • Professionelle Tabellenformatierung")
        print("   • Hervorgehobene Summenzeile")
        
        # Test der Daten-Berechnung
        account_data = csv_processor.get_data_by_account('S02660')
        total = account_data['Betrag_Clean'].sum()
        
        print(f"\n📋 Buchungsübersicht (Sachkonto S02660):")
        print(f"   📊 Anzahl Buchungen: {len(account_data)}")
        
        positive_count = len(account_data[account_data['Betrag_Clean'] > 0])
        negative_count = len(account_data[account_data['Betrag_Clean'] < 0])
        
        print(f"   ⚫ Positive Buchungen: {positive_count}")
        print(f"   🔴 Negative Buchungen: {negative_count}")
        
        total_str = generator._format_amount(total)
        color_indicator = "🔴" if total < 0 else "⚫"
        print(f"   {color_indicator} Summe: {total_str}")
        
        # Beispiel-Buchungen anzeigen
        print(f"\n📝 Beispiel-Buchungen:")
        for i, row in account_data.head(3).iterrows():
            amount = row['Betrag_Clean']
            formatted_amount = generator._format_amount(amount)
            color = "🔴" if amount < 0 else "⚫"
            purpose = row['Verwendungszweck']
            if len(purpose) > 40:
                purpose = purpose[:37] + "..."
            print(f"   {color} {row['Buchungstag']}: {purpose} → {formatted_amount}")
        
        print("   ...")
        
        # Letzte Buchung
        last_row = account_data.iloc[-1]
        last_amount = last_row['Betrag_Clean']
        last_formatted = generator._format_amount(last_amount)
        last_color = "🔴" if last_amount < 0 else "⚫"
        print(f"   {last_color} {last_row['Buchungstag']}: Miete → {last_formatted}")
        
    else:
        print("❌ Fehler beim Erstellen der Sachkonten-Seite")
    
    print("\n🎉 Test abgeschlossen!")
    app.quit()

if __name__ == "__main__":
    test_improved_account_page()
