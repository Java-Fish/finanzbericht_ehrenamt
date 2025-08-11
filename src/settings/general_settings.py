# -*- coding: utf-8 -*-
"""
Allgemeine Einstellungen Tab
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QGroupBox, QFormLayout, QCheckBox,
                               QPushButton, QFileDialog, QMessageBox, QLineEdit,
                               QColorDialog)
from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor, QPalette, QPixmap, QPainter, QIcon
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
        
        # Darstellungseinstellungen
        appearance_group = QGroupBox("Darstellung")
        appearance_layout = QFormLayout(appearance_group)
        
        # Überschriftenfarbe
        self.create_header_color_controls(appearance_layout)
        
        layout.addWidget(appearance_group)
        
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
            "kumuliere Quartale", 
            "Quartalsweise"
        ])
        self.quarter_mode_combo.setCurrentText("kumuliere Quartale")
        
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
        
    def create_header_color_controls(self, layout):
        """Erstellt die Farbauswahl-Controls für Überschriftenfarbe"""
        
        # Container für RGB-Eingabe und Farbwähler
        color_container = QWidget()
        color_layout = QHBoxLayout(color_container)
        color_layout.setContentsMargins(0, 0, 0, 0)
        
        # RGB-Eingabefelder
        rgb_container = QWidget()
        rgb_layout = QHBoxLayout(rgb_container)
        rgb_layout.setContentsMargins(0, 0, 0, 0)
        
        # R, G, B Labels und Eingabefelder
        rgb_layout.addWidget(QLabel("R:"))
        self.red_input = QLineEdit()
        self.red_input.setMaximumWidth(50)
        self.red_input.setPlaceholderText("0")
        self.red_input.textChanged.connect(self.on_rgb_changed)
        rgb_layout.addWidget(self.red_input)
        
        rgb_layout.addWidget(QLabel("G:"))
        self.green_input = QLineEdit()
        self.green_input.setMaximumWidth(50)
        self.green_input.setPlaceholderText("0")
        self.green_input.textChanged.connect(self.on_rgb_changed)
        rgb_layout.addWidget(self.green_input)
        
        rgb_layout.addWidget(QLabel("B:"))
        self.blue_input = QLineEdit()
        self.blue_input.setMaximumWidth(50)
        self.blue_input.setPlaceholderText("255")
        self.blue_input.textChanged.connect(self.on_rgb_changed)
        rgb_layout.addWidget(self.blue_input)
        
        color_layout.addWidget(rgb_container)
        
        # Farbwähler-Button mit Farbvorschau
        self.color_button = QPushButton()
        self.color_button.setMaximumWidth(40)
        self.color_button.setMaximumHeight(30)
        self.color_button.clicked.connect(self.open_color_dialog)
        self.color_button.setToolTip("Farbwähler öffnen")
        color_layout.addWidget(self.color_button)
        
        # HEX-Eingabefeld
        hex_container = QWidget()
        hex_layout = QHBoxLayout(hex_container)
        hex_layout.setContentsMargins(0, 0, 0, 0)
        
        hex_layout.addWidget(QLabel("HEX:"))
        self.hex_input = QLineEdit()
        self.hex_input.setMaximumWidth(80)
        self.hex_input.setPlaceholderText("#0000FF")
        self.hex_input.textChanged.connect(self.on_hex_changed)
        hex_layout.addWidget(self.hex_input)
        
        color_layout.addWidget(hex_container)
        
        # Standard-Farbe setzen (Blau)
        self.current_color = QColor(0, 0, 255)  # Blau als Standard
        self.update_color_preview()
        self.update_color_fields()
        
        layout.addRow("Überschriftenfarbe:", color_container)
        
    def update_color_preview(self):
        """Aktualisiert die Farbvorschau im Button"""
        pixmap = QPixmap(32, 24)
        pixmap.fill(self.current_color)
        
        # Schwarzen Rahmen hinzufügen
        painter = QPainter(pixmap)
        painter.setPen(QColor(0, 0, 0))
        painter.drawRect(0, 0, 31, 23)
        painter.end()
        
        self.color_button.setIcon(QIcon(pixmap))
        
    def update_color_fields(self):
        """Aktualisiert alle Farbfelder basierend auf der aktuellen Farbe"""
        # RGB-Werte aktualisieren
        self.red_input.blockSignals(True)
        self.green_input.blockSignals(True)
        self.blue_input.blockSignals(True)
        self.hex_input.blockSignals(True)
        
        self.red_input.setText(str(self.current_color.red()))
        self.green_input.setText(str(self.current_color.green()))
        self.blue_input.setText(str(self.current_color.blue()))
        self.hex_input.setText(self.current_color.name().upper())
        
        self.red_input.blockSignals(False)
        self.green_input.blockSignals(False)
        self.blue_input.blockSignals(False)
        self.hex_input.blockSignals(False)
        
    def on_rgb_changed(self):
        """Wird aufgerufen wenn RGB-Werte geändert werden"""
        try:
            r = int(self.red_input.text() or "0")
            g = int(self.green_input.text() or "0") 
            b = int(self.blue_input.text() or "0")
            
            # Werte auf 0-255 begrenzen
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            self.current_color = QColor(r, g, b)
            self.update_color_preview()
            
            # HEX-Feld aktualisieren (ohne Signal zu triggern)
            self.hex_input.blockSignals(True)
            self.hex_input.setText(self.current_color.name().upper())
            self.hex_input.blockSignals(False)
            
        except ValueError:
            # Ungültige Eingabe ignorieren
            pass
            
    def on_hex_changed(self):
        """Wird aufgerufen wenn HEX-Wert geändert wird"""
        hex_text = self.hex_input.text().strip()
        
        # # hinzufügen falls nicht vorhanden
        if hex_text and not hex_text.startswith('#'):
            hex_text = '#' + hex_text
            
        if QColor.isValidColor(hex_text):
            self.current_color = QColor(hex_text)
            self.update_color_preview()
            
            # RGB-Felder aktualisieren (ohne Signale zu triggern)
            self.red_input.blockSignals(True)
            self.green_input.blockSignals(True)
            self.blue_input.blockSignals(True)
            
            self.red_input.setText(str(self.current_color.red()))
            self.green_input.setText(str(self.current_color.green()))
            self.blue_input.setText(str(self.current_color.blue()))
            
            self.red_input.blockSignals(False)
            self.green_input.blockSignals(False)
            self.blue_input.blockSignals(False)
            
    def open_color_dialog(self):
        """Öffnet den Farbwähler-Dialog"""
        color = QColorDialog.getColor(
            self.current_color, 
            self, 
            "Überschriftenfarbe wählen",
            QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        
        if color.isValid():
            self.current_color = color
            self.update_color_preview()
            self.update_color_fields()
        
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
            self.quarter_mode_combo.setCurrentText("kumuliere Quartale")
        else:
            self.quarter_mode_combo.setCurrentText("Quartalsweise")
            
        # Berichterstellungs-Optionen laden
        generate_quarterly = self.settings.value("generate_quarterly_reports", True, type=bool)
        self.generate_quarterly_reports_cb.setChecked(generate_quarterly)
        
        generate_accounts = self.settings.value("generate_account_reports", True, type=bool)
        self.generate_account_reports_cb.setChecked(generate_accounts)
        
        generate_chart = self.settings.value("generate_chart_report", True, type=bool)
        self.generate_chart_report_cb.setChecked(generate_chart)
        
        # Überschriftenfarbe laden
        header_color = self.settings.value("header_color", "#0000FF")  # Standardfarbe Blau
        if QColor.isValidColor(header_color):
            self.current_color = QColor(header_color)
        else:
            self.current_color = QColor(0, 0, 255)  # Fallback auf Blau
        self.update_color_preview()
        self.update_color_fields()
        
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
        quarter_mode = "cumulative" if quarter_mode_text == "kumuliere Quartale" else "quarterly"
        self.settings.setValue("quarter_mode", quarter_mode)
        
        # Berichterstellungs-Optionen speichern
        self.settings.setValue("generate_quarterly_reports", self.generate_quarterly_reports_cb.isChecked())
        self.settings.setValue("generate_account_reports", self.generate_account_reports_cb.isChecked())
        self.settings.setValue("generate_chart_report", self.generate_chart_report_cb.isChecked())
        
        # Überschriftenfarbe speichern
        self.settings.setValue("header_color", self.current_color.name())
        
        # Sicherstellen, dass alle Änderungen persistent gespeichert werden
        self.settings.sync()
        
    def reset_to_defaults(self):
        """Setzt die Einstellungen auf Standard zurück"""
        self.language_combo.setCurrentText("Deutsch")
        self.decimal_combo.setCurrentText(",")
        self.csv_separator_combo.setCurrentText(";")
        self.quarter_mode_combo.setCurrentText("kumuliere Quartale")
        self.generate_quarterly_reports_cb.setChecked(True)
        self.generate_account_reports_cb.setChecked(True)
        
        # Überschriftenfarbe auf Standard zurücksetzen
        self.current_color = QColor(0, 0, 255)  # Blau
        self.update_color_preview()
        self.update_color_fields()
        
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
