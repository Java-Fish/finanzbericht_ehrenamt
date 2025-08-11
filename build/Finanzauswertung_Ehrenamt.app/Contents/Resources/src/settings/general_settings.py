# -*- coding: utf-8 -*-
"""
Allgemeine Einstellungen Tab
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QGroupBox, QFormLayout, QCheckBox,
                               QPushButton, QFileDialog, QMessageBox)
from PySide6.QtCore import QSettings
import json


class GeneralSettingsTab(QWidget):
    """Tab für allgemeine Einstellungen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.init_ui()
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Spracheinstellungen
        language_group = QGroupBox("Sprache")
        language_layout = QFormLayout(language_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Deutsch", "English"])
        self.language_combo.setCurrentText("Deutsch")
        
        language_layout.addRow("Sprache:", self.language_combo)
        layout.addWidget(language_group)
        
        # Zahlenformat
        number_group = QGroupBox("Zahlenformat")
        number_layout = QFormLayout(number_group)
        
        self.decimal_combo = QComboBox()
        self.decimal_combo.addItems([",", "."])
        self.decimal_combo.setCurrentText(",")
        
        number_layout.addRow("Kommatrennzeichen:", self.decimal_combo)
        layout.addWidget(number_group)
        
        # CSV-Einstellungen
        csv_group = QGroupBox("CSV-Import")
        csv_layout = QFormLayout(csv_group)
        
        self.csv_separator_combo = QComboBox()
        self.csv_separator_combo.addItems([";", ",", "Tab"])
        self.csv_separator_combo.setCurrentText(";")
        
        csv_layout.addRow("Spaltentrennzeichen:", self.csv_separator_combo)
        layout.addWidget(csv_group)
        
        # Quartalsauswertung
        quarter_group = QGroupBox("Quartalsauswertung")
        quarter_layout = QFormLayout(quarter_group)
        
        self.quarter_mode_combo = QComboBox()
        self.quarter_mode_combo.addItems([
            "ältere Quartale einschließend", 
            "Quartalsweise"
        ])
        self.quarter_mode_combo.setCurrentText("ältere Quartale einschließend")
        
        quarter_layout.addRow("Berechnungsmodus:", self.quarter_mode_combo)
        layout.addWidget(quarter_group)
        
        # Berichterstellung
        reports_group = QGroupBox("Berichterstellung")
        reports_layout = QFormLayout(reports_group)
        
        self.generate_quarterly_reports_cb = QCheckBox()
        self.generate_quarterly_reports_cb.setChecked(True)
        reports_layout.addRow("Quartalsberichte erstellen:", self.generate_quarterly_reports_cb)
        
        self.generate_account_reports_cb = QCheckBox()
        self.generate_account_reports_cb.setChecked(True)
        reports_layout.addRow("Sachkontenberichte erstellen:", self.generate_account_reports_cb)
        
        self.generate_chart_report_cb = QCheckBox()
        self.generate_chart_report_cb.setChecked(True)
        reports_layout.addRow("Balkendiagramm erstellen:", self.generate_chart_report_cb)
        
        layout.addWidget(reports_group)
        
        # Einstellungen Export/Import
        settings_group = QGroupBox("Einstellungen verwalten")
        settings_layout = QVBoxLayout(settings_group)
        
        export_import_layout = QHBoxLayout()
        
        self.export_settings_btn = QPushButton("Einstellungen exportieren")
        self.export_settings_btn.clicked.connect(self.export_settings)
        export_import_layout.addWidget(self.export_settings_btn)
        
        self.import_settings_btn = QPushButton("Einstellungen importieren")
        self.import_settings_btn.clicked.connect(self.import_settings)
        export_import_layout.addWidget(self.import_settings_btn)
        
        settings_layout.addLayout(export_import_layout)
        layout.addWidget(settings_group)
        
        # Spacer am Ende
        layout.addStretch()
        
    def load_settings(self):
        """Lädt die Einstellungen"""
        # Sprache laden
        language = self.settings.value("language", "de")
        if language == "de":
            self.language_combo.setCurrentText("Deutsch")
        else:
            self.language_combo.setCurrentText("English")
            
        # Dezimaltrennzeichen laden
        decimal_separator = self.settings.value("decimal_separator", ",")
        self.decimal_combo.setCurrentText(decimal_separator)
        
        # CSV-Trennzeichen laden
        csv_separator = self.settings.value("csv_separator", ";")
        # Tab-Character als "Tab" anzeigen
        if csv_separator == "\t":
            csv_separator = "Tab"
        self.csv_separator_combo.setCurrentText(csv_separator)
        
        # Quartalsauswertungs-Modus laden
        quarter_mode = self.settings.value("quarter_mode", "cumulative")
        if quarter_mode == "cumulative":
            self.quarter_mode_combo.setCurrentText("ältere Quartale einschließend")
        else:
            self.quarter_mode_combo.setCurrentText("Quartalsweise")
            
        # Berichterstellungs-Optionen laden
        generate_quarterly = self.settings.value("generate_quarterly_reports", True, type=bool)
        self.generate_quarterly_reports_cb.setChecked(generate_quarterly)
        
        generate_accounts = self.settings.value("generate_account_reports", True, type=bool)
        self.generate_account_reports_cb.setChecked(generate_accounts)
        
        generate_chart = self.settings.value("generate_chart_report", True, type=bool)
        self.generate_chart_report_cb.setChecked(generate_chart)
        
    def save_settings(self):
        """Speichert die Einstellungen"""
        # Sprache speichern
        language_text = self.language_combo.currentText()
        language_code = "de" if language_text == "Deutsch" else "en"
        self.settings.setValue("language", language_code)
        
        # Dezimaltrennzeichen speichern
        decimal_separator = self.decimal_combo.currentText()
        self.settings.setValue("decimal_separator", decimal_separator)
        
        # CSV-Trennzeichen speichern
        csv_separator = self.csv_separator_combo.currentText()
        # Tab als '\t' speichern
        if csv_separator == "Tab":
            csv_separator = "\t"
        self.settings.setValue("csv_separator", csv_separator)
        
        # Quartalsauswertungs-Modus speichern
        quarter_mode_text = self.quarter_mode_combo.currentText()
        quarter_mode = "cumulative" if quarter_mode_text == "ältere Quartale einschließend" else "quarterly"
        self.settings.setValue("quarter_mode", quarter_mode)
        
        # Berichterstellungs-Optionen speichern
        self.settings.setValue("generate_quarterly_reports", self.generate_quarterly_reports_cb.isChecked())
        self.settings.setValue("generate_account_reports", self.generate_account_reports_cb.isChecked())
        self.settings.setValue("generate_chart_report", self.generate_chart_report_cb.isChecked())
        
    def reset_to_defaults(self):
        """Setzt die Einstellungen auf Standard zurück"""
        self.language_combo.setCurrentText("Deutsch")
        self.decimal_combo.setCurrentText(",")
        self.csv_separator_combo.setCurrentText(";")
        self.quarter_mode_combo.setCurrentText("ältere Quartale einschließend")
        self.generate_quarterly_reports_cb.setChecked(True)
        self.generate_account_reports_cb.setChecked(True)
        
    def export_settings(self):
        """Exportiert alle Anwendungseinstellungen in eine JSON-Datei"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Einstellungen exportieren",
            "einstellungen_export.json",
            "JSON-Dateien (*.json);;Alle Dateien (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Alle Einstellungen sammeln
            export_data = {}
            
            # QSettings auslesen
            self.settings.sync()
            all_keys = self.settings.allKeys()
            
            for key in all_keys:
                value = self.settings.value(key)
                
                # Verschiedene Datentypen für JSON serialisierbar machen
                if hasattr(value, 'toString'):  # QDateTime, QDate, etc.
                    export_data[key] = value.toString()
                elif isinstance(value, bool):
                    export_data[key] = value
                elif value is None:
                    export_data[key] = None
                else:
                    export_data[key] = str(value)
                    
            # JSON-Datei schreiben
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
            QMessageBox.information(
                self,
                "Export erfolgreich",
                f"Einstellungen wurden erfolgreich exportiert nach:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export fehlgeschlagen",
                f"Fehler beim Exportieren der Einstellungen:\n{str(e)}"
            )
            
    def import_settings(self):
        """Importiert Anwendungseinstellungen aus einer JSON-Datei"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Einstellungen importieren",
            "",
            "JSON-Dateien (*.json);;Alle Dateien (*)"
        )
        
        if not file_path:
            return
            
        # Sicherheitsabfrage
        reply = QMessageBox.question(
            self,
            "Einstellungen importieren",
            "Möchten Sie wirklich alle aktuellen Einstellungen durch die importierten ersetzen?\n\n"
            "Diese Aktion kann nicht rückgängig gemacht werden.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        try:
            # JSON-Datei lesen
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
                
            # Aktuelle Einstellungen löschen
            self.settings.clear()
            
            # Importierte Einstellungen setzen
            for key, value in import_data.items():
                self.settings.setValue(key, value)
                
            self.settings.sync()
            
            # UI aktualisieren
            self.load_settings()
            
            QMessageBox.information(
                self,
                "Import erfolgreich",
                f"Einstellungen wurden erfolgreich importiert aus:\n{file_path}\n\n"
                "Bitte starten Sie die Anwendung neu, damit alle Änderungen wirksam werden."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import fehlgeschlagen",
                f"Fehler beim Importieren der Einstellungen:\n{str(e)}"
            )
