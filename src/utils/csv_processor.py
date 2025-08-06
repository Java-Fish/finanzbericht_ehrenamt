# -*- coding: utf-8 -*-
"""
CSV-Datenverarbeitung für BWA-Generierung
"""

import pandas as pd
import csv
from PySide6.QtCore import QSettings
from typing import List, Dict, Tuple, Optional
from datetime import datetime, date
import re
from .file_handler import FileHandler


class CSVProcessor:
    """Verarbeitet CSV-Dateien für BWA-Analyse"""
    
    def __init__(self):
        self.settings = QSettings()
        self.raw_data = None
        self.processed_data = None
        self.file_handler = FileHandler()
        
    def load_file(self, file_path: str, sheet_name: str = None) -> bool:
        """Lädt eine Datei (CSV, Excel, ODS) und verarbeitet sie"""
        try:
            # Datei mit dem FileHandler laden
            self.raw_data = self.file_handler.process_file(file_path, sheet_name)
            
            # FileHandler gibt bereits ein DataFrame zurück
            if not isinstance(self.raw_data, pd.DataFrame):
                print(f"Fehler: FileHandler gab kein DataFrame zurück: {type(self.raw_data)}")
                return False
            
            # Spaltennamen standardisieren (Leerzeichen entfernen)
            self.raw_data.columns = self.raw_data.columns.str.strip()
            
            # Daten verarbeiten
            return self._process_data()
            
        except Exception as e:
            print(f"Fehler beim Laden der Datei: {e}")
            return False
        
    def get_csv_separator(self) -> str:
        """Holt das CSV-Trennzeichen aus den Einstellungen"""
        separator = self.settings.value("csv_separator", ";")
        if separator == "Tab":
            separator = "\t"
        return separator
    
    def normalize_account_number(self, account_nr) -> str:
        """Normalisiert eine Sachkontonummer zu einem String-Format"""
        if pd.isna(account_nr):
            return ""
        
        # Zu String konvertieren und Whitespace entfernen
        account_str = str(account_nr).strip()
        
        # Prüfen ob es eine Zahl ist (auch Floats)
        if account_str.replace('.', '').replace('-', '').isdigit():
            try:
                # Float zu Int zu String (entfernt .0 Endungen)
                float_val = float(account_str)
                if float_val.is_integer():
                    return str(int(float_val))
                else:
                    return account_str  # Behalte Original wenn echte Dezimalzahl
            except ValueError:
                pass
        
        return account_str
        
    def load_csv_file(self, file_path: str) -> bool:
        """Lädt eine CSV-Datei und verarbeitet sie (Legacy-Methode für Kompatibilität)"""
        return self.load_file(file_path)
        
    def has_multiple_sheets(self, file_path: str) -> bool:
        """Prüft ob eine Datei mehrere Arbeitsblätter hat"""
        return self.file_handler.has_multiple_sheets(file_path)
        
    def get_sheet_names(self, file_path: str) -> List[str]:
        """Gibt die Namen aller Arbeitsblätter einer Datei zurück"""
        return self.file_handler.get_sheet_names(file_path)
            
    def _process_data(self) -> bool:
        """Verarbeitet die geladenen Rohdaten"""
        if self.raw_data is None:
            return False
            
        try:
            # Kopie für Verarbeitung erstellen
            df = self.raw_data.copy()
            
            # Erforderliche Spalten prüfen
            required_columns = ['Sachkontonr.', 'Betrag', 'Buchungstag']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"Fehlende Spalten: {missing_columns}")
                return False
            
            # Optionale Spalten identifizieren
            optional_columns = ['Buchungsnummer', 'Buchungsnr.', 'Buchungs-Nr.', 'Verwendungszweck', 'Beschreibung']
            
            # Buchungsnummer-Spalte finden oder erstellen
            buchungsnummer_col = None
            for col in optional_columns:
                if col in df.columns:
                    buchungsnummer_col = col
                    break
            
            # Falls keine Buchungsnummer-Spalte gefunden, aus Verwendungszweck extrahieren
            if buchungsnummer_col is None and 'Verwendungszweck' in df.columns:
                # Versuche Buchungsnummer aus Verwendungszweck zu extrahieren (Format: B240027, B250145)
                df['Buchungsnummer'] = df['Verwendungszweck'].str.extract(r'(B\d+)', expand=False)
                buchungsnummer_col = 'Buchungsnummer'
            elif buchungsnummer_col is None:
                # Fallback: leere Buchungsnummer erstellen
                df['Buchungsnummer'] = ''
                buchungsnummer_col = 'Buchungsnummer'
            
            # Optionale Spalten identifizieren
            optional_columns = ['Belegnummer', 'Belegnr.', 'Beleg-Nr.', 'Verwendungszweck', 'Beschreibung']
            
            # Belegnummer-Spalte finden oder erstellen
            belegnummer_col = None
            for col in optional_columns:
                if col in df.columns:
                    belegnummer_col = col
                    break
            
            # Falls keine Belegnummer-Spalte gefunden, aus Verwendungszweck extrahieren
            if belegnummer_col is None and 'Verwendungszweck' in df.columns:
                # Versuche Belegnummer aus Verwendungszweck zu extrahieren (Format: B240027, B250145)
                df['Belegnummer'] = df['Verwendungszweck'].str.extract(r'(B\d+)', expand=False)
                belegnummer_col = 'Belegnummer'
            elif belegnummer_col is None:
                # Fallback: leere Belegnummer erstellen
                df['Belegnummer'] = ''
                belegnummer_col = 'Belegnummer'
                return False
                
            # Sachkontonr. als String sicherstellen und normalisieren
            df['Sachkontonr.'] = df['Sachkontonr.'].apply(self.normalize_account_number)
            
            # Leere Zeilen entfernen
            df = df.dropna(subset=['Sachkontonr.', 'Betrag'])
            
            # Betrag verarbeiten (Euro-Zeichen entfernen, Komma durch Punkt ersetzen)
            df['Betrag_Clean'] = df['Betrag'].apply(self._clean_amount)
            
            # Buchungstag verarbeiten
            df['Buchungstag_Clean'] = df['Buchungstag'].apply(self._parse_date)
            
            # Nur Zeilen mit gültigen Daten behalten
            df = df.dropna(subset=['Betrag_Clean', 'Buchungstag_Clean'])
            
            # Quartal hinzufügen
            df['Quartal'] = df['Buchungstag_Clean'].apply(self._get_quarter)
            
            self.processed_data = df
            return True
            
        except Exception as e:
            print(f"Fehler bei der Datenverarbeitung: {e}")
            return False
            
    def _clean_amount(self, amount_str: str) -> Optional[float]:
        """Bereinigt Betragswerte"""
        if pd.isna(amount_str) or amount_str == '':
            return None
            
        try:
            # Euro-Zeichen und Leerzeichen entfernen
            cleaned = str(amount_str).replace('€', '').replace(' ', '')
            
            # Dezimaltrennzeichen standardisieren
            decimal_separator = self.settings.value("decimal_separator", ",")
            if decimal_separator == ",":
                # Deutsche Notation: 1.234,56 -> 1234.56
                if ',' in cleaned and '.' in cleaned:
                    # Beide Zeichen vorhanden, Punkt ist Tausendertrennzeichen
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                elif ',' in cleaned:
                    # Nur Komma vorhanden, ist Dezimaltrennzeichen
                    cleaned = cleaned.replace(',', '.')
            else:
                # Englische Notation: 1,234.56 -> 1234.56
                if ',' in cleaned and '.' in cleaned:
                    # Beide Zeichen vorhanden, Komma ist Tausendertrennzeichen
                    cleaned = cleaned.replace(',', '')
                    
            return float(cleaned)
            
        except (ValueError, TypeError):
            return None
            
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parst Datumswerte"""
        if pd.isna(date_str) or date_str == '':
            return None
            
        try:
            # Verschiedene Datumsformate versuchen
            formats = ['%Y.%m.%d', '%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
            
            for fmt in formats:
                try:
                    return datetime.strptime(str(date_str).strip(), fmt).date()
                except ValueError:
                    continue
                    
            return None
            
        except Exception:
            return None
            
    def _get_quarter(self, date_obj: date) -> int:
        """Bestimmt das Quartal für ein Datum"""
        if date_obj is None:
            return 0
            
        month = date_obj.month
        if month <= 3:
            return 1
        elif month <= 6:
            return 2
        elif month <= 9:
            return 3
        else:
            return 4
            
    def get_account_numbers(self) -> List[str]:
        """Gibt alle eindeutigen Sachkontonummern zurück"""
        if self.processed_data is None:
            return []
            
        # Sachkontonr. sind bereits als String gespeichert
        accounts = self.processed_data['Sachkontonr.'].unique()
        return sorted([str(acc).strip() for acc in accounts if pd.notna(acc) and str(acc).strip()])
        
    def get_account_name(self, account_number: str) -> Optional[str]:
        """Gibt den Namen/Beschreibung eines Sachkontos zurück, falls vorhanden"""
        if self.processed_data is None:
            return None
            
        # account_number als String sicherstellen
        account_number = str(account_number).strip()
            
        # Mögliche Spalten für Kontobezeichnungen
        name_columns = ['Sachkonto', 'Sachkontobezeichnung', 'Kontobezeichnung', 'Bezeichnung', 'Name', 'Beschreibung']
        
        for col in name_columns:
            if col in self.processed_data.columns:
                # Erste Zeile mit diesem Sachkonto finden
                # Sachkontonr. sind bereits als String gespeichert
                matching_rows = self.processed_data[self.processed_data['Sachkontonr.'] == account_number]
                if not matching_rows.empty:
                    name = matching_rows[col].iloc[0]
                    if pd.notna(name) and str(name).strip():
                        return str(name).strip()
        return None
        
    def get_all_account_names(self) -> Dict[str, str]:
        """Gibt ein Dictionary aller Sachkonten mit ihren Namen zurück"""
        if self.processed_data is None:
            return {}
            
        account_names = {}
        account_numbers = self.get_account_numbers()
        
        for account_num in account_numbers:
            name = self.get_account_name(account_num)
            if name:
                account_names[account_num] = name
                
        return account_names
        
    def get_data_by_quarter(self, quarter: int) -> pd.DataFrame:
        """Gibt Daten für ein bestimmtes Quartal zurück (basierend auf Einstellungen)"""
        if self.processed_data is None:
            return pd.DataFrame()
            
        # Quartals-Modus aus Einstellungen laden
        settings = QSettings()
        quarter_mode = settings.value("quarter_mode", "cumulative")
        
        if quarter_mode == "cumulative":
            return self.get_data_by_quarter_cumulative(quarter)
        else:
            return self.get_data_by_quarter_individual(quarter)
            
    def get_data_by_quarter_individual(self, quarter: int) -> pd.DataFrame:
        """Gibt Daten nur für das spezifische Quartal zurück (quartalsweise)"""
        if self.processed_data is None:
            return pd.DataFrame()
            
        return self.processed_data[self.processed_data['Quartal'] == quarter].copy()
        
    def get_data_by_quarter_cumulative(self, quarter: int) -> pd.DataFrame:
        """Gibt kumulative Daten vom Jahresanfang bis Ende des Quartals zurück"""
        if self.processed_data is None:
            return pd.DataFrame()
            
        # Für kumulative Auswertung: alle Quartale von 1 bis einschließlich dem gewünschten
        return self.processed_data[self.processed_data['Quartal'] <= quarter].copy()
        
    def get_data_by_account(self, account_number: str) -> pd.DataFrame:
        """Gibt Daten für ein bestimmtes Sachkonto zurück"""
        if self.processed_data is None:
            return pd.DataFrame()
            
        return self.processed_data[
            self.processed_data['Sachkontonr.'] == account_number
        ].copy()
        
    def get_year_data(self) -> pd.DataFrame:
        """Gibt alle Daten des Jahres zurück"""
        if self.processed_data is None:
            return pd.DataFrame()
            
        return self.processed_data.copy()
        
    def get_summary_by_account_group(self, account_mappings: Dict[str, str]) -> Dict[str, Dict[str, float]]:
        """Erstellt Zusammenfassung nach BWA-Gruppen"""
        if self.processed_data is None:
            return {}
            
        summary = {}
        
        # Für jede BWA-Gruppe
        for account, group in account_mappings.items():
            if group not in summary:
                summary[group] = {
                    'Q1': 0.0, 'Q2': 0.0, 'Q3': 0.0, 'Q4': 0.0, 'Jahr': 0.0
                }
                
            # Daten für dieses Sachkonto
            account_data = self.get_data_by_account(account)
            
            if not account_data.empty:
                # Nach Quartalen summieren
                for quarter in range(1, 5):
                    quarter_data = account_data[account_data['Quartal'] == quarter]
                    quarter_sum = quarter_data['Betrag_Clean'].sum()
                    summary[group][f'Q{quarter}'] += quarter_sum
                    
                # Jahressumme
                year_sum = account_data['Betrag_Clean'].sum()
                summary[group]['Jahr'] += year_sum
                
        return summary
        
    def get_summary_by_account(self) -> Dict[str, Dict[str, float]]:
        """Erstellt Zusammenfassung nach Sachkonten"""
        if self.processed_data is None:
            return {}
            
        summary = {}
        accounts = self.get_account_numbers()
        
        for account in accounts:
            account_data = self.get_data_by_account(account)
            
            if not account_data.empty:
                summary[account] = {
                    'Q1': 0.0, 'Q2': 0.0, 'Q3': 0.0, 'Q4': 0.0, 'Jahr': 0.0
                }
                
                # Nach Quartalen summieren
                for quarter in range(1, 5):
                    quarter_data = account_data[account_data['Quartal'] == quarter]
                    quarter_sum = quarter_data['Betrag_Clean'].sum()
                    summary[account][f'Q{quarter}'] = quarter_sum
                    
                # Jahressumme
                year_sum = account_data['Betrag_Clean'].sum()
                summary[account]['Jahr'] = year_sum
                
        return summary
