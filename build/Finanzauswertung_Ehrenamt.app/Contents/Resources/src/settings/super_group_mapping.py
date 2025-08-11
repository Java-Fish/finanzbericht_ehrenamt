# -*- coding: utf-8 -*-
"""
Obergruppen-Mapping Tab für BWA-Obergruppierung
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                               QLineEdit, QLabel, QPushButton, QGroupBox,
                               QSplitter, QListWidgetItem, QMessageBox)
from PySide6.QtCore import QSettings, Qt, Signal
import json


class SuperGroupMappingTab(QWidget):
    """Tab für BWA-Obergruppen-Zuordnung"""
    
    # Signal wird ausgesendet wenn sich Obergruppen-Mappings ändern
    super_mappings_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.super_group_mappings = {}  # Dict: bwa_group -> super_group
        self.available_bwa_groups = set()  # Verfügbare BWA-Gruppen
        self.init_ui()
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Splitter für linke und rechte Seite
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Linke Seite - BWA-Gruppen-Liste
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        groups_group = QGroupBox("BWA-Gruppen")
        groups_layout = QVBoxLayout(groups_group)
        
        # Info-Text
        info_label = QLabel(
            "Hier werden alle BWA-Gruppen angezeigt, die in der Sachkonten-Zuordnung "
            "verwendet wurden. Wählen Sie eine Gruppe aus, um sie einer Obergruppe zuzuordnen."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666666; font-style: italic; margin: 10px;")
        groups_layout.addWidget(info_label)
        
        self.groups_list = QListWidget()
        self.groups_list.currentItemChanged.connect(self.on_group_selected)
        groups_layout.addWidget(self.groups_list)
        
        # Button zum Aktualisieren der Gruppenliste
        self.refresh_button = QPushButton("Gruppenliste aktualisieren")
        self.refresh_button.clicked.connect(self.refresh_groups)
        groups_layout.addWidget(self.refresh_button)
        
        left_layout.addWidget(groups_group)
        splitter.addWidget(left_widget)
        
        # Rechte Seite - Obergruppen-Zuordnung
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        mapping_group = QGroupBox("Obergruppen-Zuordnung")
        mapping_layout = QVBoxLayout(mapping_group)
        
        # Info Label
        self.info_label = QLabel("Wählen Sie eine BWA-Gruppe aus der Liste")
        self.info_label.setStyleSheet("color: gray; font-style: italic;")
        mapping_layout.addWidget(self.info_label)
        
        # Aktuelle BWA-Gruppe
        self.current_group_label = QLabel("")
        self.current_group_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        mapping_layout.addWidget(self.current_group_label)
        
        # Obergruppen-Eingabe
        super_group_label = QLabel("Obergruppe:")
        mapping_layout.addWidget(super_group_label)
        
        self.super_group_input = QLineEdit()
        self.super_group_input.setPlaceholderText("z.B. 'Einnahmen', 'Ausgaben', 'Betriebskosten'...")
        self.super_group_input.textChanged.connect(self.on_super_group_changed)
        mapping_layout.addWidget(self.super_group_input)
        
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
        
        # Vorschläge für häufige Obergruppen
        suggestions_label = QLabel("Häufige Obergruppen:")
        mapping_layout.addWidget(suggestions_label)
        
        suggestions_layout = QVBoxLayout()
        suggestions = [
            "Einnahmen", "Ausgaben", "Betriebskosten", "Personalkosten",
            "Verwaltungskosten", "Projektkosten", "Sonstige Kosten"
        ]
        
        # Suggestions als Buttons
        for i in range(0, len(suggestions), 2):
            row_layout = QHBoxLayout()
            for j in range(2):
                if i + j < len(suggestions):
                    suggestion_btn = QPushButton(suggestions[i + j])
                    suggestion_btn.clicked.connect(
                        lambda checked, text=suggestions[i + j]: self.super_group_input.setText(text)
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
        
    def on_group_selected(self, current, previous):
        """Wird aufgerufen wenn eine BWA-Gruppe ausgewählt wird"""
        if current is None:
            self.current_group_label.setText("")
            self.super_group_input.setText("")
            self.save_mapping_button.setEnabled(False)
            self.clear_mapping_button.setEnabled(False)
            self.info_label.setText("Wählen Sie eine BWA-Gruppe aus der Liste")
            return
            
        group_name = current.text().split(" → ")[0]  # Nur der Gruppenname
        self.current_group_label.setText(f"BWA-Gruppe: {group_name}")
        
        # Aktuelle Obergruppen-Zuordnung laden
        super_group = self.super_group_mappings.get(group_name, "")
        self.super_group_input.setText(super_group)
        
        self.save_mapping_button.setEnabled(True)
        self.clear_mapping_button.setEnabled(True)
        self.info_label.setText("Geben Sie eine Obergruppe für diese BWA-Gruppe ein")
        
    def on_super_group_changed(self):
        """Wird aufgerufen wenn sich der Obergruppen-Text ändert"""
        current_item = self.groups_list.currentItem()
        if current_item:
            self.save_mapping_button.setEnabled(True)
            
    def save_current_mapping(self):
        """Speichert die aktuelle Obergruppen-Zuordnung"""
        current_item = self.groups_list.currentItem()
        if not current_item:
            return
            
        group_name = current_item.text().split(" → ")[0]  # Nur der Gruppenname
        super_group_name = self.super_group_input.text().strip()
        
        if super_group_name:
            self.super_group_mappings[group_name] = super_group_name
            # Visual feedback in der Liste
            current_item.setText(f"{group_name} → {super_group_name}")
        else:
            # Wenn Obergruppe leer ist, Zuordnung entfernen
            if group_name in self.super_group_mappings:
                del self.super_group_mappings[group_name]
            current_item.setText(group_name)
            
        self.save_settings()
        
        # Signal senden dass sich Obergruppen-Mappings geändert haben
        self.super_mappings_changed.emit()
        
    def clear_current_mapping(self):
        """Löscht die aktuelle Obergruppen-Zuordnung"""
        current_item = self.groups_list.currentItem()
        if not current_item:
            return
            
        group_name = current_item.text().split(" → ")[0]  # Nur der Gruppenname
        
        if group_name in self.super_group_mappings:
            del self.super_group_mappings[group_name]
            
        current_item.setText(group_name)
        self.super_group_input.setText("")
        self.save_settings()
        
        # Signal senden dass sich Obergruppen-Mappings geändert haben
        self.super_mappings_changed.emit()
        
    def refresh_groups(self):
        """Aktualisiert die BWA-Gruppenliste"""
        # Diese Methode wird von der Hauptanwendung aufgerufen
        # wenn sich BWA-Gruppen ändern
        QMessageBox.information(
            self, 
            "Information", 
            "BWA-Gruppen werden automatisch aktualisiert, wenn sich "
            "Sachkonten-Zuordnungen ändern."
        )
        
    def update_groups_from_mappings(self, bwa_groups):
        """Aktualisiert die BWA-Gruppenliste basierend auf verfügbaren Gruppen"""
        # Sortierte Liste der BWA-Gruppen
        self.available_bwa_groups = set(bwa_groups)
        sorted_groups = sorted(self.available_bwa_groups)
        
        # Liste leeren und neu befüllen
        self.groups_list.clear()
        
        for group in sorted_groups:
            item = QListWidgetItem()
            
            # Prüfen ob bereits eine Obergruppen-Zuordnung existiert
            if group in self.super_group_mappings:
                super_group = self.super_group_mappings[group]
                item.setText(f"{group} → {super_group}")
            else:
                item.setText(group)
                
            self.groups_list.addItem(item)
            
    def load_settings(self):
        """Lädt die Einstellungen"""
        # Obergruppen-Mappings laden
        mappings_json = self.settings.value("super_group_mappings", "{}")
        try:
            self.super_group_mappings = json.loads(mappings_json)
        except (json.JSONDecodeError, TypeError):
            self.super_group_mappings = {}
            
    def save_settings(self):
        """Speichert die Einstellungen"""
        # Obergruppen-Mappings speichern
        mappings_json = json.dumps(self.super_group_mappings)
        self.settings.setValue("super_group_mappings", mappings_json)
        
    def reset_to_defaults(self):
        """Setzt die Einstellungen auf Standard zurück"""
        self.super_group_mappings = {}
        self.groups_list.clear()
        self.super_group_input.setText("")
        self.current_group_label.setText("")
        self.save_settings()
        
    def get_super_group_mappings(self):
        """Gibt die aktuellen Obergruppen-Mappings zurück"""
        return self.super_group_mappings.copy()
