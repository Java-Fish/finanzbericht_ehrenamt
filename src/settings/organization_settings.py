# -*- coding: utf-8 -*-
"""
Organisationseinstellungen Tab
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QTextEdit, QPushButton, QGroupBox, 
                               QFormLayout, QFileDialog, QFrame)
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QPixmap
import os


class OrganizationSettingsTab(QWidget):
    """Tab für Organisationseinstellungen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.logo_path = None
        self.init_ui()
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Grunddaten der Organisation
        basic_group = QGroupBox("Grunddaten")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Name der Organisation")
        basic_layout.addRow("Name:", self.name_edit)
        
        self.street_edit = QLineEdit()
        self.street_edit.setPlaceholderText("Straße und Hausnummer")
        basic_layout.addRow("Straße:", self.street_edit)
        
        self.zip_edit = QLineEdit()
        self.zip_edit.setPlaceholderText("Postleitzahl")
        basic_layout.addRow("PLZ:", self.zip_edit)
        
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("Stadt")
        basic_layout.addRow("Stadt:", self.city_edit)
        
        layout.addWidget(basic_group)
        
        # Kontaktdaten
        contact_group = QGroupBox("Kontaktdaten")
        contact_layout = QFormLayout(contact_group)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("organisation@beispiel.de")
        contact_layout.addRow("E-Mail:", self.email_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+49 123 456789")
        contact_layout.addRow("Telefon:", self.phone_edit)
        
        layout.addWidget(contact_group)
        
        # Kontostand
        balance_group = QGroupBox("Kontostand")
        balance_layout = QFormLayout(balance_group)
        
        self.opening_balance_input = QLineEdit()
        self.opening_balance_input.setText("0,00")
        self.opening_balance_input.setPlaceholderText("0,00")
        balance_layout.addRow("Kontostand zum 01.01.:", self.opening_balance_input)
        
        layout.addWidget(balance_group)
        
        # Weitere Informationen
        info_group = QGroupBox("Weitere Informationen")
        info_layout = QVBoxLayout(info_group)
        
        self.info_edit = QTextEdit()
        self.info_edit.setPlaceholderText(
            "Weitere Informationen über die Organisation...\n"
            "Zweck, Aktivitäten, besondere Hinweise etc."
        )
        self.info_edit.setMaximumHeight(100)
        info_layout.addWidget(self.info_edit)
        
        layout.addWidget(info_group)
        
        # Logo
        logo_group = QGroupBox("Logo")
        logo_layout = QVBoxLayout(logo_group)
        
        # Logo Vorschau
        self.logo_frame = QFrame()
        self.logo_frame.setFrameStyle(QFrame.Shape.Box)
        self.logo_frame.setMinimumSize(150, 150)
        self.logo_frame.setMaximumSize(150, 150)
        self.logo_frame.setStyleSheet("""
            QFrame {
                border: 2px dashed #cccccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
        """)
        
        logo_frame_layout = QVBoxLayout(self.logo_frame)
        self.logo_label = QLabel("Kein Logo")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet("border: none; color: #666666;")
        logo_frame_layout.addWidget(self.logo_label)
        
        # Logo Buttons
        logo_button_layout = QHBoxLayout()
        
        self.logo_select_button = QPushButton("Logo auswählen")
        self.logo_select_button.clicked.connect(self.select_logo)
        logo_button_layout.addWidget(self.logo_select_button)
        
        self.logo_remove_button = QPushButton("Logo entfernen")
        self.logo_remove_button.clicked.connect(self.remove_logo)
        self.logo_remove_button.setEnabled(False)
        logo_button_layout.addWidget(self.logo_remove_button)
        
        # Logo Layout zusammenfügen
        logo_top_layout = QHBoxLayout()
        logo_top_layout.addWidget(self.logo_frame)
        logo_top_layout.addStretch()
        
        logo_layout.addLayout(logo_top_layout)
        logo_layout.addLayout(logo_button_layout)
        
        layout.addWidget(logo_group)
        
        # Spacer am Ende
        layout.addStretch()
        
    def select_logo(self):
        """Öffnet Dialog zur Logo-Auswahl"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Logo auswählen")
        file_dialog.setNameFilter(
            "Bilddateien (*.png *.jpg *.jpeg *.svg);;"
            "PNG-Dateien (*.png);;"
            "JPEG-Dateien (*.jpg *.jpeg);;"
            "SVG-Dateien (*.svg);;"
            "Alle Dateien (*.*)"
        )
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.logo_path = selected_files[0]
                self.update_logo_preview()
                
    def remove_logo(self):
        """Entfernt das aktuelle Logo"""
        self.logo_path = None
        self.update_logo_preview()
        
    def update_logo_preview(self):
        """Aktualisiert die Logo-Vorschau"""
        if self.logo_path and os.path.exists(self.logo_path):
            # Logo laden und skalieren
            pixmap = QPixmap(self.logo_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    140, 140, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.logo_label.setPixmap(scaled_pixmap)
                self.logo_label.setText("")
                self.logo_remove_button.setEnabled(True)
            else:
                self.logo_label.setText("Fehler beim Laden")
                self.logo_remove_button.setEnabled(False)
        else:
            self.logo_label.clear()
            self.logo_label.setText("Kein Logo")
            self.logo_remove_button.setEnabled(False)
            
    def load_settings(self):
        """Lädt die Einstellungen"""
        self.name_edit.setText(self.settings.value("organization/name", ""))
        self.street_edit.setText(self.settings.value("organization/street", ""))
        self.zip_edit.setText(self.settings.value("organization/zip", ""))
        self.city_edit.setText(self.settings.value("organization/city", ""))
        self.email_edit.setText(self.settings.value("organization/email", ""))
        self.phone_edit.setText(self.settings.value("organization/phone", ""))
        self.info_edit.setPlainText(self.settings.value("organization/info", ""))
        
        # Anfangskontostand laden
        opening_balance = self.settings.value("opening_balance", 0.0, type=float)
        # Deutsche Formatierung anzeigen
        opening_balance_text = f"{opening_balance:.2f}".replace(".", ",")
        self.opening_balance_input.setText(opening_balance_text)
        
        # Logo laden
        self.logo_path = self.settings.value("organization/logo_path", None)
        self.update_logo_preview()
        
    def save_settings(self):
        """Speichert die Einstellungen"""
        self.settings.setValue("organization/name", self.name_edit.text())
        self.settings.setValue("organization/street", self.street_edit.text())
        self.settings.setValue("organization/zip", self.zip_edit.text())
        self.settings.setValue("organization/city", self.city_edit.text())
        self.settings.setValue("organization/email", self.email_edit.text())
        self.settings.setValue("organization/phone", self.phone_edit.text())
        self.settings.setValue("organization/info", self.info_edit.toPlainText())
        self.settings.setValue("organization/logo_path", self.logo_path or "")
        
        # Anfangskontostand speichern
        opening_balance_text = self.opening_balance_input.text().strip()
        # Deutsche Dezimalformatierung in Float umwandeln
        try:
            opening_balance = float(opening_balance_text.replace(",", ".").replace(" ", ""))
        except ValueError:
            opening_balance = 0.0
        self.settings.setValue("opening_balance", opening_balance)
        
        # Sicherstellen, dass alle Änderungen persistent gespeichert werden
        self.settings.sync()
        
    def reset_to_defaults(self):
        """Setzt die Einstellungen auf Standard zurück"""
        self.name_edit.clear()
        self.street_edit.clear()
        self.zip_edit.clear()
        self.city_edit.clear()
        self.email_edit.clear()
        self.phone_edit.clear()
        self.info_edit.clear()
        self.opening_balance_input.setText("0,00")
        self.logo_path = None
        self.update_logo_preview()
