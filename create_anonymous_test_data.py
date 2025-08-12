#!/usr/bin/env python3
"""
Anonymisiert die Original-CSV-Datei für Tests
"""

import pandas as pd
import random
import string
from datetime import datetime, timedelta

def generate_random_string(length=10):
    """Generiert zufällige Strings"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_purpose():
    """Generiert zufällige Verwendungszwecke"""
    purposes = [
        "Testbuchung", "Beispielzahlung", "Probetransaktion", 
        "Demozahlung", "Testtransaktion", "Beispielbetrag",
        "Probezahlung", "Beispielüberweisung", "Testübertrag",
        "Demobetrag", "Probeausgabe", "Testeinnahme"
    ]
    return random.choice(purposes) + " " + generate_random_string(5)

def generate_random_account_name():
    """Generiert zufällige Sachkonto-Bezeichnungen"""
    categories = [
        "Test Einnahmen", "Test Ausgaben", "Test Kosten", "Test Spenden",
        "Beispiel Gebühren", "Demo Miete", "Test Material", "Beispiel Porto",
        "Test Reisekosten", "Demo Telefon", "Beispiel Büro", "Test Veranstaltung",
        "Demo Verwaltung", "Test Honorare", "Beispiel Zinsen", "Test Abschreibung"
    ]
    return random.choice(categories) + " " + generate_random_string(3)

def generate_random_amount():
    """Generiert zufällige Beträge"""
    # Positive und negative Beträge zwischen -5000 und +5000
    amount = round(random.uniform(-5000, 5000), 2)
    return f"{amount:.2f} €" if amount >= 0 else f"{amount:.2f} €"

def anonymize_csv():
    """Anonymisiert die CSV-Datei"""
    print("📁 Lade Original-CSV...")
    
    # Original-CSV laden
    original_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/Finanzübersicht_2024.csv"
    df = pd.read_csv(original_path, sep=';', encoding='utf-8')
    
    print(f"✅ {len(df)} Zeilen geladen")
    
    # Anonymisierung
    print("🎭 Anonymisiere Daten...")
    
    # Zufällige Sachkonto-Namen generieren (eindeutig pro Sachkontonr.)
    unique_accounts = df['Sachkontonr.'].unique()
    account_name_mapping = {
        account: generate_random_account_name() 
        for account in unique_accounts
    }
    
    # Anonymisierung anwenden
    df_anon = df.copy()
    
    # Sachkonto-Namen ersetzen
    df_anon['Sachkonto'] = df_anon['Sachkontonr.'].map(account_name_mapping)
    
    # Verwendungszweck anonymisieren
    df_anon['Verwendungszweck'] = [generate_random_purpose() for _ in range(len(df_anon))]
    
    # Begünstigter anonymisieren
    df_anon['Beguenstigter/Zahlungspflichtiger'] = [
        f"Test Person {generate_random_string(3)}" 
        for _ in range(len(df_anon))
    ]
    
    # Sensible Spalten entfernen
    columns_to_remove = ['Kontonummer/IBAN', 'BIC (SWIFT-Code)']
    for col in columns_to_remove:
        if col in df_anon.columns:
            df_anon.drop(col, axis=1, inplace=True)
    
    # Beträge randomisieren (aber Struktur beibehalten)
    df_anon['Betrag'] = [generate_random_amount() for _ in range(len(df_anon))]
    
    # Anonymisierte Datei speichern
    output_path = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/test_anonymous.csv"
    df_anon.to_csv(output_path, sep=';', index=False, encoding='utf-8')
    
    print(f"✅ Anonymisierte Datei erstellt: {output_path}")
    print(f"📊 Entfernte Spalten: {columns_to_remove}")
    print(f"📊 Neue Spalten: {list(df_anon.columns)}")
    
    # Statistiken
    print(f"\n📈 Statistiken:")
    print(f"Einträge: {len(df_anon)}")
    print(f"Sachkonten: {len(unique_accounts)}")
    
    # Datum-Bereich (erste und letzte 5 Werte anzeigen)
    buchungstage = df_anon['Buchungstag'].dropna()
    if len(buchungstage) > 0:
        print(f"Buchungstage (Beispiele): {buchungstage.iloc[:3].tolist()}")
    
    return output_path

if __name__ == "__main__":
    random.seed(42)  # Für reproduzierbare Ergebnisse
    anonymize_csv()
