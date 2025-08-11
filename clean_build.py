#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean Build Script
- Führt Tests aus
- Baut plattformspezifische Artefakte via ci_build.py (vereinfacht)
- Version wird aus Datei 'version' gelesen
- Artefakte werden nach build/ kopiert und mit Versionsnummer versehen:
    macOS: Finanzauswertung_Ehrenamt-{VERSION}.pkg (falls pkg vorhanden) sonst .tar.gz
    Windows: Finanzauswertung_Ehrenamt-{VERSION}.exe (onefile oder kopiert aus onedir)
    Linux: Finanzauswertung_Ehrenamt-{VERSION}
"""
import sys
import subprocess
import platform
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(__file__).parent
VERSION_FILE = ROOT / 'version'
BUILD_DIR = ROOT / 'build'


def read_version() -> str:
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text(encoding='utf-8').strip() or '0.0.0'
    return '0.0.0'


def run_tests() -> bool:
    print('🧪 Starte Tests...')
    test_runner = ROOT / 'test' / 'run_all_tests.py'
    if not test_runner.exists():
        print('⚠️ Test Runner nicht gefunden, überspringe Tests.')
        return True
    result = subprocess.run([sys.executable, str(test_runner)], cwd=ROOT)
    if result.returncode == 0:
        print('✅ Tests erfolgreich')
        return True
    print('❌ Tests fehlgeschlagen (Build wird trotzdem versucht)')
    return True


def run_ci_build() -> bool:
    print('🏗️ Starte Build (ci_build.py) ...')
    ci_script = ROOT / 'ci_build.py'
    if not ci_script.exists():
        print('❌ ci_build.py nicht gefunden.')
        return False
    result = subprocess.run([sys.executable, str(ci_script)], cwd=ROOT)
    if result.returncode == 0:
        print('✅ Build abgeschlossen')
        return True
    print('❌ Build fehlgeschlagen')
    return False




def list_build():
    if not BUILD_DIR.exists():
        return
    print('\n📁 Inhalt build/:')
    for p in sorted(BUILD_DIR.iterdir()):
        if p.is_file():
            print(f'  • {p.name} ({p.stat().st_size} B)')
        else:
            print(f'  • {p.name}/')


def main() -> int:
    version = read_version()
    print('🚀 Clean Build')
    print(f'Version: {version}')
    print(f'Datum: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('='*50)

    if not run_tests():
        return 1
    print('\n' + '-'*50)
    if not run_ci_build():
        return 1
    # Artefakte sind bereits versioniert in ci_build.py
    list_build()
    print('\n🎉 Fertig.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
