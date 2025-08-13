#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für responsives Hauptfenster-Layout
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QRect
from src.main_window import MainWindow

def test_responsive_layout():
    """Testet das responsive Layout bei verschiedenen Fenstergrößen"""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    print("=== Responsives Layout Test ===")
    
    # Hauptfenster erstellen
    main_window = MainWindow()
    
    # Test verschiedene Fenstergrößen
    test_sizes = [
        (600, 400),   # Minimum
        (750, 500),   # Standard
        (1000, 700),  # Groß
        (1200, 800)   # Sehr groß
    ]
    
    print("\nTeste verschiedene Fenstergrößen:")
    
    for width, height in test_sizes:
        # Fenstergröße setzen
        main_window.resize(width, height)
        
        # Aktualisieren lassen
        app.processEvents()
        
        # Drop-Area-Größe überprüfen
        drop_area = main_window.file_drop_area
        drop_size = drop_area.size()
        
        # Verhältnis berechnen
        width_ratio = drop_size.width() / width
        height_ratio = drop_size.height() / height
        
        print(f"  Fenster {width}x{height}:")
        print(f"    Drop-Area: {drop_size.width()}x{drop_size.height()}")
        print(f"    Verhältnis: {width_ratio:.2f} x {height_ratio:.2f}")
        
        # Überprüfen, ob sich die Drop-Area vernünftig anpasst (jetzt vollflächig)
        reasonable_width = 0.8 <= width_ratio <= 1.0
        reasonable_height = 0.8 <= height_ratio <= 1.0
        
        print(f"    Angemessene Größe: {'✅' if reasonable_width and reasonable_height else '❌'}")
    
    # Test Mindestgrößen
    print(f"\nMindestgrößen-Test:")
    
    # Hauptfenster Mindestgröße
    min_size = main_window.minimumSize()
    print(f"  Hauptfenster Mindestgröße: {min_size.width()}x{min_size.height()}")
    
    # Drop-Area Mindestgröße
    drop_area = main_window.file_drop_area
    drop_min_size = drop_area.minimumSize()
    print(f"  Drop-Area Mindestgröße: {drop_min_size.width()}x{drop_min_size.height()}")
    
    # Layout-Eigenschaften überprüfen
    print(f"\nLayout-Eigenschaften:")
    
    # Central Widget Layout
    central_widget = main_window.centralWidget()
    layout = central_widget.layout()
    
    margins = layout.contentsMargins()
    spacing = layout.spacing()
    
    print(f"  Layout-Margins: {margins.left()}, {margins.top()}, {margins.right()}, {margins.bottom()}")
    print(f"  Layout-Spacing: {spacing}")
    
    # Stretch-Faktoren überprüfen (sollten jetzt 0 sein, da vollflächig)
    stretch_count = 0
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.spacerItem():
            stretch_count += 1
    
    print(f"  Stretch-Bereiche: {stretch_count} (erwartet: 0 für vollflächig)")
    
    # Button-Styling überprüfen
    button = drop_area.select_button
    button_style = button.styleSheet()
    has_min_width = "min-width" in button_style
    has_max_width = "max-width" in button_style
    
    print(f"  Button min-width gesetzt: {'✅' if has_min_width else '❌'}")
    print(f"  Button max-width gesetzt: {'✅' if has_max_width else '❌'}")
    
    # Gesamtbewertung
    print(f"\n=== Bewertung ===")
    
    layout_features = [
        min_size.width() == 600 and min_size.height() == 400,  # Korrekte Mindestgröße
        drop_min_size.width() == 350 and drop_min_size.height() == 250,  # Drop-Area Mindestgröße
        stretch_count == 0,  # Vollflächig (keine Stretch-Bereiche)
        margins.left() == 10 and margins.right() == 10,  # Reduzierte Margins
        spacing == 0,  # Kein Layout-Spacing für vollflächig
        has_min_width and has_max_width  # Button-Styling
    ]
    
    feature_names = [
        "Hauptfenster-Mindestgröße (600x400)",
        "Drop-Area-Mindestgröße (350x250)", 
        "Vollflächiges Design (0 Stretch-Bereiche)",
        "Reduzierte Margins (10px)",
        "Kein Layout-Spacing (0px)",
        "Button Min/Max-Width"
    ]
    
    for i, (feature, name) in enumerate(zip(layout_features, feature_names)):
        print(f"  {name}: {'✅' if feature else '❌'}")
    
    all_features_ok = all(layout_features)
    
    if all_features_ok:
        print("\n✅ VOLLFLÄCHIGES LAYOUT ERFOLGREICH!")
        print("   📏 Kompakte Standardgröße (750x500)")
        print("   📐 Angemessene Mindestgröße (600x400)")
        print("   🎯 Drop-Area füllt gesamten verfügbaren Platz")
        print("   🎨 Verbessertes Button-Styling")
        print("   📱 Vollflächige Anpassung an Fenstergröße")
        print("   🚫 Kein grauer Hintergrund sichtbar")
    else:
        print("\n❌ LAYOUT-PROBLEME GEFUNDEN!")
    
    print("\n=== Test abgeschlossen ===")

if __name__ == "__main__":
    test_responsive_layout()
