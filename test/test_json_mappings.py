#!/usr/bin/env python3
"""
Test für das Auslesen der Mappings aus JSON
"""

import os
import sys
import json
from PySide6.QtCore import QSettings

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.csv_processor import CSVProcessor

def test_json_mappings():
    """Teste das Auslesen der Mappings aus JSON"""
    print("🔍 Teste JSON Mappings...")
    
    # JSON-Datei aus dem vorherigen Test verwenden
    json_path = "/tmp/test_export.json"
    
    if not os.path.exists(json_path):
        print(f"❌ JSON-Datei nicht gefunden: {json_path}")
        return False
    
    # JSON-Datei einlesen und Struktur prüfen
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    print("📋 JSON-Struktur:")
    for key in json_data.keys():
        print(f"  - {key}")
    
    # Mappings prüfen
    if 'account_mappings' in json_data:
        account_mappings = json_data['account_mappings']
        print(f"✅ Account-Mappings gefunden: {len(account_mappings)} Einträge")
        for k, v in list(account_mappings.items())[:3]:
            print(f"  - {k}: {v}")
    else:
        print("❌ Keine Account-Mappings in JSON gefunden")
        return False
    
    if 'super_group_mappings' in json_data:
        super_group_mappings = json_data['super_group_mappings']
        print(f"✅ Super-Group-Mappings gefunden: {len(super_group_mappings)} Einträge")
        for k, v in list(super_group_mappings.items())[:3]:
            print(f"  - {k}: {v}")
    else:
        print("❌ Keine Super-Group-Mappings in JSON gefunden")
        return False
    
    # CSV-Processor mit JSON testen
    print("\n📥 Teste CSV-Processor mit JSON...")
    
    processor = CSVProcessor()
    success = processor.load_file(json_path)
    
    if not success:
        print("❌ JSON konnte nicht geladen werden")
        return False
    
    print(f"✅ JSON geladen: {len(processor.processed_data)} Einträge")
    print(f"JSON-Quelle: {processor.is_json_source}")
    
    # Mappings aus CSV-Processor abrufen
    print("\n🔍 Teste Mapping-Abruf...")
    
    account_mappings = processor.get_json_account_mappings()
    if account_mappings:
        print(f"✅ Account-Mappings abgerufen: {len(account_mappings)} Einträge")
        for k, v in list(account_mappings.items())[:3]:
            print(f"  - {k}: {v}")
    else:
        print("❌ Keine Account-Mappings abgerufen")
        return False
    
    super_group_mappings = processor.get_json_super_group_mappings()
    if super_group_mappings:
        print(f"✅ Super-Group-Mappings abgerufen: {len(super_group_mappings)} Einträge")
        for k, v in list(super_group_mappings.items())[:3]:
            print(f"  - {k}: {v}")
    else:
        print("❌ Keine Super-Group-Mappings abgerufen")
        return False
    
    print("\n🎉 Mapping-Test erfolgreich!")
    return True

if __name__ == "__main__":
    success = test_json_mappings()
    print(f"\n{'✅ Mappings-Test erfolgreich' if success else '❌ Mappings-Test fehlgeschlagen'}")
    sys.exit(0 if success else 1)
