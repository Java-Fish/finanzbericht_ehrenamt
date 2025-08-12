#!/usr/bin/env python3
"""
Konfiguriert Basis-Einstellungen für JSON Roundtrip Tests
"""

import os
import sys
from PySide6.QtCore import QSettings

def setup_minimal_settings():
    """Konfiguriert minimale Einstellungen für Tests"""
    print("⚙️ Konfiguriere minimale Einstellungen...")
    
    settings = QSettings()
    
    # Organisation
    settings.setValue("organization/name", "Test Organisation e.V.")
    settings.setValue("organization/street", "Teststraße 123")
    settings.setValue("organization/zip", "12345")
    settings.setValue("organization/city", "Teststadt")
    settings.setValue("organization/phone", "0123 456789")
    settings.setValue("organization/email", "test@example.org")
    settings.setValue("organization/info", "Test Verein für JSON-Tests")
    
    # Kontostand
    settings.setValue("opening_balance", 1000.0)
    
    # JSON Export aktivieren
    settings.setValue("json_export", True)
    
    # Quartalsberichte
    settings.setValue("generate_quarterly_reports", True)
    settings.setValue("generate_account_reports", True)
    settings.setValue("generate_chart_report", True)
    settings.setValue("quarter_mode", "cumulative")
    
    print("✅ Basis-Einstellungen konfiguriert")
    
    # Account-Mappings testen
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from settings.account_mapping import AccountMapping
        
        account_mapping = AccountMapping()
        mappings = account_mapping.get_account_mappings()
        
        print(f"📊 Account Mappings: {len(mappings) if mappings else 0} Einträge")
        
        if not mappings:
            print("⚠️ Keine Account-Mappings gefunden - erstelle Standard-Mappings")
            
            # Standard-Mappings für häufige Sachkonten
            standard_mappings = {
                "S03220": "Spenden",
                "S03223": "Spenden Wildvogelhilfe", 
                "S03215": "Einnahmen Verein",
                "S03216": "Mitgliedsbeiträge",
                "S02660": "Miete und Nebenkosten",
                "S02720": "Projektausgaben",
                "S02702": "Telefon/IT",
                "S02701": "Büromaterial/Porto",
                "S02703": "Reisekosten",
                "S02705": "Veranstaltungskosten",
                "S02710": "Jugendarbeit",
                "S02711": "Verwaltungskosten",
                "S02712": "Ehrenamtspauschale",
                "S02802": "Geschenke/Ehrungen",
                "S02811": "Werbekosten",
                "S04712": "Bankgebühren"
            }
            
            # Standard-Mappings setzen
            for account, name in standard_mappings.items():
                account_mapping.set_account_mapping(account, name)
            
            print(f"✅ {len(standard_mappings)} Standard-Mappings erstellt")
        
    except Exception as e:
        print(f"⚠️ Account-Mappings Fehler: {e}")
    
    print("\n📋 Einstellungen wurden konfiguriert. Die Anwendung kann jetzt getestet werden.")

if __name__ == "__main__":
    setup_minimal_settings()
