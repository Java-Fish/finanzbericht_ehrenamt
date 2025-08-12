# -*- coding: utf-8 -*-
"""
Sachkonten-Mapping Tab für BWA-Gruppierung
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                               QLineEdit, QLabel, QPushButton, QGroupBox,
                               QSplitter, QListWidgetItem, QMessageBox, QFileDialog)
from PySide6.QtCore import QSettings, Qt, Signal
import json
import pandas as pd
import csv
import os


class AccountMappingTab(QWidget):
    """Tab für Sachkonten-Gruppierung"""
    
    # Signal wird ausgesendet wenn sich Mappings ändern
    mappings_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.account_mappings = {}  # Dict: account_number -> group_name
        self.account_names = {}     # Dict: account_number -> account_name
        self.init_ui()
    
    def normalize_account_number(self, account_nr) -> str:
        """Normalisiert eine Sachkontonummer zu einem String-Format (konsistent mit CSVProcessor)"""
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
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Splitter für linke und rechte Seite
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Linke Seite - Sachkonten-Liste
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        accounts_group = QGroupBox("Sachkonten")
        accounts_layout = QVBoxLayout(accounts_group)
        
        self.accounts_list = QListWidget()
        self.accounts_list.currentItemChanged.connect(self.on_account_selected)
        accounts_layout.addWidget(self.accounts_list)
        
        # Button zum Aktualisieren der Kontenliste
        self.refresh_button = QPushButton("Kontenliste aktualisieren")
        self.refresh_button.clicked.connect(self.refresh_accounts)
        accounts_layout.addWidget(self.refresh_button)
        
        # Import/Export Buttons
        import_export_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Export CSV")
        self.export_button.clicked.connect(self.export_mappings_to_csv)
        self.export_button.setToolTip("Exportiert BWA-Gruppierungen in eine CSV-Datei")
        import_export_layout.addWidget(self.export_button)
        
        self.import_button = QPushButton("Import CSV")
        self.import_button.clicked.connect(self.import_mappings_from_csv)
        self.import_button.setToolTip("Importiert BWA-Gruppierungen aus einer CSV-Datei")
        import_export_layout.addWidget(self.import_button)
        
        accounts_layout.addLayout(import_export_layout)
        
        left_layout.addWidget(accounts_group)
        splitter.addWidget(left_widget)
        
        # Rechte Seite - Gruppenzuweisung
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        mapping_group = QGroupBox("Gruppenzuweisung")
        mapping_layout = QVBoxLayout(mapping_group)
        
        # Info Label
        self.info_label = QLabel("Wählen Sie ein Sachkonto aus der Liste")
        self.info_label.setStyleSheet("color: gray; font-style: italic;")
        mapping_layout.addWidget(self.info_label)
        
        # Aktuelles Sachkonto
        self.current_account_label = QLabel("")
        self.current_account_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        mapping_layout.addWidget(self.current_account_label)
        
        # Sachkonto-Name bearbeiten
        account_name_label = QLabel("Sachkonto-Name:")
        mapping_layout.addWidget(account_name_label)
        
        self.account_name_input = QLineEdit()
        self.account_name_input.setPlaceholderText("Name des Sachkontos eingeben...")
        self.account_name_input.textChanged.connect(self.on_account_name_changed)
        mapping_layout.addWidget(self.account_name_input)
        
        # Gruppeneingabe
        group_label = QLabel("BWA-Gruppe:")
        mapping_layout.addWidget(group_label)
        
        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("z.B. 'Spenden', 'Verwaltungskosten', 'Projektkosten'...")
        self.group_input.textChanged.connect(self.on_group_changed)
        mapping_layout.addWidget(self.group_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_mapping_button = QPushButton("Zuordnung speichern")
        self.save_mapping_button.clicked.connect(self.save_current_mapping)
        self.save_mapping_button.setEnabled(False)
        button_layout.addWidget(self.save_mapping_button)
        
        self.clear_mapping_button = QPushButton("Zuordnung löschen")
        self.clear_mapping_button.clicked.connect(self.clear_current_mapping)
        self.clear_mapping_button.setEnabled(False)
        button_layout.addWidget(self.clear_mapping_button)
        
        mapping_layout.addLayout(button_layout)
        
        # Vorschläge für häufige Gruppen
        suggestions_label = QLabel("Häufige BWA-Gruppen:")
        mapping_layout.addWidget(suggestions_label)
        
        suggestions_layout = QVBoxLayout()
        suggestions = [
            "Spenden", "Mitgliedsbeiträge", "Förderungen", "Sonstige Einnahmen",
            "Bürokosten", "Verwaltungskosten", "Projektkosten", "Personalkosten",
            "Reisekosten", "Telefon/IT", "Miete", "Versicherungen", "Werbung"
        ]
        
        # Suggestions als Buttons
        for i in range(0, len(suggestions), 3):
            row_layout = QHBoxLayout()
            for j in range(3):
                if i + j < len(suggestions):
                    suggestion_btn = QPushButton(suggestions[i + j])
                    suggestion_btn.clicked.connect(
                        lambda checked, text=suggestions[i + j]: self.group_input.setText(text)
                    )
                    suggestion_btn.setMaximumHeight(30)
                    row_layout.addWidget(suggestion_btn)
                else:
                    row_layout.addStretch()
            suggestions_layout.addLayout(row_layout)
        
        mapping_layout.addLayout(suggestions_layout)
        mapping_layout.addStretch()
        
        right_layout.addWidget(mapping_group)
        splitter.addWidget(right_widget)
        
        # Splitter-Verhältnis setzen
        splitter.setSizes([300, 400])
        
    def on_account_selected(self, current, previous):
        """Wird aufgerufen wenn ein Sachkonto ausgewählt wird"""
        if current is None:
            self.current_account_label.setText("")
            self.account_name_input.setText("")
            self.group_input.setText("")
            self.save_mapping_button.setEnabled(False)
            self.clear_mapping_button.setEnabled(False)
            self.info_label.setText("Wählen Sie ein Sachkonto aus der Liste")
            return
            
        # Kontonummer aus dem Anzeige-Text extrahieren und als String sicherstellen
        account_text = current.text()
        account_number = str(account_text.split(" →")[0].split(" -")[0].strip())
        
        self.current_account_label.setText(f"Sachkonto: {account_number}")
        
        # Aktuelle Kontoname laden
        account_name = self.account_names.get(account_number, "")
        self.account_name_input.setText(account_name)
        
        # Aktuelle Gruppenzuordnung laden
        group = self.account_mappings.get(account_number, "")
        self.group_input.setText(group)
        
        self.save_mapping_button.setEnabled(True)
        self.clear_mapping_button.setEnabled(True)
        self.info_label.setText("Bearbeiten Sie den Namen und die BWA-Gruppe für dieses Sachkonto")
        
    def on_group_changed(self):
        """Wird aufgerufen wenn sich der Gruppentext ändert"""
        current_item = self.accounts_list.currentItem()
        if current_item:
            self.save_mapping_button.setEnabled(True)
            
    def on_account_name_changed(self):
        """Wird aufgerufen wenn sich der Kontoname ändert"""
        current_item = self.accounts_list.currentItem()
        if current_item:
            self.save_mapping_button.setEnabled(True)
            
    def save_current_mapping(self):
        """Speichert die aktuelle Zuordnung (Name und Gruppe)"""
        current_item = self.accounts_list.currentItem()
        if not current_item:
            return
            
        # Kontonummer aus dem Anzeige-Text extrahieren und als String sicherstellen
        account_text = current_item.text()
        account_number = str(account_text.split(" →")[0].split(" -")[0].strip())
        
        account_name = self.account_name_input.text().strip()
        group_name = self.group_input.text().strip()
        
        # Kontoname speichern
        if account_name:
            self.account_names[account_number] = account_name
        else:
            # Wenn Name leer ist, aus Dictionary entfernen
            if account_number in self.account_names:
                del self.account_names[account_number]
        
        # Gruppenzuordnung speichern
        if group_name:
            self.account_mappings[account_number] = group_name
        else:
            # Wenn Gruppe leer ist, Zuordnung entfernen
            if account_number in self.account_mappings:
                del self.account_mappings[account_number]
        
        # Anzeige in der Liste aktualisieren
        self.update_account_item_display(current_item, account_number)
            
        self.save_settings()
        
        # Signal senden dass sich Mappings geändert haben
        self.mappings_changed.emit()
        
    def update_account_item_display(self, item, account_number):
        """Aktualisiert die Anzeige eines Sachkonto-Items in der Liste"""
        account_name = self.account_names.get(account_number, "")
        group_name = self.account_mappings.get(account_number, "")
        
        # Format: "1000 - Kassenkonto → Spenden"
        display_text = account_number
        
        if account_name:
            display_text += f" - {account_name}"
            
        if group_name:
            display_text += f" → {group_name}"
            
        item.setText(display_text)
        
    def clear_current_mapping(self):
        """Löscht die aktuelle Name- und Gruppenzuordnung"""
        current_item = self.accounts_list.currentItem()
        if not current_item:
            return
            
        # Kontonummer aus dem Anzeige-Text extrahieren und als String sicherstellen
        account_text = current_item.text()
        account_number = str(account_text.split(" →")[0].split(" -")[0].strip())
        
        # Name und Gruppe aus den Eingabefeldern löschen
        self.account_name_input.setText("")
        self.group_input.setText("")
        
        # Aus den Dictionaries entfernen
        if account_number in self.account_names:
            del self.account_names[account_number]
        if account_number in self.account_mappings:
            del self.account_mappings[account_number]
        
        # Anzeige aktualisieren
        self.update_account_item_display(current_item, account_number)
        
        self.save_settings()
        
        # Signal senden dass sich Mappings geändert haben
        self.mappings_changed.emit()
        
    def refresh_accounts(self):
        """Aktualisiert die Sachkontenliste"""
        # Diese Methode wird später von der Hauptanwendung aufgerufen
        # wenn neue CSV-Daten geladen werden
        QMessageBox.information(
            self, 
            "Information", 
            "Um neue Sachkonten zu laden, importieren Sie eine CSV-Datei über die Hauptanwendung."
        )
        
    def update_accounts_from_csv(self, account_numbers, account_names_dict=None):
        """Aktualisiert die Kontenliste basierend auf CSV-Daten"""
        # Wenn Kontennamen übergeben wurden, diese speichern
        if account_names_dict:
            for account_num, account_name in account_names_dict.items():
                if account_name and account_name.strip():
                    # Sachkontonummer normalisieren (konsistent mit CSVProcessor)
                    normalized_num = self.normalize_account_number(account_num)
                    if normalized_num:
                        self.account_names[normalized_num] = account_name.strip()
        
        # Sortierte Liste der Kontonummern (alle als String normalisiert)
        normalized_accounts = [self.normalize_account_number(acc) for acc in account_numbers]
        sorted_accounts = sorted(set(acc for acc in normalized_accounts if acc))
        
        # Liste leeren und neu befüllen
        self.accounts_list.clear()
        
        for account in sorted_accounts:
            item = QListWidgetItem()
            # account ist bereits String
            self.update_account_item_display(item, account)
            self.accounts_list.addItem(item)
            
    def load_settings(self):
        """Lädt die Einstellungen"""
        # Sachkonten-Mappings laden
        mappings_json = self.settings.value("account_mappings", "{}")
        try:
            self.account_mappings = json.loads(mappings_json)
        except (json.JSONDecodeError, TypeError):
            self.account_mappings = {}
            
        # Sachkonten-Namen laden
        names_json = self.settings.value("account_names", "{}")
        try:
            self.account_names = json.loads(names_json)
        except (json.JSONDecodeError, TypeError):
            self.account_names = {}
            
    def save_settings(self):
        """Speichert die Einstellungen"""
        # Sachkonten-Mappings speichern
        mappings_json = json.dumps(self.account_mappings)
        self.settings.setValue("account_mappings", mappings_json)
        
        # Sachkonten-Namen speichern
        names_json = json.dumps(self.account_names)
        self.settings.setValue("account_names", names_json)
        
        # Sicherstellen, dass alle Änderungen persistent gespeichert werden
        self.settings.sync()
        
    def reset_to_defaults(self):
        """Setzt die Einstellungen auf Standard zurück"""
        self.account_mappings = {}
        self.account_names = {}
        self.accounts_list.clear()
        self.account_name_input.setText("")
        self.group_input.setText("")
        self.current_account_label.setText("")
        self.save_settings()
        
    def get_account_mappings(self):
        """Gibt die aktuellen Sachkonten-Mappings zurück"""
        return self.account_mappings.copy()
        
    def get_account_names(self):
        """Gibt die aktuellen Sachkonten-Namen zurück"""
        return self.account_names.copy()
        
    def get_all_bwa_groups(self):
        """Gibt alle verwendeten BWA-Gruppen zurück"""
        bwa_groups = set()
        for account, group in self.account_mappings.items():
            if group:  # Nur wenn eine Gruppe zugeordnet ist
                bwa_groups.add(group)
        return sorted(list(bwa_groups))
    
    def export_mappings_to_csv(self):
        """Exportiert BWA-Gruppierungen in eine CSV-Datei"""
        try:
            # Dateiname für Export vorschlagen
            suggested_filename = "bwa_gruppen_export.csv"
            
            # Datei-Dialog öffnen
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "BWA-Gruppierungen exportieren",
                suggested_filename,
                "CSV-Dateien (*.csv)"
            )
            
            if not file_path:
                return  # Benutzer hat abgebrochen
            
            # Sicherstellen dass Datei .csv Endung hat
            if not file_path.lower().endswith('.csv'):
                file_path += '.csv'
            
            # CSV-Daten vorbereiten
            csv_data = []
            
            # Alle Konten mit Namen und Gruppierungen sammeln
            all_accounts = set(self.account_names.keys()) | set(self.account_mappings.keys())
            
            for account_nr in sorted(all_accounts):
                account_name = self.account_names.get(account_nr, "")
                bwa_group = self.account_mappings.get(account_nr, "")
                
                # Nur Konten mit mindestens einem Namen oder einer Gruppe exportieren
                if account_name or bwa_group:
                    csv_data.append({
                        'Sachkontonr.': account_nr,
                        'Sachkonto': account_name,
                        'BWA-Gruppe': bwa_group
                    })
            
            # CSV-Datei schreiben
            if csv_data:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Sachkontonr.', 'Sachkonto', 'BWA-Gruppe']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                    
                    # Header schreiben
                    writer.writeheader()
                    
                    # Daten schreiben
                    for row in csv_data:
                        writer.writerow(row)
                
                QMessageBox.information(
                    self,
                    "Export erfolgreich",
                    f"BWA-Gruppierungen wurden erfolgreich exportiert.\n\n"
                    f"Datei: {file_path}\n"
                    f"Einträge: {len(csv_data)}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Keine Daten",
                    "Keine BWA-Gruppierungen zum Exportieren gefunden."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export-Fehler",
                f"Fehler beim Exportieren der BWA-Gruppierungen:\n{str(e)}"
            )
    
    def import_mappings_from_csv(self):
        """Importiert BWA-Gruppierungen aus einer CSV-Datei"""
        try:
            # Datei-Dialog öffnen
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "BWA-Gruppierungen importieren",
                "",
                "CSV-Dateien (*.csv)"
            )
            
            if not file_path:
                return  # Benutzer hat abgebrochen
            
            # Bestätigung vor Import
            reply = QMessageBox.question(
                self,
                "Import bestätigen",
                "Möchten Sie die BWA-Gruppierungen importieren?\n\n"
                "Hinweis: Bestehende Zuordnungen werden überschrieben, "
                "wenn die Sachkontonummer bereits existiert.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # CSV-Datei einlesen
            imported_count = 0
            skipped_count = 0
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Detect delimiter (try both ; and ,)
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                else:
                    delimiter = ','
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Erwartete Spalten prüfen
                expected_columns = ['Sachkontonr.', 'Sachkonto', 'BWA-Gruppe']
                if not all(col in reader.fieldnames for col in expected_columns):
                    QMessageBox.warning(
                        self,
                        "Ungültige CSV-Datei",
                        f"Die CSV-Datei muss folgende Spalten enthalten:\n"
                        f"{', '.join(expected_columns)}\n\n"
                        f"Gefundene Spalten: {', '.join(reader.fieldnames or [])}"
                    )
                    return
                
                # Daten importieren
                for row in reader:
                    sachkontonr = str(row.get('Sachkontonr.', '')).strip()
                    sachkonto = row.get('Sachkonto', '').strip()
                    bwa_gruppe = row.get('BWA-Gruppe', '').strip()
                    
                    if not sachkontonr:
                        skipped_count += 1
                        continue
                    
                    # Kontonummer normalisieren
                    normalized_account = self.normalize_account_number(sachkontonr)
                    if not normalized_account:
                        skipped_count += 1
                        continue
                    
                    # Kontoname importieren (falls vorhanden)
                    if sachkonto:
                        self.account_names[normalized_account] = sachkonto
                    
                    # BWA-Gruppe importieren (falls vorhanden)
                    if bwa_gruppe:
                        self.account_mappings[normalized_account] = bwa_gruppe
                    
                    imported_count += 1
            
            # Einstellungen speichern
            self.save_settings()
            
            # Anzeige aktualisieren
            self.refresh_account_list_display()
            
            # Signal senden dass sich Mappings geändert haben
            self.mappings_changed.emit()
            
            # Erfolgsmeldung
            message = f"Import erfolgreich abgeschlossen!\n\n"
            message += f"Importiert: {imported_count} Einträge\n"
            if skipped_count > 0:
                message += f"Übersprungen: {skipped_count} Einträge"
            
            QMessageBox.information(self, "Import erfolgreich", message)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import-Fehler",
                f"Fehler beim Importieren der BWA-Gruppierungen:\n{str(e)}"
            )
    
    def refresh_account_list_display(self):
        """Aktualisiert die Anzeige aller Elemente in der Kontenliste"""
        for i in range(self.accounts_list.count()):
            item = self.accounts_list.item(i)
            if item:
                # Kontonummer aus dem aktuellen Text extrahieren
                account_text = item.text()
                account_number = str(account_text.split(" →")[0].split(" -")[0].strip())
                self.update_account_item_display(item, account_number)
