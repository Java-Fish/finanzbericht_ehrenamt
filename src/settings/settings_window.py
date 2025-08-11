# -*- coding: utf-8 -*-
"""
Einstellungsfenster der Anwendung
"""

from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                               QTabWidget, QScrollArea, QPushButton, QMenuBar, QMenu)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction
import os

from .general_settings import GeneralSettingsTab
from .organization_settings import OrganizationSettingsTab
from .mapping_settings import MappingSettingsTab
from .account_mapping import AccountMappingTab
from .super_group_mapping import SuperGroupMappingTab
from ..utils.icon_helper import get_app_icon


class SettingsWindow(QMainWindow):
    """Einstellungsfenster mit Tabs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.parent_window = parent
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        self.setWindowTitle("Einstellungen")
        self.setMinimumSize(700, 500)
        self.resize(800, 600)
        
        # Window Icon setzen
        self.setWindowIcon(get_app_icon())
        
        # Menüleiste für Einstellungen erstellen
        self.create_menu_bar()
        
        # Zentrales Widget mit Scroll-Bereich
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Scroll-Bereich für die Tabs
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Tabs erstellen
        self.general_tab = GeneralSettingsTab()
        self.organization_tab = OrganizationSettingsTab()
        self.mapping_tab = MappingSettingsTab()
        self.account_mapping_tab = AccountMappingTab()
        self.super_group_mapping_tab = SuperGroupMappingTab()
        
        # Signal-Verbindungen für Datenaktualisierung
        self.account_mapping_tab.mappings_changed.connect(self.update_super_group_bwa_groups)
        
        # Tabs hinzufügen
        self.tab_widget.addTab(self.general_tab, "Allgemein")
        self.tab_widget.addTab(self.organization_tab, "Organisation")
        self.tab_widget.addTab(self.mapping_tab, "Zuordnung")
        self.tab_widget.addTab(self.account_mapping_tab, "BWA-Gruppen")
        self.tab_widget.addTab(self.super_group_mapping_tab, "Obergruppen")
        
        # Tab Widget in Scroll-Bereich setzen
        scroll_area.setWidget(self.tab_widget)
        layout.addWidget(scroll_area)
        
    def create_menu_bar(self):
        """Erstellt die Menüleiste für Einstellungen"""
        menubar = self.menuBar()
        
        # Zurück
        back_action = QAction("Zurück", self)
        back_action.triggered.connect(self.go_back)
        menubar.addAction(back_action)
        
        # Speichern
        save_action = QAction("Speichern", self)
        save_action.triggered.connect(self.save_settings)
        menubar.addAction(save_action)
        
        # Zurücksetzen
        reset_action = QAction("Zurücksetzen", self)
        reset_action.triggered.connect(self.reset_settings)
        menubar.addAction(reset_action)
        
    def go_back(self):
        """Kehrt zum Hauptfenster zurück"""
        self.close()
        if self.parent_window:
            self.parent_window.raise_()
            self.parent_window.activateWindow()
            
    def save_settings(self):
        """Speichert alle Einstellungen"""
        # Allgemeine Einstellungen speichern
        self.general_tab.save_settings()
        
        # Organisationseinstellungen speichern
        self.organization_tab.save_settings()
        
        # Zuordnungseinstellungen speichern
        self.mapping_tab.save_settings()
        
        # BWA-Gruppen speichern
        self.account_mapping_tab.save_settings()
        
        # Obergruppen-Mappings speichern
        self.super_group_mapping_tab.save_settings()
        
        # Sicherstellen, dass alle Änderungen persistent gespeichert werden
        self.settings.sync()
        
        # Bestätigung (könnte später durch eine Statusleiste ersetzt werden)
        print("Einstellungen gespeichert")
        
    def reset_settings(self):
        """Setzt alle Einstellungen auf Standard zurück"""
        # Alle Tabs zurücksetzen
        self.general_tab.reset_to_defaults()
        self.organization_tab.reset_to_defaults()
        self.mapping_tab.reset_to_defaults()
        self.account_mapping_tab.reset_to_defaults()
        self.super_group_mapping_tab.reset_to_defaults()
        
        print("Einstellungen zurückgesetzt")
        
    def load_settings(self):
        """Lädt alle Einstellungen"""
        # Alle Tabs laden ihre Einstellungen
        self.general_tab.load_settings()
        self.organization_tab.load_settings()
        self.mapping_tab.load_settings()
        self.account_mapping_tab.load_settings()
        self.super_group_mapping_tab.load_settings()
        
        # Obergruppen-Tab mit verfügbaren BWA-Gruppen aktualisieren
        self.update_super_group_bwa_groups()
        
    def update_account_mappings(self, account_numbers, account_names=None):
        """Aktualisiert die Sachkonten-Liste im BWA-Gruppen Tab"""
        self.account_mapping_tab.update_accounts_from_csv(account_numbers, account_names)
        
    def update_super_group_bwa_groups(self):
        """Aktualisiert die BWA-Gruppen in der Obergruppen-Zuordnung"""
        # Alle verwendeten BWA-Gruppen sammeln
        bwa_groups = self.account_mapping_tab.get_all_bwa_groups()
        self.super_group_mapping_tab.update_groups_from_mappings(bwa_groups)
        
    def closeEvent(self, event):
        """Wird beim Schließen des Fensters aufgerufen"""
        # Alle Einstellungen automatisch speichern
        self.save_settings()
        
        # Fenstergeometrie speichern
        self.settings.setValue("settings_window/geometry", self.saveGeometry())
        
        # Sicherstellen, dass alle Änderungen persistent gespeichert werden
        self.settings.sync()
        
        event.accept()
