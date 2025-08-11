# -*- coding: utf-8 -*-
"""
BWA-PDF-Generator
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import black, blue, red, gray, green
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                               TableStyle, PageBreak, Image)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics import renderPDF
from PySide6.QtCore import QSettings
from datetime import datetime, date
from typing import Dict, List, Optional
import os
import tempfile
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io


class BWAPDFGenerator:
    """Generiert BWA-PDFs basierend auf CSV-Daten"""
    
    def __init__(self):
        self.settings = QSettings()
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Erstellt benutzerdefinierte Styles mit aktueller Farbe"""
        # Aktuelle Überschriftenfarbe laden
        header_color = self._get_header_color()
        
        # Titel-Style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=header_color
        )
        
        # Untertitel-Style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Gruppen-Style
        self.group_style = ParagraphStyle(
            'GroupHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=10,
            spaceBefore=15,
            textColor=header_color,
            leftIndent=10
        )
        
        # Normal-Style für Tabellen
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT
        )
        
    def _get_header_color(self):
        """Gibt die eingestellte Überschriftenfarbe zurück"""
        header_color_hex = self.settings.value("header_color", "#0000FF")  # Standard: Blau
        try:
            # HEX zu RGB konvertieren
            if header_color_hex.startswith('#'):
                hex_color = header_color_hex[1:]
            else:
                hex_color = header_color_hex
                
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return colors.Color(r, g, b)
        except (ValueError, IndexError):
            # Fallback auf Standardblau bei ungültiger Farbe
            return blue
        
    def _get_opening_balance(self) -> float:
        """Holt den Anfangskontostand aus den Einstellungen"""
        return self.settings.value("opening_balance", 0.0, type=float)
        
    def _calculate_total_amount(self, csv_processor) -> float:
        """Berechnet die Gesamtsumme aller Buchungen"""
        year_data = csv_processor.get_year_data()  # Alle Daten des Jahres
        if year_data.empty:
            return 0.0
        # Einheitlich Betrag_Clean verwenden
        return year_data['Betrag_Clean'].sum() if 'Betrag_Clean' in year_data.columns else 0.0
        
    def _calculate_new_balance(self, csv_processor) -> float:
        """Berechnet den neuen Kontostand (Anfang + Summe aller Buchungen)"""
        opening_balance = self._get_opening_balance()
        total_amount = self._calculate_total_amount(csv_processor)
        return opening_balance + total_amount
        
    def _calculate_quarter_balance(self, quarter: int, csv_processor) -> float:
        """Berechnet den Kontostand für ein spezifisches Quartal"""
        opening_balance = self._get_opening_balance()
        quarter_data = csv_processor.get_data_by_quarter(quarter)
        
        # quarter_data ist ein DataFrame, wir brauchen die Summe der Beträge
        if quarter_data.empty:
            quarter_total = 0.0
        else:
            quarter_total = quarter_data['Betrag_Clean'].sum() if 'Betrag_Clean' in quarter_data.columns else 0.0
        
        return opening_balance + quarter_total
        
    def generate_bwa_pdf(self, output_path: str, csv_processor, account_mappings: Dict[str, str]) -> bool:
        """Generiert das komplette BWA-PDF basierend auf Einstellungen"""
        try:
            # Styles vor jeder PDF-Generierung neu erstellen um aktuelle Farben zu berücksichtigen
            self._create_custom_styles()
            
            # Einstellungen laden
            settings = QSettings()
            generate_quarterly = settings.value("generate_quarterly_reports", True, type=bool)
            generate_accounts = settings.value("generate_account_reports", True, type=bool)
            generate_chart = settings.value("generate_chart_report", True, type=bool)
            quarter_mode = settings.value("quarter_mode", "cumulative")
            
            # PDF-Dokument erstellen
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Story (Inhalt) sammeln
            story = []
            
            # 1. Deckblatt (immer erstellen)
            story.extend(self._create_cover_page(csv_processor))
            story.append(PageBreak())
            
            # 2-5. Quartalsauswertungen (optional)
            if generate_quarterly:
                for quarter in range(1, 5):
                    story.extend(self._create_quarter_page(quarter, csv_processor, account_mappings))
                    story.append(PageBreak())
                    
            # 6. Jahresauswertung (immer erstellen)
            story.extend(self._create_year_page(csv_processor, account_mappings))
            story.append(PageBreak())
            
            # 7. Balkendiagramm (optional)
            if generate_chart:
                story.extend(self._create_chart_page(csv_processor))
                story.append(PageBreak())
            
            # 8. Sachkonten-Einzelauswertungen (optional)
            if generate_accounts:
                accounts = csv_processor.get_account_numbers()
                for account in accounts:
                    story.extend(self._create_account_page(account, csv_processor))
                    story.append(PageBreak())
                
            # PDF erstellen
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Fehler bei der PDF-Generierung: {e}")
            return False
            
    def _load_super_group_mappings(self) -> Dict[str, str]:
        """Lädt die Obergruppen-Mappings aus den Einstellungen"""
        mappings_json = self.settings.value("super_group_mappings", "{}")
        try:
            return json.loads(mappings_json)
        except (json.JSONDecodeError, TypeError):
            return {}
            
    def _create_cover_page(self, csv_processor) -> List:
        """Erstellt das Deckblatt mit Organisationsinformationen, Logo und Kontodaten"""
        elements = []
        
        # Titel
        title = Paragraph("Betriebswirtschaftliche Auswertung", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Jahr (aktuelles Jahr)
        year = datetime.now().year
        year_para = Paragraph(f"Geschäftsjahr {year}", self.subtitle_style)
        elements.append(year_para)
        elements.append(Spacer(1, 1.5*cm))
        
        # Organisationsdaten (oben im Dokument)
        org_name = self.settings.value("organization/name", "")
        org_street = self.settings.value("organization/street", "")
        org_zip = self.settings.value("organization/zip", "")
        org_city = self.settings.value("organization/city", "")
        org_phone = self.settings.value("organization/phone", "")
        org_email = self.settings.value("organization/email", "")
        org_info = self.settings.value("organization/info", "")
        
        # Organisationsname (fett und größer)
        if org_name:
            org_name_style = ParagraphStyle(
                'OrgName',
                parent=self.normal_style,
                fontSize=14,
                alignment=TA_CENTER,
                textColor=self._get_header_color(),
                spaceBefore=5,
                spaceAfter=5
            )
            elements.append(Paragraph(f"<b>{org_name}</b>", org_name_style))
            
        # Adresse
        if org_street or org_zip or org_city:
            address_parts = []
            if org_street:
                address_parts.append(org_street)
            if org_zip and org_city:
                address_parts.append(f"{org_zip} {org_city}")
            elif org_city:
                address_parts.append(org_city)
                
            if address_parts:
                address_text = "<br/>".join(address_parts)
                address_style = ParagraphStyle(
                    'Address',
                    parent=self.normal_style,
                    alignment=TA_CENTER,
                    spaceBefore=3,
                    spaceAfter=3
                )
                elements.append(Paragraph(address_text, address_style))
                
        # Kontaktdaten
        contact_parts = []
        if org_phone:
            contact_parts.append(f"Tel: {org_phone}")
        if org_email:
            contact_parts.append(f"E-Mail: {org_email}")
            
        if contact_parts:
            contact_text = " | ".join(contact_parts)
            contact_style = ParagraphStyle(
                'Contact',
                parent=self.normal_style,
                alignment=TA_CENTER,
                fontSize=9,
                spaceBefore=3,
                spaceAfter=10
            )
            elements.append(Paragraph(contact_text, contact_style))
            
        # Zusätzliche Organisationsinfos
        if org_info:
            info_style = ParagraphStyle(
                'OrgInfo',
                parent=self.normal_style,
                alignment=TA_CENTER,
                fontSize=9,
                textColor=gray,
                spaceBefore=5,
                spaceAfter=15
            )
            elements.append(Paragraph(org_info, info_style))
        
        elements.append(Spacer(1, 1*cm))
        
        # Logo mittig unter den Organisationsinformationen
        logo_path = self.settings.value("organization/logo_path", "")
        if logo_path and os.path.exists(logo_path):
            try:
                # Logo zentriert mit angemessener Größe
                logo = Image(logo_path, width=6*cm, height=4*cm, kind='proportional')
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 1.5*cm))
            except Exception as e:
                # Fallback falls Logo nicht geladen werden kann
                elements.append(Spacer(1, 0.5*cm))
        else:
            elements.append(Spacer(1, 0.5*cm))
                
        # Kontostandsinformationen unter dem Logo
        balance_title_style = ParagraphStyle(
            'BalanceTitle',
            parent=self.group_style,
            alignment=TA_CENTER,
            fontSize=12,
            textColor=self._get_header_color(),
            spaceBefore=10,
            spaceAfter=10
        )
        balance_title = Paragraph("<b>Kontostandsübersicht</b>", balance_title_style)
        elements.append(balance_title)
        
        # Anfangskontostand
        opening_balance = self._get_opening_balance()
        opening_style = ParagraphStyle(
            'BalanceData',
            parent=self.normal_style,
            alignment=TA_CENTER,
            spaceBefore=3,
            spaceAfter=3
        )
        opening_para = Paragraph(f"Kontostand zum 01.01.: {self._format_amount(opening_balance)}", opening_style)
        elements.append(opening_para)
        
        # Summe aller Buchungen
        total_amount = self._calculate_total_amount(csv_processor)
        total_para = Paragraph(f"Summe aller Buchungen: {self._format_amount(total_amount)}", opening_style)
        elements.append(total_para)
        
        # Neuer Kontostand (hervorgehoben)
        new_balance = self._calculate_new_balance(csv_processor)
        final_balance_style = ParagraphStyle(
            'FinalBalance',
            parent=self.normal_style,
            alignment=TA_CENTER,
            fontSize=11,
            textColor=self._get_header_color(),
            spaceBefore=5,
            spaceAfter=10
        )
        new_balance_para = Paragraph(f"<b>Aktueller Kontostand: {self._format_amount(new_balance)}</b>", final_balance_style)
        elements.append(new_balance_para)
        
        elements.append(Spacer(1, 1*cm))
                
        # Erstellungsdatum
        creation_date = datetime.now().strftime("%d.%m.%Y")
        date_style = ParagraphStyle(
            'CreationDate',
            parent=self.normal_style,
            alignment=TA_CENTER,
            fontSize=9,
            textColor=gray
        )
        date_para = Paragraph(f"Erstellt am: {creation_date}", date_style)
        elements.append(date_para)
        
        return elements
        
    def _create_quarter_page(self, quarter: int, csv_processor, account_mappings: Dict[str, str]) -> List:
        """Erstellt eine Quartalsauswertung basierend auf dem gewählten Modus"""
        elements = []
        
        # Einstellungen für Quartals-Modus laden
        settings = QSettings()
        quarter_mode = settings.value("quarter_mode", "cumulative")
        
        # Titel je nach Modus
        quarter_ranges_individual = {
            1: "01.01. - 31.03.",
            2: "01.04. - 30.06.", 
            3: "01.07. - 30.09.",
            4: "01.10. - 31.12."
        }
        
        quarter_ranges_cumulative = {
            1: "01.01. - 31.03.",
            2: "01.01. - 30.06.", 
            3: "01.01. - 30.09.",
            4: "01.01. - 31.12."
        }
        
        year = datetime.now().year
        
        if quarter_mode == "cumulative":
            quarter_range = quarter_ranges_cumulative[quarter]
            title = f"BWA Quartal {quarter} kumulativ ({quarter_range}) {year}"
        else:
            quarter_range = quarter_ranges_individual[quarter]
            title = f"BWA Quartal {quarter} quartalsweise ({quarter_range}) {year}"
            
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 1*cm))
        
        # Quartals-Daten holen
        quarter_data = csv_processor.get_data_by_quarter(quarter)
        
        if quarter_data.empty:
            elements.append(Paragraph("Keine Daten für dieses Quartal verfügbar.", self.normal_style))
            return elements
            
        # BWA-Tabelle erstellen
        summary = self._create_quarter_summary(quarter_data, account_mappings)
        table = self._create_bwa_table(summary, f"Q{quarter}")
        
        if table:
            elements.append(table)
            
        # Kontostandsentwicklung immer auf eigene Seite
        elements.append(PageBreak())
        balance_title = Paragraph(f"<b>Kontostandsentwicklung Q{quarter}</b>", self.group_style)
            
        elements.append(balance_title)
        elements.append(Spacer(1, 0.5*cm))
        
        opening_balance = self._get_opening_balance()
        quarter_balance = self._calculate_quarter_balance(quarter, csv_processor)
        
        # Quartalssumme berechnen aus DataFrame
        if quarter_data.empty:
            quarter_total = 0.0
        else:
            quarter_total = quarter_data['Betrag_Clean'].sum() if 'Betrag_Clean' in quarter_data.columns else 0.0
        
        balance_para = Paragraph(f"Kontostand 01.01.: {self._format_amount(opening_balance)}", self.normal_style)
        elements.append(balance_para)
        
        quarter_para = Paragraph(f"Summe Quartal {quarter}: {self._format_amount(quarter_total)}", self.normal_style)
        elements.append(quarter_para)
        
        new_balance_para = Paragraph(f"<b>Kontostand nach Q{quarter}: {self._format_amount(quarter_balance)}</b>", self.normal_style)
        elements.append(new_balance_para)
        
        # Balkendiagramm hinzufügen (falls aktiviert)
        chart_enabled = self.settings.value("generate_chart_report", True, type=bool)
        if chart_enabled:
            elements.append(Spacer(1, 1*cm))
            chart_title = Paragraph("<b>Obergruppen-Übersicht</b>", self.group_style)
            elements.append(chart_title)
            elements.append(Spacer(1, 0.5*cm))
            
            chart = self._create_supergroup_bar_chart(summary, f"Q{quarter}")
            if chart is not None:
                elements.append(chart)
            
        return elements
        
    def _create_year_page(self, csv_processor, account_mappings: Dict[str, str]) -> List:
        """Erstellt die Jahresauswertung"""
        elements = []
        
        # Titel
        year = datetime.now().year
        title = f"BWA Jahresauswertung {year}"
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 1*cm))
        
        # Jahres-Daten holen
        year_data = csv_processor.get_year_data()
        
        if year_data.empty:
            elements.append(Paragraph("Keine Daten für das Jahr verfügbar.", self.normal_style))
            return elements
            
        # BWA-Tabelle erstellen
        summary = self._create_year_summary(year_data, account_mappings)
        table = self._create_bwa_table(summary, "Jahr")
        
        if table:
            elements.append(table)
            
        # Kontostandsentwicklung immer auf eigene Seite
        elements.append(PageBreak())
        balance_title = Paragraph(f"<b>Kontostandsentwicklung Jahr</b>", self.group_style)
            
        elements.append(balance_title)
        elements.append(Spacer(1, 0.5*cm))
        
        opening_balance = self._get_opening_balance()
        new_balance = self._calculate_new_balance(csv_processor)
        # Einheitlich Betrag_Clean verwenden
        year_total = year_data['Betrag_Clean'].sum() if not year_data.empty and 'Betrag_Clean' in year_data.columns else 0.0
        
        balance_para = Paragraph(f"Kontostand 01.01.: {self._format_amount(opening_balance)}", self.normal_style)
        elements.append(balance_para)
        
        year_para = Paragraph(f"Summe Gesamtjahr: {self._format_amount(year_total)}", self.normal_style)
        elements.append(year_para)
        
        new_balance_para = Paragraph(f"<b>Kontostand 31.12.: {self._format_amount(new_balance)}</b>", self.normal_style)
        elements.append(new_balance_para)
        
        # Balkendiagramm hinzufügen (falls aktiviert)
        chart_enabled = self.settings.value("generate_chart_report", True, type=bool)
        if chart_enabled:
            elements.append(Spacer(1, 1*cm))
            chart_title = Paragraph("<b>Obergruppen-Übersicht</b>", self.group_style)
            elements.append(chart_title)
            elements.append(Spacer(1, 0.5*cm))
            
            chart = self._create_supergroup_bar_chart(summary, "Jahr")
            if chart is not None:
                elements.append(chart)
            
        return elements
        
    def _create_account_page(self, account_number: str, csv_processor) -> List:
        """Erstellt eine Sachkonto-Einzelauswertung mit professioneller Formatierung"""
        elements = []
        
        # Titel mit Account-Nummer
        title = f"Sachkonto {account_number}"
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Kontodaten holen
        account_data = csv_processor.get_data_by_account(account_number)
        
        if account_data.empty:
            elements.append(Paragraph("Keine Buchungen für dieses Sachkonto.", self.normal_style))
            return elements
            
        # Sachkonto-Name (falls in den Daten vorhanden)
        if 'Sachkonto' in account_data.columns:
            account_name = account_data['Sachkonto'].iloc[0]
            if account_name and str(account_name) != 'nan':
                subtitle = Paragraph(account_name, self.subtitle_style)
                elements.append(subtitle)
                elements.append(Spacer(1, 0.5*cm))
                
        # Buchungstabelle erstellen - mit Buchungsnummer als erste Spalte
        table_data = [['Buchungsnr.', 'Datum', 'Verwendungszweck', 'Betrag']]
        
        total = 0.0
        row_index = 1  # Start nach Header
        style_commands = []
        
        for _, row in account_data.iterrows():
            # Buchungsnummer holen (falls vorhanden)
            buchungsnr = row['Buchungsnr.'] if 'Buchungsnr.' in row and pd.notna(row['Buchungsnr.']) else ''
            
            # Datum im Format DD.MM.YYYY
            date_str = ''
            if 'Buchungstag' in row:
                if hasattr(row['Buchungstag'], 'strftime'):
                    date_str = row['Buchungstag'].strftime('%d.%m.%Y')
                else:
                    # Fallback für String-Format
                    try:
                        date_obj = pd.to_datetime(row['Buchungstag'])
                        date_str = date_obj.strftime('%d.%m.%Y')
                    except:
                        date_str = str(row['Buchungstag'])
            
            purpose = row['Verwendungszweck'] if 'Verwendungszweck' in row else ''
            amount = row['Betrag_Clean']
            
            # Verwendungszweck kürzen wenn zu lang
            if len(str(purpose)) > 50:  # Etwas kürzer wegen der zusätzlichen Spalte
                purpose = str(purpose)[:47] + "..."
                
            # Betrag mit neuer Formatierungsmethode
            amount_str = self._format_amount(amount)
                
            table_data.append([buchungsnr, date_str, purpose, amount_str])
            
            # Farbformatierung für negative/positive Beträge
            if amount < 0:
                style_commands.append(('TEXTCOLOR', (3, row_index), (3, row_index), colors.red))
            else:
                style_commands.append(('TEXTCOLOR', (3, row_index), (3, row_index), colors.black))
                
            # Zebrastreifen für bessere Lesbarkeit
            if row_index % 2 == 0:
                style_commands.append(('BACKGROUND', (0, row_index), (-1, row_index), colors.Color(0.98, 0.98, 0.98)))
            
            row_index += 1
            total += amount
            
                # Summenzeile ohne HTML-Tags
        total_str = self._format_amount(total)
        table_data.append(['', '', 'GESAMTERGEBNIS JAHR', total_str])
        
        # Styling für Summenzeile
        style_commands.extend([
            ('BACKGROUND', (0, row_index), (-1, row_index), colors.Color(0.9, 0.9, 0.9)),
            ('FONTNAME', (0, row_index), (-1, row_index), 'Helvetica-Bold'),
            ('FONTSIZE', (0, row_index), (-1, row_index), 10),
            ('TOPPADDING', (0, row_index), (-1, row_index), 8),
            ('BOTTOMPADDING', (0, row_index), (-1, row_index), 8),
        ])
        
        # Textfarbe für Summe (rot bei negativ)
        if total < 0:
            style_commands.append(('TEXTCOLOR', (3, row_index), (3, row_index), colors.red))
        else:
            style_commands.append(('TEXTCOLOR', (3, row_index), (3, row_index), colors.black))
        
        # Tabelle formatieren - angepasste Spaltenbreiten für 4 Spalten
        table = Table(table_data, colWidths=[2*cm, 2.5*cm, 8.5*cm, 3*cm])
        
        # Basis-Styling - angepasst für 4 Spalten
        base_style = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.2, 0.2)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),  # Betrag-Spalte rechts ausrichten
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.7, 0.7, 0.7)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Alle Styling-Kommandos kombinieren
        all_styles = base_style + style_commands
        table.setStyle(TableStyle(all_styles))
        
        elements.append(table)
        
        return elements
        
    def _create_quarter_summary(self, quarter_data, account_mappings: Dict[str, str]) -> Dict[str, float]:
        """Erstellt Zusammenfassung für ein Quartal"""
        summary = {}
        
        # Gruppiert nach BWA-Gruppen
        for _, row in quarter_data.iterrows():
            account = str(row['Sachkontonr.'])
            amount = row['Betrag_Clean']
            
            group = account_mappings.get(account, f"Nicht zugeordnet ({account})")
            
            if group not in summary:
                summary[group] = 0.0
                
            summary[group] += amount
            
        return summary
        
    def _create_year_summary(self, year_data, account_mappings: Dict[str, str]) -> Dict[str, float]:
        """Erstellt Zusammenfassung für das Jahr"""
        return self._create_quarter_summary(year_data, account_mappings)
        
    def _create_bwa_table(self, summary: Dict[str, float], period: str) -> Optional[Table]:
        """Erstellt eine formatierte BWA-Tabelle mit Obergruppen-Struktur"""
        if not summary:
            return None
            
        # Obergruppen-Mappings laden
        super_group_mappings = self._load_super_group_mappings()
        
        # Daten nach Obergruppen organisieren
        super_groups = {}  # {super_group: {bwa_group: amount}}
        
        for bwa_group, amount in summary.items():
            super_group = super_group_mappings.get(bwa_group, "Nicht zugeordnet")
            
            if super_group not in super_groups:
                super_groups[super_group] = {}
            super_groups[super_group][bwa_group] = amount
        
        # Tabellendaten vorbereiten
        table_data = [['Obergruppe / BWA-Gruppe', f'Betrag {period}']]
        
        # Obergruppen sortiert anzeigen
        total_overall = 0.0
        row_index = 1  # Start nach Header
        style_commands = []
        
        # Dezente Farben für Obergruppen
        super_group_colors = [
            colors.Color(0.95, 0.95, 1.0),    # Sehr helles Blau
            colors.Color(0.95, 1.0, 0.95),    # Sehr helles Grün  
            colors.Color(1.0, 0.98, 0.9),     # Sehr helles Gelb
            colors.Color(1.0, 0.95, 0.95),    # Sehr helles Rosa
            colors.Color(0.98, 0.95, 1.0),    # Sehr helles Lila
            colors.Color(0.95, 1.0, 1.0),     # Sehr helles Cyan
            colors.Color(1.0, 1.0, 0.95),     # Cremeweiß
            colors.Color(0.97, 0.97, 0.97),   # Sehr helles Grau
        ]
        
        color_index = 0
        
        for super_group in sorted(super_groups.keys()):
            bwa_groups = super_groups[super_group]
            super_group_total = sum(bwa_groups.values())
            
            # Obergruppen-Header mit formatiertem Betrag
            super_group_total_str = self._format_amount(super_group_total)
            table_data.append([super_group, super_group_total_str])
            
            # Farbe für diese Obergruppe
            bg_color = super_group_colors[color_index % len(super_group_colors)]
            
            # Styling für Obergruppen-Header
            style_commands.extend([
                ('BACKGROUND', (0, row_index), (-1, row_index), bg_color),
                ('FONTNAME', (0, row_index), (-1, row_index), 'Helvetica-Bold'),
                ('FONTSIZE', (0, row_index), (-1, row_index), 11),
                ('TOPPADDING', (0, row_index), (-1, row_index), 8),
                ('BOTTOMPADDING', (0, row_index), (-1, row_index), 8),
            ])
            
            # Textfarbe für Obergruppen-Summe (rot bei negativ)
            if super_group_total < 0:
                style_commands.append(('TEXTCOLOR', (1, row_index), (1, row_index), colors.red))
            else:
                style_commands.append(('TEXTCOLOR', (1, row_index), (1, row_index), colors.black))
            
            row_index += 1
            
            # BWA-Gruppen innerhalb der Obergruppe
            for bwa_group in sorted(bwa_groups.keys()):
                amount = bwa_groups[bwa_group]
                amount_str = self._format_amount(amount)
                
                table_data.append([f"  • {bwa_group}", amount_str])
                
                # Hintergrundfarbe für BWA-Gruppe (heller als Obergruppe)
                lighter_color = colors.Color(
                    min(1.0, bg_color.red + 0.03),
                    min(1.0, bg_color.green + 0.03), 
                    min(1.0, bg_color.blue + 0.03)
                )
                style_commands.append(('BACKGROUND', (0, row_index), (-1, row_index), lighter_color))
                
                # Textfarbe für BWA-Gruppen-Betrag (rot bei negativ)
                if amount < 0:
                    style_commands.append(('TEXTCOLOR', (1, row_index), (1, row_index), colors.red))
                else:
                    style_commands.append(('TEXTCOLOR', (1, row_index), (1, row_index), colors.black))
                
                row_index += 1
            
            # Leerzeile nach jeder Obergruppe
            table_data.append(['', ''])
            style_commands.append(('BACKGROUND', (0, row_index), (-1, row_index), colors.white))
            row_index += 1
            
            total_overall += super_group_total
            color_index += 1
        
        # Gesamtergebnis
        if super_groups:
            result_str = self._format_amount(total_overall)
            
            table_data.append(['', ''])  # Extra Leerzeile
            table_data.append([f'GESAMTERGEBNIS {period.upper()}', result_str])
            
            # Styling für Gesamtergebnis
            style_commands.extend([
                ('BACKGROUND', (0, row_index + 1), (-1, row_index + 1), colors.Color(0.9, 0.9, 0.9)),
                ('FONTNAME', (0, row_index + 1), (-1, row_index + 1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, row_index + 1), (-1, row_index + 1), 12),
                ('TOPPADDING', (0, row_index + 1), (-1, row_index + 1), 10),
                ('BOTTOMPADDING', (0, row_index + 1), (-1, row_index + 1), 10),
            ])
            
            # Textfarbe für Gesamtergebnis (rot bei negativ)
            if total_overall < 0:
                style_commands.append(('TEXTCOLOR', (1, row_index + 1), (1, row_index + 1), colors.red))
            else:
                style_commands.append(('TEXTCOLOR', (1, row_index + 1), (1, row_index + 1), colors.black))
        
        # Tabelle erstellen
        table = Table(table_data, colWidths=[12*cm, 5*cm])
        
        # Basis-Styling
        base_style = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.2, 0.2)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.7, 0.7, 0.7)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Alle Styling-Kommandos kombinieren
        all_styles = base_style + style_commands
        table.setStyle(TableStyle(all_styles))
        
        return table
        
    def _format_amount(self, amount: float) -> str:
        """Formatiert einen Betrag mit deutscher Zahlendarstellung"""
        formatted = f"{abs(amount):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        if amount < 0:
            formatted = f"-{formatted}"
        return formatted
    
    def _create_chart_page(self, csv_processor) -> List:
        """Erstellt eine Seite mit Balkendiagramm aller Sachkonten"""
        story = []
        
        # Titel
        title = Paragraph("Sachkonten-Übersicht (Balkendiagramm)", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Daten für das Diagramm sammeln
        accounts = csv_processor.get_account_numbers()
        chart_data = []
        
        for account in accounts:
            # Jahressaldo für das Konto ermitteln
            year_data = csv_processor.get_data_by_quarter(5)  # Gesamtjahr
            if account in year_data:
                balance = year_data[account]
                account_name = csv_processor.get_account_name(account) or f"Konto {account}"
                chart_data.append({
                    'account': account,
                    'name': account_name,
                    'balance': balance
                })
        
        # Nach Betrag sortieren (größte zuerst)
        chart_data.sort(key=lambda x: abs(x['balance']), reverse=True)
        
        # Balkendiagramm erstellen
        chart_image = self._create_balance_chart(chart_data)
        if chart_image:
            story.append(chart_image)
        
        return story
    
    def _create_balance_chart(self, chart_data: List[Dict]) -> Optional[Image]:
        """Erstellt ein horizontales Balkendiagramm für Kontosalden"""
        if not chart_data:
            return None
        
        try:
            # Matplotlib-Stil setzen (kompatibel)
            plt.rcParams.update({'font.size': 10, 'figure.facecolor': 'white'})
            
            # Figure erstellen
            fig, ax = plt.subplots(figsize=(12, max(8, len(chart_data) * 0.4)))
            fig.patch.set_facecolor('white')
            
            # Daten vorbereiten
            accounts = [f"{item['account']} - {item['name']}" if item['name'] else f"Konto {item['account']}" for item in chart_data]
            balances = [item['balance'] for item in chart_data]
            
            # Farben basierend auf Vorzeichen
            colors = ['#28a745' if balance >= 0 else '#dc3545' for balance in balances]
            
            # Horizontales Balkendiagramm
            bars = ax.barh(accounts, balances, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
            
            # Achsen-Formatierung
            ax.set_xlabel('Saldo (€)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Sachkonten', fontsize=12, fontweight='bold')
            ax.set_title('Sachkonten-Salden im Überblick', fontsize=14, fontweight='bold', pad=20)
            
            # X-Achse formatieren (Euro-Beträge)
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f} €'.replace(',', '.')))
            
            # Nulllinie hervorheben
            ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
            
            # Grid anpassen
            ax.grid(True, axis='x', alpha=0.3)
            ax.set_axisbelow(True)
            
            # Layout optimieren
            plt.tight_layout()
            
            # Werte auf den Balken anzeigen
            for i, (bar, balance) in enumerate(zip(bars, balances)):
                if balance != 0:
                    # Position für Text bestimmen
                    x_pos = balance + (max(balances) - min(balances)) * 0.01 if balance >= 0 else balance - (max(balances) - min(balances)) * 0.01
                    ha = 'left' if balance >= 0 else 'right'
                    
                    # Formatierter Betrag
                    formatted_balance = f'{balance:,.0f} €'.replace(',', '.')
                    ax.text(x_pos, i, formatted_balance, ha=ha, va='center', fontweight='bold', fontsize=9)
            
            # Als Bytes speichern
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Temporäre Datei für ReportLab
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_file.write(img_buffer.read())
            temp_file.close()
            
            # ReportLab Image erstellen
            image = Image(temp_file.name, width=18*cm, height=12*cm)
            
            # Aufräumen
            plt.close(fig)
            img_buffer.close()
            
            return image
            
        except Exception as e:
            print(f"Fehler beim Erstellen des Diagramms: {e}")
            return None
    
    def _create_supergroup_bar_chart(self, summary: Dict[str, float], period: str) -> Optional[Drawing]:
        """Erstellt ein horizontales Balkendiagramm der Obergruppen"""
        try:
            # Obergruppen-Mappings laden
            super_group_mappings = self._load_super_group_mappings()
            
            # Daten nach Obergruppen organisieren
            super_groups = {}  # {super_group: total_amount}
            
            for bwa_group, amount in summary.items():
                super_group = super_group_mappings.get(bwa_group, "Nicht zugeordnet")
                
                if super_group not in super_groups:
                    super_groups[super_group] = 0.0
                super_groups[super_group] += amount
            
            # Wenn keine Daten vorhanden sind
            if not super_groups:
                return None
            
            # Sortiere nach Betrag (größte positive zuerst, dann negative)
            sorted_groups = sorted(super_groups.items(), 
                                 key=lambda x: x[1], reverse=True)
            
            # Diagramm-Dimensionen
            chart_width = 16 * cm
            chart_height = max(4 * cm, len(sorted_groups) * 0.8 * cm)
            drawing = Drawing(chart_width, chart_height)
            
            # Maximalen Betrag finden für Skalierung
            max_amount = max(abs(amount) for _, amount in sorted_groups) if sorted_groups else 1
            if max_amount == 0:
                max_amount = 1
            
            # Zeichenbereich definieren
            margin = 1 * cm
            bar_area_width = chart_width - 2 * margin
            bar_height = 0.6 * cm
            bar_spacing = 0.8 * cm
            
            # Mittellinie (0€-Linie)
            center_x = margin + bar_area_width / 2
            
            # Balken zeichnen
            y_pos = chart_height - margin - bar_height
            
            for super_group, amount in sorted_groups:
                # Balkenbreite berechnen (proportional zum Betrag)
                bar_width = (abs(amount) / max_amount) * (bar_area_width / 2)
                
                # Farbe bestimmen
                if amount >= 0:
                    bar_color = green
                    bar_x = center_x  # Positive Balken nach rechts
                else:
                    bar_color = red
                    bar_x = center_x - bar_width  # Negative Balken nach links
                
                # Balken zeichnen
                rect = Rect(bar_x, y_pos, bar_width, bar_height,
                           fillColor=bar_color, strokeColor=bar_color)
                drawing.add(rect)
                
                # Label links vom Balken (Gruppename)
                label_x = margin - 0.2 * cm
                label_text = f"{super_group}"
                if len(label_text) > 20:  # Kürzen wenn zu lang
                    label_text = label_text[:17] + "..."
                
                label = String(label_x, y_pos + bar_height/2 - 0.1*cm, 
                              label_text, fontSize=9, textAnchor='end')
                drawing.add(label)
                
                # Wert rechts vom Balken
                value_x = center_x + bar_area_width / 2 + 0.2 * cm
                value_text = self._format_amount(amount)
                value = String(value_x, y_pos + bar_height/2 - 0.1*cm,
                              value_text, fontSize=9, textAnchor='start')
                drawing.add(value)
                
                y_pos -= bar_spacing
            
            # Mittellinie (0€-Linie) zeichnen
            zero_line = Line(center_x, margin, center_x, chart_height - margin,
                           strokeColor=black, strokeWidth=1)
            drawing.add(zero_line)
            
            # 0€ Label
            zero_label = String(center_x, margin - 0.3*cm, "0€", 
                              fontSize=10, textAnchor='middle')
            drawing.add(zero_label)
            
            return drawing
            
        except Exception as e:
            print(f"Fehler beim Erstellen des Balkendiagramms: {e}")
            return None
