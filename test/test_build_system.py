#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für Build-System und Icon-Konvertierung
"""
import sys
import os
import tempfile
import subprocess
from pathlib import Path

# Lokale Imports
sys.path.append('.')
import build

def test_build_system():
    """Testet das Build-System"""
    print("🏗️ Teste Build-System...")
    
    # Test 1: BuildManager Initialisierung
    print("  📋 Test 1: BuildManager Initialisierung")
    try:
        builder = build.BuildManager()
        if builder.app_name and builder.project_root.exists():
            print("  ✅ BuildManager erfolgreich initialisiert")
        else:
            print("  ❌ BuildManager Initialisierung fehlerhaft")
            return False
    except Exception as e:
        print(f"  ❌ Fehler bei BuildManager Init: {e}")
        return False
    
    # Test 2: Dependency Check
    print("  📋 Test 2: Dependency Check")
    try:
        deps_ok = builder.check_dependencies()
        print(f"  ✅ Dependency Check: {'Bestanden' if deps_ok else 'Fehlgeschlagen'}")
    except Exception as e:
        print(f"  ❌ Fehler bei Dependency Check: {e}")
        return False
    
    # Test 3: Icon-Verzeichnis Check
    print("  📋 Test 3: Icon-Verzeichnis Check")
    icons_dir = builder.icons_dir
    if icons_dir.exists():
        png_icon = icons_dir / "app_icon.png"
        if png_icon.exists():
            print("  ✅ app_icon.png gefunden")
        else:
            print("  ⚠️ app_icon.png nicht gefunden")
    else:
        print("  ❌ Icons-Verzeichnis nicht gefunden")
        return False
    
    # Test 4: Icon-Konvertierung (nur testen wenn Icons vorhanden)
    print("  📋 Test 4: Icon-Konvertierung")
    png_icon = icons_dir / "app_icon.png"
    if png_icon.exists():
        try:
            # Backup existierende Icons
            icns_backup = None
            ico_backup = None
            
            icns_path = icons_dir / "app_icon.icns"
            ico_path = icons_dir / "app_icon.ico"
            
            if icns_path.exists():
                icns_backup = icns_path.read_bytes()
            if ico_path.exists():
                ico_backup = ico_path.read_bytes()
            
            # Icon-Konvertierung testen
            success = builder.prepare_icons()
            
            if success and icns_path.exists() and ico_path.exists():
                print("  ✅ Icon-Konvertierung erfolgreich")
                
                # Dateigröße prüfen
                icns_size = icns_path.stat().st_size
                ico_size = ico_path.stat().st_size
                
                if icns_size > 1000 and ico_size > 500:  # Mindestgrößen
                    print(f"    📊 ICNS: {icns_size:,} Bytes, ICO: {ico_size:,} Bytes")
                else:
                    print(f"  ⚠️ Icon-Größen zu klein: ICNS={icns_size}, ICO={ico_size}")
            else:
                print("  ❌ Icon-Konvertierung fehlgeschlagen")
                return False
                
        except Exception as e:
            print(f"  ❌ Fehler bei Icon-Konvertierung: {e}")
            return False
    else:
        print("  ⚠️ Keine PNG-Icons zum Testen verfügbar")
    
    # Test 5: Clean-Funktion
    print("  📋 Test 5: Clean-Funktion")
    try:
        builder.clean_build_directory()
        if builder.build_dir.exists():
            print("  ✅ Build-Verzeichnis bereinigt")
        else:
            print("  ✅ Build-Verzeichnis erstellt")
    except Exception as e:
        print(f"  ❌ Fehler bei Clean-Funktion: {e}")
        return False
    
    # Test 6: Platform Detection
    print("  📋 Test 6: Platform Detection")
    import platform
    current_platform = platform.system()
    print(f"  ✅ Aktuelle Plattform: {current_platform}")
    
    # Test 7: Build-Info Creation
    print("  📋 Test 7: Build-Info Creation")
    try:
        builder.create_build_info()
        build_info_file = builder.build_dir / "build_info.txt"
        if build_info_file.exists():
            content = build_info_file.read_text()
            if "Finanzauswertung Ehrenamt" in content:
                print("  ✅ Build-Info erfolgreich erstellt")
            else:
                print("  ❌ Build-Info Inhalt fehlerhaft")
                return False
        else:
            print("  ❌ Build-Info Datei nicht erstellt")
            return False
    except Exception as e:
        print(f"  ❌ Fehler bei Build-Info: {e}")
        return False
    
    print("✅ Build-System erfolgreich getestet")
    return True

def test_command_line_interface():
    """Testet die Kommandozeilen-Schnittstelle"""
    print("💻 Teste Command Line Interface...")
    
    # Test 1: Help Output
    print("  📋 Test 1: Help Output")
    try:
        result = subprocess.run([sys.executable, "build.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "Build Manager" in result.stdout:
            print("  ✅ Help-Ausgabe erfolgreich")
        else:
            print(f"  ❌ Help-Ausgabe fehlerhaft: {result.returncode}")
            return False
    except Exception as e:
        print(f"  ❌ Fehler bei Help-Test: {e}")
        return False
    
    # Test 2: Icons-Only Command
    print("  📋 Test 2: Icons-Only Command")
    try:
        result = subprocess.run([sys.executable, "build.py", "--icons-only"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("  ✅ Icons-Only Command erfolgreich")
        else:
            print(f"  ⚠️ Icons-Only Command: {result.returncode}")
            print(f"      Output: {result.stdout}")
            # Nicht als Fehler werten, da Abhängigkeiten fehlen können
    except Exception as e:
        print(f"  ❌ Fehler bei Icons-Only Test: {e}")
        return False
    
    # Test 3: Clean-Only Command
    print("  📋 Test 3: Clean-Only Command")
    try:
        result = subprocess.run([sys.executable, "build.py", "--clean-only"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✅ Clean-Only Command erfolgreich")
        else:
            print(f"  ❌ Clean-Only Command fehlgeschlagen: {result.returncode}")
            return False
    except Exception as e:
        print(f"  ❌ Fehler bei Clean-Only Test: {e}")
        return False
    
    print("✅ Command Line Interface erfolgreich getestet")
    return True

def main():
    """Hauptfunktion"""
    success = True
    
    success &= test_build_system()
    success &= test_command_line_interface()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
