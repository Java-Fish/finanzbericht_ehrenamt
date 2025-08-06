# -*- coding: utf-8 -*-
"""
Dateiverarbeitung für verschiedene Formate
"""

import os
import pandas as pd
import chardet
from pathlib import Path


class FileHandler:
    """Klasse zur Verarbeitung verschiedener Dateiformate"""
    
    def __init__(self):
        self.supported_extensions = ['.xlsx', '.xls', '.ods', '.csv']
        
    def process_file(self, file_path, sheet_name=None):
        """Verarbeitet eine Datei und gibt den Inhalt zurück"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Datei nicht gefunden: {file_path}")
            
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in self.supported_extensions:
            raise ValueError(f"Nicht unterstütztes Dateiformat: {file_extension}")
            
        try:
            if file_extension in ['.xlsx', '.xls']:
                return self._process_excel(file_path, sheet_name)
            elif file_extension == '.ods':
                return self._process_ods(file_path, sheet_name)
            elif file_extension == '.csv':
                return self._process_csv(file_path)
        except Exception as e:
            raise Exception(f"Fehler beim Verarbeiten der Datei: {str(e)}")
            
    def get_sheet_names(self, file_path):
        """Gibt die Namen aller Arbeitsblätter einer Excel/ODS-Datei zurück"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Datei nicht gefunden: {file_path}")
            
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in ['.xlsx', '.xls', '.ods']:
            return None  # CSV-Dateien haben keine Blätter
            
        try:
            if file_extension in ['.xlsx', '.xls']:
                engine = 'openpyxl' if file_extension == '.xlsx' else 'xlrd'
                excel_file = pd.ExcelFile(file_path, engine=engine)
                return excel_file.sheet_names
            elif file_extension == '.ods':
                try:
                    excel_file = pd.ExcelFile(file_path, engine='odf')
                    return excel_file.sheet_names
                except ImportError:
                    raise Exception(
                        "Für ODS-Dateien ist das 'odfpy' Paket erforderlich. "
                        "Installieren Sie es mit: pip install odfpy"
                    )
        except Exception as e:
            raise Exception(f"Fehler beim Lesen der Blatt-Namen: {str(e)}")
            
    def has_multiple_sheets(self, file_path):
        """Prüft ob eine Datei mehrere Arbeitsblätter hat"""
        sheet_names = self.get_sheet_names(file_path)
        return sheet_names is not None and len(sheet_names) > 1
            
    def _process_excel(self, file_path, sheet_name=None):
        """Verarbeitet Excel-Dateien"""
        print(f"Verarbeite Excel-Datei: {file_path}")
        if sheet_name:
            print(f"Arbeitsblatt: {sheet_name}")
        
        # Excel-Datei lesen
        engine = 'openpyxl' if file_path.endswith('.xlsx') else 'xlrd'
        
        # Wenn kein sheet_name angegeben, das erste Blatt nehmen
        if sheet_name is None:
            excel_file = pd.ExcelFile(file_path, engine=engine)
            sheet_name = excel_file.sheet_names[0]
            print(f"Kein Blatt angegeben, verwende erstes Blatt: {sheet_name}")
        
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine=engine)
        
        # Grundlegende Informationen ausgeben
        print(f"Anzahl Zeilen: {len(df)}")
        print(f"Anzahl Spalten: {len(df.columns)}")
        print(f"Spalten: {list(df.columns)}")
        
        return df
        
    def _process_ods(self, file_path, sheet_name=None):
        """Verarbeitet LibreOffice Calc Dateien"""
        print(f"Verarbeite ODS-Datei: {file_path}")
        if sheet_name:
            print(f"Arbeitsblatt: {sheet_name}")
        
        # ODS-Datei lesen (requires odfpy: pip install odfpy)
        try:
            # Wenn kein sheet_name angegeben, das erste Blatt nehmen
            if sheet_name is None:
                excel_file = pd.ExcelFile(file_path, engine='odf')
                sheet_name = excel_file.sheet_names[0]
                print(f"Kein Blatt angegeben, verwende erstes Blatt: {sheet_name}")
                
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='odf')
        except ImportError:
            raise Exception(
                "Für ODS-Dateien ist das 'odfpy' Paket erforderlich. "
                "Installieren Sie es mit: pip install odfpy"
            )
        
        print(f"Anzahl Zeilen: {len(df)}")
        print(f"Anzahl Spalten: {len(df.columns)}")
        print(f"Spalten: {list(df.columns)}")
        
        return df
        
    def _process_csv(self, file_path):
        """Verarbeitet CSV-Dateien"""
        print(f"Verarbeite CSV-Datei: {file_path}")
        
        # Encoding erkennen
        encoding = self._detect_encoding(file_path)
        print(f"Erkanntes Encoding: {encoding}")
        
        # CSV-Datei lesen mit automatischer Trennzeichen-Erkennung
        try:
            # Zuerst versuchen mit Semikolon (typisch für deutsche CSV)
            df = pd.read_csv(file_path, encoding=encoding, sep=';', engine='python')
            if len(df.columns) == 1:
                # Falls nur eine Spalte, versuche Komma als Trennzeichen
                df = pd.read_csv(file_path, encoding=encoding, sep=',', engine='python')
        except Exception:
            # Fallback: pandas automatische Erkennung
            df = pd.read_csv(file_path, encoding=encoding, sep=None, engine='python')
        
        print(f"Anzahl Zeilen: {len(df)}")
        print(f"Anzahl Spalten: {len(df.columns)}")
        print(f"Spalten: {list(df.columns)}")
        
        return df
        
    def _detect_encoding(self, file_path):
        """Erkennt das Encoding einer Datei"""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # Erste 10KB lesen
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                
                # Fallback auf häufige Encodings
                if not encoding or result['confidence'] < 0.7:
                    # Typische Encodings für deutsche Dateien
                    common_encodings = ['utf-8', 'iso-8859-1', 'cp1252', 'utf-16']
                    for enc in common_encodings:
                        try:
                            with open(file_path, 'r', encoding=enc) as test_file:
                                test_file.read(1000)
                            return enc
                        except (UnicodeDecodeError, UnicodeError):
                            continue
                    return 'utf-8'  # Letzter Fallback
                    
                return encoding
        except Exception:
            return 'utf-8'  # Standard-Fallback
            
    def get_file_info(self, file_path):
        """Gibt grundlegende Informationen über eine Datei zurück"""
        if not os.path.exists(file_path):
            return None
            
        file_stats = os.stat(file_path)
        file_extension = Path(file_path).suffix.lower()
        
        return {
            'name': os.path.basename(file_path),
            'path': file_path,
            'size': file_stats.st_size,
            'extension': file_extension,
            'is_supported': file_extension in self.supported_extensions
        }
