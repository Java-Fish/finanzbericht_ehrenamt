#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup-Script für die Finanzauswertung Ehrenamt Anwendung
"""

import subprocess
import sys
import os


def check_python_version():
    """Prüft ob Python 3.13+ installiert ist"""
    if sys.version_info < (3, 13):
        print("Fehler: Python 3.13 oder höher ist erforderlich.")
        print(f"Aktuelle Version: {sys.version}")
        return False
    return True


def install_requirements():
    """Installiert die erforderlichen Python-Pakete"""
    try:
        print("Installiere erforderliche Pakete...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Alle Pakete erfolgreich installiert!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler bei der Installation: {e}")
        return False


def create_desktop_entry_linux():
    """Erstellt einen Desktop-Eintrag für Linux"""
    desktop_entry = f"""[Desktop Entry]
Name=Finanzauswertung Ehrenamt
Comment=Finanzauswertung für ehrenamtliche Organisationen
Exec={sys.executable} {os.path.abspath('main.py')}
Icon={os.path.abspath('resources/icons/app_icon.png')}
Terminal=false
Type=Application
Categories=Office;Finance;
StartupWMClass=finanzauswertung-ehrenamt
"""
    
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(desktop_dir, exist_ok=True)
    
    desktop_file = os.path.join(desktop_dir, "finanzauswertung-ehrenamt.desktop")
    
    try:
        with open(desktop_file, 'w') as f:
            f.write(desktop_entry)
        
        # Desktop-Datei ausführbar machen
        subprocess.run(["chmod", "+x", desktop_file])
        print(f"✅ Desktop-Eintrag erstellt: {desktop_file}")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Desktop-Eintrags: {e}")
        return False


def main():
    """Hauptfunktion des Setup-Scripts"""
    print("=" * 50)
    print("  Finanzauswertung Ehrenamt - Setup")
    print("=" * 50)
    
    # Python-Version prüfen
    if not check_python_version():
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} gefunden")
    
    # Abhängigkeiten installieren
    if not install_requirements():
        sys.exit(1)
    
    # Betriebssystem-spezifische Einrichtung
    if sys.platform.startswith('linux'):
        create_desktop_entry_linux()
    
    print("\n" + "=" * 50)
    print("✅ Setup erfolgreich abgeschlossen!")
    print("\nSie können die Anwendung jetzt starten:")
    print("  - Direkt: python main.py")
    print("  - Über Script: ./start_app.sh (macOS/Linux) oder start_app.bat (Windows)")
    
    if sys.platform.startswith('linux'):
        print("  - Über Anwendungsmenü: 'Finanzauswertung Ehrenamt'")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
