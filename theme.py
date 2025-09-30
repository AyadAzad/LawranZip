from PySide6.QtGui import QPalette, QColor

#
# Legendary Themes v3 by Lawran
#

def get_dark_theme_palette():
    """Returns the palette for the refined dark theme."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1a1b1e"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e0e1e3"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#202124"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2b2c30"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#202124"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#e0e1e3"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e0e1e3"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#2b2c30"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#e0e1e3"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff5c5c"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#3498db"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#3498db"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    return palette

def get_light_theme_palette():
    """Returns the palette for the refined light theme."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f9f9f9"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#1d1d1d"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f0f0f0"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#1d1d1d"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#1d1d1d"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#f0f0f0"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1d1d1d"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#d9534f"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#2980b9"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2980b9"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    return palette


def get_aurora_theme_palette():
    """Returns the palette for the new aurora theme."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#161b22"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#21262d"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#161b22"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#21262d"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#f778ba"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#58a6ff"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#1f6feb"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    return palette

def get_base_stylesheet():
    """Returns the base QSS for all themes."""
    return '''
        /* General */
        * {
            font-family: "Segoe UI", "Roboto", "Helvetica Neue", "Arial", sans-serif;
            font-size: 14px;
        }
        QMainWindow {
            background-color: %WINDOW_BG%;
        }
        QWidget {
            color: %TEXT_COLOR%;
            background-color: %WINDOW_BG%;
        }
        /* Tooltip */
        QToolTip {
            border: 1px solid %BORDER_COLOR%;
            background-color: %TOOLTIP_BG%;
            color: %TOOLTIP_TEXT%;
            padding: 8px;
            border-radius: 4px;
        }
        /* Tree Widget */
        QTreeWidget {
            background-color: %BASE_BG%;
            border: 1px solid %BORDER_COLOR%;
            border-radius: 4px;
            padding: 5px;
        }
        QTreeWidget::item {
            padding: 6px 4px;
            border-radius: 4px;
        }
        QTreeWidget::item:hover {
            background-color: %ALTERNATE_BG%;
        }
        QTreeWidget::item:selected {
            background-color: %HIGHLIGHT_COLOR%;
            color: %HIGHLIGHTED_TEXT%;
        }
        /* Header */
        QHeaderView::section {
            background-color: %BASE_BG%;
            border: none;
            border-bottom: 1px solid %BORDER_COLOR%;
            padding: 8px;
            font-weight: 600;
        }
        /* Buttons */
        QPushButton {
            background-color: %BUTTON_BG%;
            border: 1px solid %BORDER_COLOR%;
            padding: 8px 18px;
            border-radius: 4px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: %ALTERNATE_BG%;
            border-color: %HIGHLIGHT_COLOR%;
        }
        QPushButton:pressed {
            background-color: %BORDER_COLOR%;
        }
        QPushButton:disabled {
            background-color: %BASE_BG%;
            color: %DISABLED_TEXT%;
            border-color: %DISABLED_BORDER%;
        }
        /* Line Edit */
        QLineEdit {
            background-color: %BASE_BG%;
            border: 1px solid %BORDER_COLOR%;
            border-radius: 4px;
            padding: 6px;
        }
        QLineEdit:focus {
            border: 2px solid %HIGHLIGHT_COLOR%;
        }
        QLineEdit:read-only {
            background-color: %ALTERNATE_BG%;
        }
        /* Progress Bar */
        QProgressBar {
            border: 1px solid %BORDER_COLOR%;
            border-radius: 4px;
            text-align: center;
            color: %TEXT_COLOR%;
            font-weight: 600;
        }
        QProgressBar::chunk {
            background-color: %PROGRESS_CHUNK%;
            border-radius: 4px;
        }
        /* Menu */
        QMenuBar {
            background-color: %WINDOW_BG%;
            border-bottom: 1px solid %BORDER_COLOR%;
        }
        QMenuBar::item {
            background: transparent;
            padding: 6px 12px;
        }
        QMenuBar::item:selected {
            background: %ALTERNATE_BG%;
            border-radius: 4px;
        }
        QMenu {
            background-color: %BASE_BG%;
            border: 1px solid %BORDER_COLOR%;
            padding: 5px;
        }
        QMenu::item {
            padding: 6px 24px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: %HIGHLIGHT_COLOR%;
            color: %HIGHLIGHTED_TEXT%;
        }
        /* Scrollbar */
        QScrollBar:vertical {
            border: none;
            background: %BASE_BG%;
            width: 14px;
            margin: 16px 0 16px 0;
        }
        QScrollBar::handle:vertical {
            background: %ALTERNATE_BG%;
            min-height: 25px;
            border-radius: 7px;
        }
        QScrollBar::handle:vertical:hover {
            background: %BORDER_COLOR%;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        QScrollBar:horizontal {
            border: none;
            background: %BASE_BG%;
            height: 14px;
            margin: 0 16px 0 16px;
        }
        QScrollBar::handle:horizontal {
            background: %ALTERNATE_BG%;
            min-width: 25px;
            border-radius: 7px;
        }
        QScrollBar::handle:horizontal:hover {
            background: %BORDER_COLOR%;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
    '''

def get_stylesheet(theme_name):
    """Returns the QSS for the specified theme."""
    base_sheet = get_base_stylesheet()
    colors = {}

    if theme_name == 'dark':
        colors = {
            "%WINDOW_BG%"       : "#1a1b1e",
            "%BASE_BG%"         : "#202124",
            "%ALTERNATE_BG%"   : "#2b2c30",
            "%TEXT_COLOR%"      : "#e0e1e3",
            "%BORDER_COLOR%"    : "#3c3d40",
            "%BUTTON_BG%"      : "#2b2c30",
            "%TOOLTIP_BG%"     : "#202124",
            "%TOOLTIP_TEXT%"   : "#e0e1e3",
            "%HIGHLIGHT_COLOR%" : "#3498db",
            "%HIGHLIGHTED_TEXT%": "#ffffff",
            "%PROGRESS_CHUNK%"  : "#3498db",
            "%DISABLED_TEXT%"   : "#6c6e73",
            "%DISABLED_BORDER%" : "#2b2c30",
        }
    elif theme_name == 'light':
        colors = {
            "%WINDOW_BG%"       : "#f9f9f9",
            "%BASE_BG%"         : "#ffffff",
            "%ALTERNATE_BG%"   : "#f0f0f0",
            "%TEXT_COLOR%"      : "#1d1d1d",
            "%BORDER_COLOR%"    : "#dcdcdc",
            "%BUTTON_BG%"      : "#f0f0f0",
            "%TOOLTIP_BG%"     : "#ffffff",
            "%TOOLTIP_TEXT%"   : "#1d1d1d",
            "%HIGHLIGHT_COLOR%" : "#2980b9",
            "%HIGHLIGHTED_TEXT%": "#ffffff",
            "%PROGRESS_CHUNK%"  : "#2980b9",
            "%DISABLED_TEXT%"   : "#a0a0a0",
            "%DISABLED_BORDER%" : "#e0e0e0",
        }
    elif theme_name == 'aurora':
        colors = {
            "%WINDOW_BG%"       : "#0d1117",
            "%BASE_BG%"         : "#161b22",
            "%ALTERNATE_BG%"   : "#21262d",
            "%TEXT_COLOR%"      : "#c9d1d9",
            "%BORDER_COLOR%"    : "#30363d",
            "%BUTTON_BG%"      : "#21262d",
            "%TOOLTIP_BG%"     : "#161b22",
            "%TOOLTIP_TEXT%"   : "#c9d1d9",
            "%HIGHLIGHT_COLOR%" : "#1f6feb",
            "%HIGHLIGHTED_TEXT%": "#ffffff",
            "%PROGRESS_CHUNK%"  : "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1f6feb, stop:1 #2ea043)",
            "%DISABLED_TEXT%"   : "#484f58",
            "%DISABLED_BORDER%" : "#21262d",
        }

    stylesheet = base_sheet
    for placeholder, color in colors.items():
        stylesheet = stylesheet.replace(placeholder, color)
    return stylesheet
