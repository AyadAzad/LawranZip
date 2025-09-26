import sys
import os

import pyzipper
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QListWidget, QLabel, QLineEdit,
    QDialog, QMessageBox, QProgressBar
)
from PySide6.QtCore import  QThread, Signal, Slot
from PySide6.QtGui import  QAction


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Password")
        self.setModal(True)
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        label = QLabel("This archive is password protected. Please enter the password:")
        layout.addWidget(label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_password(self):
        return self.password_input.text()


class WorkerThread(QThread):
    progress = Signal(int)
    finished = Signal(bool, str)
    requires_password = Signal()

    def __init__(self, operation, source, destination, password=None, files_to_add=None):
        super().__init__()
        self.operation = operation  # 'extract' or 'create'
        self.source = source
        self.destination = destination
        self.password = password
        self.files_to_add = files_to_add
        self._password_provided = False
        self._provided_password = None

    def run(self):
        try:
            if self.operation == 'extract':
                self.extract_archive()
            elif self.operation == 'create':
                self.create_archive()
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))

    def extract_archive(self):
        try:
            with pyzipper.AESZipFile(self.source, 'r') as zip_file:
                # Check if any file in the archive is encrypted
                needs_password = any(info.flag_bits & 0x1 for info in zip_file.filelist)

                if needs_password and not self.password:
                    self.requires_password.emit()
                    # Wait for password to be set (this would need to be handled differently in a real app)
                    # For simplicity, we'll just fail here and let the UI handle it
                    raise Exception("Password required")

                if needs_password and self.password:
                    zip_file.setpassword(self.password.encode('utf-8'))

                total_files = len(zip_file.namelist())
                for i, file_name in enumerate(zip_file.namelist()):
                    zip_file.extract(file_name, self.destination)
                    progress_percent = int((i + 1) / total_files * 100)
                    self.progress.emit(progress_percent)

        except RuntimeError as e:
            if "password required" in str(e).lower() or "bad password" in str(e).lower():
                self.requires_password.emit()
                raise Exception("Password required or incorrect")
            else:
                raise e

    def create_archive(self):
        try:
            compression = pyzipper.ZIP_DEFLATED

            with pyzipper.AESZipFile(self.destination, 'w', compression=compression) as zip_file:
                if self.password:
                    zip_file.setpassword(self.password.encode('utf-8'))
                    # Use AES encryption if password is provided
                    zip_file.setencryption(pyzipper.WZ_AES, nbits=256)

                total_files = len(self.files_to_add)
                for i, file_path in enumerate(self.files_to_add):
                    arcname = os.path.basename(file_path) if os.path.isfile(file_path) else os.path.basename(
                        file_path.rstrip(os.sep))

                    if os.path.isdir(file_path):
                        for root, dirs, files in os.walk(file_path):
                            for file in files:
                                full_path = os.path.join(root, file)
                                relative_path = os.path.relpath(full_path, os.path.dirname(file_path))
                                zip_file.write(full_path, relative_path)
                    else:
                        zip_file.write(file_path, arcname)

                    progress_percent = int((i + 1) / total_files * 100)
                    self.progress.emit(progress_percent)

        except Exception as e:
            raise e


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyZip - Simple Archive Manager")
        self.setGeometry(100, 100, 800, 600)

        self.current_archive = None
        self.worker_thread = None

        self.init_ui()
        self.create_menu()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Button layout
        button_layout = QHBoxLayout()

        self.add_files_btn = QPushButton("Add Files")
        self.add_folder_btn = QPushButton("Add Folder")
        self.extract_btn = QPushButton("Extract")
        self.browse_archive_btn = QPushButton("Open Archive")

        self.add_files_btn.clicked.connect(self.add_files)
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.extract_btn.clicked.connect(self.extract_archive)
        self.browse_archive_btn.clicked.connect(self.open_archive)

        self.extract_btn.setEnabled(False)

        button_layout.addWidget(self.add_files_btn)
        button_layout.addWidget(self.add_folder_btn)
        button_layout.addWidget(self.browse_archive_btn)
        button_layout.addWidget(self.extract_btn)
        button_layout.addStretch()

        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # Status label
        self.status_label = QLabel("Ready")

        # Add widgets to main layout
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.file_list)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.status_label)

        central_widget.setLayout(main_layout)

    def create_menu(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open Archive", self)
        open_action.triggered.connect(self.open_archive)
        file_menu.addAction(open_action)

        add_files_action = QAction("Add Files", self)
        add_files_action.triggered.connect(self.add_files)
        file_menu.addAction(add_files_action)

        add_folder_action = QAction("Add Folder", self)
        add_folder_action.triggered.connect(self.add_folder)
        file_menu.addAction(add_folder_action)

        extract_action = QAction("Extract", self)
        extract_action.triggered.connect(self.extract_archive)
        file_menu.addAction(extract_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_archive(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Archive", "", "Archive Files (*.zip *.ZIP);;All Files (*)"
        )

        if file_path:
            self.current_archive = file_path
            self.load_archive_contents()
            self.extract_btn.setEnabled(True)
            self.status_label.setText(f"Loaded: {os.path.basename(file_path)}")

    def load_archive_contents(self):
        if not self.current_archive:
            return

        self.file_list.clear()

        try:
            with pyzipper.AESZipFile(self.current_archive, 'r') as zip_file:
                for file_info in zip_file.filelist:
                    item_text = file_info.filename
                    if file_info.flag_bits & 0x1:  # Encrypted file
                        item_text += " 🔒"
                    self.file_list.addItem(item_text)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read archive: {str(e)}")

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Add", "", "All Files (*)"
        )

        if files:
            self.create_archive_dialog(files)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder to Add"
        )

        if folder:
            self.create_archive_dialog([folder])

    def create_archive_dialog(self, files_to_add):
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Archive", "", "Zip Files (*.zip)"
        )

        if not save_path:
            return

        if not save_path.endswith('.zip'):
            save_path += '.zip'

        # Ask for password
        password = None
        use_password = QMessageBox.question(
            self, "Password Protection",
            "Do you want to protect this archive with a password?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes

        if use_password:
            password_dialog = PasswordDialog(self)
            if password_dialog.exec() == QDialog.Accepted:
                password = password_dialog.get_password()
                if not password:
                    QMessageBox.warning(self, "Warning", "No password entered. Archive will not be encrypted.")
            else:
                return  # User cancelled

        self.start_compression_task('create', None, save_path, password, files_to_add)

    def extract_archive(self):
        if not self.current_archive:
            QMessageBox.warning(self, "Warning", "No archive loaded!")
            return

        extract_path = QFileDialog.getExistingDirectory(
            self, "Select Extraction Directory"
        )

        if not extract_path:
            return

        self.start_compression_task('extract', self.current_archive, extract_path)

    def start_compression_task(self, operation, source, destination, password=None, files_to_add=None):
        # Disable buttons during operation
        self.set_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Processing...")

        # Create and start worker thread
        self.worker_thread = WorkerThread(operation, source, destination, password, files_to_add)
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.on_operation_finished)
        self.worker_thread.requires_password.connect(self.on_password_required)
        self.worker_thread.start()

    @Slot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    @Slot(bool, str)
    def on_operation_finished(self, success, error_message):
        self.set_buttons_enabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.status_label.setText("Operation completed successfully!")
            QMessageBox.information(self, "Success", "Operation completed successfully!")

            # If we created an archive, load it
            if self.worker_thread.operation == 'create':
                self.current_archive = self.worker_thread.destination
                self.load_archive_contents()
                self.extract_btn.setEnabled(True)
        else:
            self.status_label.setText(f"Error: {error_message}")
            QMessageBox.critical(self, "Error", f"Operation failed: {error_message}")

    @Slot()
    def on_password_required(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()

        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == QDialog.Accepted:
            password = password_dialog.get_password()
            if password:
                # Restart the operation with password
                self.start_compression_task(
                    self.worker_thread.operation,
                    self.worker_thread.source,
                    self.worker_thread.destination,
                    password,
                    self.worker_thread.files_to_add
                )
            else:
                QMessageBox.warning(self, "Error", "Password is required for this archive")
                self.set_buttons_enabled(True)
                self.progress_bar.setVisible(False)
        else:
            self.set_buttons_enabled(True)
            self.progress_bar.setVisible(False)
            self.status_label.setText("Operation cancelled")

    def set_buttons_enabled(self, enabled):
        self.add_files_btn.setEnabled(enabled)
        self.add_folder_btn.setEnabled(enabled)
        self.extract_btn.setEnabled(enabled and bool(self.current_archive))
        self.browse_archive_btn.setEnabled(enabled)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()