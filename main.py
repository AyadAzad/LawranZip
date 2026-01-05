import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
from main_window import MainWindow
from translator import Translator


def main():
    app = QApplication(sys.argv)

    base_path = os.path.dirname(os.path.abspath(__file__))
    translations_dir = os.path.join(base_path, 'translations')

    translator = Translator(translations_dir)
    translator.load_language('en')

    window = MainWindow(translator)

    # Define a function to handle arguments after the window is shown
    def process_arguments():
        try:
            if len(sys.argv) > 2:  # Context menu actions like "extract here", "create zip"
                window._is_command_line = True
                # Connect the finished signal to quit the app
                window.command_line_finished.connect(app.quit)
                # Hide the window for command line operations if desired, 
                # but for now let's keep it hidden or show a progress dialog.
                # The MainWindow init sets it to hidden by default until .show() is called.
                # But for command line ops, we might NOT want to show the main window, 
                # just the progress dialogs.
                window.handle_command_line_arguments(sys.argv)
            elif len(sys.argv) == 2:  # Double-click "open" action
                file_path = sys.argv[1]
                # Show the window first!
                window.show()
                # Then load the archive
                window.open_archive_from_path(file_path)
            else:  # No arguments, just launch the app normally
                window.show()
        except Exception as e:
            # If something goes wrong, at least show the window and an error
            window.show()
            QMessageBox.critical(window, "Error", f"An error occurred during startup: {str(e)}")

    # Use QTimer to run argument processing immediately after the event loop starts
    QTimer.singleShot(0, process_arguments)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
