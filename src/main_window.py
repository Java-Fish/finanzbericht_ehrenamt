# -*- coding: utf-8 -*-
"""
Hauptfenster der Finanzauswertung Anwendung
"""

from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QMenuBar, 
                               QMenu, QLabel, QFrame, QApplication, QMessageBox,
                               QFileDialog, QProgressDialog, QDialog)
from PySide6.QtCore import Qt, QSettings, QTimer, QEasingCurve, QPropertyAnimation, QRect
from PySide6.QtGui import QAction, QFont, QDragEnterEvent, QDropEvent
import os

from .widgets.file_drop_area import FileDropArea
from .settings.settings_window import SettingsWindow
from .dialogs.about_dialog import AboutDialog
from .utils.file_handler import FileHandler
from .utils.csv_processor import CSVProcessor
from .utils.bwa_generator import BWAPDFGenerator
from .utils.icon_helper import get_app_icon


class MainWindow(QMainWindow):
    """Hauptfenster der Anwendung"""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        self.settings_window = None
        self.file_handler = FileHandler()
        self.csv_processor = CSVProcessor()
        self.bwa_generator = BWAPDFGenerator()
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        self.setWindowTitle("Finanzauswertung Ehrenamt")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Window Icon setzen
        self.setWindowIcon(get_app_icon())
        
        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Menüleiste erstellen
        self.create_menu_bar()
        
        # File Drop Area
        self.file_drop_area = FileDropArea()
        self.file_drop_area.file_selected.connect(self.handle_file_selection)
        self.file_drop_area.reset_requested.connect(self.reset_csv_data)
        self.file_drop_area.settings_requested.connect(self.open_mapping_settings)
        self.file_drop_area.bwa_requested.connect(self.generate_bwa)
        layout.addWidget(self.file_drop_area)
        
        # Drag and Drop aktivieren
        self.setAcceptDrops(True)
        
    def create_menu_bar(self):
        """Erstellt die Menüleiste"""
        menubar = self.menuBar()
        
        # Einstellungen Menü
        settings_menu = menubar.addMenu("Einstellungen")
        settings_action = QAction("Einstellungen öffnen", self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)
        
        # Über Menü
        about_menu = menubar.addMenu("Über")
        about_action = QAction("Über diese Anwendung", self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)
        
    def open_settings(self):
        """Öffnet das Einstellungsfenster mit Animation"""
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self)
            
        # Animation für das Fenster
        self.animate_window_transition()
        
        # Einstellungsfenster anzeigen
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
        
    def animate_window_transition(self):
        """Animiert den Übergang zum Einstellungsfenster"""
        # Einfache Rotation Animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Aktuelle Geometrie als Startpunkt
        current_geometry = self.geometry()
        
        # Ziel-Geometrie (leicht verschoben für visuellen Effekt)
        target_geometry = QRect(
            current_geometry.x() + 20,
            current_geometry.y() + 20,
            current_geometry.width(),
            current_geometry.height()
        )
        
        self.animation.setStartValue(current_geometry)
        self.animation.setEndValue(target_geometry)
        
        # Animation zurück zur ursprünglichen Position
        def reset_position():
            reset_animation = QPropertyAnimation(self, b"geometry")
            reset_animation.setDuration(300)
            reset_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            reset_animation.setStartValue(target_geometry)
            reset_animation.setEndValue(current_geometry)
            reset_animation.start()
            
        self.animation.finished.connect(reset_position)
        self.animation.start()
        
    def show_about(self):
        """Zeigt den Über-Dialog"""
        dialog = AboutDialog(self)
        dialog.exec()
        
    def import_file(self):
        """Importiert eine Datei (CSV, Excel, ODS) für BWA-Analyse"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Datei importieren")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter(
            "Tabellendateien (*.xlsx *.xls *.ods *.csv);;"
            "Excel-Dateien (*.xlsx *.xls);;"
            "LibreOffice Calc (*.ods);;"
            "CSV-Dateien (*.csv);;"
            "Alle Dateien (*)"
        )
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                self.process_file(file_paths[0])
                
    def import_csv_file(self):
        """Legacy-Methode für CSV-Import (für Kompatibilität)"""
        self.import_file()
                
    def generate_bwa(self):
        """Generiert ein BWA-PDF"""
        if self.csv_processor.processed_data is None:
            QMessageBox.warning(
                self, 
                "Keine Daten", 
                "Bitte importieren Sie zuerst eine CSV-Datei."
            )
            return
            
        # Sachkonten-Mappings aus Einstellungen holen
        if not self.settings_window:
            self.settings_window = SettingsWindow(self)
            
        account_mappings = self.settings_window.account_mapping_tab.get_account_mappings()
        
        # Bei direktem Aufruf sollten alle Sachkonten zugeordnet sein
        # Falls nicht, trotzdem nachfragen
        if not self.check_mapping_completeness():
            result = QMessageBox.question(
                self,
                "Unvollständige Zuordnung", 
                "Nicht alle Sachkonten sind BWA-Gruppen zugeordnet.\n\n"
                "Möchten Sie trotzdem eine BWA erstellen? "
                "Nicht zugeordnete Sachkonten werden als 'Nicht zugeordnet' angezeigt.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if result == QMessageBox.StandardButton.No:
                return
            
        # Speicherort für PDF wählen
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("BWA-PDF speichern")
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setNameFilter("PDF-Dateien (*.pdf)")
        file_dialog.setDefaultSuffix("pdf")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                self.create_bwa_pdf(file_paths[0], account_mappings)
                
    def create_bwa_pdf(self, output_path: str, account_mappings: dict):
        """Erstellt das BWA-PDF"""
        # Progress Dialog
        progress = QProgressDialog("BWA-PDF wird erstellt...", "Abbrechen", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(True)
        progress.setAutoReset(True)
        progress.show()
        
        try:
            progress.setValue(10)
            QApplication.processEvents()
            
            # PDF generieren
            success = self.bwa_generator.generate_bwa_pdf(
                output_path, 
                self.csv_processor, 
                account_mappings
            )
            
            progress.setValue(100)
            QApplication.processEvents()
            
            if success:
                QMessageBox.information(
                    self,
                    "Erfolgreich",
                    f"BWA-PDF wurde erfolgreich erstellt:\n{output_path}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Fehler",
                    "Bei der PDF-Erstellung ist ein Fehler aufgetreten."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Bei der PDF-Erstellung ist ein Fehler aufgetreten:\n{str(e)}"
            )
        finally:
            progress.close()
            
    def process_csv_file(self, file_path: str):
        """Verarbeitet eine CSV-Datei"""
        progress = QProgressDialog("CSV-Datei wird verarbeitet...", "Abbrechen", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(True)
        progress.setAutoReset(True)
        progress.show()
        
        try:
            progress.setValue(20)
            QApplication.processEvents()
            
            # CSV verarbeiten
            success = self.csv_processor.load_csv_file(file_path)
            
            progress.setValue(60)
            QApplication.processEvents()
            
            if success:
                # Sachkonten-Liste aktualisieren
                account_numbers = self.csv_processor.get_account_numbers()
                
                if not self.settings_window:
                    self.settings_window = SettingsWindow(self)
                    # Signal für Mapping-Änderungen verbinden
                    self.settings_window.account_mapping_tab.mappings_changed.connect(self.update_file_status)
                    
                self.settings_window.update_account_mappings(account_numbers)
                
                progress.setValue(100)
                QApplication.processEvents()
                
                # Mapping-Status prüfen
                mapping_complete = self.check_mapping_completeness()
                
                # Datei-Status im Drop-Bereich anzeigen
                self.file_drop_area.show_imported_file(file_path, mapping_complete)
                
                # Unterschiedliche Nachrichten je nach Zuordnungsstatus
                if mapping_complete:
                    QMessageBox.information(
                        self,
                        "Erfolgreich",
                        f"CSV-Datei wurde erfolgreich importiert.\n\n"
                        f"Anzahl Datensätze: {len(self.csv_processor.processed_data)}\n"
                        f"Anzahl Sachkonten: {len(account_numbers)}\n\n"
                        f"✅ Alle Sachkonten sind BWA-Gruppen zugeordnet.\n"
                        f"Sie können nun eine BWA erstellen."
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Import erfolgreich - Zuordnung erforderlich",
                        f"CSV-Datei wurde erfolgreich importiert.\n\n"
                        f"Anzahl Datensätze: {len(self.csv_processor.processed_data)}\n"
                        f"Anzahl Sachkonten: {len(account_numbers)}\n\n"
                        f"⚠️ Nicht alle Sachkonten sind BWA-Gruppen zugeordnet.\n"
                        f"Bitte ordnen Sie die Sachkonten in den Einstellungen zu."
                    )
            else:
                QMessageBox.critical(
                    self,
                    "Fehler",
                    "Die CSV-Datei konnte nicht verarbeitet werden.\n\n"
                    "Bitte prüfen Sie:\n"
                    "- Das CSV-Trennzeichen in den Einstellungen\n"
                    "- Ob die Spalten 'Sachkontonr.', 'Betrag' und 'Buchungstag' vorhanden sind"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Bei der Verarbeitung ist ein Fehler aufgetreten:\n{str(e)}"
            )
        finally:
            progress.close()
        
    def handle_file_selection(self, file_path):
        """Behandelt die Auswahl einer Datei"""
        if file_path and os.path.exists(file_path):
            self.process_file(file_path)
                
    def process_file(self, file_path: str):
        """Verarbeitet eine Datei (CSV, Excel, ODS)"""
        try:
            # Prüfen ob die Datei mehrere Arbeitsblätter hat
            sheet_name = None
            if self.csv_processor.has_multiple_sheets(file_path):
                sheet_names = self.csv_processor.get_sheet_names(file_path)
                if sheet_names and len(sheet_names) > 1:
                    # Blatt-Auswahl-Dialog anzeigen
                    from .dialogs.sheet_selection_dialog import SheetSelectionDialog
                    dialog = SheetSelectionDialog(file_path, sheet_names, self)
                    
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        sheet_name = dialog.get_selected_sheet()
                    else:
                        return  # Benutzer hat abgebrochen
                elif sheet_names:
                    # Nur ein Blatt vorhanden, automatisch verwenden
                    sheet_name = sheet_names[0]
            
            # Datei verarbeiten
            self.process_file_with_sheet(file_path, sheet_name)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler beim Datei-Import",
                f"Fehler beim Verarbeiten der Datei:\n{str(e)}"
            )
            
    def process_file_with_sheet(self, file_path: str, sheet_name: str = None):
        """Verarbeitet eine Datei mit dem angegebenen Arbeitsblatt"""
        file_ext = os.path.splitext(file_path)[1].lower()
        file_type = "CSV-Datei" if file_ext == '.csv' else "Datei"
        
        progress = QProgressDialog(f"{file_type} wird verarbeitet...", "Abbrechen", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(True)
        progress.setAutoReset(True)
        progress.show()
        
        try:
            progress.setValue(20)
            QApplication.processEvents()
            
            # Datei verarbeiten
            success = self.csv_processor.load_file(file_path, sheet_name)
            
            progress.setValue(60)
            QApplication.processEvents()
            
            if success:
                # Sachkonten-Liste aktualisieren
                account_numbers = self.csv_processor.get_account_numbers()
                account_names = self.csv_processor.get_all_account_names()
                
                if not self.settings_window:
                    self.settings_window = SettingsWindow(self)
                    # Signal für Mapping-Änderungen verbinden
                    self.settings_window.account_mapping_tab.mappings_changed.connect(self.update_file_status)
                    
                self.settings_window.update_account_mappings(account_numbers, account_names)
                
                progress.setValue(100)
                QApplication.processEvents()
                
                # Mapping-Status prüfen
                mapping_complete = self.check_mapping_completeness()
                
                # Datei-Status im Drop-Bereich anzeigen
                sheet_info = f" (Blatt: {sheet_name})" if sheet_name else ""
                display_path = f"{file_path}{sheet_info}"
                self.file_drop_area.show_imported_file(display_path, mapping_complete)
                
                # Unterschiedliche Nachrichten je nach Zuordnungsstatus
                if mapping_complete:
                    QMessageBox.information(
                        self,
                        "Erfolgreich",
                        f"{file_type} wurde erfolgreich importiert.\n\n"
                        f"Anzahl Datensätze: {len(self.csv_processor.processed_data)}\n"
                        f"Anzahl Sachkonten: {len(account_numbers)}\n"
                        f"{sheet_info}\n\n"
                        f"✅ Alle Sachkonten sind BWA-Gruppen zugeordnet.\n"
                        f"Sie können nun eine BWA erstellen."
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Import erfolgreich - Zuordnung erforderlich",
                        f"{file_type} wurde erfolgreich importiert.\n\n"
                        f"Anzahl Datensätze: {len(self.csv_processor.processed_data)}\n"
                        f"Anzahl Sachkonten: {len(account_numbers)}\n"
                        f"{sheet_info}\n\n"
                        f"⚠️ Nicht alle Sachkonten sind BWA-Gruppen zugeordnet.\n"
                        f"Bitte ordnen Sie die Sachkonten in den Einstellungen zu."
                    )
            else:
                QMessageBox.critical(
                    self,
                    "Fehler",
                    f"Die {file_type} konnte nicht verarbeitet werden.\n\n"
                    f"Bitte prüfen Sie:\n"
                    f"- Das Dateiformat\n"
                    f"- Ob die Spalten 'Sachkontonr.', 'Betrag' und 'Buchungstag' vorhanden sind"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Bei der Verarbeitung ist ein Fehler aufgetreten:\n{str(e)}"
            )
        finally:
            progress.close()
                
    def reset_csv_data(self):
        """Setzt die CSV-Daten zurück und zeigt das Standard-Drop-Area"""
        # CSV-Prozessor zurücksetzen
        self.csv_processor = CSVProcessor()
        
        # FileDropArea zurücksetzen
        self.file_drop_area.reset_to_default()
        
    def open_mapping_settings(self):
        """Öffnet die Einstellungen auf dem BWA-Gruppen Tab"""
        if not self.settings_window:
            self.settings_window = SettingsWindow(self)
            # Signal für Mapping-Änderungen verbinden
            self.settings_window.account_mapping_tab.mappings_changed.connect(self.update_file_status)
            
        # BWA-Gruppen Tab aktivieren (Index 3)
        self.settings_window.tab_widget.setCurrentIndex(3)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
        
    def update_file_status(self):
        """Aktualisiert den Status der importierten Datei"""
        if self.file_drop_area.get_current_file():
            mapping_complete = self.check_mapping_completeness()
            self.file_drop_area.show_imported_file(
                self.file_drop_area.get_current_file(), 
                mapping_complete
            )
        
    def check_mapping_completeness(self) -> bool:
        """Prüft ob alle Sachkonten zugeordnet sind"""
        if self.csv_processor.processed_data is None:
            return False
            
        # Sachkonten aus CSV holen
        account_numbers = self.csv_processor.get_account_numbers()
        
        # Mappings aus Einstellungen holen
        if not self.settings_window:
            self.settings_window = SettingsWindow(self)
            
        account_mappings = self.settings_window.account_mapping_tab.get_account_mappings()
        
        # Prüfen ob alle Sachkonten eine Gruppenzuordnung haben
        for account in account_numbers:
            if account not in account_mappings or not account_mappings[account].strip():
                return False
                
        return len(account_numbers) > 0  # Mindestens ein Sachkonto muss vorhanden sein
            
    def load_settings(self):
        """Lädt die gespeicherten Einstellungen"""
        # Fenstergeometrie wiederherstellen
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        # Weitere Einstellungen laden
        language = self.settings.value("language", "de")
        decimal_separator = self.settings.value("decimal_separator", ",")
        
    def closeEvent(self, event):
        """Wird beim Schließen der Anwendung aufgerufen"""
        # Einstellungen speichern
        self.settings.setValue("geometry", self.saveGeometry())
        
        # Einstellungsfenster schließen falls geöffnet
        if self.settings_window:
            self.settings_window.close()
            
        event.accept()
