#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Manager für Finanzauswertung Ehrenamt
Unterstützt Windows und macOS App-Builds
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# Icon-Konvertierung
try:
    from icnsutil import IcnsFile
    ICNS_AVAILABLE = True
except ImportError:
    ICNS_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class BuildManager:
    """Verwaltet den Build-Prozess für verschiedene Plattformen"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.app_name = "Finanzauswertung Ehrenamt"
        self.app_version = "1.0.0"
        self.icons_dir = self.project_root / "resources" / "icons"
        
    def prepare_icons(self):
        """Konvertiert PNG-Icon zu .icns (macOS) und .ico (Windows) Formaten"""
        print("🎨 Bereite Icons vor...")
        
        png_icon = self.icons_dir / "app_icon.png"
        if not png_icon.exists():
            print("❌ Basis-Icon app_icon.png nicht gefunden!")
            return False
        
        success = True
        
        # .icns für macOS erstellen
        if self._create_icns_icon(png_icon):
            print("✅ macOS .icns Icon erstellt")
        else:
            print("⚠️ macOS .icns Icon konnte nicht erstellt werden")
            success = False
            
        # .ico für Windows erstellen  
        if self._create_ico_icon(png_icon):
            print("✅ Windows .ico Icon erstellt")
        else:
            print("⚠️ Windows .ico Icon konnte nicht erstellt werden")
            success = False
            
        return success
    
    def _create_icns_icon(self, png_path: Path) -> bool:
        """Erstellt .icns Icon für macOS aus PNG"""
        if not ICNS_AVAILABLE:
            print("⚠️ icnsutil nicht verfügbar - .icns Icon wird übersprungen")
            return False
            
        try:
            icns_path = self.icons_dir / "app_icon.icns"
            
            # Einfacherer Ansatz - direkt von PNG zu ICNS mit icnsutil
            import subprocess
            
            # icnsutil command line tool verwenden
            cmd = [
                sys.executable, "-m", "icnsutil", "compose",
                str(icns_path), str(png_path), "-f"  # -f für force overwrite
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and icns_path.exists():
                return True
            else:
                print(f"icnsutil Fehler: {result.stderr}")
                
                # Fallback: Manuell mit PIL und icnsutil library
                with Image.open(png_path) as img:
                    # Bild muss quadratisch sein
                    if img.width != img.height:
                        size = min(img.width, img.height)
                        img = img.crop((0, 0, size, size))
                    
                    # Standardgröße für macOS: 1024x1024
                    if img.size != (1024, 1024):
                        img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
                    
                    # Als temporäres PNG speichern
                    temp_png = self.icons_dir / "temp_1024.png"
                    img.save(temp_png, 'PNG')
                    
                    # ICNS erstellen
                    icns = IcnsFile()
                    icns.add_media(file=str(temp_png))
                    icns.write(str(icns_path))
                    
                    # Temp-Datei löschen
                    temp_png.unlink(missing_ok=True)
                    
                return icns_path.exists()
            
        except Exception as e:
            print(f"Fehler beim Erstellen der .icns Datei: {e}")
            return False
    
    def _create_ico_icon(self, png_path: Path) -> bool:
        """Erstellt .ico Icon für Windows aus PNG"""
        if not PIL_AVAILABLE:
            print("⚠️ Pillow nicht verfügbar - .ico Icon wird übersprungen")
            return False
            
        try:
            ico_path = self.icons_dir / "app_icon.ico"
            
            with Image.open(png_path) as img:
                # ICO unterstützt mehrere Größen in einer Datei
                ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                icon_images = []
                
                for size in ico_sizes:
                    resized = img.resize(size, Image.Resampling.LANCZOS)
                    icon_images.append(resized)
                
                # ICO-Datei mit allen Größen speichern
                icon_images[0].save(
                    ico_path,
                    format='ICO',
                    sizes=ico_sizes,
                    append_images=icon_images[1:]
                )
                
            return ico_path.exists()
            
        except Exception as e:
            print(f"Fehler beim Erstellen der .ico Datei: {e}")
            return False
        
    def clean_build_directory(self):
        """Löscht alte Build-Dateien"""
        print("🧹 Lösche alte Build-Dateien...")
        
        paths_to_clean = [
            self.build_dir,
            'dist',
            '__pycache__',
            '*.spec'
        ]
        
        for path in paths_to_clean:
            if isinstance(path, str):
                if path.endswith('*'):
                    # Glob pattern
                    import glob
                    for file in glob.glob(path):
                        try:
                            if os.path.isfile(file):
                                os.remove(file)
                            elif os.path.isdir(file):
                                shutil.rmtree(file)
                        except Exception as e:
                            print(f"Warnung: Konnte {file} nicht löschen: {e}")
                else:
                    path = Path(path)
            
            if path.exists():
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path)
                    print(f"✅ {path} gelöscht")
                except Exception as e:
                    print(f"Warnung: Konnte {path} nicht löschen: {e}")
        
        # Build-Verzeichnis erstellen
        self.build_dir.mkdir(exist_ok=True)
    
    def check_dependencies(self):
        """Prüft ob alle Build-Abhängigkeiten installiert sind"""
        print("🔍 Prüfe Build-Abhängigkeiten...")
        
        try:
            import PyInstaller
            print(f"✅ PyInstaller {PyInstaller.__version__} gefunden")
        except ImportError:
            print("❌ PyInstaller nicht gefunden")
            print("Installiere mit: pip install pyinstaller")
            return False
        
        # Icon-Konvertierungs-Bibliotheken prüfen
        if ICNS_AVAILABLE:
            print("✅ icnsutil für macOS Icons verfügbar")
        else:
            print("⚠️ icnsutil nicht verfügbar - macOS .icns Icons werden übersprungen")
            print("Installiere mit: pip install icnsutil")
            
        if PIL_AVAILABLE:
            print("✅ Pillow für Windows Icons verfügbar")
        else:
            print("⚠️ Pillow nicht verfügbar - Windows .ico Icons werden übersprungen")
            print("Installiere mit: pip install Pillow")
        
        # Andere wichtige Abhängigkeiten prüfen
        required_modules = [
            'PySide6', 'pandas', 'openpyxl', 'chardet', 'odf', 'fitz', 'PIL'
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module} verfügbar")
            except ImportError:
                print(f"❌ {module} nicht gefunden")
                missing_modules.append(module)
        
        if missing_modules:
            print(f"\\nFehlende Module: {', '.join(missing_modules)}")
            print("Installiere mit: pip install -r requirements.txt")
            return False
        
        return True
    
    def build_windows_app(self):
        """Baut eine Windows .exe-Datei"""
        print("🏗️ Baue Windows App...")
        
        if platform.system() != "Windows":
            print("⚠️ Windows-Build nur auf Windows-Systemen möglich")
            print("💡 Tipp: Verwende GitHub Actions für automatische Windows-Builds")
            print("   Siehe: .github/workflows/build.yml")
            return False
        
        # Icons vorbereiten
        self.prepare_icons()
        
        # Icon-Pfad bestimmen
        icon_path = self.icons_dir / "app_icon.ico"
        if not icon_path.exists():
            icon_path = self.icons_dir / "app_icon.png"  # Fallback
        
        # PyInstaller Kommando für Windows
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", self.app_name.replace(" ", "_"),
            "--distpath", str(self.build_dir),
            "--workpath", "temp_build",
            "--specpath", "temp_build",
            "--icon", str(icon_path),
            "--add-data", f"{self.project_root / 'resources'};resources",
            "--add-data", f"{self.project_root / 'src'};src",
            "--hidden-import", "PySide6",
            "--hidden-import", "pandas",
            "--hidden-import", "openpyxl",
            "--hidden-import", "chardet",
            "--hidden-import", "odf",
            "--hidden-import", "fitz",
            "--hidden-import", "PIL",
            "main.py"
        ]
        
        print(f"📋 Verwende Icon: {icon_path}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Windows App erfolgreich gebaut")
            
            # Temp-Verzeichnisse aufräumen
            for temp_dir in ["temp_build", "dist"]:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Windows Build fehlgeschlagen: {e}")
            print(f"Fehler-Output: {e.stderr}")
            return False
    
    def build_macos_app(self):
        """Baut eine macOS .app-Datei"""
        print("🏗️ Baue macOS App...")
        
        if platform.system() != "Darwin":
            print("⚠️ macOS-Build nur auf macOS-Systemen möglich")
            print("💡 Tipp: Verwende GitHub Actions für automatische macOS-Builds")
            print("   Siehe: .github/workflows/build.yml")
            return False
        
        # Icons vorbereiten
        self.prepare_icons()
        
        # PyInstaller Kommando für macOS - ohne onefile für macOS .app kompatibilität
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onedir",  # Geändert zu onedir für macOS App Bundle
            "--windowed",
            "--name", self.app_name.replace(" ", "_"),
            "--distpath", str(self.build_dir),
            "--workpath", "temp_build",
            "--specpath", "temp_build",
            "--add-data", f"{self.project_root / 'resources'}:resources",
            "--add-data", f"{self.project_root / 'src'}:src",
            "--hidden-import", "PySide6",
            "--hidden-import", "pandas",
            "--hidden-import", "openpyxl", 
            "--hidden-import", "chardet",
            "--hidden-import", "odf",
            "--hidden-import", "fitz",
            "--hidden-import", "PIL",
            "main.py"
        ]
        
        # Icon hinzufügen - Priorität: .icns > .png
        icon_paths = [
            self.icons_dir / "app_icon.icns",
            self.icons_dir / "app_icon.png"
        ]
        
        for icon_path in icon_paths:
            if icon_path.exists():
                cmd.extend(["--icon", str(icon_path)])
                print(f"📋 Verwende Icon: {icon_path}")
                break
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ macOS App erfolgreich gebaut")
            
            # Temp-Verzeichnisse aufräumen
            for temp_dir in ["temp_build", "dist"]:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ macOS Build fehlgeschlagen: {e}")
            print(f"Fehler-Output: {e.stderr}")
            return False
    
    def build_linux_app(self):
        """Baut eine Linux-Executable"""
        print("🏗️ Baue Linux App...")
        
        if platform.system() != "Linux":
            print("⚠️ Linux-Build nur auf Linux-Systemen möglich")
            print("💡 Tipp: Verwende GitHub Actions für automatische Linux-Builds")
            print("   Siehe: .github/workflows/build.yml")
            return False
        
        # Icons vorbereiten
        self.prepare_icons()
        
        # Icon-Pfad bestimmen (PNG für Linux)
        icon_path = self.icons_dir / "app_icon.png"
        
        # PyInstaller Kommando für Linux
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", self.app_name.replace(" ", "_"),
            "--distpath", str(self.build_dir),
            "--workpath", "temp_build",
            "--specpath", "temp_build",
            "--add-data", f"{self.project_root / 'resources'}:resources",
            "--add-data", f"{self.project_root / 'src'}:src",
            "--hidden-import", "PySide6",
            "--hidden-import", "pandas",
            "--hidden-import", "openpyxl",
            "--hidden-import", "chardet",
            "--hidden-import", "odf",
            "--hidden-import", "fitz",
            "--hidden-import", "PIL",
            "main.py"
        ]
        
        # Icon nur hinzufügen wenn vorhanden
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])
            print(f"📋 Verwende Icon: {icon_path}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Linux App erfolgreich gebaut")
            
            # Temp-Verzeichnisse aufräumen
            for temp_dir in ["temp_build", "dist"]:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Linux Build fehlgeschlagen: {e}")
            print(f"Fehler-Output: {e.stderr}")
            return False
    
    def create_build_info(self):
        """Erstellt Build-Informationen"""
        info_file = self.build_dir / "build_info.txt"
        
        with open(info_file, "w", encoding="utf-8") as f:
            f.write(f"Finanzauswertung Ehrenamt\\n")
            f.write(f"Version: {self.app_version}\\n")
            f.write(f"Build-Datum: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\\n")
            f.write(f"Plattform: {platform.system()} {platform.release()}\\n")
            f.write(f"Python: {sys.version}\\n")
    
    def build_for_current_platform(self):
        """Baut die App für die aktuelle Plattform"""
        current_platform = platform.system()
        
        if current_platform == "Windows":
            return self.build_windows_app()
        elif current_platform == "Darwin":
            return self.build_macos_app()
        elif current_platform == "Linux":
            return self.build_linux_app()
        else:
            print(f"❌ Plattform {current_platform} wird nicht unterstützt")
            print("💡 Unterstützte Plattformen: Windows, macOS (Darwin), Linux")
            return False
    
    def build(self, platform_name=None):
        """Startet den Build-Prozess"""
        print(f"🚀 Finanzauswertung Ehrenamt - Build Manager")
        print(f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print(f"Aktuelle Plattform: {platform.system()}")
        
        if not self.check_dependencies():
            return False
        
        self.clean_build_directory()
        
        if platform_name:
            if platform_name.lower() == "windows":
                success = self.build_windows_app()
            elif platform_name.lower() == "macos":
                success = self.build_macos_app()
            elif platform_name.lower() == "linux":
                success = self.build_linux_app()
            else:
                print(f"❌ Unbekannte Plattform: {platform_name}")
                print("💡 Verfügbare Plattformen: windows, macos, linux")
                return False
        else:
            success = self.build_for_current_platform()
        
        if success:
            self.create_build_info()
            print(f"\\n🎉 Build erfolgreich abgeschlossen!")
            print(f"📁 Build-Verzeichnis: {self.build_dir}")
            
            # Zeige verfügbare Dateien
            build_files = list(self.build_dir.glob("*"))
            if build_files:
                print(f"\\n📱 Gebaute Dateien:")
                for file in build_files:
                    print(f"  • {file.name}")
        
        return success

def main():
    """Hauptfunktion für Kommandozeilenbenutzung"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Manager für Finanzauswertung Ehrenamt")
    parser.add_argument("--platform", choices=["windows", "macos", "linux"], 
                       help="Ziel-Plattform (standard: aktuelle Plattform)")
    parser.add_argument("--clean-only", action="store_true",
                       help="Nur Build-Verzeichnis säubern")
    parser.add_argument("--icons-only", action="store_true",
                       help="Nur Icons aus PNG konvertieren (.icns und .ico)")
    
    args = parser.parse_args()
    
    builder = BuildManager()
    
    if args.clean_only:
        builder.clean_build_directory()
        print("✅ Build-Verzeichnis gesäubert")
        return 0
        
    if args.icons_only:
        success = builder.prepare_icons()
        if success:
            print("✅ Icons erfolgreich erstellt")
            return 0
        else:
            print("❌ Icon-Erstellung fehlgeschlagen")
            return 1
    
    success = builder.build(args.platform)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
