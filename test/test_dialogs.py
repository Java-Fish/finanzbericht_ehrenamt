#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für Dialog-Module (about_dialog, sheet_selection_dialog)
"""

import sys
import os
from pathlib import Path

# Import setup
try:
    from test_utils import setup_import_paths, create_qapplication
    setup_import_paths()
except ImportError:
    # Fallback wenn test_utils nicht verfügbar
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

def test_dialog_imports():
    """Testet Import der Dialog-Module"""
    print("🔍 Teste Dialog-Imports...")
    
    try:
        from src.dialogs.about_dialog import AboutDialog
        print("   ✅ AboutDialog importiert")
    except ImportError as e:
        print(f"   ❌ AboutDialog Import fehlgeschlagen: {e}")
        return False
    
    try:
        from src.dialogs.sheet_selection_dialog import SheetSelectionDialog
        print("   ✅ SheetSelectionDialog importiert")
    except ImportError as e:
        print(f"   ❌ SheetSelectionDialog Import fehlgeschlagen: {e}")
        return False
    
    return True

def test_about_dialog_creation():
    """Testet AboutDialog Erstellung (ohne GUI-Anzeige)"""
    print("📄 Teste AboutDialog Erstellung...")
    
    try:
        # Import mit Fallback
        try:
            from test_utils import create_qapplication
        except ImportError:
            def create_qapplication():
                try:
                    from PySide6.QtWidgets import QApplication
                    app = QApplication.instance()
                    if app is None:
                        app = QApplication(sys.argv)
                        app.setQuitOnLastWindowClosed(False)
                    return app
                except ImportError:
                    return None
        
        from src.dialogs.about_dialog import AboutDialog
        
        # QApplication für GUI-Objekte
        app = create_qapplication()
        if app is None:
            print("⚠️ GUI-Framework nicht verfügbar - Test übersprungen")
            return True
        
        # Dialog erstellen (ohne anzeigen)
        dialog = AboutDialog(None)
        
        # Basis-Eigenschaften prüfen
        if hasattr(dialog, 'setWindowTitle'):
            print("   ✅ Dialog hat Basis-Funktionalität")
        else:
            print("   ❌ Dialog fehlt Basis-Funktionalität")
            return False
        
        # Dialog cleanup
        dialog.deleteLater()
        
        return True
        
    except Exception as e:
        print(f"   ❌ AboutDialog Erstellung fehlgeschlagen: {e}")
        return False

def test_sheet_selection_dialog_creation():
    """Testet SheetSelectionDialog Erstellung (ohne GUI-Anzeige)"""
    print("📊 Teste SheetSelectionDialog Erstellung...")
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from test_utils import create_qapplication
        from src.dialogs.sheet_selection_dialog import SheetSelectionDialog
        
        # QApplication für GUI-Objekte
        app = create_qapplication()
        if app is None:
            print("⚠️ GUI-Framework nicht verfügbar - Test übersprungen")
            return True
        
        # Test-Daten
        test_file_path = "test.xlsx"
        test_sheet_names = ["Sheet1", "Daten", "Auswertung"]
        
        # Dialog erstellen (ohne anzeigen)
        dialog = SheetSelectionDialog(test_file_path, test_sheet_names, None)
        
        # Basis-Funktionalität prüfen
        if hasattr(dialog, 'get_selected_sheet'):
            print("   ✅ Dialog hat Auswahl-Funktionalität")
        else:
            print("   ❌ Dialog fehlt Auswahl-Funktionalität")
            return False
        
        # Dialog cleanup
        dialog.deleteLater()
        
        return True
        
    except Exception as e:
        print(f"   ❌ SheetSelectionDialog Erstellung fehlgeschlagen: {e}")
        return False

def test_dialogs():
    """Haupttest-Funktion für alle Dialog-Tests"""
    print("🎭 Teste Dialog-System...")
    
    tests = [
        test_dialog_imports,
        test_about_dialog_creation,
        test_sheet_selection_dialog_creation
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
    print(f"\n📊 Dialog-Tests: {passed}/{total} erfolgreich")
    
    return failed == 0

if __name__ == "__main__":
    success = test_dialogs()
    sys.exit(0 if success else 1)
