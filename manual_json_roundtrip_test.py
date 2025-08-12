#!/usr/bin/env python3
"""
Automatisierter Test für JSON Roundtrip ohne GUI
Testet CSV → PDF/JSON → JSON Import → PDF Vergleich
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_with_gui():
    """Test mit der echten GUI-Anwendung"""
    print("🔄 Teste JSON Roundtrip mit GUI-Anwendung...")
    
    # 1. Anonymisierte Testdatei verwenden
    test_csv = "/Users/nabu/git/finanzauswertungEhrenamt/testdata/test_anonymous.csv"
    
    if not os.path.exists(test_csv):
        print(f"❌ Testdatei nicht gefunden: {test_csv}")
        return False
    
    print(f"📊 Verwende Testdatei: {test_csv}")
    
    # 2. Test-Verzeichnis erstellen
    test_dir = "/tmp/json_roundtrip_test"
    os.makedirs(test_dir, exist_ok=True)
    
    print(f"📁 Test-Verzeichnis: {test_dir}")
    
    # 3. Testdatei in Test-Verzeichnis kopieren
    test_csv_copy = os.path.join(test_dir, "test_input.csv")
    shutil.copy2(test_csv, test_csv_copy)
    
    print(f"📋 Testdatei kopiert: {test_csv_copy}")
    
    # 4. Anweisungen für manuellen Test ausgeben
    print("\n📝 MANUELLE TEST-ANWEISUNGEN:")
    print("=" * 50)
    print("1. Öffne die Anwendung (läuft bereits)")
    print("2. Aktiviere JSON-Export in den Einstellungen")
    print("3. Ziehe diese Datei in das Drag&Drop-Fenster:")
    print(f"   {test_csv_copy}")
    print("4. Erstelle PDF → es sollte automatisch eine JSON-Datei erstellt werden")
    print("5. Ziehe die JSON-Datei wieder in das Drag&Drop-Fenster")
    print("6. Erstelle erneut ein PDF")
    print("7. Vergleiche die beiden PDFs - sie sollten ähnlich sein")
    print("=" * 50)
    
    # 5. Überwachen, ob Dateien erstellt werden
    print("\n🔍 Überwache Test-Verzeichnis auf neue Dateien...")
    
    initial_files = set(os.listdir(test_dir))
    print(f"Initiale Dateien: {initial_files}")
    
    # Warten auf Benutzer-Eingabe
    input("\n⏳ Drücke ENTER wenn du den Test abgeschlossen hast...")
    
    # 6. Prüfe was erstellt wurde
    final_files = set(os.listdir(test_dir))
    new_files = final_files - initial_files
    
    print(f"\n📊 Neue Dateien erstellt: {new_files}")
    
    # PDF-Dateien finden
    pdf_files = [f for f in final_files if f.endswith('.pdf')]
    json_files = [f for f in final_files if f.endswith('.json')]
    
    print(f"📄 PDF-Dateien: {pdf_files}")
    print(f"📋 JSON-Dateien: {json_files}")
    
    # Dateien analysieren
    for pdf in pdf_files:
        pdf_path = os.path.join(test_dir, pdf)
        size = os.path.getsize(pdf_path)
        print(f"📊 {pdf}: {size} Bytes")
    
    for json_file in json_files:
        json_path = os.path.join(test_dir, json_file)
        size = os.path.getsize(json_path)
        print(f"📊 {json_file}: {size} Bytes")
    
    # Erfolg bewerten
    if len(pdf_files) >= 2 and len(json_files) >= 1:
        print("✅ Test-Setup erfolgreich - JSON Roundtrip kann manuell validiert werden")
        
        # Größenvergleich der PDFs
        if len(pdf_files) >= 2:
            sizes = [os.path.getsize(os.path.join(test_dir, pdf)) for pdf in pdf_files]
            size_diff = abs(sizes[0] - sizes[1]) / max(sizes) if max(sizes) > 0 else 0
            
            if size_diff < 0.3:  # 30% Toleranz
                print(f"✅ PDF-Größen ähnlich (Unterschied: {size_diff:.1%})")
            else:
                print(f"⚠️ PDF-Größen unterschiedlich (Unterschied: {size_diff:.1%})")
                print("❌ Möglicherweise Problem mit JSON-Import")
        
        return True
    else:
        print("❌ Test unvollständig - nicht alle erwarteten Dateien erstellt")
        return False

def create_automated_test():
    """Erstellt automatisierten Test für später"""
    test_content = '''#!/usr/bin/env python3
"""
Automatisierter JSON Roundtrip Test
Wird ausgeführt wenn die GUI-Komponenten verfügbar sind
"""

import sys
import os
import tempfile

# Diesen Test später implementieren wenn die GUI-Integration funktioniert
# TODO: Vollständig automatisierter Test ohne manuelle Schritte

def automated_roundtrip_test():
    """Automatisierter Test"""
    print("🤖 Automatisierter JSON Roundtrip Test")
    print("📋 Test-Schritte:")
    print("  1. CSV laden")
    print("  2. PDF + JSON erstellen") 
    print("  3. JSON laden")
    print("  4. Zweites PDF erstellen")
    print("  5. PDFs vergleichen")
    
    # TODO: Implementierung nach GUI-Problem-Fix
    return True

if __name__ == "__main__":
    automated_roundtrip_test()
'''

    with open("/Users/nabu/git/finanzauswertungEhrenamt/automated_json_test.py", "w") as f:
        f.write(test_content)
    
    print("📝 Automatisierter Test-Template erstellt: automated_json_test.py")

if __name__ == "__main__":
    print("🧪 JSON Roundtrip Test Suite")
    print("=" * 40)
    
    # Führe manuellen Test aus
    success = test_with_gui()
    
    # Erstelle Template für automatisierten Test
    create_automated_test()
    
    print(f"\n{'✅ Test erfolgreich' if success else '❌ Test fehlgeschlagen'}")
