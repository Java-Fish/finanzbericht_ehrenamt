# -*- coding: utf-8 -*-
"""
Icon Helper - Zentralisierte Logo/Icon-Verwaltung
"""

import os
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt


def get_app_icon() -> QIcon:
    """
    Gibt das Anwendungsicon zurück
    
    Returns:
        QIcon: Das Anwendungsicon oder ein leeres Icon falls nicht gefunden
    """
    logo_path = get_icon_path("app_icon.png")
    if os.path.exists(logo_path):
        return QIcon(logo_path)
    return QIcon()


def get_app_pixmap(size: int = 80) -> QPixmap:
    """
    Gibt das Anwendungslogo als Pixmap zurück
    
    Args:
        size (int): Gewünschte Größe (Quadrat)
        
    Returns:
        QPixmap: Das skalierte Logo oder ein leeres Pixmap
    """
    logo_path = get_icon_path("app_icon.png")
    if os.path.exists(logo_path):
        pixmap = QPixmap(logo_path)
        return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    return QPixmap()


def get_icon_path(filename: str) -> str:
    """
    Erstellt den vollständigen Pfad zu einer Icon-Datei
    
    Args:
        filename (str): Name der Icon-Datei
        
    Returns:
        str: Vollständiger Pfad zur Icon-Datei
    """
    # Vom aktuellen Modul aus navigieren: src/utils/ -> projekt/resources/icons/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(project_root, "resources", "icons", filename)


def app_icon_exists() -> bool:
    """
    Prüft, ob das Anwendungsicon existiert
    
    Returns:
        bool: True wenn das Icon existiert
    """
    return os.path.exists(get_icon_path("app_icon.png"))
