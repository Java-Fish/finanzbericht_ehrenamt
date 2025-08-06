#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für Widget-Module (file_drop_area)
"""

import sys
import os
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_widget_imports():
    """Testet Import der Widget-Module"""
    print("🔍 Teste Widget-Imports...")
    
    try:
        from src.widgets.file_drop_area import FileDropArea
        print("   ✅ FileDropArea importiert")
    except ImportError as e:
        print(f"   ❌ FileDropArea Import fehlgeschlagen: {e}")
        return False
    
    return True

def test_file_drop_area_functionality():
    """Testet FileDropArea Funktionalität (ohne GUI-Anzeige)"""
    print("📂 Teste FileDropArea Funktionalität...")
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from test_utils import create_qapplication
        from src.widgets.file_drop_area import FileDropArea
        
        # QApplication für GUI-Objekte
        app = create_qapplication()
        if app is None:
            print("⚠️ GUI-Framework nicht verfügbar - Test übersprungen")
            return True
        
        # Widget erstellen (ohne anzeigen)
        widget = FileDropArea()
        
        # Basis-Eigenschaften prüfen
        if hasattr(widget, 'file_selected'):
            print("   ✅ Widget hat Signal-System")
        else:
            print("   ❌ Widget fehlt Signal-System")
            return False
        
        # Methoden prüfen
        expected_methods = ['reset_to_default', 'show_imported_file', 'get_current_file']
        for method in expected_methods:
            if hasattr(widget, method):
                print(f"   ✅ Methode {method} vorhanden")
            else:
                print(f"   ❌ Methode {method} fehlt")
                return False
        
        # Widget cleanup
        widget.deleteLater()
        
        return True
        
    except Exception as e:
        print(f"   ❌ FileDropArea Test fehlgeschlagen: {e}")
        return False

def test_file_drop_area_state_management():
    """Testet FileDropArea State Management"""
    print("📊 Teste FileDropArea State Management...")
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from test_utils import create_qapplication
        from src.widgets.file_drop_area import FileDropArea
        
        # QApplication für GUI-Objekte
        app = create_qapplication()
        if app is None:
            print("⚠️ GUI-Framework nicht verfügbar - Test übersprungen")
            return True
        
        # Widget erstellen
        widget = FileDropArea()
        
        # Reset testen
        widget.reset_to_default()
        current_file = widget.get_current_file()
        if current_file is None:
            print("   ✅ Reset funktioniert korrekt")
        else:
            print(f"   ❌ Reset fehlgeschlagen, aktueller Wert: {current_file}")
            return False
        
        # Datei setzen testen
        test_file = "/test/path/test.csv"
        widget.show_imported_file(test_file, True)
        
        current_file = widget.get_current_file()
        if current_file == test_file:
            print("   ✅ Datei-Status Update funktioniert")
        else:
            print(f"   ❌ Datei-Status Update fehlgeschlagen: erwartet {test_file}, erhalten {current_file}")
            return False
        
        # Widget cleanup
        widget.deleteLater()
        
        return True
        
    except Exception as e:
        print(f"   ❌ FileDropArea State Test fehlgeschlagen: {e}")
        return False

def test_widgets():
    """Haupttest-Funktion für alle Widget-Tests"""
    print("🧩 Teste Widget-System...")
    
    tests = [
        test_widget_imports,
        test_file_drop_area_functionality,
        test_file_drop_area_state_management
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Test {test.__name__} fehlgeschlagen: {e}")
            failed += 1
    
    total = passed + failed
    print(f"\n📊 Widget-Tests: {passed}/{total} erfolgreich")
    
    return failed == 0

if __name__ == "__main__":
    success = test_widgets()
    sys.exit(0 if success else 1)
