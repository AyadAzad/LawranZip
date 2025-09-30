from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeView, QDialogButtonBox,
    QFileSystemModel, QHeaderView, QPushButton, QComboBox, QLineEdit, QLabel
)
from PySide6.QtCore import QDir, Qt, QStandardPaths
from PySide6.QtGui import QIcon
import os


class FileBrowserDialog(QDialog):
    def __init__(self, parent=None, directory_only=False, file_only=False, name_filters=None):
        super().__init__(parent)
        self.setMinimumSize(900, 600)

        self.directory_only = directory_only
        self.file_only = file_only

        # Main layout
        main_layout = QVBoxLayout(self)

        # Navigation bar layout
        nav_layout = QHBoxLayout()

        # Back and Forward buttons
        self.back_button = QPushButton("◀")
        self.back_button.setMaximumWidth(40)
        self.back_button.setToolTip("Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)

        self.forward_button = QPushButton("▶")
        self.forward_button.setMaximumWidth(40)
        self.forward_button.setToolTip("Forward")
        self.forward_button.clicked.connect(self.go_forward)
        self.forward_button.setEnabled(False)

        self.up_button = QPushButton("⬆")
        self.up_button.setMaximumWidth(40)
        self.up_button.setToolTip("Up One Level")
        self.up_button.clicked.connect(self.go_up)

        # Path bar (editable)
        self.path_edit = QLineEdit()
        self.path_edit.returnPressed.connect(self.navigate_to_path)

        # Quick access combo box
        self.quick_access_combo = QComboBox()
        self.quick_access_combo.setMinimumWidth(150)
        self.populate_quick_access()
        self.quick_access_combo.currentIndexChanged.connect(self.on_quick_access_changed)

        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.up_button)
        nav_layout.addWidget(QLabel("Path:"))
        nav_layout.addWidget(self.path_edit)
        nav_layout.addWidget(self.quick_access_combo)

        main_layout.addLayout(nav_layout)

        # Initialize the file system model
        self.model = QFileSystemModel()
        self.model.setRootPath("")  # Show entire file system

        # Apply name filters if provided
        if name_filters:
            self.model.setNameFilters(name_filters)
            self.model.setNameFilterDisables(False)

        # Set up the tree view
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)

        # Start at root to show all drives
        if os.name == 'nt':  # Windows
            root_index = self.model.index("")
        else:  # Linux/Mac
            root_index = self.model.index("/")

        self.tree_view.setRootIndex(root_index)
        self.current_path = self.model.filePath(root_index)

        # Configure columns
        self.tree_view.setColumnWidth(0, 350)
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree_view.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tree_view.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        # Show all columns
        self.tree_view.setColumnHidden(1, False)  # Size
        self.tree_view.setColumnHidden(2, False)  # Type
        self.tree_view.setColumnHidden(3, False)  # Date Modified

        # Enable proper selection
        self.tree_view.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.tree_view.setSelectionMode(
            QTreeView.SelectionMode.SingleSelection if (directory_only or file_only)
            else QTreeView.SelectionMode.ExtendedSelection
        )

        # Enable animations and sorting
        self.tree_view.setAnimated(True)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setExpandsOnDoubleClick(True)

        # Set window title and filter based on mode
        if directory_only:
            self.setWindowTitle("Select a Directory")
            self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Drives)
        elif file_only:
            self.setWindowTitle("Open Archive")
            self.model.setFilter(
                QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot | QDir.Filter.Drives)
        else:
            self.setWindowTitle("Select Files and Folders to Archive")
            self.model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot | QDir.Filter.Drives)

        main_layout.addWidget(self.tree_view)

        # Current path display
        path_info_layout = QHBoxLayout()
        self.current_path_label = QLabel()
        self.update_path_label()
        path_info_layout.addWidget(self.current_path_label)
        path_info_layout.addStretch()
        main_layout.addLayout(path_info_layout)

        # Set up button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Initially disable OK button
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)

        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

        # Navigation history
        self.history = []
        self.history_index = -1

        # Connect signals
        self.tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.tree_view.doubleClicked.connect(self.on_double_clicked)
        self.tree_view.expanded.connect(self.on_item_expanded)

        # Update path bar
        self.update_path_edit()

    def populate_quick_access(self):
        """Populate quick access dropdown with common locations"""
        self.quick_access_combo.addItem("Quick Access", "")

        if os.name == 'nt':  # Windows
            # Add drives
            for drive in QDir.drives():
                drive_path = drive.absolutePath()
                self.quick_access_combo.addItem(f"Drive {drive_path}", drive_path)
        else:  # Linux/Mac
            self.quick_access_combo.addItem("Root /", "/")

        # Add standard locations
        desktop = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
        documents = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        downloads = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
        home = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation)

        if desktop:
            self.quick_access_combo.addItem("Desktop", desktop)
        if documents:
            self.quick_access_combo.addItem("Documents", documents)
        if downloads:
            self.quick_access_combo.addItem("Downloads", downloads)
        if home:
            self.quick_access_combo.addItem("Home", home)

    def on_quick_access_changed(self, index):
        """Handle quick access selection"""
        if index > 0:  # Skip "Quick Access" label
            path = self.quick_access_combo.itemData(index)
            if path and os.path.exists(path):
                self.navigate_to(path)
            # Reset to "Quick Access" label
            self.quick_access_combo.setCurrentIndex(0)

    def navigate_to(self, path):
        """Navigate to a specific path"""
        if not os.path.exists(path):
            return

        index = self.model.index(path)
        if index.isValid():
            self.tree_view.setRootIndex(index)
            self.current_path = path

            # Add to history
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]

            if not self.history or self.history[-1] != path:
                self.history.append(path)
                self.history_index = len(self.history) - 1

            self.update_navigation_buttons()
            self.update_path_edit()
            self.update_path_label()

    def navigate_to_path(self):
        """Navigate to path entered in path bar"""
        path = self.path_edit.text()
        if os.path.exists(path):
            self.navigate_to(path)

    def go_back(self):
        """Go back in navigation history"""
        if self.history_index > 0:
            self.history_index -= 1
            path = self.history[self.history_index]
            index = self.model.index(path)
            if index.isValid():
                self.tree_view.setRootIndex(index)
                self.current_path = path
                self.update_navigation_buttons()
                self.update_path_edit()
                self.update_path_label()

    def go_forward(self):
        """Go forward in navigation history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            path = self.history[self.history_index]
            index = self.model.index(path)
            if index.isValid():
                self.tree_view.setRootIndex(index)
                self.current_path = path
                self.update_navigation_buttons()
                self.update_path_edit()
                self.update_path_label()

    def go_up(self):
        """Go up one directory level"""
        current_index = self.tree_view.rootIndex()
        parent_index = current_index.parent()

        if parent_index.isValid():
            parent_path = self.model.filePath(parent_index)
            self.navigate_to(parent_path)
        elif os.name == 'nt':  # Windows - go to root showing all drives
            self.navigate_to("")
        else:  # Linux/Mac - go to root
            parent_path = os.path.dirname(self.current_path)
            if parent_path and parent_path != self.current_path:
                self.navigate_to(parent_path)

    def update_navigation_buttons(self):
        """Update back/forward button states"""
        self.back_button.setEnabled(self.history_index > 0)
        self.forward_button.setEnabled(self.history_index < len(self.history) - 1)

    def update_path_edit(self):
        """Update the path edit field"""
        self.path_edit.setText(self.current_path if self.current_path else "Computer")

    def update_path_label(self):
        """Update the current path label"""
        display_path = self.current_path if self.current_path else "Computer"
        self.current_path_label.setText(f"Current location: {display_path}")

    def on_item_expanded(self, index):
        """Handle item expansion - navigate into folder"""
        # This allows single-click expand while preserving double-click navigation

    def on_selection_changed(self, selected, deselected):
        """Handle selection changes and enable/disable OK button"""
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()

        if not selected_indexes:
            self.ok_button.setEnabled(False)
            return

        # Get the first selected index (column 0)
        index = selected_indexes[0]

        if self.directory_only:
            is_dir = self.model.isDir(index)
            self.ok_button.setEnabled(is_dir)
        elif self.file_only:
            is_file = not self.model.isDir(index)
            self.ok_button.setEnabled(is_file)
        else:
            self.ok_button.setEnabled(True)

    def on_double_clicked(self, index):
        """Handle double-click events"""
        is_dir = self.model.isDir(index)

        if is_dir:
            # Navigate into the directory
            dir_path = self.model.filePath(index)
            self.navigate_to(dir_path)
        else:
            # If it's a file in file_only mode, accept
            if self.file_only:
                self.accept()

    def get_selected_paths(self):
        """Return list of selected file/folder paths"""
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        name_indexes = [index for index in selected_indexes if index.column() == 0]

        # Return absolute paths
        paths = []
        for index in name_indexes:
            file_path = self.model.filePath(index)
            # If we're in root view, construct full path
            if not file_path:
                file_path = self.model.fileName(index)
            paths.append(file_path)

        return paths

    def get_selected_path(self):
        """Return single selected path (for directory_only or file_only mode)"""
        paths = self.get_selected_paths()
        return paths[0] if paths else None