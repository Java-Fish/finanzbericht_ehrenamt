#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Management für Finanzauswertung Ehrenamt
"""

import sys
import argparse
from pathlib import Path

def run_fast_tests():
    """Führt schnelle Tests aus"""
    from fast_test_runner import FastTestRunner
    runner = FastTestRunner()
    successful, failed = runner.run_all_tests()
    return 0 if failed == 0 else 1

def run_full_tests():
    """Führt alle Tests aus (kann länger dauern)"""
    from run_all_tests import TestRunner
    runner = TestRunner()
    successful, failed = runner.run_all_tests()
    return 0 if failed == 0 else 1

def update_badges():
    """Aktualisiert nur die README-Badges"""
    from run_all_tests import TestRunner
    runner = TestRunner()
    
    # Schnelle Tests für Badge-Update
    runner.generate_test_badge(12, 0)  # Aktuelle Werte
    runner.generate_coverage_report()
    runner.update_readme_badges()
    
    print("✅ Badges aktualisiert")
    return 0

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description="Test-Management für Finanzauswertung Ehrenamt")
    parser.add_argument("mode", choices=["fast", "full", "badges"], 
                       help="Test-Modus: fast=schnelle Tests, full=alle Tests, badges=nur Badge-Update")
    
    args = parser.parse_args()
    
    if args.mode == "fast":
        return run_fast_tests()
    elif args.mode == "full":
        return run_full_tests()
    elif args.mode == "badges":
        return update_badges()

if __name__ == "__main__":
    sys.exit(main())
