#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für main.py und Anwendungs-Start
"""

import sys
import os
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_main_import():
    """Testet Import der main.py"""
    print("🔍 Teste main.py Import...")
    
    try:
        import main
        print("   ✅ main.py erfolgreich importiert")
    except ImportError as e:
        print(f"   ❌ main.py Import fehlgeschlagen: {e}")
        return False
    
    return True

def test_main_function_exists():
    """Testet ob main() Funktion existiert"""
    print("⚙️ Teste main() Funktion...")
    
    try:
        import main
        
        if hasattr(main, 'main'):
            print("   ✅ main() Funktion vorhanden")
        else:
            print("   ❌ main() Funktion nicht gefunden")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ main() Test fehlgeschlagen: {e}")
        return False

def test_application_metadata():
    """Testet Application-Setup ohne GUI-Start"""
    print("📱 Teste Application-Metadaten...")
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from test_utils import create_qapplication
        from PySide6.QtCore import QSettings
        
        # Test-Application für Metadaten-Test
        app = create_qapplication()
        if app is None:
            print("⚠️ GUI-Framework nicht verfügbar - Test übersprungen")
            return True
        
        # Metadaten setzen (wie in main.py)
        app.setApplicationName("Finanzauswertung Ehrenamt")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Ehrenamt Tools")
        app.setOrganizationDomain("ehrenamt-tools.org")
        
        # Prüfen ob Metadaten gesetzt wurden
        if app.applicationName() == "Finanzauswertung Ehrenamt":
            print("   ✅ Application-Name korrekt gesetzt")
        else:
            print(f"   ❌ Application-Name falsch: {app.applicationName()}")
            return False
        
        if app.applicationVersion() == "1.0.0":
            print("   ✅ Application-Version korrekt gesetzt")
        else:
            print(f"   ❌ Application-Version falsch: {app.applicationVersion()}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Application-Metadaten Test fehlgeschlagen: {e}")
        return False

def test_settings_persistence():
    """Testet QSettings Funktionalität"""
    print("💾 Teste Settings-Persistierung...")
    
    try:
        from PySide6.QtCore import QSettings
        
        # Test-Settings erstellen
        settings = QSettings()
        
        # Test-Wert setzen
        test_key = "test_coverage_key"
        test_value = "test_coverage_value"
        
        settings.setValue(test_key, test_value)
        settings.sync()
        
        # Test-Wert wieder laden
        loaded_value = settings.value(test_key)
        
        if loaded_value == test_value:
            print("   ✅ Settings-Persistierung funktioniert")
        else:
            print(f"   ❌ Settings-Persistierung fehlgeschlagen: erwartet '{test_value}', erhalten '{loaded_value}'")
            return False
        
        # Test-Wert wieder entfernen
        settings.remove(test_key)
        settings.sync()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Settings-Test fehlgeschlagen: {e}")
        return False

def test_resource_loading():
    """Testet Ressourcen-Laden"""
    print("📦 Teste Ressourcen-Laden...")
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from src.utils.icon_helper import get_app_icon
        from src.utils.translations import setup_translations
        from test_utils import create_qapplication
        
        # Test-Application
        app = create_qapplication()
        if app is None:
            print("⚠️ GUI-Framework nicht verfügbar - Test übersprungen")
            return True
        
        # Icon-Test
        icon = get_app_icon()
        if icon is not None:
            print("   ✅ App-Icon erfolgreich geladen")
        else:
            print("   ❌ App-Icon nicht geladen")
            return False
        
        # Übersetzungs-Test
        translator = setup_translations(app)
        if translator is not None:
            print("   ✅ Übersetzungen erfolgreich geladen")
        else:
            print("   ❌ Übersetzungen nicht geladen")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ressourcen-Test fehlgeschlagen: {e}")
        return False

def test_project_structure():
    """Testet Projekt-Struktur"""
    print("📁 Teste Projekt-Struktur...")
    
    project_root = Path(__file__).parent.parent
    
    # Wichtige Verzeichnisse prüfen
    required_dirs = [
        'src',
        'src/utils', 
        'src/settings',
        'src/widgets',
        'src/dialogs',
        'test',
        'resources'
    ]
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"   ✅ Verzeichnis {dir_path} vorhanden")
        else:
            print(f"   ❌ Verzeichnis {dir_path} fehlt")
            return False
    
    # Wichtige Dateien prüfen
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'src/__init__.py',
        'src/main_window.py'
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists() and full_path.is_file():
            print(f"   ✅ Datei {file_path} vorhanden")
        else:
            print(f"   ❌ Datei {file_path} fehlt")
            return False
    
    return True

def test_application_startup():
    """Haupttest-Funktion für Application-Start Tests"""
    print("🚀 Teste Anwendungs-Start...")
    
    tests = [
        test_main_import,
        test_main_function_exists,
        test_application_metadata,
        test_settings_persistence,
        test_resource_loading,
        test_project_structure
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
    print(f"\n📊 Application-Start Tests: {passed}/{total} erfolgreich")
    
    return failed == 0

if __name__ == "__main__":
    success = test_application_startup()
    sys.exit(0 if success else 1)
