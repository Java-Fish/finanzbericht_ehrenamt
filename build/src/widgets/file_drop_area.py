# -*- coding: utf-8 -*-
"""
File Drop Area Widget - Ermöglicht Drag & Drop von Dateien
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                               QFileDialog, QFrame)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QPalette, QPixmap
import os


class FileDropArea(QFrame):
    """Widget für Drag & Drop von Dateien"""
    
    # Signal wird ausgesendet wenn eine Datei ausgewählt wurde
    file_selected = Signal(str)
    
    # Signal wird ausgesendet wenn eine neue Datei importiert werden soll
    reset_requested = Signal()
    
    # Signal wird ausgesendet wenn zu den Einstellungen navigiert werden soll
    settings_requested = Signal()
    
    # Signal wird ausgesendet wenn BWA generiert werden soll
    bwa_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.current_file = None  # Aktuell geladene Datei
        self.init_ui()
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        # Frame-Stil setzen
        self.setFrameStyle(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMidLineWidth(1)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # Icon/Bild (Platzhalter)
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setMinimumSize(100, 100)
        self.icon_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaaaaa;
                border-radius: 10px;
                background-color: #f5f5f5;
                color: #666666;
                font-size: 48px;
            }
        """)
        self.icon_label.setText("📁")
        layout.addWidget(self.icon_label)
        
        # Haupttext
        self.main_label = QLabel("Datei hier hineinziehen")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.main_label.setFont(font)
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.main_label)
        
        # Beschreibungstext
        self.desc_label = QLabel(
            "Unterstützte Formate: Excel (.xlsx, .xls), "
            "LibreOffice Calc (.ods), CSV (.csv)"
        )
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.desc_label)
        
        # Oder-Trenner
        separator_label = QLabel("oder")
        separator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator_label.setStyleSheet("color: #999999; font-style: italic;")
        layout.addWidget(separator_label)
        
        # Datei auswählen Button
        self.select_button = QPushButton("Datei auswählen")
        self.select_button.setMinimumHeight(40)
        self.select_button.clicked.connect(self.select_file)
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        layout.addWidget(self.select_button)
        
        # Bereich für importierte Datei-Info (initial versteckt)
        self.file_info_widget = QWidget()
        self.file_info_layout = QVBoxLayout(self.file_info_widget)
        self.file_info_layout.setContentsMargins(0, 0, 0, 0)
        self.file_info_layout.setSpacing(10)
        
        # Import-Status Icon
        self.import_status_label = QLabel()
        self.import_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.import_status_label.setStyleSheet("""
            QLabel {
                border: 2px solid #4CAF50;
                border-radius: 10px;
                background-color: #e8f5e8;
                color: #2e7d32;
                font-size: 32px;
                padding: 20px;
            }
        """)
        self.import_status_label.setText("✅")
        self.file_info_layout.addWidget(self.import_status_label)
        
        # Dateiname
        self.file_name_label = QLabel()
        font_name = QFont()
        font_name.setPointSize(14)
        font_name.setBold(True)
        self.file_name_label.setFont(font_name)
        self.file_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_name_label.setWordWrap(True)
        self.file_name_label.setStyleSheet("color: #2e7d32; margin: 5px;")
        self.file_info_layout.addWidget(self.file_name_label)
        
        # Dateipfad
        self.file_path_label = QLabel()
        self.file_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_path_label.setWordWrap(True)
        self.file_path_label.setStyleSheet("""
            color: #666666; 
            font-size: 11px; 
            margin: 5px;
            background-color: #f5f5f5;
            border-radius: 5px;
            padding: 5px;
        """)
        self.file_info_layout.addWidget(self.file_path_label)
        
        # Status-spezifische Aktionsbuttons
        # Button für Sachkonto-Zuordnung (bei unvollständiger Zuordnung)
        self.mapping_button = QPushButton("Sachkonten zuordnen")
        self.mapping_button.setMinimumHeight(40)
        self.mapping_button.clicked.connect(self.request_settings)
        self.mapping_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 14px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        self.file_info_layout.addWidget(self.mapping_button)
        
        # Button für BWA-Generierung (bei vollständiger Zuordnung)
        self.bwa_button = QPushButton("BWA erstellen")
        self.bwa_button.setMinimumHeight(40)
        self.bwa_button.clicked.connect(self.request_bwa)
        self.bwa_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 14px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #3D8B40;
            }
        """)
        self.file_info_layout.addWidget(self.bwa_button)
        
        # Neue Datei Button (immer vorhanden)
        self.new_file_button = QPushButton("Neue Datei importieren")
        self.new_file_button.setMinimumHeight(35)
        self.new_file_button.clicked.connect(self.request_reset)
        self.new_file_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                font-size: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.file_info_layout.addWidget(self.new_file_button)
        
        # File Info Widget zur Hauptlayout hinzufügen (initial versteckt)
        layout.addWidget(self.file_info_widget)
        self.file_info_widget.hide()
        
        # Mindestgröße setzen
        self.setMinimumSize(400, 300)
        
        # Standard-Stil
        self.set_default_style()
        
    def set_default_style(self):
        """Setzt den Standard-Stil"""
        self.setStyleSheet("""
            FileDropArea {
                background-color: #fafafa;
                border: 2px dashed #cccccc;
                border-radius: 10px;
            }
        """)
        
    def set_hover_style(self):
        """Setzt den Hover-Stil beim Drag-Over"""
        self.setStyleSheet("""
            FileDropArea {
                background-color: #e8f5e8;
                border: 2px dashed #4CAF50;
                border-radius: 10px;
            }
        """)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Wird aufgerufen wenn ein Drag-Operation startet"""
        if event.mimeData().hasUrls():
            # Prüfen ob es sich um unterstützte Dateien handelt
            urls = event.mimeData().urls()
            if len(urls) == 1:  # Nur eine Datei erlaubt
                file_path = urls[0].toLocalFile()
                if self.is_supported_file(file_path):
                    event.acceptProposedAction()
                    self.set_hover_style()
                    return
        event.ignore()
        
    def dragLeaveEvent(self, event):
        """Wird aufgerufen wenn der Drag-Vorgang das Widget verlässt"""
        self.set_default_style()
        
    def dropEvent(self, event: QDropEvent):
        """Wird aufgerufen wenn eine Datei gedroppt wird"""
        self.set_default_style()
        
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                file_path = urls[0].toLocalFile()
                if self.is_supported_file(file_path):
                    self.file_selected.emit(file_path)
                    event.acceptProposedAction()
                    return
        event.ignore()
        
    def select_file(self):
        """Öffnet einen Datei-Dialog zur Auswahl"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Datei auswählen")
        file_dialog.setNameFilter(
            "Tabellendateien (*.xlsx *.xls *.ods *.csv);;"
            "Excel-Dateien (*.xlsx *.xls);;"
            "LibreOffice Calc (*.ods);;"
            "CSV-Dateien (*.csv);;"
            "Alle Dateien (*.*)"
        )
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self.file_selected.emit(file_path)
                
    def is_supported_file(self, file_path):
        """Prüft ob die Datei ein unterstütztes Format hat"""
        if not os.path.isfile(file_path):
            return False
            
        supported_extensions = ['.xlsx', '.xls', '.ods', '.csv']
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in supported_extensions
        
    def show_imported_file(self, file_path, mapping_complete=False):
        """Zeigt an, dass eine Datei erfolgreich importiert wurde
        
        Args:
            file_path: Pfad zur importierten Datei
            mapping_complete: True wenn alle Sachkonten zugeordnet sind
        """
        self.current_file = file_path
        
        # Standard-Elemente verstecken
        self.icon_label.hide()
        self.main_label.hide()
        self.desc_label.hide()
        self.select_button.hide()
        
        # Datei-Info anzeigen
        file_name = os.path.basename(file_path)
        self.file_name_label.setText(f"Importiert: {file_name}")
        
        # Pfad kürzen wenn zu lang
        display_path = file_path
        if len(display_path) > 60:
            display_path = f"...{display_path[-57:]}"
        self.file_path_label.setText(display_path)
        
        # Status-spezifische Anzeige
        if mapping_complete:
            self._show_ready_state()
        else:
            self._show_warning_state()
            
        self.file_info_widget.show()
        
    def _show_warning_state(self):
        """Zeigt den Warnung-Zustand (orange) - Sachkonten nicht vollständig zugeordnet"""
        # Orange Warnung-Icon
        self.import_status_label.setText("⚠️")
        self.import_status_label.setStyleSheet("""
            QLabel {
                border: 2px solid #FF9800;
                border-radius: 10px;
                background-color: #FFF3E0;
                color: #E65100;
                font-size: 32px;
                padding: 20px;
            }
        """)
        
        # Dateiname in Orange
        self.file_name_label.setStyleSheet("color: #E65100; margin: 5px;")
        
        # Mapping-Button anzeigen, BWA-Button verstecken
        self.mapping_button.show()
        self.bwa_button.hide()
        
        # Rahmen-Stil auf Orange setzen
        self.setStyleSheet("""
            FileDropArea {
                background-color: #FFF3E0;
                border: 2px solid #FF9800;
                border-radius: 10px;
            }
        """)
        
    def _show_ready_state(self):
        """Zeigt den Bereit-Zustand (grün) - alle Sachkonten zugeordnet"""
        # Grünes Häkchen
        self.import_status_label.setText("✅")
        self.import_status_label.setStyleSheet("""
            QLabel {
                border: 2px solid #4CAF50;
                border-radius: 10px;
                background-color: #e8f5e8;
                color: #2e7d32;
                font-size: 32px;
                padding: 20px;
            }
        """)
        
        # Dateiname in Grün
        self.file_name_label.setStyleSheet("color: #2e7d32; margin: 5px;")
        
        # BWA-Button anzeigen, Mapping-Button verstecken
        self.bwa_button.show()
        self.mapping_button.hide()
        
        # Rahmen-Stil auf Grün setzen
        self.setStyleSheet("""
            FileDropArea {
                background-color: #e8f5e8;
                border: 2px solid #4CAF50;
                border-radius: 10px;
            }
        """)
        
    def request_settings(self):
        """Sendet Signal für Einstellungen-Anfrage"""
        self.settings_requested.emit()
        
    def request_bwa(self):
        """Sendet Signal für BWA-Generierung"""
        self.bwa_requested.emit()
        
    def reset_to_default(self):
        """Setzt das Widget auf den Standard-Zustand zurück"""
        self.current_file = None
        
        # Datei-Info verstecken
        self.file_info_widget.hide()
        
        # Status-Buttons verstecken
        self.mapping_button.hide()
        self.bwa_button.hide()
        
        # Standard-Elemente anzeigen
        self.icon_label.show()
        self.main_label.show()
        self.desc_label.show()
        self.select_button.show()
        
        # Standard-Stil setzen
        self.set_default_style()
        
    def request_reset(self):
        """Sendet Signal für Reset-Anfrage"""
        self.reset_requested.emit()
        
    def get_current_file(self):
        """Gibt den Pfad der aktuell geladenen Datei zurück"""
        return self.current_file
