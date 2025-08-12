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
                               TableStyle, PageBreak, Image, BaseDocTemplate, 
                               PageTemplate, Frame)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics import renderPDF
from PySide6.QtCore import QSettings
from datetime import datetime, date
from typing import Dict, List, Optional
import os
import json
import pandas as pd


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
        """Holt den Anfangskontostand aus den Einstellungen oder JSON-Daten"""
        # Wenn JSON-Daten verfügbar sind, diese verwenden
        if hasattr(self, '_temp_opening_balance'):
            return self._temp_opening_balance
        
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
        
    def generate_bwa_pdf(self, output_path: str, csv_processor, account_mappings: Dict[str, str] = None) -> bool:
        """Generiert das komplette BWA-PDF basierend auf Einstellungen oder JSON-Daten"""
        try:
            # Styles vor jeder PDF-Generierung neu erstellen um aktuelle Farben zu berücksichtigen
            self._create_custom_styles()
            
            # Prüfen ob Daten aus JSON stammen
            if csv_processor.is_json_source:
                return self._generate_bwa_from_json(output_path, csv_processor)
            
            # Standard-CSV-Verarbeitung
            return self._generate_bwa_from_csv(output_path, csv_processor, account_mappings)
            
        except Exception as e:
            print(f"Fehler bei der PDF-Generierung: {e}")
            return False
    
    def _generate_bwa_from_json(self, output_path: str, csv_processor) -> bool:
        """Generiert BWA-PDF aus JSON-Daten (überschreibt Einstellungen)"""
        try:
            # JSON-Daten aus dem CSV-Processor laden
            json_org_data = csv_processor.get_json_organization_data()
            json_balance_info = csv_processor.get_json_balance_info()
            json_account_mappings = csv_processor.get_json_account_mappings()
            json_super_group_mappings = csv_processor.get_json_super_group_mappings()
            
            # Temporäre Einstellungen aus JSON setzen
            self._apply_json_settings_temporarily(json_org_data, json_balance_info, json_super_group_mappings)
            
            # BWA generieren mit JSON-Daten
            result = self._generate_bwa_from_csv(output_path, csv_processor, json_account_mappings)
            
            # Einstellungen nach Generierung zurücksetzen (optional)
            # self._restore_original_settings()
            
            return result
            
        except Exception as e:
            print(f"Fehler bei der JSON-BWA-Generierung: {e}")
            return False
    
    def _apply_json_settings_temporarily(self, org_data: Dict, balance_info: Dict, super_group_mappings: Dict):
        """Wendet JSON-Daten temporär auf die Einstellungen an"""
        if org_data:
            # Organisation temporär überschreiben (ohne zu speichern)
            self._temp_org_data = org_data
            
        if balance_info:
            # Kontostand temporär überschreiben
            self._temp_opening_balance = balance_info.get('opening_balance', 0.0)
            
        if super_group_mappings:
            # Obergruppen temporär überschreiben
            self._temp_super_group_mappings = super_group_mappings
    
    def _generate_bwa_from_csv(self, output_path: str, csv_processor, account_mappings: Dict[str, str]) -> bool:
        """Generiert BWA-PDF aus CSV-Daten (Standard-Methode)"""
        try:
            # Styles vor jeder PDF-Generierung neu erstellen um aktuelle Farben zu berücksichtigen
            self._create_custom_styles()
            
            # Einstellungen laden
            settings = QSettings()
            generate_quarterly = settings.value("generate_quarterly_reports", True, type=bool)
            generate_accounts = settings.value("generate_account_reports", True, type=bool)
            generate_chart = settings.value("generate_chart_report", True, type=bool)
            quarter_mode = settings.value("quarter_mode", "cumulative")
            
            # Footer-Callback definieren
            def add_footer(canvas, doc):
                """Fügt Footer auf jeder Seite hinzu"""
                self._add_footer_to_page(canvas, doc)
            
            # PDF-Dokument mit Footer-Support erstellen
            doc = BaseDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=3*cm  # Mehr Platz für Footer
            )
            
            # Frame für den Hauptinhalt
            frame = Frame(
                2*cm,  # x
                3*cm,  # y (Platz für Footer lassen)
                A4[0] - 4*cm,  # width
                A4[1] - 5*cm,  # height (von Top-Margin bis Bottom-Margin)
                id='normal'
            )
            
            # PageTemplate mit Footer-Callback
            template = PageTemplate(
                id='normal',
                frames=[frame],
                onPage=add_footer
            )
            
            doc.addPageTemplates([template])
            
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
            # Für die Gesamtseitenzahl verwenden wir eine Schätzung
            # oder einen späteren Two-Pass-Ansatz
            self._total_pages = 0  # Wird bei Bedarf später gesetzt
            doc.build(story)
            
            # Nach dem Build kennen wir die Seitenzahl
            self._total_pages = doc.page
            
            # JSON-Export (falls aktiviert und nicht JSON-Quelle)
            if not csv_processor.is_json_source:
                json_export_enabled = settings.value("json_export", False, type=bool)
                if json_export_enabled:
                    self._generate_json_export(output_path, csv_processor, account_mappings)
            
            return True
            
        except Exception as e:
            print(f"Fehler bei der PDF-Generierung: {e}")
            return False
            
    def _load_super_group_mappings(self) -> Dict[str, str]:
        """Lädt die Obergruppen-Mappings aus den Einstellungen oder JSON-Daten"""
        # Wenn JSON-Daten verfügbar sind, diese verwenden
        if hasattr(self, '_temp_super_group_mappings'):
            return self._temp_super_group_mappings
        
        mappings_json = self.settings.value("super_group_mappings", "{}")
        try:
            return json.loads(mappings_json)
        except (json.JSONDecodeError, TypeError):
            return {}
            
    def _add_footer_to_page(self, canvas, doc):
        """Fügt Footer zu einer Seite hinzu"""
        # Footer-Einstellungen laden
        show_page_number = self.settings.value("show_page_number", True, type=bool)
        show_organization_footer = self.settings.value("show_organization_footer", True, type=bool)
        
        # Footer-Position (unten auf der Seite)
        footer_y = 1.5 * cm
        
        # Seitenzahl links (falls aktiviert)
        if show_page_number:
            page_num = canvas.getPageNumber()
            page_text = f"Seite {page_num}"
            
            canvas.saveState()
            canvas.setFont("Helvetica", 9)
            canvas.setFillColor(colors.lightgrey)  # Helle Schrift
            canvas.drawString(2 * cm, footer_y, page_text)
            canvas.restoreState()
        
        # Organisation rechts (falls aktiviert und vorhanden)
        if show_organization_footer:
            # Organisation aus den normalen Einstellungen laden (nicht aus organization_data JSON)
            organization_name = self.settings.value("organization/name", "")
            
            if organization_name:
                canvas.saveState()
                canvas.setFont("Helvetica", 9)
                canvas.setFillColor(colors.lightgrey)  # Helle Schrift
                # Rechts ausrichten
                text_width = canvas.stringWidth(organization_name, "Helvetica", 9)
                page_width = A4[0]
                canvas.drawString(page_width - 2 * cm - text_width, footer_y, organization_name)
                canvas.restoreState()
            
    def _generate_json_export(self, pdf_path: str, csv_processor, account_mappings: Dict[str, str]) -> bool:
        """Generiert JSON-Export der BWA-Daten parallel zum PDF"""
        try:
            # JSON-Pfad aus PDF-Pfad ableiten
            json_path = pdf_path.rsplit('.', 1)[0] + '.json'
            
            # Einstellungen laden
            settings = QSettings()
            generate_quarterly = settings.value("generate_quarterly_reports", True, type=bool)
            generate_accounts = settings.value("generate_account_reports", True, type=bool)
            quarter_mode = settings.value("quarter_mode", "cumulative")
            
            # Account-Mappings und Super-Group-Mappings laden
            super_group_mappings = self._load_super_group_mappings()
            
            # Account-Namen aus QSettings laden
            account_names = {}
            settings.beginGroup("account_names")
            for key in settings.allKeys():
                account_names[key] = settings.value(key, "")
            settings.endGroup()
            
            # JSON-Datenstruktur aufbauen
            json_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "year": datetime.now().year,
                    "quarter_mode": quarter_mode,
                    "generated_reports": {
                        "quarterly": generate_quarterly,
                        "account_details": generate_accounts
                    }
                },
                "organization": self._get_organization_data(),
                "balance_info": self._get_balance_info(csv_processor),
                "account_mappings": account_mappings if account_mappings else {},
                "account_names": account_names if account_names else {},
                "super_group_mappings": super_group_mappings if super_group_mappings else {},
                "yearly_summary": self._get_yearly_summary_data(csv_processor, account_mappings),
                "quarterly_summaries": [],
                "account_details": []
            }
            
            # Quartalsauswertungen hinzufügen (falls aktiviert)
            if generate_quarterly:
                for quarter in range(1, 5):
                    quarter_data = self._get_quarter_summary_data(quarter, csv_processor, account_mappings)
                    if quarter_data:
                        json_data["quarterly_summaries"].append(quarter_data)
            
            # Sachkonten-Details hinzufügen (falls aktiviert)
            if generate_accounts:
                accounts = csv_processor.get_account_numbers()
                for account in accounts:
                    account_data = self._get_account_detail_data(account, csv_processor)
                    if account_data:
                        json_data["account_details"].append(account_data)
            
            # JSON-Datei schreiben
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"JSON-Export erstellt: {json_path}")
            return True
            
        except Exception as e:
            print(f"Fehler beim JSON-Export: {e}")
            return False
    
    def _get_organization_data(self) -> Dict:
        """Holt Organisationsdaten für JSON-Export"""
        return {
            "name": self.settings.value("organization/name", ""),
            "street": self.settings.value("organization/street", ""),
            "zip": self.settings.value("organization/zip", ""),
            "city": self.settings.value("organization/city", ""),
            "phone": self.settings.value("organization/phone", ""),
            "email": self.settings.value("organization/email", ""),
            "info": self.settings.value("organization/info", "")
        }
    
    def _get_balance_info(self, csv_processor) -> Dict:
        """Holt Kontostandsinformationen für JSON-Export"""
        opening_balance = self._get_opening_balance()
        total_amount = self._calculate_total_amount(csv_processor)
        new_balance = self._calculate_new_balance(csv_processor)
        
        return {
            "opening_balance": float(opening_balance),
            "total_transactions": float(total_amount),
            "closing_balance": float(new_balance)
        }
    
    def _get_yearly_summary_data(self, csv_processor, account_mappings: Dict[str, str]) -> Dict:
        """Erstellt Jahresübersicht für JSON-Export"""
        year_data = csv_processor.get_year_data()
        
        if year_data.empty:
            return {"summary": {}, "total": 0.0}
        
        # Account-Namen aus QSettings laden
        settings = QSettings()
        account_names = {}
        settings.beginGroup("account_names")
        for key in settings.allKeys():
            account_names[key] = settings.value(key, "")
        settings.endGroup()
        
        # Detaillierte Zusammenfassung erstellen
        detailed_summary = self._create_detailed_year_summary(year_data, account_mappings, account_names)
        summary = detailed_summary.get('summary', {})
        detailed_accounts = detailed_summary.get('detailed_accounts', {})
        total = sum(summary.values()) if summary else 0.0
        
        # Obergruppen-Zuordnung hinzufügen
        super_group_mappings = self._load_super_group_mappings()
        grouped_summary = {}
        
        for bwa_group, amount in summary.items():
            super_group = super_group_mappings.get(bwa_group, "Nicht zugeordnet")
            if super_group not in grouped_summary:
                grouped_summary[super_group] = {}
            grouped_summary[super_group][bwa_group] = float(amount)
        
        return {
            "summary": grouped_summary,
            "bwa_groups": {k: float(v) for k, v in summary.items()},
            "detailed_accounts": detailed_accounts,
            "total": float(total)
        }
    
    def _get_quarter_summary_data(self, quarter: int, csv_processor, account_mappings: Dict[str, str]) -> Optional[Dict]:
        """Erstellt Quartalsübersicht für JSON-Export"""
        quarter_data = csv_processor.get_data_by_quarter(quarter)
        
        if quarter_data.empty:
            return None
        
        # Account-Namen aus QSettings laden
        settings = QSettings()
        account_names = {}
        settings.beginGroup("account_names")
        for key in settings.allKeys():
            account_names[key] = settings.value(key, "")
        settings.endGroup()
        
        # Detaillierte Zusammenfassung erstellen
        detailed_summary = self._create_detailed_quarter_summary(quarter_data, account_mappings, account_names)
        summary = detailed_summary.get('summary', {})
        detailed_accounts = detailed_summary.get('detailed_accounts', {})
        total = sum(summary.values()) if summary else 0.0
        
        # Kontostandsberechnung
        opening_balance = self._get_opening_balance()
        quarter_balance = self._calculate_quarter_balance(quarter, csv_processor)
        quarter_total = quarter_data['Betrag_Clean'].sum() if 'Betrag_Clean' in quarter_data.columns else 0.0
        
        # Obergruppen-Zuordnung
        super_group_mappings = self._load_super_group_mappings()
        grouped_summary = {}
        
        for bwa_group, amount in summary.items():
            super_group = super_group_mappings.get(bwa_group, "Nicht zugeordnet")
            if super_group not in grouped_summary:
                grouped_summary[super_group] = {}
            grouped_summary[super_group][bwa_group] = float(amount)
        
        return {
            "quarter": quarter,
            "summary": grouped_summary,
            "bwa_groups": {k: float(v) for k, v in summary.items()},
            "detailed_accounts": detailed_accounts,
            "total": float(total),
            "balance_info": {
                "opening_balance": float(opening_balance),
                "quarter_transactions": float(quarter_total),
                "quarter_end_balance": float(quarter_balance)
            }
        }
    
    def _get_account_detail_data(self, account_number: str, csv_processor) -> Optional[Dict]:
        """Erstellt Sachkonto-Details für JSON-Export"""
        account_data = csv_processor.get_data_by_account(account_number)
        
        if account_data.empty:
            return None
        
        # Sachkonto-Name ermitteln
        account_name = ""
        if 'Sachkonto' in account_data.columns:
            name = account_data['Sachkonto'].iloc[0]
            if name and str(name) != 'nan':
                account_name = str(name)
        
        # Buchungen aufbereiten
        transactions = []
        total = 0.0
        
        for _, row in account_data.iterrows():
            # Datum formatieren
            date_str = ""
            if 'Buchungstag' in row:
                try:
                    if hasattr(row['Buchungstag'], 'strftime'):
                        date_str = row['Buchungstag'].strftime('%Y-%m-%d')
                    else:
                        date_obj = pd.to_datetime(row['Buchungstag'])
                        date_str = date_obj.strftime('%Y-%m-%d')
                except:
                    date_str = str(row['Buchungstag'])
            
            buchungsnr = row['Buchungsnr.'] if 'Buchungsnr.' in row and pd.notna(row['Buchungsnr.']) else ''
            purpose = row['Verwendungszweck'] if 'Verwendungszweck' in row else ''
            amount = row['Betrag_Clean']
            
            transactions.append({
                "booking_number": str(buchungsnr),
                "date": date_str,
                "purpose": str(purpose),
                "amount": float(amount)
            })
            
            total += amount
        
        return {
            "account_number": str(account_number),
            "account_name": account_name,
            "total": float(total),
            "transaction_count": len(transactions),
            "transactions": transactions
        }
            
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
        
        # Organisationsdaten (aus Einstellungen oder JSON)
        if hasattr(self, '_temp_org_data'):
            # JSON-Organisationsdaten verwenden
            org_data = self._temp_org_data
            org_name = org_data.get("name", "")
            org_street = org_data.get("street", "")
            org_zip = org_data.get("zip", "")
            org_city = org_data.get("city", "")
            org_phone = org_data.get("phone", "")
            org_email = org_data.get("email", "")
            org_info = org_data.get("info", "")
        else:
            # Standard-Einstellungen verwenden
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
            
        # Account-Namen aus QSettings laden
        settings = QSettings()
        account_names = {}
        settings.beginGroup("account_names")
        for key in settings.allKeys():
            account_names[key] = settings.value(key, "")
        settings.endGroup()
        
        # Detaillierte BWA-Tabelle erstellen
        detailed_summary = self._create_detailed_quarter_summary(quarter_data, account_mappings, account_names)
        table = self._create_detailed_bwa_table(detailed_summary, f"Q{quarter}")
        
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
            chart_title = Paragraph("<b>BWA-Gruppen-Übersicht</b>", self.group_style)
            elements.append(chart_title)
            elements.append(Spacer(1, 0.5*cm))
            
            summary = detailed_summary.get('summary', {})
            chart = self._create_bwa_group_bar_chart(summary, f"Q{quarter}")
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
            
        # Account-Namen aus QSettings laden
        settings = QSettings()
        account_names = {}
        settings.beginGroup("account_names")
        for key in settings.allKeys():
            account_names[key] = settings.value(key, "")
        settings.endGroup()
        
        # Detaillierte BWA-Tabelle erstellen
        detailed_summary = self._create_detailed_year_summary(year_data, account_mappings, account_names)
        table = self._create_detailed_bwa_table(detailed_summary, "Jahr")
        
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
            chart_title = Paragraph("<b>BWA-Gruppen-Übersicht</b>", self.group_style)
            elements.append(chart_title)
            elements.append(Spacer(1, 0.5*cm))
            
            summary = detailed_summary.get('summary', {})
            chart = self._create_bwa_group_bar_chart(summary, "Jahr")
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
    
    def _create_detailed_quarter_summary(self, quarter_data, account_mappings: Dict[str, str], account_names: Dict[str, str] = None) -> Dict:
        """Erstellt detaillierte Zusammenfassung für ein Quartal mit einzelnen Sachkonten"""
        summary = {}
        detailed_accounts = {}  # {bwa_group: {account: {'name': str, 'amount': float}}}
        
        if account_names is None:
            account_names = {}
        
        # Gruppiert nach BWA-Gruppen und sammelt Sachkonto-Details
        for _, row in quarter_data.iterrows():
            account = str(row['Sachkontonr.'])
            amount = row['Betrag_Clean']
            
            group = account_mappings.get(account, f"Nicht zugeordnet ({account})")
            account_name = account_names.get(account, f"Sachkonto {account}")
            
            # BWA-Gruppen-Summe
            if group not in summary:
                summary[group] = 0.0
                detailed_accounts[group] = {}
            
            summary[group] += amount
            
            # Sachkonto-Details sammeln
            if account not in detailed_accounts[group]:
                detailed_accounts[group][account] = {
                    'name': account_name,
                    'amount': 0.0
                }
            
            detailed_accounts[group][account]['amount'] += amount
            
        return {
            'summary': summary,
            'detailed_accounts': detailed_accounts
        }
        
    def _create_year_summary(self, year_data, account_mappings: Dict[str, str]) -> Dict[str, float]:
        """Erstellt Zusammenfassung für das Jahr"""
        return self._create_quarter_summary(year_data, account_mappings)
    
    def _create_detailed_year_summary(self, year_data, account_mappings: Dict[str, str], account_names: Dict[str, str] = None) -> Dict:
        """Erstellt detaillierte Zusammenfassung für das Jahr mit einzelnen Sachkonten"""
        return self._create_detailed_quarter_summary(year_data, account_mappings, account_names)
        
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
    
    def _create_detailed_bwa_table(self, detailed_summary: Dict, period: str) -> Optional[Table]:
        """Erstellt eine detaillierte BWA-Tabelle mit Obergruppen, BWA-Gruppen und Sachkonten"""
        if not detailed_summary or 'summary' not in detailed_summary:
            return None
            
        summary = detailed_summary['summary']
        detailed_accounts = detailed_summary.get('detailed_accounts', {})
        
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
                bwa_group_amount = bwa_groups[bwa_group]
                bwa_group_amount_str = self._format_amount(bwa_group_amount)
                
                table_data.append([f"  • {bwa_group}", bwa_group_amount_str])
                
                # Hintergrundfarbe für BWA-Gruppe (heller als Obergruppe)
                lighter_color = colors.Color(
                    min(1.0, bg_color.red + 0.03),
                    min(1.0, bg_color.green + 0.03), 
                    min(1.0, bg_color.blue + 0.03)
                )
                style_commands.append(('BACKGROUND', (0, row_index), (-1, row_index), lighter_color))
                
                # Textfarbe für BWA-Gruppen-Betrag (rot bei negativ)
                if bwa_group_amount < 0:
                    style_commands.append(('TEXTCOLOR', (1, row_index), (1, row_index), colors.red))
                else:
                    style_commands.append(('TEXTCOLOR', (1, row_index), (1, row_index), colors.black))
                
                row_index += 1
                
                # Sachkonten unter dieser BWA-Gruppe anzeigen
                if bwa_group in detailed_accounts:
                    accounts = detailed_accounts[bwa_group]
                    
                    # Sachkonten nach Betrag sortieren (größte zuerst)
                    sorted_accounts = sorted(accounts.items(), 
                                           key=lambda x: abs(x[1]['amount']), 
                                           reverse=True)
                    
                    for account_nr, account_data in sorted_accounts:
                        account_name = account_data['name']
                        account_amount = account_data['amount']
                        account_amount_str = self._format_amount(account_amount)
                        
                        # Sachkonto-Name kürzen falls zu lang
                        display_name = account_name
                        if len(display_name) > 45:
                            display_name = display_name[:42] + "..."
                        
                        table_data.append([f"    {account_nr}: {display_name}", account_amount_str])
                        
                        # Noch hellere Hintergrundfarbe für Sachkonten
                        account_color = colors.Color(
                            min(1.0, lighter_color.red + 0.02),
                            min(1.0, lighter_color.green + 0.02), 
                            min(1.0, lighter_color.blue + 0.02)
                        )
                        style_commands.append(('BACKGROUND', (0, row_index), (-1, row_index), account_color))
                        
                        # Kleinere Schrift für Sachkonten
                        style_commands.append(('FONTSIZE', (0, row_index), (-1, row_index), 9))
                        
                        # Textfarbe für Sachkonto-Betrag (rot bei negativ)
                        if account_amount < 0:
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
        chart_data = {}
        
        # Für jedes Sachkonto den Gesamtsaldo berechnen
        for account in accounts:
            account_data = csv_processor.get_data_by_account(account)
            if not account_data.empty:
                # Sicherstellen, dass Beträge numerisch sind
                try:
                    total_balance = float(account_data['Betrag'].sum())
                except (ValueError, TypeError):
                    # Falls das fehlschlägt, bereinige die Daten (entferne € und ersetze , durch .)
                    amounts = account_data['Betrag'].astype(str)
                    amounts = amounts.str.replace('€', '').str.replace(',', '.').str.strip()
                    numeric_amounts = pd.to_numeric(amounts, errors='coerce')
                    total_balance = float(numeric_amounts.sum())
                
                account_name = csv_processor.get_account_name(account)
                
                # Sachkonto-Namen aus QSettings holen falls vorhanden
                settings = QSettings()
                stored_name = settings.value(f"account_names/{account}", "")
                if stored_name:
                    account_name = stored_name
                
                # Display-Name erstellen
                display_name = f"{account}: {account_name}" if account_name else f"Konto {account}"
                chart_data[display_name] = total_balance
        
        # Leeren Text hinzufügen falls keine Daten
        if not chart_data:
            no_data_text = Paragraph("Keine Sachkontendaten verfügbar", self.normal_style)
            story.append(no_data_text)
            return story
        
        # Balkendiagramm erstellen
        chart = self._create_account_balance_chart(chart_data)
        if chart:
            story.append(chart)
        else:
            error_text = Paragraph("Fehler beim Erstellen des Balkendiagramms", self.normal_style)
            story.append(error_text)
        
        return story
    
    def _create_account_balance_chart(self, account_data: Dict[str, float]) -> Optional[Drawing]:
        """Erstellt ein horizontales Balkendiagramm für Sachkonto-Salden"""
        try:
            # Wenn keine Daten vorhanden sind
            if not account_data:
                return None
            
            # Nach Betrag sortieren (größte absolute Werte zuerst)
            sorted_accounts = sorted(account_data.items(), 
                                   key=lambda x: abs(x[1]), reverse=True)
            
            # ALLE Konten anzeigen (nicht mehr auf 20 begrenzen)
            
            # Diagramm-Dimensionen (dynamisch basierend auf Anzahl Konten)
            chart_width = 16 * cm
            chart_height = max(8 * cm, len(sorted_accounts) * 0.5 * cm)
            drawing = Drawing(chart_width, chart_height)
            
            # Skalierung für große Ausreißer optimieren
            amounts = [abs(amount) for _, amount in sorted_accounts]
            
            # Outlier-Erkennung: Werte die 3x größer als der Median sind
            median_amount = sorted(amounts)[len(amounts)//2] if amounts else 1
            outlier_threshold = median_amount * 3
            max_amount = median_amount * 4  # Maximale Skalierung begrenzen
            
            # Zeichenbereich definieren
            left_margin = 5.5 * cm  # Mehr Platz für Sachkonto-Namen und Zickzack-Linien
            right_margin = 2.5 * cm  # Mehr Platz für Beträge und Asterisk-Markierungen
            bar_area_width = chart_width - left_margin - right_margin  # 8 cm für Balken
            bar_height = 0.4 * cm
            bar_spacing = 0.5 * cm
            
            # Mittellinie (0€-Linie)
            center_x = left_margin + bar_area_width / 2
            
            # Balken zeichnen
            y_pos = chart_height - left_margin - bar_height
            
            for account_name, amount in sorted_accounts:
                abs_amount = abs(amount)
                is_outlier = abs_amount > outlier_threshold
                
                # Balkenbreite berechnen (begrenzt für Outlier)
                display_amount = min(abs_amount, max_amount)
                bar_width = (display_amount / max_amount) * (bar_area_width / 2)
                
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
                
                # Outlier-Kennzeichnung: Zickzack-Linie am Ende des Balkens
                if is_outlier:
                    # Zickzack-Linie für gekürzten Balken
                    zigzag_x = bar_x + bar_width if amount >= 0 else bar_x
                    zigzag_y = y_pos + bar_height/2
                    
                    # Kleine Zickzack-Linien
                    for i in range(3):
                        x_offset = (-0.1 + i * 0.05) * cm if amount < 0 else (0.05 + i * 0.05) * cm
                        y_offset1 = -0.05 * cm if i % 2 == 0 else 0.05 * cm
                        y_offset2 = 0.05 * cm if i % 2 == 0 else -0.05 * cm
                        
                        zigzag_line1 = Line(zigzag_x + x_offset, zigzag_y + y_offset1,
                                          zigzag_x + x_offset + 0.02*cm, zigzag_y + y_offset2,
                                          strokeColor=black, strokeWidth=1)
                        drawing.add(zigzag_line1)
                
                # Label links vom Balken (Sachkonto-Name)
                label_x = left_margin - 0.3 * cm  # Mehr Abstand zum Balken
                label_text = account_name
                if len(label_text) > 45:  # Längere Sachkonto-Namen erlauben
                    label_text = label_text[:42] + "..."
                
                label = String(label_x, y_pos + bar_height/2 - 0.1*cm, 
                              label_text, fontSize=8, textAnchor='end')
                drawing.add(label)
                
                # Wert rechts vom Balken (mit Outlier-Kennzeichnung)
                value_x = left_margin + bar_area_width + 0.2 * cm  # Mehr Abstand zum Balken
                value_text = self._format_amount(amount)
                if is_outlier:
                    value_text += " *"  # Asterisk für gekürzte Balken
                
                value = String(value_x, y_pos + bar_height/2 - 0.1*cm,
                              value_text, fontSize=8, textAnchor='start')
                drawing.add(value)
                
                y_pos -= bar_spacing
            
            # Mittellinie (0€-Linie) zeichnen
            zero_line = Line(center_x, left_margin, center_x, chart_height - left_margin,
                           strokeColor=black, strokeWidth=1)
            drawing.add(zero_line)
            
            # 0€ Label unter dem Diagramm
            zero_label_y = left_margin - 0.7*cm
            zero_label = String(center_x, zero_label_y, "0€", 
                              fontSize=9, textAnchor='middle')
            drawing.add(zero_label)
            
            # Legende für gekürzte Balken
            outliers_count = sum(1 for _, amount in sorted_accounts if abs(amount) > outlier_threshold)
            if outliers_count > 0:
                legend_y = chart_height - 0.5*cm
                legend_text = f"* = Balken gekürzt (Skalierung begrenzt) - {outliers_count} Ausreißer"
                legend_label = String(chart_width/2, legend_y, legend_text, 
                                    fontSize=8, textAnchor='middle')
                drawing.add(legend_label)
            
            # Info-Text für Anzahl Konten
            info_y = chart_height - (0.8*cm if outliers_count > 0 else 0.5*cm)
            info_text = f"Alle {len(sorted_accounts)} Sachkonten (nach Betragshöhe sortiert)"
            info_label = String(chart_width/2, info_y, info_text, 
                              fontSize=8, textAnchor='middle')
            drawing.add(info_label)
            
            return drawing
            
        except Exception as e:
            print(f"Fehler beim Erstellen des Sachkonto-Balkendiagramms: {e}")
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

    def _create_bwa_group_bar_chart(self, summary: Dict[str, float], period: str) -> Optional[Drawing]:
        """Erstellt ein horizontales Balkendiagramm der BWA-Gruppen"""
        try:
            # BWA-Gruppen direkt aus dem Summary verwenden
            bwa_groups = summary.copy()
            
            # Wenn keine Daten vorhanden sind
            if not bwa_groups:
                return None
            
            # Sortiere nach Betrag (größte positive zuerst, dann negative)
            sorted_groups = sorted(bwa_groups.items(), 
                                 key=lambda x: x[1], reverse=True)
            
            # Diagramm-Dimensionen (optimiert für maximale Platznutzung)
            chart_width = 16 * cm  # Zurück zu 16cm für bessere Platznutzung
            chart_height = max(4 * cm, len(sorted_groups) * 0.8 * cm)
            drawing = Drawing(chart_width, chart_height)
            
            # Maximalen Betrag finden für Skalierung
            max_amount = max(abs(amount) for _, amount in sorted_groups) if sorted_groups else 1
            if max_amount == 0:
                max_amount = 1
            
            # Zeichenbereich definieren (optimiert für maximale Balkenbreite)
            left_margin = 3.5 * cm  # Genug Platz für BWA-Gruppennamen links
            right_margin = 1.5 * cm  # Kompakter rechter Rand für Beträge
            bar_area_width = chart_width - left_margin - right_margin  # 11 cm für Balken
            bar_height = 0.6 * cm
            bar_spacing = 0.8 * cm
            
            # Mittellinie (0€-Linie)
            center_x = left_margin + bar_area_width / 2
            
            # Balken zeichnen
            y_pos = chart_height - left_margin - bar_height
            
            for bwa_group, amount in sorted_groups:
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
                
                # Label links vom Balken (BWA-Gruppenname)
                label_x = left_margin - 0.2 * cm
                label_text = f"{bwa_group}"
                if len(label_text) > 35:  # Noch längere Namen erlauben
                    label_text = label_text[:32] + "..."
                
                label = String(label_x, y_pos + bar_height/2 - 0.1*cm, 
                              label_text, fontSize=9, textAnchor='end')
                drawing.add(label)
                
                # Wert rechts vom Balken (kompakter positioniert)
                value_x = left_margin + bar_area_width + 0.1 * cm  # Näher an die Balken
                value_text = self._format_amount(amount)
                value = String(value_x, y_pos + bar_height/2 - 0.1*cm,
                              value_text, fontSize=9, textAnchor='start')
                drawing.add(value)
                
                y_pos -= bar_spacing
            
            # Mittellinie (0€-Linie) zeichnen (nur im Diagrammbereich)
            zero_line = Line(center_x, left_margin, center_x, chart_height - left_margin,
                           strokeColor=black, strokeWidth=1)
            drawing.add(zero_line)
            
            # 0€ Label deutlich unter dem Diagramm positionieren (außerhalb des Diagrammbereichs)
            zero_label_y = left_margin - 0.7*cm  # Deutlich unter dem unteren Diagrammrand
            zero_label = String(center_x, zero_label_y, "0€", 
                              fontSize=9, textAnchor='middle')
            drawing.add(zero_label)
            
            return drawing
            
        except Exception as e:
            print(f"Fehler beim Erstellen des BWA-Gruppen-Balkendiagramms: {e}")
            return None
