# -*- coding: utf-8 -*-
"""
Dialog zur Auswahl eines Arbeitsblatts aus Excel/ODS-Dateien
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QComboBox, QPushButton, QDialogButtonBox,
                              QTextEdit, QSplitter)
from PySide6.QtCore import Qt
import pandas as pd


class SheetSelectionDialog(QDialog):
    """Dialog zur Auswahl eines Arbeitsblatts"""
    
    def __init__(self, file_path, sheet_names, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.sheet_names = sheet_names
        self.selected_sheet = None
        self.preview_data = None
        
        self.setWindowTitle("Arbeitsblatt auswählen")
        self.setModal(True)
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_initial_preview()
        
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        layout = QVBoxLayout(self)
        
        # Dateiname anzeigen
        file_info = QLabel(f"Datei: {self.file_path}")
        file_info.setWordWrap(True)
        layout.addWidget(file_info)
        
        # Anweisungstext
        instruction = QLabel(
            "Diese Datei enthält mehrere Arbeitsblätter. "
            "Wählen Sie das Blatt aus, das die zu importierenden Daten enthält:"
        )
        instruction.setWordWrap(True)
        instruction.setStyleSheet("font-weight: bold; margin: 10px 0px;")
        layout.addWidget(instruction)
        
        # Blatt-Auswahl
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Arbeitsblatt:"))
        
        self.sheet_combo = QComboBox()
        self.sheet_combo.addItems(self.sheet_names)
        self.sheet_combo.currentTextChanged.connect(self.on_sheet_changed)
        selection_layout.addWidget(self.sheet_combo)
        
        # Vorschau-Button
        self.preview_button = QPushButton("Vorschau aktualisieren")
        self.preview_button.clicked.connect(self.load_preview)
        selection_layout.addWidget(self.preview_button)
        
        selection_layout.addStretch()
        layout.addLayout(selection_layout)
        
        # Splitter für Vorschau-Bereiche
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Datenvorschau
        preview_label = QLabel("Datenvorschau (erste 10 Zeilen):")
        preview_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(200)
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(self.get_monospace_font())
        
        preview_widget = self.create_widget_with_label(preview_label, self.preview_text)
        splitter.addWidget(preview_widget)
        
        # Spalten-Info
        columns_label = QLabel("Verfügbare Spalten:")
        columns_label.setStyleSheet("font-weight: bold;")
        
        self.columns_text = QTextEdit()
        self.columns_text.setMaximumHeight(150)
        self.columns_text.setReadOnly(True)
        
        columns_widget = self.create_widget_with_label(columns_label, self.columns_text)
        splitter.addWidget(columns_widget)
        
        layout.addWidget(splitter)
        
        # Dialog-Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
    def create_widget_with_label(self, label, widget):
        """Erstellt ein Widget mit Label"""
        from PySide6.QtWidgets import QWidget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label)
        layout.addWidget(widget)
        return container
        
    def get_monospace_font(self):
        """Gibt eine Monospace-Schriftart zurück"""
        from PySide6.QtGui import QFont
        font = QFont("Courier")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(9)
        return font
        
    def on_sheet_changed(self, sheet_name):
        """Wird aufgerufen wenn ein anderes Blatt ausgewählt wird"""
        if sheet_name:
            self.load_preview()
            
    def load_initial_preview(self):
        """Lädt die initiale Vorschau"""
        if self.sheet_names:
            self.load_preview()
            
    def load_preview(self):
        """Lädt eine Vorschau des ausgewählten Blatts"""
        current_sheet = self.sheet_combo.currentText()
        if not current_sheet:
            return
            
        try:
            self.preview_button.setEnabled(False)
            self.preview_button.setText("Lade Vorschau...")
            
            # Datei einlesen
            file_extension = self.file_path.lower()
            if file_extension.endswith(('.xlsx', '.xls')):
                engine = 'openpyxl' if file_extension.endswith('.xlsx') else 'xlrd'
                df = pd.read_excel(self.file_path, sheet_name=current_sheet, engine=engine)
            elif file_extension.endswith('.ods'):
                df = pd.read_excel(self.file_path, sheet_name=current_sheet, engine='odf')
            else:
                return
                
            self.preview_data = df
            
            # Vorschau aktualisieren
            self.update_preview_display(df)
            
        except Exception as e:
            self.preview_text.setText(f"Fehler beim Laden der Vorschau: {str(e)}")
            self.columns_text.setText("Keine Spalteninformationen verfügbar")
        finally:
            self.preview_button.setEnabled(True)
            self.preview_button.setText("Vorschau aktualisieren")
            
    def update_preview_display(self, df):
        """Aktualisiert die Vorschau-Anzeige"""
        if df is None or df.empty:
            self.preview_text.setText("Das Arbeitsblatt enthält keine Daten.")
            self.columns_text.setText("Keine Spalten verfügbar")
            return
            
        # Datenvorschau (erste 10 Zeilen)
        preview_df = df.head(10)
        preview_str = preview_df.to_string(max_cols=10, max_colwidth=20)
        self.preview_text.setText(preview_str)
        
        # Spalten-Information
        columns_info = []
        columns_info.append(f"Anzahl Spalten: {len(df.columns)}")
        columns_info.append(f"Anzahl Zeilen: {len(df)}")
        columns_info.append("")
        columns_info.append("Spalten:")
        
        for i, col in enumerate(df.columns, 1):
            # Datentyp bestimmen
            dtype = str(df[col].dtype)
            if dtype.startswith('int'):
                dtype_display = "Zahl (ganz)"
            elif dtype.startswith('float'):
                dtype_display = "Zahl (dezimal)"
            elif dtype == 'object':
                dtype_display = "Text"
            elif 'datetime' in dtype:
                dtype_display = "Datum"
            else:
                dtype_display = dtype
                
            columns_info.append(f"{i:2d}. {col} ({dtype_display})")
            
        self.columns_text.setText("\n".join(columns_info))
        
    def accept(self):
        """Bestätigt die Auswahl"""
        self.selected_sheet = self.sheet_combo.currentText()
        super().accept()
        
    def get_selected_sheet(self):
        """Gibt das ausgewählte Blatt zurück"""
        return self.selected_sheet
        
    def get_preview_data(self):
        """Gibt die Vorschau-Daten zurück"""
        return self.preview_data
