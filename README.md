# 📊 Finanzauswertung Ehrenamt

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-31/31%20passing%20(100%)-brightgreen.svg)](test/)
[![Coverage](https://img.shields.io/badge/coverage-95.0%-brightgreen.svg)](test/)
[![PySide6](https://img.shields.io/badge/PySide6-GUI-green.svg)](https://www.qt.io/qt-for-python)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/Java-Fish/finanzbericht_ehrenamt)
[![Made with AI](https://img.shields.io/badge/Made%20with-AI%20%F0%9F%A4%96-ff69b4.svg)](https://github.com/Java-Fish/finanzbericht_ehrenamt)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Eine benutzerfreundliche Desktop-Anwendung zur **BWA-Erstellung** und **Finanzanalyse** für ehrenamtliche Organisationen, Vereine und kleine Unternehmen.

## ✨ Features

### 📈 **BWA-Generierung**
- **Automatische BWA-Erstellung** aus Buchungsdaten
- **Quartalsbezogene Auswertungen** (einzeln oder kumulativ)
- **Flexible Sachkonto-Gruppierung** in BWA-Kategorien
- **PDF-Export** für professionelle Berichte

### 📁 **Datei-Import**
- **Multi-Format-Support**: Excel (.xlsx), LibreOffice Calc (.ods), CSV
- **Multi-Sheet-Unterstützung**: Automatische Blatt-Auswahl bei Excel/ODS
- **Drag & Drop Interface**: Einfaches Importieren per Ziehen & Ablegen
- **Intelligente Spalten-Erkennung**: Automatische Zuordnung von Sachkonto, Betrag, Datum

### 🏢 **Organisationsverwaltung**
- **Organisationsprofile**: Speicherung von Vereinsdaten und Logo
- **Sachkonto-Namen**: Automatische Extraktion und manuelle Bearbeitung
- **Flexible Konfiguration**: Anpassbare BWA-Gruppierungen
- **Einstellungs-Export/Import**: Backup und Wiederherstellung

### 🎨 **Benutzerfreundlichkeit**
- **Moderne GUI**: Intuitive Benutzeroberfläche mit PySide6
- **Plattformübergreifend**: Windows, macOS und Linux
- **Deutsche Lokalisierung**: Vollständig auf Deutsch
- **Responsive Design**: Anpassungsfähige Layouts

## 🚀 Schneller Einstieg

### Option 1: Fertige App (Empfohlen)

**Windows:**
```bash
python clear_build.py
# Starte: build/Finanzauswertung_Ehrenamt.exe
```

**macOS:**
```bash
python clear_build.py
# Starte: open "build/Finanzauswertung_Ehrenamt.app"
```

### Option 2: Aus Quellcode

1. **Repository klonen:**
   ```bash
   git clone https://github.com/Java-Fish/finanzbericht_ehrenamt.git
   cd finanzbericht_ehrenamt
   ```

2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Anwendung starten:**
   ```bash
   python main.py
   ```

## 🛠️ Installation & Build

### 📦 **Schnell-Installation**

```bash
# 1. Repository klonen
git clone https://github.com/Java-Fish/finanzbericht_ehrenamt.git
cd finanzbericht_ehrenamt

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. App starten
python main.py
```

### 🏗️ **Cross-Platform Building**

#### **Lokale Builds:**
```bash
# Automatisch für aktuelle Plattform
python build.py

# Spezifische Plattform (nur auf entsprechendem System)
python build.py --platform windows  # Nur auf Windows
python build.py --platform macos    # Nur auf macOS  
python build.py --platform linux    # Nur auf Linux
```

#### **Windows .exe ohne Windows-System:**
```bash
# 🚀 EMPFOHLEN: GitHub Actions (Automatisch & Kostenlos)
git push origin main
# → Erstellt automatisch .exe, .app und Linux builds

# Alternative: VirtualBox Windows VM
# Siehe: docs/CROSS_PLATFORM_BUILD.md für Details
```

### Systemanforderungen
- **Python 3.8+** (empfohlen: Python 3.10+)
- **Betriebssystem**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **RAM**: Mindestens 4 GB (empfohlen: 8 GB)
- **Festplatte**: 500 MB freier Speicherplatz

### Build-Kommandos

```bash
# Alle Tests ausführen
python test/run_all_tests.py

# App für aktuelle Plattform bauen
python build.py

# Clean Build (Tests + App-Build)
python clear_build.py

# Nur Build-Ordner säubern
python build.py --clean-only
```

## 📋 Verwendung

### 1. **Erste Schritte**
1. **App starten** (siehe Schneller Einstieg)
2. **Organisation einrichten**: Vereinsdaten und Logo hinzufügen
3. **Finanzdaten importieren**: Excel/ODS/CSV-Datei per Drag & Drop

### 2. **Datei-Import**
- **Unterstützte Formate**: `.xlsx`, `.ods`, `.csv`
- **Erforderliche Spalten**: 
  - `Sachkontonr.` (Kontonummer)
  - `Betrag` (Buchungsbetrag)
  - `Buchungstag` (Datum)
- **Optional**: `Sachkonto` (Kontoname), `Beschreibung`

### 3. **BWA-Gruppierung**
- **Sachkonten zuordnen**: Konten den BWA-Kategorien zuweisen
- **Obergruppen definieren**: Individuelle Gruppierungen erstellen
- **Namen bearbeiten**: Sachkonto-Bezeichnungen anpassen

### 4. **Auswertung generieren**
- **Quartal auswählen**: Q1, Q2, Q3, Q4
- **Modus wählen**: Einzelquartal oder kumulativ
- **PDF erstellen**: Professioneller BWA-Bericht

## 📁 Projektstruktur

```
finanzbericht_ehrenamt/
├── 📂 src/                    # Hauptquellcode
│   ├── 📂 gui/               # Benutzeroberfläche
│   ├── 📂 utils/             # Hilfsfunktionen
│   ├── 📂 dialogs/           # Dialoge
│   └── 📂 settings/          # Einstellungen
├── 📂 resources/             # Ressourcen (Icons, etc.)
├── 📂 test/                  # Tests
├── 📂 handbuch/              # Dokumentation
├── 📂 build/                 # Gebaute Apps
├── 🐍 main.py               # Haupteinstiegspunkt
├── 🔨 build.py              # Build-Manager
├── 🧪 clear_build.py        # Test + Build
└── 📋 requirements.txt      # Python-Abhängigkeiten
```

## 🧪 Tests

```bash
# Alle Tests ausführen
python test/run_all_tests.py

# Einzelne Tests
python test/test_string_consistency.py
python test/test_multi_sheet_import.py
python test/test_account_names.py
```

## 🤝 Mitwirken

1. **Fork** des Repositories erstellen
2. **Feature Branch** erstellen (`git checkout -b feature/AmazingFeature`)
3. **Änderungen committen** (`git commit -m 'Add some AmazingFeature'`)
4. **Branch pushen** (`git push origin feature/AmazingFeature`)
5. **Pull Request** öffnen

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz - siehe [LICENSE](LICENSE) Datei für Details.

## 🆘 Support & Dokumentation

- **📖 Handbuch**: [handbuch/](handbuch/) - Vollständige Dokumentation
- **🐛 Issues**: [GitHub Issues](https://github.com/Java-Fish/finanzbericht_ehrenamt/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/Java-Fish/finanzbericht_ehrenamt/discussions)

## 🙏 Danksagungen

- **Qt/PySide6** für das hervorragende GUI-Framework
- **pandas** für die leistungsstarke Datenverarbeitung
- **OpenPyXL** für Excel-Unterstützung
- **PyMuPDF** für PDF-Generierung
- **AI-Tools** für Entwicklungsunterstützung

---

<div align="center">

**[⭐ Stern geben](https://github.com/Java-Fish/finanzbericht_ehrenamt)** • **[🐛 Bug melden](https://github.com/Java-Fish/finanzbericht_ehrenamt/issues)** • **[💡 Feature vorschlagen](https://github.com/Java-Fish/finanzbericht_ehrenamt/discussions)**

Gemacht mit ❤️ für ehrenamtliche Organisationen

</div>

### Dateien verwenden
1. **Datei importieren:**
   - Ziehen Sie eine Excel-, LibreOffice Calc- oder CSV-Datei in die Drag & Drop-Fläche
   - Oder klicken Sie auf "Datei auswählen" um den Dateiexplorer zu öffnen

## Entwicklung

### App erstellen
```bash
# Alle Schritte auf einmal
make build-release

# Oder einzeln:
make clean          # Build-Dateien löschen
make install        # Abhängigkeiten installieren  
make test           # Tests ausführen
make build          # App erstellen
```

### Verfügbare Make-Kommandos
- `make build` - Erstellt die standalone .app-Datei
- `make clean` - Löscht Build-Dateien
- `make install` - Installiert Abhängigkeiten
- `make test` - Führt Tests aus
- `make run` - Startet die Anwendung direkt
- `make build-release` - Vollständiger Release-Build

## Lizenz

Dieses Projekt steht unter der Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).

Das bedeutet:
- ✅ Sie dürfen das Werk teilen und bearbeiten
- ✅ Namensnennung erforderlich
- ❌ Keine kommerzielle Nutzung
- ✅ Weitergabe unter gleichen Bedingungen erlaubt

Vollständige Lizenz: https://creativecommons.org/licenses/by-nc/4.0/

## Entwicklung

### Projektstruktur
```
finanzauswertungEhrenamt/
├── main.py                 # Haupteinstiegspunkt
├── requirements.txt        # Python-Abhängigkeiten
├── src/                   # Hauptquellcode
│   ├── main_window.py     # Hauptfenster
│   ├── settings/          # Einstellungen-Module
│   ├── widgets/           # Benutzerdefinierte Widgets
│   └── utils/             # Hilfsfunktionen
├── resources/             # Ressourcen (Icons, Übersetzungen)
└── LICENSE                # Lizenzdatei
```

## Unterstützte Dateiformate

- Microsoft Excel (.xlsx, .xls)
- LibreOffice Calc (.ods)
- CSV-Dateien (.csv)

## Systemanforderungen

- **macOS**: 10.14 oder höher
- **Windows**: Windows 10 oder höher
- **Linux**: Ubuntu 18.04 LTS oder äquivalent

## Beitragen

Beiträge sind willkommen! Bitte beachten Sie die CC BY-NC 4.0 Lizenz bei Ihren Beiträgen.
