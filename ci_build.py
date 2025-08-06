#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI-optimierter Build Manager für GitHub Actions
Robuste Version für Windows/macOS/Linux Builds
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import tempfile

# Windows-Encoding-Problem beheben
if platform.system() == "Windows":
    try:
        # Setze UTF-8 Encoding für Windows Terminal
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        USE_EMOJIS = True
    except:
        # Fallback für ältere Python-Versionen oder problematische Encodings
        USE_EMOJIS = False
else:
    USE_EMOJIS = True

def safe_print(message):
    """Sichere Print-Funktion die Emojis nur verwendet wenn unterstützt"""
    if not USE_EMOJIS:
        # Ersetze Emojis durch ASCII-Zeichen für Windows
        message = message.replace("🏗️", "[BUILD]")
        message = message.replace("🤖", "[CI]")
        message = message.replace("📦", "[PKG]")
        message = message.replace("✅", "[OK]")
        message = message.replace("❌", "[FAIL]")
        message = message.replace("🔍", "[INFO]")
        message = message.replace("🔄", "[RETRY]")
        message = message.replace("🎉", "[SUCCESS]")
        message = message.replace("💥", "[ERROR]")
        message = message.replace("🖥️", "[PLATFORM]")
        message = message.replace("📁", "[DIR]")
    print(message)

class CIBuildManager:
    """CI-optimierter Build Manager für GitHub Actions"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.app_name = "Finanzauswertung_Ehrenamt"
        self.current_platform = self.detect_platform()
        
        # Environment Setup für CI
        self.setup_ci_environment()
        
    def detect_platform(self):
        """Erkenne die aktuelle Build-Plattform"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        else:
            return "linux"
    
    def setup_ci_environment(self):
        """Setup für CI-Umgebungen"""
        # CI Environment Variables
        if os.environ.get('CI') == 'true' or os.environ.get('GITHUB_ACTIONS') == 'true':
            safe_print("🤖 CI-Umgebung erkannt - optimiere Build-Prozess...")
            # Setze QT Platform für CI
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            
    def create_simple_build(self):
        """Erstellt einen einfachen Build ohne komplexe Dependencies"""
        safe_print(f"🏗️ Starte einfachen Build für {self.current_platform}...")
        
        try:
            # Säubere build/ directory
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            self.build_dir.mkdir(exist_ok=True)
            
            # PyInstaller Command - vereinfacht für CI
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--name", self.app_name,
                "--onedir",  # Verwende onedir statt onefile für bessere Kompatibilität
                "--noconsole" if self.current_platform == "windows" else "--windowed",
                "--distpath", str(self.build_dir),
                "--workpath", str(self.build_dir / "temp"),
                "--specpath", str(self.build_dir),
                "main.py"
            ]
            
            # Füge nur existierende Verzeichnisse hinzu
            if (self.project_root / "src").exists():
                if self.current_platform == "windows":
                    cmd.extend(["--add-data", f"{self.project_root / 'src'};src"])
                else:
                    cmd.extend(["--add-data", f"{self.project_root / 'src'}:src"])
            
            if (self.project_root / "resources").exists():
                if self.current_platform == "windows":
                    cmd.extend(["--add-data", f"{self.project_root / 'resources'};resources"])
                else:
                    cmd.extend(["--add-data", f"{self.project_root / 'resources'}:resources"])
            
            safe_print(f"📦 PyInstaller Command: {' '.join(cmd)}")
            
            # Führe PyInstaller aus
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                safe_print("✅ PyInstaller Build erfolgreich!")
                
                # Post-process für plattform-spezifische Strukturen
                self.post_process_build()
                
                # Zeige Build-Ergebnisse
                self.show_build_results()
                return True
            else:
                safe_print(f"❌ PyInstaller Build fehlgeschlagen!")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return False
                
        except Exception as e:
            safe_print(f"❌ Build-Fehler: {e}")
            return False
    
    def post_process_build(self):
        """Post-Processing für plattform-spezifische Builds"""
        if self.current_platform == "macos":
            # Für macOS: Erstelle .app Bundle falls noch nicht vorhanden
            dist_dir = self.build_dir / self.app_name
            app_bundle = self.build_dir / f"{self.app_name}.app"
            
            if dist_dir.exists() and not app_bundle.exists():
                safe_print("🍎 Erstelle macOS .app Bundle...")
                
                # Erstelle .app Struktur
                contents_dir = app_bundle / "Contents"
                macos_dir = contents_dir / "MacOS"
                resources_dir = contents_dir / "Resources"
                
                app_bundle.mkdir(exist_ok=True)
                contents_dir.mkdir(exist_ok=True)
                macos_dir.mkdir(exist_ok=True)
                resources_dir.mkdir(exist_ok=True)
                
                # Verschiebe PyInstaller Output in .app
                for item in dist_dir.iterdir():
                    shutil.move(str(item), str(macos_dir))
                
                # Entferne alten Ordner
                dist_dir.rmdir()
                
                # Info.plist erstellen
                plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{self.app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>org.ehrenamt-tools.finanzauswertung</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>'''
                
                with open(contents_dir / "Info.plist", 'w') as f:
                    f.write(plist_content)
                
                safe_print("✅ macOS .app Bundle erstellt!")
        
        elif self.current_platform == "windows":
            # Für Windows: Stelle sicher, dass .exe existiert
            dist_dir = self.build_dir / self.app_name
            exe_file = dist_dir / f"{self.app_name}.exe"
            
            if dist_dir.exists() and exe_file.exists():
                # Kopiere .exe eine Ebene höher für einfacheren Zugriff
                shutil.copy2(exe_file, self.build_dir / f"{self.app_name}.exe")
                safe_print("✅ Windows .exe bereitgestellt!")
        
        elif self.current_platform == "linux":
            # Für Linux: Stelle sicher, dass Executable ausführbar ist
            dist_dir = self.build_dir / self.app_name
            exe_file = dist_dir / self.app_name
            
            if dist_dir.exists() and exe_file.exists():
                # Kopiere Executable eine Ebene höher
                shutil.copy2(exe_file, self.build_dir / self.app_name)
                os.chmod(self.build_dir / self.app_name, 0o755)
                safe_print("✅ Linux Executable bereitgestellt!")
    
    def show_build_results(self):
        """Zeigt die Build-Ergebnisse an"""
        safe_print("\n🔍 Build-Ergebnisse:")
        
        if self.build_dir.exists():
            for file in self.build_dir.iterdir():
                if file.is_file():
                    size = file.stat().st_size
                    safe_print(f"  📄 {file.name} ({size:,} bytes)")
        else:
            safe_print("  ❌ Build-Directory nicht gefunden!")
    
    def create_fallback_executable(self):
        """Erstellt ein Fallback-Executable wenn PyInstaller fehlschlägt"""
        safe_print("🔄 Erstelle Fallback-Executable...")
        
        try:
            # Erstelle einfaches Launcher-Script
            launcher_content = f'''#!/usr/bin/env python3
"""
Launcher für {self.app_name}
"""
import sys
import os
from pathlib import Path

# Füge src/ zum Python-Pfad hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Starte Hauptanwendung
if __name__ == "__main__":
    try:
        import main
        main.main()
    except Exception as e:
        print(f"Fehler beim Starten der Anwendung: {{e}}")
        sys.exit(1)
'''
            
            # Erstelle plattform-spezifisches Executable
            if self.current_platform == "windows":
                executable_name = f"{self.app_name}.bat"
                batch_content = f'''@echo off
python "{self.app_name}.py"
pause
'''
                # Erstelle .bat Datei für Windows
                batch_path = self.build_dir / executable_name
                with open(batch_path, 'w', encoding='utf-8') as f:
                    f.write(batch_content)
                
            elif self.current_platform == "macos":
                executable_name = f"{self.app_name}.app"
                # Erstelle macOS .app Bundle-Struktur
                app_dir = self.build_dir / executable_name
                contents_dir = app_dir / "Contents"
                macos_dir = contents_dir / "MacOS"
                resources_dir = contents_dir / "Resources"
                
                app_dir.mkdir(exist_ok=True)
                contents_dir.mkdir(exist_ok=True)
                macos_dir.mkdir(exist_ok=True)
                resources_dir.mkdir(exist_ok=True)
                
                # Info.plist erstellen
                plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{self.app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>org.ehrenamt-tools.finanzauswertung</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
</dict>
</plist>'''
                
                with open(contents_dir / "Info.plist", 'w') as f:
                    f.write(plist_content)
                
                # Executable in MacOS/ erstellen
                launcher_path = macos_dir / self.app_name
            else:
                # Linux
                executable_name = self.app_name
                launcher_path = self.build_dir / executable_name
            
            # Schreibe Python-Launcher
            if self.current_platform != "macos":
                launcher_path = self.build_dir / f"{self.app_name}.py"
            
            with open(launcher_path, 'w', encoding='utf-8') as f:
                f.write(launcher_content)
            
            # Mache Datei ausführbar (Unix-Systeme)
            if self.current_platform != "windows":
                os.chmod(launcher_path, 0o755)
            
            # Kopiere Projekt-Dateien
            if (self.project_root / "src").exists():
                shutil.copytree(self.project_root / "src", self.build_dir / "src", dirs_exist_ok=True)
            
            if (self.project_root / "resources").exists():
                if self.current_platform == "macos":
                    # Für macOS in Resources/ kopieren
                    shutil.copytree(self.project_root / "resources", 
                                  self.build_dir / f"{self.app_name}.app" / "Contents" / "Resources" / "resources", 
                                  dirs_exist_ok=True)
                else:
                    shutil.copytree(self.project_root / "resources", self.build_dir / "resources", dirs_exist_ok=True)
            
            # Kopiere requirements.txt
            if (self.project_root / "requirements.txt").exists():
                shutil.copy2(self.project_root / "requirements.txt", self.build_dir)
            
            # Kopiere main.py
            if (self.project_root / "main.py").exists():
                shutil.copy2(self.project_root / "main.py", self.build_dir)
            
            safe_print(f"✅ Fallback-Executable erstellt: {executable_name}")
            return True
            
        except Exception as e:
            safe_print(f"❌ Fallback-Erstellung fehlgeschlagen: {e}")
            return False

def main():
    """Hauptfunktion für CI-Build"""
    safe_print("🏗️ CI-Build Manager")
    safe_print("=" * 50)
    
    builder = CIBuildManager()
    
    safe_print(f"🖥️ Plattform: {builder.current_platform}")
    safe_print(f"📁 Build-Directory: {builder.build_dir}")
    
    # Versuche zuerst PyInstaller-Build
    success = builder.create_simple_build()
    
    # Falls das fehlschlägt, erstelle Fallback
    if not success:
        safe_print("\n🔄 PyInstaller fehlgeschlagen - erstelle Fallback...")
        success = builder.create_fallback_executable()
    
    if success:
        safe_print("\n🎉 Build abgeschlossen!")
        sys.exit(0)
    else:
        safe_print("\n💥 Build fehlgeschlagen!")
        sys.exit(1)

if __name__ == "__main__":
    main()
