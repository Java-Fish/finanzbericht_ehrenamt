# -*- coding: utf-8 -*-
"""
Zuordnungseinstellungen Tab - für die Spalten-Zuordnung
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QScrollArea, QGroupBox, QFormLayout)
from PySide6.QtCore import QSettings, Qt


class MappingSettingsTab(QWidget):
    """Tab für Spalten-Zuordnungseinstellungen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.mapping_widgets = {}
        self.init_ui()
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Beschreibung
        description = QLabel(
            "Ordnen Sie die Spalten Ihrer Tabelle den erwarteten Bezeichnungen zu.\n"
            "Links stehen die erwarteten Spaltenbezeichnungen, rechts tragen Sie "
            "die entsprechenden Spaltennamen aus Ihrer Datei ein."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #666666; margin-bottom: 10px;")
        layout.addWidget(description)
        
        # Scroll-Bereich für die Zuordnungen
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Zuordnungsgruppe
        mapping_group = QGroupBox("Spalten-Zuordnungen")
        mapping_layout = QFormLayout(mapping_group)
        mapping_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        mapping_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # Erwartete Spaltenbezeichnungen
        expected_columns = [
            ("Buchungsnummer", "booking_number"),
            ("Sachkontonummer", "account_number"),
            ("Sachkonto", "account_name"),
            ("Buchungstag", "booking_date"),
            ("Verwendungszweck", "purpose"),
            ("Begünstigter/Zahlungspflichtiger", "counterpart"),
            ("Kontonummer/IBAN", "iban"),
            ("BIC (SWIFT-Code)", "bic"),
            ("Betrag", "amount")
        ]
        
        # Eingabefelder für jede erwartete Spalte erstellen
        for display_name, key in expected_columns:
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Spaltenname für '{display_name}'")
            
            # Tooltip mit zusätzlichen Informationen
            tooltip_texts = {
                "booking_number": "Eindeutige Kennung der Buchung",
                "account_number": "Nummer des Sachkontos (z.B. 4711)",
                "account_name": "Bezeichnung des Sachkontos (z.B. 'Büromaterial')",
                "booking_date": "Datum der Buchung (verschiedene Formate werden erkannt)",
                "purpose": "Verwendungszweck oder Buchungstext",
                "counterpart": "Name des Zahlungsempfängers oder -pflichtigen",
                "iban": "IBAN oder Kontonummer",
                "bic": "BIC/SWIFT-Code der Bank",
                "amount": "Betrag (positiv oder negativ)"
            }
            
            if key in tooltip_texts:
                line_edit.setToolTip(tooltip_texts[key])
            
            self.mapping_widgets[key] = line_edit
            
            # Label mit besserer Formatierung
            label = QLabel(f"{display_name}:")
            label.setMinimumWidth(200)
            label.setStyleSheet("font-weight: bold;")
            
            mapping_layout.addRow(label, line_edit)
        
        scroll_layout.addWidget(mapping_group)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
    def load_settings(self):
        """Lädt die Einstellungen"""
        for key, widget in self.mapping_widgets.items():
            value = self.settings.value(f"mapping/{key}", "")
            widget.setText(value)
            
    def save_settings(self):
        """Speichert die Einstellungen"""
        for key, widget in self.mapping_widgets.items():
            value = widget.text().strip()
            self.settings.setValue(f"mapping/{key}", value)
        
        # Sicherstellen, dass alle Änderungen persistent gespeichert werden
        self.settings.sync()
            
    def reset_to_defaults(self):
        """Setzt die Einstellungen auf Standard zurück"""
        # Standard-Zuordnungen (typische deutsche Spaltenbezeichnungen)
        defaults = {
            "booking_number": "Buchungsnummer",
            "account_number": "Sachkonto",
            "account_name": "Sachkontobezeichnung", 
            "booking_date": "Buchungstag",
            "purpose": "Verwendungszweck",
            "counterpart": "Empfänger",
            "iban": "IBAN",
            "bic": "BIC",
            "amount": "Betrag"
        }
        
        for key, widget in self.mapping_widgets.items():
            default_value = defaults.get(key, "")
            widget.setText(default_value)
