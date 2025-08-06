"""
Test-Utilities für robuste GUI-Tests in verschiedenen Umgebungen.
"""
import sys
import os


def setup_gui_test_environment():
    """
    Richtet die Test-Umgebung für GUI-Tests ein.
    Funktioniert sowohl lokal als auch in CI/CD-Umgebungen ohne Display.
    """
    # Setze QT_QPA_PLATFORM für headless Testing
    if 'QT_QPA_PLATFORM' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    # Deaktiviere Qt-Warnungen für Tests
    os.environ['QT_LOGGING_RULES'] = 'qt.qpa.xcb.warning=false'


def setup_import_paths():
    """
    Richtet die Import-Pfade für Tests ein.
    Funktioniert sowohl lokal als auch in CI/CD-Umgebungen.
    """
    # Finde das Projekt-Root-Verzeichnis
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Füge Projekt-Root zum Python-Pfad hinzu, wenn nicht bereits vorhanden
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Stelle sicher, dass src-Verzeichnis existiert
    src_dir = os.path.join(project_root, 'src')
    if not os.path.exists(src_dir):
        raise ImportError(f"Source directory not found: {src_dir}")


def create_qapplication():
    """
    Erstellt eine QApplication-Instanz für Tests.
    Wiederverwendet existierende Instanz wenn möglich.
    """
    try:
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            # Wichtig: App nicht beenden nach Tests
            app.setQuitOnLastWindowClosed(False)
        
        return app
    except ImportError:
        # Fallback für Umgebungen ohne PySide6
        return None


def skip_if_no_display():
    """
    Decorator um Tests zu überspringen wenn kein Display verfügbar ist.
    """
    import unittest
    
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            try:
                app = create_qapplication()
                if app is None:
                    raise unittest.SkipTest("GUI-Framework nicht verfügbar")
                return test_func(*args, **kwargs)
            except Exception as e:
                if "cannot connect to display" in str(e).lower():
                    raise unittest.SkipTest(f"Kein Display verfügbar: {e}")
                raise
        return wrapper
    return decorator


def safe_gui_test(test_func):
    """
    Decorator für sichere GUI-Tests.
    Richtet Umgebung ein und behandelt Display-Probleme.
    """
    import unittest
    
    def wrapper(*args, **kwargs):
        try:
            setup_gui_test_environment()
            setup_import_paths()
            return test_func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in [
                "cannot connect to display", 
                "no display", 
                "display not found",
                "xcb"
            ]):
                raise unittest.SkipTest(f"GUI-Test übersprungen (kein Display): {e}")
            raise
    
    return wrapper


# Automatisches Setup beim Import
setup_gui_test_environment()
setup_import_paths()
