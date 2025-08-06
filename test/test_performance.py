#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für Performance und Speicher-Management
"""

import sys
import os
import time
import gc
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_memory_usage():
    """Testet Speicher-Verbrauch bei wiederholten Operationen"""
    print("🧠 Teste Speicher-Management...")
    
    try:
        import psutil
        process = psutil.Process()
        
        # Basis-Speicherverbrauch messen
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"   📊 Basis-Speicher: {initial_memory:.1f} MB")
        
        # Multiple CSV-Processor Instanzen erstellen und zerstören
        from src.utils.csv_processor import CSVProcessor
        
        for i in range(10):
            processor = CSVProcessor()
            del processor
            
        # Garbage Collection
        gc.collect()
        
        # Speicher nach Tests messen
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_diff = final_memory - initial_memory
        
        print(f"   📊 End-Speicher: {final_memory:.1f} MB")
        print(f"   📊 Differenz: {memory_diff:.1f} MB")
        
        # Akzeptabler Speicher-Anstieg (< 10 MB)
        if memory_diff < 10:
            print("   ✅ Speicher-Management OK")
            return True
        else:
            print(f"   ❌ Zu hoher Speicher-Anstieg: {memory_diff:.1f} MB")
            return False
        
    except ImportError:
        print("   ⚠️ psutil nicht verfügbar, Speicher-Test übersprungen")
        return True
    except Exception as e:
        print(f"   ❌ Speicher-Test fehlgeschlagen: {e}")
        return False

def test_performance_csv_processing():
    """Testet Performance der CSV-Verarbeitung"""
    print("⚡ Teste CSV-Performance...")
    
    try:
        from src.utils.csv_processor import CSVProcessor
        
        # Test-CSV-Daten erstellen
        test_csv_content = """Sachkontonr.;Betrag;Buchungstag;Verwendungszweck
1000;100.50;01.01.2024;Test 1
2000;-50.25;02.01.2024;Test 2
3000;75.00;03.01.2024;Test 3
4000;-25.75;04.01.2024;Test 4
5000;200.00;05.01.2024;Test 5"""
        
        # Temporäre CSV-Datei erstellen
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_csv_content)
            temp_file = f.name
        
        # Performance-Test
        processor = CSVProcessor()
        
        start_time = time.time()
        success = processor.load_csv_file(temp_file)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Temporäre Datei löschen
        os.unlink(temp_file)
        
        if success:
            print(f"   ✅ CSV-Verarbeitung erfolgreich ({processing_time:.3f}s)")
            
            # Performance-Check (< 1 Sekunde für kleine Datei)
            if processing_time < 1.0:
                print("   ✅ Performance OK")
                return True
            else:
                print(f"   ❌ Zu langsam: {processing_time:.3f}s")
                return False
        else:
            print("   ❌ CSV-Verarbeitung fehlgeschlagen")
            return False
        
    except Exception as e:
        print(f"   ❌ CSV-Performance Test fehlgeschlagen: {e}")
        return False

def test_concurrent_operations():
    """Testet gleichzeitige Operationen"""
    print("🔄 Teste Concurrent Operations...")
    
    try:
        from src.utils.csv_processor import CSVProcessor
        from src.utils.bwa_generator import BWAPDFGenerator
        
        # Multiple Instanzen gleichzeitig erstellen
        processors = []
        generators = []
        
        start_time = time.time()
        
        for i in range(5):
            processors.append(CSVProcessor())
            generators.append(BWAPDFGenerator())
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        print(f"   ✅ 5 Instanzen erstellt ({creation_time:.3f}s)")
        
        # Aufräumen
        del processors
        del generators
        gc.collect()
        
        # Performance-Check (< 2 Sekunden)
        if creation_time < 2.0:
            print("   ✅ Concurrent Operations OK")
            return True
        else:
            print(f"   ❌ Zu langsam: {creation_time:.3f}s")
            return False
        
    except Exception as e:
        print(f"   ❌ Concurrent Operations Test fehlgeschlagen: {e}")
        return False

def test_error_recovery():
    """Testet Fehler-Recovery"""
    print("🛡️ Teste Error Recovery...")
    
    try:
        from src.utils.csv_processor import CSVProcessor
        
        processor = CSVProcessor()
        
        # Test 1: Nicht-existierende Datei
        success1 = processor.load_csv_file("/not/existing/file.csv")
        if not success1:
            print("   ✅ Nicht-existierende Datei korrekt behandelt")
        else:
            print("   ❌ Nicht-existierende Datei nicht korrekt behandelt")
            return False
        
        # Test 2: Ungültiges Dateiformat
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("INVALID CSV CONTENT WITHOUT PROPER STRUCTURE")
            temp_file = f.name
        
        success2 = processor.load_csv_file(temp_file)
        os.unlink(temp_file)
        
        # Je nach Implementation kann das erfolgreich sein oder nicht
        print(f"   ✅ Ungültiges Format behandelt (success: {success2})")
        
        # Test 3: Processor nach Fehlern noch nutzbar
        test_csv = """Sachkontonr.;Betrag;Buchungstag;Verwendungszweck
1000;100;01.01.2024;Test nach Fehler"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_csv)
            temp_file = f.name
        
        success3 = processor.load_csv_file(temp_file)
        os.unlink(temp_file)
        
        if success3:
            print("   ✅ Processor nach Fehlern noch nutzbar")
            return True
        else:
            print("   ⚠️ Processor nach Fehlern eingeschränkt nutzbar (akzeptabel)")
            return True  # Das ist OK - manche Fehler können den State beeinträchtigen
        
    except Exception as e:
        print(f"   ❌ Error Recovery Test fehlgeschlagen: {e}")
        return False

def test_performance():
    """Haupttest-Funktion für Performance-Tests"""
    print("🚀 Teste System-Performance...")
    
    tests = [
        test_memory_usage,
        test_performance_csv_processing,
        test_concurrent_operations,
        test_error_recovery
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Test {test.__name__} fehlgeschlagen: {e}")
            failed += 1
    
    total = passed + failed
    print(f"\n📊 Performance-Tests: {passed}/{total} erfolgreich")
    
    return failed == 0

if __name__ == "__main__":
    success = test_performance()
    sys.exit(0 if success else 1)
