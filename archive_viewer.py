import zipfile
import tarfile
import rarfile
import py7zr
import pyzipper
from PySide6.QtCore import QThread, Signal


class ArchiveListThread(QThread):
    """Thread to list archive contents without blocking UI"""
    finished = Signal(bool, list, str)  # success, file_list, error_message
    requires_password = Signal()

    def __init__(self, archive_path, password=None):
        super().__init__()
        self.archive_path = archive_path
        self.password = password

    def run(self):
        try:
            file_list = self.list_archive_contents()
            self.finished.emit(True, file_list, "")
        except Exception as e:
            error_msg = str(e)
            if "password" in error_msg.lower() or "encrypted" in error_msg.lower():
                self.requires_password.emit()
                self.finished.emit(False, [], "Password required")
            else:
                self.finished.emit(False, [], f"Failed to read archive: {error_msg}")

    def list_archive_contents(self):
        """List all files in the archive"""
        file_list = []
        ext = self.archive_path.lower()

        try:
            if ext.endswith('.zip'):
                file_list = self._list_zip()
            elif ext.endswith(('.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz')):
                file_list = self._list_tar()
            elif ext.endswith('.rar'):
                file_list = self._list_rar()
            elif ext.endswith('.7z'):
                file_list = self._list_7z()
            else:
                raise Exception(f"Unsupported archive format: {ext}")
        except Exception as e:
            raise e

        return file_list

    def _list_zip(self):
        """List ZIP archive contents"""
        file_list = []

        # Try with password if provided
        if self.password:
            try:
                with pyzipper.AESZipFile(self.archive_path) as zf:
                    zf.setpassword(self.password.encode('utf-8'))
                    for info in zf.infolist():
                        file_list.append({
                            'name': info.filename,
                            'size': info.file_size,
                            'compressed_size': info.compress_size,
                            'is_dir': info.is_dir()
                        })
                return file_list
            except RuntimeError as e:
                if "password" in str(e).lower() or "bad password" in str(e).lower():
                    raise Exception("Incorrect password")
                raise e

        # Try without password
        try:
            with zipfile.ZipFile(self.archive_path, 'r') as zf:
                for info in zf.infolist():
                    file_list.append({
                        'name': info.filename,
                        'size': info.file_size,
                        'compressed_size': info.compress_size,
                        'is_dir': info.is_dir()
                    })
        except RuntimeError as e:
            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                raise Exception("Password required")
            raise e

        return file_list

    def _list_tar(self):
        """List TAR archive contents"""
        file_list = []
        with tarfile.open(self.archive_path, 'r:*') as tf:
            for member in tf.getmembers():
                file_list.append({
                    'name': member.name,
                    'size': member.size,
                    'compressed_size': member.size,
                    'is_dir': member.isdir()
                })
        return file_list

    def _list_rar(self):
        """List RAR archive contents"""
        file_list = []
        with rarfile.RarFile(self.archive_path) as rf:
            if rf.needs_password() and not self.password:
                raise Exception("Password required")

            rf.setpassword(self.password if self.password else None)

            for info in rf.infolist():
                file_list.append({
                    'name': info.filename,
                    'size': info.file_size,
                    'compressed_size': info.compress_size,
                    'is_dir': info.is_dir()
                })
        return file_list

    def _list_7z(self):
        """List 7Z archive contents"""
        file_list = []
        with py7zr.SevenZipFile(self.archive_path, mode='r', password=self.password) as zf:
            for name, info in zf.list():
                file_list.append({
                    'name': name,
                    'size': info.uncompressed,
                    'compressed_size': info.compressed,
                    'is_dir': info.is_directory
                })
        return file_list