import sys
import os
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from translator import Translator

def main():
    app = QApplication(sys.argv)

    base_path = os.path.dirname(os.path.abspath(__file__))
    translations_dir = os.path.join(base_path, 'translations')

    translator = Translator(translations_dir)
    translator.load_language('en')

    window = MainWindow(translator)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
