#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schneller Test Runner - Ohne GUI-Tests und Coverage
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

class FastTestRunner:
    """Schneller Test-Runner ohne problematische Tests"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent
        self.results = []
        
    def get_safe_test_files(self) -> list:
        """Nur sichere, schnelle Tests"""
        safe_tests = [
            'test_account_names.py',
            'test_balance.py', 
            'test_balance_migration.py',
            'test_bwa_pdf_generation.py',
            'test_helpers.py',
            'test_file_handler_errors.py',
            'test_build_system.py',
            'test_multi_sheet_import.py',
            'test_quarter_modes.py',
            'test_settings_export.py',
            'test_string_consistency.py',
            'test_super_groups.py',
            'test_dialogs.py',
            'test_widgets.py',
            'test_settings_advanced.py',
            'test_integration.py',
            'test_performance.py',
            'test_application_startup.py'
        ]
        
        # Nur existierende Tests zurückgeben
        existing_tests = []
        for test in safe_tests:
            if (self.test_dir / test).exists():
                existing_tests.append(test)
        
        return existing_tests
    
    def run_test(self, test_file: str) -> bool:
        """Führt einen Test schnell aus"""
        print(f"🧪 {test_file}")
        
        try:
            start_time = time.time()
            
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root)
            
            result = subprocess.run(
                [sys.executable, str(self.test_dir / test_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,  # Kurzer Timeout
                env=env
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"   ✅ ({duration:.1f}s)")
                self.results.append((test_file, True, duration))
                return True
            else:
                print(f"   ❌ ({duration:.1f}s)")
                self.results.append((test_file, False, duration))
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout")
            self.results.append((test_file, False, 30))
            return False
        except Exception as e:
            print(f"   💥 {str(e)[:50]}")
            self.results.append((test_file, False, 0))
            return False
    
    def run_all_tests(self):
        """Führt alle sicheren Tests aus"""
        print(f"🚀 Schneller Test-Lauf")
        print(f"📅 {datetime.now().strftime('%H:%M:%S')}")
        
        test_files = self.get_safe_test_files()
        print(f"📋 {len(test_files)} Tests gefunden")
        
        successful = 0
        failed = 0
        
        for test_file in test_files:
            if self.run_test(test_file):
                successful += 1
            else:
                failed += 1
        
        # Zusammenfassung
        total = successful + failed
        success_rate = (successful / total * 100) if total > 0 else 0
        
        print(f"\n📊 ERGEBNIS")
        print(f"✅ {successful}/{total} Tests erfolgreich ({success_rate:.0f}%)")
        
        if failed > 0:
            print(f"❌ Fehlgeschlagene Tests:")
            for test_file, success, duration in self.results:
                if not success:
                    print(f"   • {test_file}")
        
        # Badge generieren
        self.generate_badge(successful, failed)
        
        return successful, failed
    
    def generate_badge(self, successful: int, failed: int):
        """Generiert einfaches Test-Badge"""
        total = successful + failed
        if total == 0:
            return
            
        success_rate = (successful / total) * 100
        
        if success_rate == 100:
            color = "brightgreen"
        elif success_rate >= 80:
            color = "green"
        elif success_rate >= 60:
            color = "yellow"
        else:
            color = "red"
        
        badge_data = {
            "schemaVersion": 1,
            "label": "tests",
            "message": f"{successful}/{total} passing ({success_rate:.0f}%)",
            "color": color,
            "timestamp": datetime.now().isoformat()
        }
        
        badge_file = self.project_root / "test_badge.json"
        try:
            with open(badge_file, 'w') as f:
                json.dump(badge_data, f, indent=2)
            print(f"🏷️ Badge: test_badge.json")
        except Exception as e:
            print(f"❌ Badge-Fehler: {e}")

def main():
    """Hauptfunktion"""
    runner = FastTestRunner()
    successful, failed = runner.run_all_tests()
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
