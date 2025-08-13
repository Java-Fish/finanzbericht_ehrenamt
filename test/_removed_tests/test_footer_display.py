#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests für Footer-Anzeige in PDF-Dokumenten
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Pfad zur src-Verzeichnis hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtCore import QSettings
from src.utils.bwa_generator import BWAPDFGenerator
from src.utils.csv_processor import CSVProcessor


class TestFooterDisplay(unittest.TestCase):
    """Tests für Footer-Anzeige-Funktionalität"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.test_settings = QSettings('TestOrg', 'TestApp')
        self.test_settings.clear()  # Alle vorherigen Einstellungen löschen
        
        # Test-Einstellungen für Footer setzen
        self.test_settings.setValue('show_page_number', True)
        self.test_settings.setValue('show_organization_footer', True)
        self.test_settings.setValue('organization/name', 'Test Verein e.V.')
        self.test_settings.sync()
        
    def tearDown(self):
        """Cleanup nach jedem Test"""
        self.test_settings.clear()
        
    def test_footer_page_number_display(self):
        """Test: Seitenzahl wird im Footer angezeigt"""
        # Mock Canvas für Footer-Test
        mock_canvas = Mock()
        mock_canvas.getPageNumber.return_value = 1
        mock_canvas.stringWidth.return_value = 50
        
        mock_doc = Mock()
        
        # BWA-Generator mit Test-Einstellungen
        generator = BWAPDFGenerator()
        generator.settings = self.test_settings
        
        # Footer-Methode aufrufen
        generator._add_footer_to_page(mock_canvas, mock_doc)
        
        # Verifizieren dass drawString für Seitenzahl aufgerufen wurde
        self.assertTrue(mock_canvas.drawString.called)
        
        # Finde den Aufruf mit der Seitenzahl
        page_number_call = None
        for call in mock_canvas.drawString.call_args_list:
            args = call[0]
            if len(args) >= 3 and 'Seite 1' in str(args[2]):
                page_number_call = call
                break
                
        self.assertIsNotNone(page_number_call, "Seitenzahl 'Seite 1' sollte im Footer gezeichnet werden")
        
    def test_footer_organization_display(self):
        """Test: Organisation wird im Footer angezeigt"""
        # Mock Canvas für Footer-Test
        mock_canvas = Mock()
        mock_canvas.getPageNumber.return_value = 1
        mock_canvas.stringWidth.return_value = 80  # Breite des Organisations-Texts
        
        mock_doc = Mock()
        
        # BWA-Generator mit Test-Einstellungen
        generator = BWAPDFGenerator()
        generator.settings = self.test_settings
        
        # Footer-Methode aufrufen
        generator._add_footer_to_page(mock_canvas, mock_doc)
        
        # Verifizieren dass drawString für Organisation aufgerufen wurde
        self.assertTrue(mock_canvas.drawString.called)
        
        # Finde den Aufruf mit der Organisation
        org_call = None
        for call in mock_canvas.drawString.call_args_list:
            args = call[0]
            if len(args) >= 3 and 'Test Verein e.V.' in str(args[2]):
                org_call = call
                break
                
        self.assertIsNotNone(org_call, "Organisation 'Test Verein e.V.' sollte im Footer gezeichnet werden")
        
    def test_footer_disabled_options(self):
        """Test: Footer-Elemente werden nicht angezeigt wenn deaktiviert"""
        # Footer-Optionen deaktivieren
        self.test_settings.setValue('show_page_number', False)
        self.test_settings.setValue('show_organization_footer', False)
        self.test_settings.sync()
        
        # Mock Canvas
        mock_canvas = Mock()
        mock_canvas.getPageNumber.return_value = 1
        mock_doc = Mock()
        
        # BWA-Generator mit Test-Einstellungen
        generator = BWAPDFGenerator()
        generator.settings = self.test_settings
        
        # Footer-Methode aufrufen
        generator._add_footer_to_page(mock_canvas, mock_doc)
        
        # drawString sollte gar nicht aufgerufen werden
        mock_canvas.drawString.assert_not_called()
        
    def test_footer_without_organization_name(self):
        """Test: Organisations-Footer wird nicht angezeigt wenn Name leer ist"""
        # Organisation aktiviert aber kein Name gesetzt
        self.test_settings.setValue('show_organization_footer', True)
        self.test_settings.setValue('organization/name', '')  # Leerer Name
        self.test_settings.sync()
        
        # Mock Canvas
        mock_canvas = Mock()
        mock_canvas.getPageNumber.return_value = 1
        mock_doc = Mock()
        
        # BWA-Generator mit Test-Einstellungen
        generator = BWAPDFGenerator()
        generator.settings = self.test_settings
        
        # Footer-Methode aufrufen
        generator._add_footer_to_page(mock_canvas, mock_doc)
        
        # Nur Seitenzahl sollte gezeichnet werden, keine Organisation
        calls = mock_canvas.drawString.call_args_list
        page_calls = [call for call in calls if 'Seite' in str(call[0][2])]
        org_calls = [call for call in calls if 'Verein' in str(call[0][2])]
        
        self.assertEqual(len(page_calls), 1, "Seitenzahl sollte gezeichnet werden")
        self.assertEqual(len(org_calls), 0, "Organisation sollte nicht gezeichnet werden bei leerem Namen")
        
    def test_footer_lightgrey_color(self):
        """Test: Footer wird in heller Farbe angezeigt"""
        # Mock Canvas
        mock_canvas = Mock()
        mock_canvas.getPageNumber.return_value = 1
        mock_canvas.stringWidth.return_value = 50
        mock_doc = Mock()
        
        # BWA-Generator mit Test-Einstellungen
        generator = BWAPDFGenerator()
        generator.settings = self.test_settings
        
        # Footer-Methode aufrufen
        generator._add_footer_to_page(mock_canvas, mock_doc)
        
        # Verifizieren dass setFillColor mit lightgrey aufgerufen wurde
        color_calls = mock_canvas.setFillColor.call_args_list
        
        # Es sollten mindestens 2 Aufrufe geben (für Seitenzahl und Organisation)
        self.assertGreaterEqual(len(color_calls), 2, "setFillColor sollte mindestens 2x aufgerufen werden")
        
        # Prüfe dass lightgrey verwendet wird
        from reportlab.lib import colors
        lightgrey_calls = [call for call in color_calls if call[0][0] == colors.lightgrey]
        self.assertGreaterEqual(len(lightgrey_calls), 2, "Footer sollte in lightgrey angezeigt werden")

    @patch('src.utils.csv_processor.CSVProcessor')
    def test_footer_in_pdf_generation(self, mock_csv_processor):
        """Test: Footer wird in vollständiger PDF-Generierung korrekt verwendet"""
        # Mock CSV-Processor Setup
        mock_processor = Mock()
        mock_processor.get_data_by_quarter.return_value = Mock()
        mock_processor.get_data_by_quarter.return_value.empty = True
        mock_processor.get_year_data.return_value = Mock()
        mock_processor.get_year_data.return_value.empty = True
        mock_processor.get_account_numbers.return_value = []
        mock_csv_processor.return_value = mock_processor
        
        # Temporäre PDF-Datei
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            test_pdf = tmp_file.name
            
        try:
            # BWA-Generator mit Test-Einstellungen
            generator = BWAPDFGenerator()
            generator.settings = self.test_settings
            
            # PDF generieren
            success = generator.generate_bwa_pdf(test_pdf, mock_processor, {})
            
            # Verifizieren dass PDF erfolgreich erstellt wurde
            self.assertTrue(success, "PDF-Generierung sollte erfolgreich sein")
            self.assertTrue(os.path.exists(test_pdf), "PDF-Datei sollte existieren")
            
            # PDF sollte eine angemessene Größe haben
            file_size = os.path.getsize(test_pdf)
            self.assertGreater(file_size, 1000, "PDF sollte mindestens 1KB groß sein")
            
        finally:
            # Aufräumen
            if os.path.exists(test_pdf):
                os.remove(test_pdf)


if __name__ == '__main__':
    unittest.main()
