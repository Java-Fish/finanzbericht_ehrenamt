# -*- coding: utf-8 -*-
"""
Übersetzungsmanagement für die Anwendung
"""

from PySide6.QtCore import QTranslator, QLocale, QSettings
from PySide6.QtWidgets import QApplication
import os


def setup_translations(app):
    """Lädt und installiert Übersetzungen"""
    settings = QSettings()
    language = settings.value("language", "de")
    
    translator = QTranslator()
    
    # Pfad zu den Übersetzungsdateien
    translations_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'translations')
    
    if language == "en":
        translation_file = os.path.join(translations_dir, 'app_en.qm')
        if os.path.exists(translation_file):
            translator.load(translation_file)
            app.installTranslator(translator)
            
    return translator


def get_available_languages():
    """Gibt verfügbare Sprachen zurück"""
    return {
        "de": "Deutsch",
        "en": "English"
    }


def get_current_language():
    """Gibt die aktuelle Sprache zurück"""
    settings = QSettings()
    return settings.value("language", "de")
