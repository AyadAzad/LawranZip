import os
import zipfile
import tarfile
import pyzipper
import py7zr
from PySide6.QtCore import QThread, Signal


class WorkerThread(QThread):
    progress = Signal(int)
    finished = Signal(bool, str)
    requires_password = Signal()
    file_changed = Signal(str)

    def __init__(self, operation, source, destination, password=None, files_to_add=None, files_to_extract=None):
        super().__init__()
        self.operation = operation
        self.source = source
        self.destination = destination
        self.password = password
        self.files_to_add = files_to_add or []
        self.files_to_extract = files_to_extract or []

    def run(self):
        try:
            if self.operation == 'extract':
                self.extract_archive()
            elif self.operation == 'create':
                self.create_archive()
            self.finished.emit(True, "Operation completed successfully")
        except Exception as e:
            error_msg = str(e)
            if "password" in error_msg.lower() or "bad password" in error_msg.lower() or "encrypted" in error_msg.lower():
                self.requires_password.emit()
                self.finished.emit(False, "Password required or incorrect")
            else:
                self.finished.emit(False, f"Error: {error_msg}")

    def extract_archive(self):
        """Extract archive with proper error handling"""
        ext = self.source.lower()

        if ext.endswith('.zip'):
            self._extract_zip()
        elif ext.endswith(('.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz')):
            self._extract_tar()
        elif ext.endswith('.7z'):
            self._extract_7zip()
        else:
            raise Exception(f"Unsupported archive format for extraction: {ext}")

    def _extract_zip(self):
        """Extract ZIP archive"""
        if self.password:
            try:
                with pyzipper.AESZipFile(self.source) as zf:
                    zf.setpassword(self.password.encode('utf-8'))
                    members = self.files_to_extract if self.files_to_extract else zf.namelist()
                    total = len(members)
                    for i, member in enumerate(members):
                        self.file_changed.emit(f"Extracting: {member}")
                        zf.extract(member, self.destination)
                        self.progress.emit(int(((i + 1) / total) * 100))
                return
            except RuntimeError as e:
                if "password" in str(e).lower():
                    raise Exception("Incorrect password")
                raise e
            except (pyzipper.zipfile.BadZipFile, zipfile.BadZipFile):
                raise Exception("Incorrect password or corrupt file.")

        try:
            with zipfile.ZipFile(self.source, 'r') as zf:
                members = self.files_to_extract if self.files_to_extract else zf.namelist()
                total = len(members)
                for i, member in enumerate(members):
                    self.file_changed.emit(f"Extracting: {member}")
                    zf.extract(member, self.destination)
                    self.progress.emit(int(((i + 1) / total) * 100))
        except RuntimeError as e:
            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                raise Exception("Password required")
            raise e

    def _extract_tar(self):
        """Extract TAR archive"""
        with tarfile.open(self.source, 'r:*') as tf:
            members = self.files_to_extract if self.files_to_extract else tf.getnames()
            total = len(members)
            for i, member in enumerate(members):
                self.file_changed.emit(f"Extracting: {member}")
                tf.extract(member, self.destination)
                self.progress.emit(int(((i + 1) / total) * 100))

    def _extract_7zip(self):
        """Extract 7-Zip archive"""
        try:
            with py7zr.SevenZipFile(self.source, 'r', password=self.password) as zf:
                targets = self.files_to_extract if self.files_to_extract else zf.getnames()
                total = len(targets)
                for i, member in enumerate(targets):
                    self.file_changed.emit(f"Extracting: {member}")
                    zf.extract(path=self.destination, targets=[member])
                    self.progress.emit(int(((i + 1) / total) * 100))
        except py7zr.exceptions.PasswordRequired:
            raise Exception("Password required")
        except py7zr.exceptions.Bad7zFile:
            if not self.password:
                raise Exception("Password required")
            else:
                raise Exception("Incorrect password or corrupt file")

    def create_archive(self):
        """Create archive"""
        ext = self.destination.lower()

        if ext.endswith('.zip'):
            self._create_zip()
        elif ext.endswith('.7z'):
            self._create_7zip()
        elif ext.endswith(('.tar', '.tar.gz', '.tgz', '.tar.xz')):
            self._create_tar()
        else:
            raise Exception(f"Unsupported archive format for creation: {ext}")

    def _create_zip(self):
        """Create ZIP archive"""
        compression = zipfile.ZIP_LZMA
        if self.password:
            with pyzipper.AESZipFile(
                    self.destination,
                    'w',
                    compression=compression,
                    encryption=pyzipper.WZ_AES
            ) as zf:
                zf.setpassword(self.password.encode('utf-8'))
                self._add_files_to_archive(zf)
        else:
            with zipfile.ZipFile(self.destination, 'w', compression=compression) as zf:
                self._add_files_to_archive(zf)

    def _create_7zip(self):
        """Create 7-Zip archive"""
        filters = [{'id': py7zr.FILTER_LZMA2, 'preset': 9}]
        with py7zr.SevenZipFile(self.destination, 'w', password=self.password, filters=filters) as zf:
            self._add_files_to_archive(zf)

    def _create_tar(self):
        """Create TAR archive"""
        dest_lower = self.destination.lower()
        if dest_lower.endswith('.tar.xz'):
            mode = 'w:xz'
        elif dest_lower.endswith(('.tar.gz', '.tgz')):
            mode = 'w:gz'
        else:
            mode = 'w'

        with tarfile.open(self.destination, mode) as tf:
            total = len(self.files_to_add)
            for i, file_path in enumerate(self.files_to_add):
                arcname = os.path.basename(file_path)
                tf.add(file_path, arcname=arcname)
                self.progress.emit(int(((i + 1) / total) * 100))

    def _add_files_to_archive(self, archive_file):
        total = len(self.files_to_add)
        for i, file_path in enumerate(self.files_to_add):
            arcname = os.path.basename(file_path)
            if os.path.isfile(file_path):
                archive_file.write(file_path, arcname)
            elif os.path.isdir(file_path):
                if hasattr(archive_file, 'writeall'):
                    archive_file.writeall(file_path, arcname)
                else:
                    base_dir = os.path.dirname(file_path) or '.'
                    for dirpath, dirnames, filenames in os.walk(file_path):
                        for filename in filenames:
                            full_path = os.path.join(dirpath, filename)
                            rel_path = os.path.join(arcname, os.path.relpath(full_path, file_path))
                            archive_file.write(full_path, rel_path)

            self.progress.emit(int(((i + 1) / total) * 100))
