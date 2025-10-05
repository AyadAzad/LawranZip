import os
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QLabel,
    QMessageBox, QProgressBar, QHeaderView, QDialog,
    QLineEdit, QStyle, QFileIconProvider, QTreeWidgetItemIterator
)
from PySide6.QtCore import Slot, Qt, QSize, QFileInfo
from PySide6.QtGui import QAction, QIcon

from password_dialog import PasswordDialog
from worker import WorkerThread
from archive_viewer import ArchiveListThread
from file_browser_dialog import FileBrowserDialog
from theme import get_dark_theme_palette, get_light_theme_palette, get_aurora_theme_palette, get_stylesheet


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LawranZip")
        self.setGeometry(100, 100, 900, 700)

        self.current_archive = None
        self.worker_thread = None
        self.list_thread = None
        self.icon_provider = QFileIconProvider()

        self.init_ui()
        self.create_menu()
        self.set_theme('aurora')

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        self.set_icons()

        button_layout = QHBoxLayout()
        icon_size = QSize(48, 48)

        self.zip_btn = QPushButton("Zip")
        self.zip_btn.setIcon(self.zip_icon)
        self.zip_btn.setIconSize(icon_size)
        self.seven_zip_btn = QPushButton("7-Zip")
        self.seven_zip_btn.setIcon(self.seven_zip_icon)
        self.seven_zip_btn.setIconSize(icon_size)
        self.extract_btn = QPushButton("Extract")
        self.extract_btn.setIcon(self.extract_icon)
        self.extract_btn.setIconSize(icon_size)

        self.zip_btn.clicked.connect(self.create_zip_archive)
        self.seven_zip_btn.clicked.connect(self.create_7zip_archive)
        self.extract_btn.clicked.connect(self.extract_archive)

        button_layout.addWidget(self.zip_btn)
        button_layout.addWidget(self.seven_zip_btn)
        button_layout.addWidget(self.extract_btn)
        button_layout.addStretch()

        location_layout = QHBoxLayout()
        self.up_btn = QPushButton()
        self.up_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        self.up_btn.clicked.connect(self.navigate_up)
        self.home_btn = QPushButton()
        self.home_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon))
        self.home_btn.clicked.connect(self.load_desktop_directory)
        location_label = QLabel("Location:")
        self.location_bar = QLineEdit()
        self.location_bar.returnPressed.connect(self.navigate_to_path)
        location_layout.addWidget(self.up_btn)
        location_layout.addWidget(self.home_btn)
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_bar)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Size", "Type", "Modified"])
        header = self.file_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.file_tree.itemChanged.connect(self.handle_item_changed)
        self.file_tree.itemActivated.connect(self.handle_item_activated)
        self.file_tree.itemSelectionChanged.connect(self.on_item_selection_changed)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        self.status_label = QLabel("Ready")

        main_layout.addLayout(button_layout)
        main_layout.addLayout(location_layout)
        main_layout.addWidget(self.file_tree)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.status_label)

        central_widget.setLayout(main_layout)

        self.load_desktop_directory()

    def get_desktop_path(self):
        if os.name == 'nt':
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                    desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
                return os.path.expandvars(desktop_path)
            except (FileNotFoundError, ImportError):
                pass
        return os.path.expanduser("~/Desktop")

    def load_desktop_directory(self):
        desktop_path = self.get_desktop_path()
        self.load_directory_contents(desktop_path)

    def navigate_to_path(self):
        path = self.location_bar.text()
        if os.path.isdir(path):
            self.load_directory_contents(path)
        elif os.path.isfile(path):
            if any(path.lower().endswith(f'.{ext}') for ext in self.get_supported_read_extensions()):
                self.current_archive = path
                self.load_archive_contents()
            else:
                QMessageBox.warning(self, "Unsupported File", "The selected file is not a supported archive format.")
                self.location_bar.setText(os.path.dirname(path))
        else:
            QMessageBox.warning(self, "Invalid Path", "The specified path does not exist.")
            self.load_desktop_directory()

    def navigate_up(self):
        current_path = self.location_bar.text()
        if self.current_archive:
            self.load_directory_contents(os.path.dirname(current_path))
        else:
            parent_path = os.path.dirname(current_path)
            if parent_path != current_path:
                self.load_directory_contents(parent_path)

    def set_icons(self):
        style = self.style()
        self.folder_icon = QIcon.fromTheme("folder", style.standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.file_icon = QIcon.fromTheme("document-new", style.standardIcon(QStyle.StandardPixmap.SP_FileIcon))

        icons_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icons')
        self.zip_icon = QIcon(os.path.join(icons_path, 'zip.svg'))
        self.seven_zip_icon = QIcon(os.path.join(icons_path, '7zip.svg'))
        self.extract_icon = QIcon(os.path.join(icons_path, 'extract.svg'))

        self.setWindowIcon(QIcon.fromTheme("application-x-archive", self.file_icon))

    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        zip_action = QAction(self.zip_icon, "Create ZIP Archive", self)
        zip_action.triggered.connect(self.create_zip_archive)
        file_menu.addAction(zip_action)
        seven_zip_action = QAction(self.seven_zip_icon, "Create 7-Zip Archive", self)
        seven_zip_action.triggered.connect(self.create_7zip_archive)
        file_menu.addAction(seven_zip_action)
        extract_action = QAction(self.extract_icon, "Extract Archive", self)
        extract_action.triggered.connect(self.extract_archive)
        file_menu.addAction(extract_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("View")
        light_mode_action = QAction("Light Mode", self)
        light_mode_action.triggered.connect(lambda: self.set_theme('light'))
        view_menu.addAction(light_mode_action)
        dark_mode_action = QAction("Dark Mode", self)
        dark_mode_action.triggered.connect(lambda: self.set_theme('dark'))
        view_menu.addAction(dark_mode_action)
        aurora_mode_action = QAction("Aurora Mode", self)
        aurora_mode_action.triggered.connect(lambda: self.set_theme('aurora'))
        view_menu.addAction(aurora_mode_action)

    def set_theme(self, theme):
        app = QApplication.instance()
        if theme == 'dark':
            app.setPalette(get_dark_theme_palette())
        elif theme == 'light':
            app.setPalette(get_light_theme_palette())
        elif theme == 'aurora':
            app.setPalette(get_aurora_theme_palette())
        
        app.setStyleSheet(get_stylesheet(theme))

    def get_supported_read_extensions(self):
        return ['7z', 'bz2', 'gz', 'rar', 'tar', 'tbz2', 'tgz', 'txz', 'xz', 'zip', 'zipx', 'jar']

    def create_zip_archive(self):
        files_to_add = self.get_checked_items()
        if not files_to_add:
            QMessageBox.warning(self, "No Files Selected", "Please select files or folders to add to the archive.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save ZIP Archive", "", "ZIP Archive (*.zip)")

        if not save_path:
            return

        if not save_path.lower().endswith('.zip'):
            save_path += '.zip'

        password = None
        use_password = QMessageBox.question(
            self, "Password Protection",
            "Do you want to protect this archive with a password?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes

        if use_password:
            password_dialog = PasswordDialog(self)
            if password_dialog.exec() == QDialog.DialogCode.Accepted:
                password = password_dialog.get_password()
                if not password:
                    QMessageBox.warning(self, "Warning", "No password entered. Archive will not be encrypted.")
            else:
                return

        self.start_compression_task('create', None, save_path, password, files_to_add=files_to_add)

    def create_7zip_archive(self):
        files_to_add = self.get_checked_items()
        if not files_to_add:
            QMessageBox.warning(self, "No Files Selected", "Please select files or folders to add to the archive.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save 7-Zip Archive", "", "7-Zip Archive (*.7z)")

        if not save_path:
            return

        if not save_path.lower().endswith('.7z'):
            save_path += '.7z'

        password = None
        use_password = QMessageBox.question(
            self, "Password Protection",
            "Do you want to protect this archive with a password?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes

        if use_password:
            password_dialog = PasswordDialog(self)
            if password_dialog.exec() == QDialog.DialogCode.Accepted:
                password = password_dialog.get_password()
                if not password:
                    QMessageBox.warning(self, "Warning", "No password entered. Archive will not be encrypted.")
            else:
                return

        self.start_compression_task('create', None, save_path, password, files_to_add=files_to_add)

    def extract_archive(self):
        archive_to_extract = self.current_archive
        files_to_extract = None

        if archive_to_extract:
            files_to_extract = self.get_checked_items()
            if not files_to_extract:
                files_to_extract = None  # Worker treats None as all files
        else:
            selected_items = self.file_tree.selectedItems()
            if len(selected_items) == 1:
                item = selected_items[0]
                path = item.data(0, Qt.ItemDataRole.UserRole)
                if path and os.path.isfile(path) and any(path.lower().endswith(f'.{ext}') for ext in self.get_supported_read_extensions()):
                    archive_to_extract = path

            if not archive_to_extract:
                extensions = self.get_supported_read_extensions()
                name_filters = f"All Supported Archives ({' '.join(['*.' + ext for ext in extensions])});;All Files (*)"
                file_path, _ = QFileDialog.getOpenFileName(self, "Select Archive to Extract", "", name_filters)
                if not file_path:
                    return
                archive_to_extract = file_path

        if not archive_to_extract:
            return

        extract_dialog = FileBrowserDialog(self, directory_only=True)
        if extract_dialog.exec() == QDialog.DialogCode.Accepted:
            extract_path_list = extract_dialog.get_selected_paths()
            if not extract_path_list:
                return
            extract_path = extract_path_list[0]
            self.start_compression_task('extract', archive_to_extract, extract_path, files_to_extract=files_to_extract)

    def format_size(self, size):
        if size is None or size == 0:
            return ""
        power = 1024
        n = 0
        power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power and n < len(power_labels) - 1:
            size /= power
            n += 1
        return f"{size:.1f} {power_labels[n]}B"

    def get_file_type(self, filename):
        _, ext = os.path.splitext(filename)
        return ext[1:].upper() if ext else "File"

    def load_directory_contents(self, directory_path):
        self.file_tree.clear()
        self.location_bar.setText(directory_path)
        self.current_archive = None
        self.extract_btn.setEnabled(False)
        self.status_label.setText(f"Viewing: {directory_path}")

        try:
            dirs, files = [], []
            for entry in os.scandir(directory_path):
                (dirs if entry.is_dir() else files).append(entry)

            dirs.sort(key=lambda e: e.name.lower())
            files.sort(key=lambda e: e.name.lower())

            for entry in dirs + files:
                file_info = QFileInfo(entry.path)
                icon = self.icon_provider.icon(file_info)
                name = entry.name
                try:
                    stat = entry.stat()
                    size = stat.st_size
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                except OSError:
                    size, modified = 0, ''

                size_str = self.format_size(size) if not file_info.isDir() else ''
                type_str = self.icon_provider.type(file_info) or (self.get_file_type(name) if not file_info.isDir() else "Folder")

                item = QTreeWidgetItem([name, size_str, type_str, modified])
                item.setIcon(0, icon)
                item.setData(0, Qt.ItemDataRole.UserRole, entry.path)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(0, Qt.CheckState.Unchecked)
                self.file_tree.addTopLevelItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read directory '{directory_path}':\n{e}")

    def load_archive_contents(self, password=None):
        if not self.current_archive:
            return

        self.file_tree.clear()
        self.status_label.setText("Reading archive...")
        self.set_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self.list_thread = ArchiveListThread(self.current_archive, password)
        self.list_thread.finished.connect(self.on_list_finished)
        self.list_thread.requires_password.connect(self.on_list_password_required)
        self.list_thread.start()

    @Slot(bool, list, str)
    def on_list_finished(self, success, file_list, error_message):
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)

        if success:
            self.populate_tree(file_list)
            self.status_label.setText(f"Archive loaded: {len(file_list)} items")
            self.extract_btn.setEnabled(True)
        else:
            if "Password required" not in error_message:
                QMessageBox.critical(self, "Error", error_message)
                self.status_label.setText("Failed to load archive")
                self.current_archive = None
                self.location_bar.clear()

    @Slot()
    def on_list_password_required(self):
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            password = password_dialog.get_password()
            if password:
                self.load_archive_contents(password)
            else:
                QMessageBox.warning(self, "No Password", "Password is required to open this archive.")
                self.status_label.setText("Operation cancelled")
                self.current_archive = None
                self.location_bar.clear()
        else:
            self.status_label.setText("Operation cancelled")
            self.current_archive = None
            self.location_bar.clear()

    def populate_tree(self, file_list):
        self.file_tree.clear()
        items = {'': self.file_tree.invisibleRootItem()}

        for file_info in sorted(file_list, key=lambda x: x.get('name', '')):
            path = file_info.get('name', '')
            if not path:
                continue

            size = file_info.get('size', 0)
            is_dir = file_info.get('is_dir', False)
            path = path.replace('\\', '/').rstrip('/')
            path_parts = path.split('/')

            parent_path = ''
            for i, part in enumerate(path_parts):
                current_path = '/'.join(path_parts[:i + 1])
                if current_path not in items:
                    parent_item = items.get(parent_path, self.file_tree.invisibleRootItem())
                    is_current_dir = (i < len(path_parts) - 1) or is_dir
                    item_path_data = current_path + ('/' if is_current_dir else '')
                    size_str = self.format_size(size) if not is_current_dir and size else ""
                    type_str = "Folder" if is_current_dir else self.get_file_type(part)

                    item = QTreeWidgetItem(parent_item, [part, size_str, type_str, ""])
                    item.setIcon(0, self.folder_icon if is_current_dir else self.file_icon)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.CheckState.Unchecked)
                    item.setData(0, Qt.ItemDataRole.UserRole, item_path_data)
                    items[current_path] = item
                parent_path = current_path

    def get_checked_items(self):
        checked_paths = []
        iterator = QTreeWidgetItemIterator(self.file_tree, QTreeWidgetItemIterator.IteratorFlag.Checked)
        while iterator.value():
            item = iterator.value()
            parent = item.parent()
            if not parent or parent == self.file_tree.invisibleRootItem() or parent.checkState(0) != Qt.CheckState.Checked:
                path = item.data(0, Qt.ItemDataRole.UserRole)
                if path:
                    checked_paths.append(path)
            iterator += 1
        return checked_paths

    def on_item_selection_changed(self):
        if self.current_archive is None:
            selected_items = self.file_tree.selectedItems()
            can_extract = False
            if len(selected_items) == 1:
                item = selected_items[0]
                path = item.data(0, Qt.ItemDataRole.UserRole)
                if path and os.path.isfile(path) and any(path.lower().endswith(f'.{ext}') for ext in self.get_supported_read_extensions()):
                    can_extract = True
            self.extract_btn.setEnabled(can_extract)

    def handle_item_changed(self, item, column):
        if column == 0:
            self.file_tree.blockSignals(True)
            check_state = item.checkState(0)

            def update_children(parent_item):
                for i in range(parent_item.childCount()):
                    child = parent_item.child(i)
                    child.setCheckState(0, check_state)
                    update_children(child)

            update_children(item)

            def update_parents(child_item):
                parent = child_item.parent()
                if parent and parent != self.file_tree.invisibleRootItem():
                    child_states = {parent.child(i).checkState(0) for i in range(parent.childCount())}
                    if len(child_states) == 1:
                        parent.setCheckState(0, child_states.pop())
                    else:
                        parent.setCheckState(0, Qt.CheckState.PartiallyChecked)
                    update_parents(parent)

            update_parents(item)
            self.file_tree.blockSignals(False)

    def handle_item_activated(self, item, column):
        if self.current_archive is None:
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if path:
                if os.path.isdir(path):
                    self.load_directory_contents(path)
                elif os.path.isfile(path) and any(path.lower().endswith(f'.{ext}') for ext in self.get_supported_read_extensions()):
                    self.current_archive = path
                    self.location_bar.setText(path)
                    self.load_archive_contents()

    def start_compression_task(self, operation, source, destination, password=None, files_to_add=None, files_to_extract=None):
        self.set_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.status_label.setText("Processing...")

        self.worker_thread = WorkerThread(operation, source, destination, password, files_to_add, files_to_extract)
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.on_operation_finished)
        self.worker_thread.requires_password.connect(self.on_password_required)
        self.worker_thread.start()

    @Slot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    @Slot(bool, str)
    def on_operation_finished(self, success, message):
        if not success and self.worker_thread and "password" in message.lower():
            return

        self.set_buttons_enabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.status_label.setText("Operation completed successfully!")
            QMessageBox.information(self, "Success", "Operation completed successfully!")

            if self.worker_thread.operation == 'create':
                self.current_archive = self.worker_thread.destination
                self.location_bar.setText(self.current_archive)
                self.load_archive_contents()
            elif self.worker_thread.operation == 'extract':
                self.load_directory_contents(self.worker_thread.destination)

        else:
            if "password" not in message.lower():
                self.status_label.setText(f"Error: {message}")
                QMessageBox.critical(self, "Error", f"Operation failed: {message}")

    @Slot()
    def on_password_required(self):
        self.set_buttons_enabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")

        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.DialogCode.Accepted:
            password = password_dialog.get_password()
            if password:
                self.start_compression_task(
                    self.worker_thread.operation,
                    self.worker_thread.source,
                    self.worker_thread.destination,
                    password,
                    self.worker_thread.files_to_add,
                    self.worker_thread.files_to_extract
                )
            else:
                QMessageBox.warning(self, "Error", "A password was not provided.")
                self.status_label.setText("Operation cancelled")
        else:
            self.status_label.setText("Operation cancelled")

    def set_buttons_enabled(self, enabled):
        self.zip_btn.setEnabled(enabled)
        self.seven_zip_btn.setEnabled(enabled)
        self.extract_btn.setEnabled(enabled)
