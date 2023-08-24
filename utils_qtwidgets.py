# coding: utf8
import shutil
from pathlib import Path
from typing import Callable

from typedict_def import PrfInfo
from config import QtWidgets, QtCore, QtGui, QtSql


ItemStatusRole = 0x0101
ItemIdsRole = 0x0102
ItemUrlRole = 0x0103


class PushButtonWithId(QtWidgets.QPushButton):

    clicked_with_id = QtCore.Signal(str)

    def __init__(self, ids: str, parent: QtWidgets.QWidget = None, title: str = ""):
        super().__init__(title, parent)
        self.ids = ids
        self.clicked.connect(self.on_self_clicked)

    def on_self_clicked(self):
        self.clicked_with_id.emit(self.ids)


class HorizontalLine(QtWidgets.QFrame):

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)


class VerticalLine(QtWidgets.QFrame):

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)


def change_color(widget: QtWidgets.QWidget,
                 role: QtGui.QPalette.ColorRole,
                 color: str | QtCore.Qt.GlobalColor):
    pal = widget.palette()
    pal.setColor(role, color)
    widget.setPalette(pal)


def change_font(widget: QtWidgets.QWidget, family: str, size: int, bold: bool = False):
    font = widget.font()
    font.setFamily(family)
    font.setPointSize(size)
    font.setBold(bold)
    widget.setFont(font)


def accept_warning(widget: QtWidgets.QWidget, condition: bool,
                   caption: str = "Warning", text: str = "Are you sure to continue?") -> bool:
    if condition:
        b = QtWidgets.QMessageBox.question(widget, caption, text)
        if b == QtWidgets.QMessageBox.StandardButton.No:
            return True
    return False


def get_sql_database(conn_name: str, file_path: str) -> QtSql.QSqlDatabase:
    if QtSql.QSqlDatabase.contains(conn_name):
        db = QtSql.QSqlDatabase.database(conn_name, open=False)
    else:
        db = QtSql.QSqlDatabase.addDatabase("QSQLITE", conn_name)
        db.setDatabaseName(file_path)

    return db


class DeleteThread(QtCore.QThread):

    deleted = QtCore.Signal(int, int)

    def __init__(self, delete_func: Callable[[PrfInfo, list[str]], tuple[int, int]],
                 profile_info: PrfInfo, marks: list[str], parent: QtCore.QObject = None):
        super().__init__(parent)
        self.delete_func = delete_func
        self.profile_info = profile_info
        self.marks = marks  # 唯一标识符的列表，可能是 url 或 插件 id
        self.finished.connect(self.deleteLater)

    def run(self):
        success, total = self.delete_func(self.profile_info, self.marks)
        self.deleted.emit(success, total)


class DeleteThreadManager(QtCore.QObject):

    def __init__(self, total: int, progress_bar: QtWidgets.QProgressBar, parent: QtWidgets.QDialog):
        super().__init__(parent)
        self.deletion_progress = 0
        self.success_deletion = 0
        self.fail_deletion = 0
        self.total_for_deletion = total
        self.deletion_info = "成功：{success} 个；失败：{fail} 个；总共 {total} 个。"
        self.progress_bar = progress_bar
        self.parent = parent

        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)

        self.progress_bar.valueChanged.connect(self.on_pgb_del_value_changed)

    def start(self, thread: DeleteThread):
        thread.deleted.connect(self.on_del_thd_deleted)
        thread.start()

    def on_del_thd_deleted(self, success: int, total: int):
        self.success_deletion += success
        self.deletion_progress += total
        self.fail_deletion += total - success
        self.progress_bar.setValue(self.deletion_progress)

    def on_pgb_del_value_changed(self, value: int):
        if value == self.total_for_deletion:
            QtWidgets.QMessageBox.information(
                self.parent, "删除结果", self.deletion_info.format(
                    success=self.success_deletion,
                    fail=self.fail_deletion,
                    total=self.total_for_deletion
                )
            )
            self.parent.accept()


class CopyThread(QtCore.QThread):

    copied = QtCore.Signal()

    def __init__(self, src_path: Path | None, dst_path: Path | None, parent: QtCore.QObject = None):
        super().__init__(parent)
        self.src_path = src_path
        self.dst_path = dst_path
        self.finished.connect(self.deleteLater)

    def run(self):
        if self.src_path is None and self.dst_path is None:
            self.copied.emit()
            return

        if self.src_path.is_dir():
            self.dst_path.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copytree(self.src_path, self.dst_path, dirs_exist_ok=True)
            except shutil.Error:
                # LOCK 文件没有权限复制，不用管
                pass
        else:
            shutil.copyfile(self.src_path, self.dst_path)
        self.copied.emit()


class CopyThreadManager(QtCore.QObject):

    def __init__(self, num_tar_profiles: int, num_temp_exts: int,
                 progress_bar: QtWidgets.QProgressBar, parent: QtWidgets.QDialog):
        super().__init__(parent)
        self.num_tar_profiles = num_tar_profiles
        self.num_temp_exts = num_temp_exts
        self.copy_progress = 0
        self.finish_info = "已为 {p} 个用户追加 {e} 个插件。"
        self.progress_bar = progress_bar
        self.parent = parent

        self.total = num_tar_profiles * num_temp_exts
        self.progress_bar.setMaximum(self.total)
        self.progress_bar.setValue(0)

        self.progress_bar.valueChanged.connect(self.on_pgb_copy_value_changed)

    def start(self, thread: CopyThread):
        thread.copied.connect(self.on_copy_thd_copied)
        thread.start()

    def on_copy_thd_copied(self):
        self.copy_progress += 1
        self.progress_bar.setValue(self.copy_progress)

    def on_pgb_copy_value_changed(self, value: int):
        if value == self.total:
            QtWidgets.QMessageBox.information(
                self.parent, "追加结果", self.finish_info.format(
                    p=self.num_tar_profiles,
                    e=self.num_temp_exts
                )
            )
            self.parent.accept()
