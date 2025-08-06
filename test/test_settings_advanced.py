#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für Einstellungs-Module (settings-spezifische Tests)
"""

import sys
import os
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_settings_imports():
    """Testet Import aller Settings-Module"""
    print("🔍 Teste Settings-Imports...")
    
    settings_modules = [
        ('general_settings', 'GeneralSettingsTab'),
        ('organization_settings', 'OrganizationSettingsTab'),
        ('mapping_settings', 'MappingSettingsTab'),
        ('account_mapping', 'AccountMappingTab'),
        ('super_group_mapping', 'SuperGroupMappingTab')
    ]
    
    for module_name, class_name in settings_modules:
        try:
            module = __import__(f'src.settings.{module_name}', fromlist=[class_name])
            getattr(module, class_name)
            print(f"   ✅ {class_name} importiert")
        except ImportError as e:
            print(f"   ❌ {class_name} Import fehlgeschlagen: {e}")
            return False
        except AttributeError as e:
            print(f"   ❌ {class_name} nicht gefunden: {e}")
            return False
    
    return True

def test_settings_tab_base_functionality():
    """Testet Basis-Funktionalität der Settings-Tabs"""
    print("⚙️ Teste Settings-Tab Basis-Funktionalität...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.settings.general_settings import GeneralSettingsTab
        
        # QApplication für GUI-Objekte
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Tab erstellen
        tab = GeneralSettingsTab()
        
        # Standard-Methoden prüfen
        expected_methods = ['load_settings', 'save_settings', 'reset_to_defaults']
        for method in expected_methods:
            if hasattr(tab, method):
                print(f"   ✅ Methode {method} vorhanden")
            else:
                print(f"   ❌ Methode {method} fehlt")
                return False
        
        # Tab cleanup
        tab.deleteLater()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Settings-Tab Test fehlgeschlagen: {e}")
        return False

def test_account_mapping_functionality():
    """Testet AccountMappingTab spezifische Funktionalität"""
    print("🏷️ Teste AccountMapping Funktionalität...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.settings.account_mapping import AccountMappingTab
        
        # QApplication für GUI-Objekte
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Tab erstellen
        tab = AccountMappingTab()
        
        # Spezifische Methoden prüfen
        mapping_methods = ['get_account_mappings', 'update_accounts_from_csv']
        for method in mapping_methods:
            if hasattr(tab, method):
                print(f"   ✅ Mapping-Methode {method} vorhanden")
            else:
                print(f"   ❌ Mapping-Methode {method} fehlt")
                return False
        
        # Basis-Mapping-Test
        test_accounts = ['1000', '2000', '3000']
        test_names = {'1000': 'Kasse', '2000': 'Bank', '3000': 'Forderungen'}
        
        # Update-Test (ohne Exception)
        tab.update_accounts_from_csv(test_accounts, test_names)
        print("   ✅ Account-Update funktioniert")
        
        # Mapping-Abruf-Test
        mappings = tab.get_account_mappings()
        if isinstance(mappings, dict):
            print("   ✅ Mapping-Abruf liefert Dictionary")
        else:
            print(f"   ❌ Mapping-Abruf liefert falschen Typ: {type(mappings)}")
            return False
        
        # Tab cleanup
        tab.deleteLater()
        
        return True
        
    except Exception as e:
        print(f"   ❌ AccountMapping Test fehlgeschlagen: {e}")
        return False

def test_super_group_mapping_functionality():
    """Testet SuperGroupMappingTab spezifische Funktionalität"""
    print("🔝 Teste SuperGroup Mapping Funktionalität...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.settings.super_group_mapping import SuperGroupMappingTab
        
        # QApplication für GUI-Objekte
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Tab erstellen
        tab = SuperGroupMappingTab()
        
        # Spezifische Methoden prüfen
        super_methods = ['get_super_group_mappings', 'update_groups_from_mappings']
        for method in super_methods:
            if hasattr(tab, method):
                print(f"   ✅ SuperGroup-Methode {method} vorhanden")
            else:
                print(f"   ❌ SuperGroup-Methode {method} fehlt")
                return False
        
        # BWA-Gruppen Update-Test
        test_bwa_groups = ['Personalkosten', 'Materialkosten', 'Verwaltungskosten']
        tab.update_groups_from_mappings(test_bwa_groups)
        print("   ✅ BWA-Gruppen Update funktioniert")
        
        # Super-Group-Mapping-Abruf-Test
        mappings = tab.get_super_group_mappings()
        if isinstance(mappings, dict):
            print("   ✅ SuperGroup-Mapping-Abruf liefert Dictionary")
        else:
            print(f"   ❌ SuperGroup-Mapping-Abruf liefert falschen Typ: {type(mappings)}")
            return False
        
        # Tab cleanup
        tab.deleteLater()
        
        return True
        
    except Exception as e:
        print(f"   ❌ SuperGroup Test fehlgeschlagen: {e}")
        return False

def test_settings_advanced():
    """Haupttest-Funktion für erweiterte Settings-Tests"""
    print("🛠️ Teste Erweiterte Settings-Funktionalität...")
    
    tests = [
        test_settings_imports,
        test_settings_tab_base_functionality,
        test_account_mapping_functionality,
        test_super_group_mapping_functionality
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
    print(f"\n📊 Erweiterte Settings-Tests: {passed}/{total} erfolgreich")
    
    return failed == 0

if __name__ == "__main__":
    success = test_settings_advanced()
    sys.exit(0 if success else 1)
