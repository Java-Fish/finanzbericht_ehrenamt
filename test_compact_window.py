#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für das kompaktere Hauptfenster
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication
from src.main_window import MainWindow

def test_compact_main_window():
    """Testet die neue kompakte Hauptfenster-Größe"""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    print("=== Kompaktes Hauptfenster Test ===")
    
    # Hauptfenster erstellen
    main_window = MainWindow()
    
    # Aktuelle Größen überprüfen
    current_size = main_window.size()
    min_size = main_window.minimumSize()
    file_drop_area = main_window.file_drop_area
    file_drop_min_size = file_drop_area.minimumSize()
    file_drop_max_height = file_drop_area.maximumHeight()
    
    print(f"Hauptfenster:")
    print(f"  Standard-Größe: {current_size.width()}x{current_size.height()}")
    print(f"  Mindest-Größe: {min_size.width()}x{min_size.height()}")
    
    print(f"\nFileDropArea:")
    print(f"  Mindest-Größe: {file_drop_min_size.width()}x{file_drop_min_size.height()}")
    print(f"  Max-Höhe: {file_drop_max_height}")
    
    # Icon-Label überprüfen
    icon_label = file_drop_area.icon_label
    icon_size = icon_label.minimumSize()
    icon_max_size = icon_label.maximumSize()
    
    print(f"\nIcon-Label:")
    print(f"  Größe: {icon_size.width()}x{icon_size.height()}")
    print(f"  Max-Größe: {icon_max_size.width()}x{icon_max_size.height()}")
    
    # Button überprüfen
    select_button = file_drop_area.select_button
    button_height = select_button.minimumHeight()
    button_max_width = select_button.maximumWidth()
    
    print(f"\nButton:")
    print(f"  Min-Höhe: {button_height}")
    print(f"  Max-Breite: {button_max_width}")
    
    # Bewertung
    print(f"\n=== Bewertung ===")
    
    # Erwartete Werte
    expected_window_size = (750, 500)
    expected_min_size = (600, 400)
    expected_file_drop_min = (350, 250)
    expected_icon_size = (80, 80)
    
    window_size_ok = (current_size.width() == expected_window_size[0] and 
                     current_size.height() == expected_window_size[1])
    min_size_ok = (min_size.width() == expected_min_size[0] and 
                  min_size.height() == expected_min_size[1])
    file_drop_ok = (file_drop_min_size.width() == expected_file_drop_min[0] and 
                   file_drop_min_size.height() == expected_file_drop_min[1])
    icon_size_ok = (icon_size.width() == expected_icon_size[0] and 
                   icon_size.height() == expected_icon_size[1])
    
    print(f"Standard-Fenstergröße (750x500): {'✅' if window_size_ok else '❌'}")
    print(f"Mindest-Fenstergröße (600x400): {'✅' if min_size_ok else '❌'}")
    print(f"FileDropArea Mindestgröße (350x250): {'✅' if file_drop_ok else '❌'}")
    print(f"Icon-Größe (80x80): {'✅' if icon_size_ok else '❌'}")
    print(f"FileDropArea Max-Höhe gesetzt: {'✅' if file_drop_max_height > 0 else '❌'}")
    print(f"Button Max-Breite gesetzt: {'✅' if button_max_width > 0 else '❌'}")
    
    all_optimizations_ok = (window_size_ok and min_size_ok and file_drop_ok and 
                           icon_size_ok and file_drop_max_height > 0 and button_max_width > 0)
    
    if all_optimizations_ok:
        print("\n✅ KOMPAKTES DESIGN ERFOLGREICH IMPLEMENTIERT!")
        print("   📏 Fenstergröße von 1000x700 auf 750x500 reduziert")
        print("   📐 Mindestgröße von 800x600 auf 600x400 reduziert") 
        print("   📦 FileDropArea kompakter gemacht")
        print("   🎯 Icon-Größe von 100x100 auf 80x80 reduziert")
        print("   🎚️ Maximale Höhen und Breiten gesetzt")
    else:
        print("\n❌ NICHT ALLE OPTIMIERUNGEN KORREKT!")
    
    print("\n=== Test abgeschlossen ===")

if __name__ == "__main__":
    test_compact_main_window()
