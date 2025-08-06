#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für Übersetzungs-System (translations.py)
"""

import sys
import os
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_translations_import():
    """Testet Import des Übersetzungs-Moduls"""
    print("🔍 Teste Translations-Import...")
    
    try:
        from src.utils.translations import setup_translations
        print("   ✅ setup_translations importiert")
    except ImportError as e:
        print(f"   ❌ setup_translations Import fehlgeschlagen: {e}")
        return False
    
    return True

def test_translations_setup():
    """Testet Übersetzungs-Setup"""
    print("🌐 Teste Übersetzungs-Setup...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.utils.translations import setup_translations
        
        # QApplication für Übersetzungs-System
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Übersetzungen Setup testen
        translator = setup_translations(app)
        
        # Prüfen ob Translator-Objekt zurückgegeben wird
        if translator is not None:
            print("   ✅ Translator-Setup erfolgreich")
        else:
            print("   ❌ Translator-Setup fehlgeschlagen")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Übersetzungs-Setup fehlgeschlagen: {e}")
        return False

def test_icon_helper_functionality():
    """Testet Icon-Helper Funktionalität"""
    print("🎨 Teste Icon-Helper Funktionalität...")
    
    try:
        from src.utils.icon_helper import get_app_icon
        
        # Icon-Funktion testen
        icon = get_app_icon()
        
        # Prüfen ob Icon-Objekt zurückgegeben wird
        if icon is not None:
            print("   ✅ App-Icon erfolgreich geladen")
        else:
            print("   ❌ App-Icon nicht geladen")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Icon-Helper Test fehlgeschlagen: {e}")
        return False

def test_utility_modules():
    """Testet weitere Utility-Module"""
    print("🔧 Teste Utility-Module...")
    
    # Alle Utils testen
    utils_to_test = [
        ('csv_processor', 'CSVProcessor'),
        ('file_handler', 'FileHandler'),
        ('bwa_generator', 'BWAPDFGenerator'),
    ]
    
    for module_name, class_name in utils_to_test:
        try:
            module = __import__(f'src.utils.{module_name}', fromlist=[class_name])
            cls = getattr(module, class_name)
            
            # Klasse instanziieren (ohne Parameter)
            instance = cls()
            print(f"   ✅ {class_name} erfolgreich instanziiert")
            
        except ImportError as e:
            print(f"   ❌ {class_name} Import fehlgeschlagen: {e}")
            return False
        except Exception as e:
            print(f"   ❌ {class_name} Instanziierung fehlgeschlagen: {e}")
            return False
    
    return True

def test_main_window_integration():
    """Testet MainWindow Integration (ohne GUI-Anzeige)"""
    print("🏠 Teste MainWindow Integration...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.main_window import MainWindow
        
        # QApplication für GUI-Objekte
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # MainWindow erstellen (ohne anzeigen)
        window = MainWindow()
        
        # Basis-Komponenten prüfen
        components = ['csv_processor', 'bwa_generator', 'file_handler']
        for component in components:
            if hasattr(window, component):
                print(f"   ✅ Komponente {component} vorhanden")
            else:
                print(f"   ❌ Komponente {component} fehlt")
                return False
        
        # Window cleanup
        window.deleteLater()
        
        return True
        
    except Exception as e:
        print(f"   ❌ MainWindow Integration fehlgeschlagen: {e}")
        return False

def test_integration():
    """Haupttest-Funktion für Integrations-Tests"""
    print("🔗 Teste System-Integration...")
    
    tests = [
        test_translations_import,
        test_translations_setup,
        test_icon_helper_functionality,
        test_utility_modules,
        test_main_window_integration
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
    print(f"\n📊 Integrations-Tests: {passed}/{total} erfolgreich")
    
    return failed == 0

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
