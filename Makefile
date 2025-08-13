# Makefile für Finanzauswertung Ehrenamt
.PHONY: help build clean install test run

# Standard-Ziel
help:
	@echo "Verfügbare Kommandos:"
	@echo "  build     - Erstellt die standalone .app-Datei"
	@echo "  clean     - Löscht Build-Dateien"
	@echo "  install   - Installiert Abhängigkeiten"
	@echo "  test      - Führt Tests aus"
	@echo "  run       - Startet die Anwendung"

# App erstellen
build:
	@echo "🏗️  Erstelle standalone App..."
	python3 clean_build.py

# Build-Dateien löschen
clean:
	@echo "🧹 Lösche Build-Dateien..."
	rm -rf build/ dist/ __pycache__/ *.pyc
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Abhängigkeiten installieren
install:
	@echo "📦 Installiere Abhängigkeiten..."
	pip3 install -r requirements.txt

# Tests ausführen
test:
	@echo "🧪 Führe Tests aus..."
	python3 test/run_all_tests.py

# Anwendung direkt starten (für Entwicklung)
run:
	@echo "🚀 Starte Anwendung..."
	python3 main.py

# Vollständiger Build-Prozess
build-release: clean install test build
	@echo "✅ Release-Build abgeschlossen!"
