#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Übersicht für Finanzauswertung Ehrenamt
Zeigt verfügbare Tests und deren Status an
"""

import os
import sys
from pathlib import Path

def show_test_overview():
    """Zeigt eine Übersicht aller verfügbaren Tests"""
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    print("📋 Test-Übersicht - Finanzauswertung Ehrenamt")
    print("=" * 60)
    
    # Alle Test-Dateien finden
    test_files = list(test_dir.glob("test_*.py"))
    test_files.sort()
    
    # Problematische Tests (werden nicht automatisch ausgeführt)
    problematic_tests = {
        'test_application_startup.py': 'GUI-Fenster',
        'test_dialogs.py': 'GUI-Dialoge',
        'test_widgets.py': 'GUI-Widgets', 
        'test_color_settings_ui.py': 'GUI-Einstellungen',
        'test_icon_display.py': 'GUI-Icon-Display',
        'test_footer_display.py': 'GUI-Footer-Display',
        'test_cover_page_demo.py': 'Demo mit Nutzerinteraktion',
        'test_csv_processor_edge_cases.py': 'Kann GUI erstellen',
        'test_improved_table.py': 'Potentiell GUI-blockierend',
        'test_account_page.py': 'Potentiell GUI-blockierend',
        'test_logo.py': 'Potentiell GUI-blockierend',
        'test_setup.py': 'Potentiell GUI-blockierend',
        'test_manager.py': 'Utility-Script',
        'fast_test_runner.py': 'Test-Runner',
        'ci_test_runner.py': 'CI-Test-Runner',
        'demo_obergruppen.py': 'Demo-Script',
        'run_all_tests.py': 'Test-Runner selbst'
    }
    
    # Automatische Tests
    automatic_tests = []
    manual_tests = []
    
    for test_file in test_files:
        if test_file.name in problematic_tests:
            manual_tests.append((test_file.name, problematic_tests[test_file.name]))
        else:
            automatic_tests.append(test_file.name)
    
    print(f"\n✅ Automatische Tests ({len(automatic_tests)}):")
    print("   (Werden von run_all_tests.py und clean_build.py ausgeführt)")
    for i, test in enumerate(automatic_tests, 1):
        print(f"   {i:2d}. {test}")
    
    print(f"\n⚠️  Manuelle Tests ({len(manual_tests)}):")
    print("   (Benötigen Nutzerinteraktion oder können GUI erstellen)")
    for i, (test, reason) in enumerate(manual_tests, 1):
        print(f"   {i:2d}. {test} - {reason}")
    
    print(f"\n📊 Gesamt: {len(test_files)} Tests")
    print(f"   • {len(automatic_tests)} automatisch")
    print(f"   • {len(manual_tests)} manuell")
    
    print(f"\n🚀 Ausführung:")
    print(f"   Alle automatischen Tests: python test/run_all_tests.py")
    print(f"   Einzelner Test: python test/test_<name>.py")
    print(f"   Build mit Tests: python clear_build.py")

if __name__ == "__main__":
    show_test_overview()
