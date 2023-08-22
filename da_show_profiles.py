# coding: utf8
from typing import Callable
from config import QtWidgets, QtCore, is_compatible

from typedict_def import PrfInfo, PrfDB
from utils_general import sort_profiles_id_func, get_errmsg
from utils_chromium import get_exec_path
from utils_qtwidgets import accept_warning


class DaShowProfiles(QtWidgets.QDialog):

    def __init__(self, browser: str, profiles_db: PrfDB,
                 delete_func: Callable[[PrfInfo, str], bool],
                 parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.browser = browser
        self.profiles_db = profiles_db
        self.delete_func = delete_func

        self.resize(400, 360)
        self.vly_m = QtWidgets.QVBoxLayout()
        self.setLayout(self.vly_m)

        self.lne_info = QtWidgets.QLineEdit(self)
        self.lne_info.setReadOnly(True)
        self.vly_m.addWidget(self.lne_info)

        self.trw_profiles = QtWidgets.QTreeWidget(self)
        self.trw_profiles.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.vly_m.addWidget(self.trw_profiles)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.pbn_delete_selected = QtWidgets.QPushButton("删除所选", self)
        self.pbn_open = QtWidgets.QPushButton("打开", self)
        self.pbn_cancel = QtWidgets.QPushButton("取消", self)
        self.hly_bot.addWidget(self.pbn_delete_selected)
        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_open)
        self.hly_bot.addWidget(self.pbn_cancel)
        self.vly_m.addLayout(self.hly_bot)

        self.pbn_delete_selected.clicked.connect(self.on_pbn_delete_selected_clicked)
        self.pbn_open.clicked.connect(self.on_pbn_open_clicked)
        self.pbn_cancel.clicked.connect(self.reject)

        self._process = QtCore.QProcess(self)

    def update_list(self, profiles: list[tuple[str, ...]], info: str):
        self.trw_profiles.clear()
        self.trw_profiles.setColumnCount(3)
        self.trw_profiles.setHeaderLabels(["ID", "名称", "位置"])

        profiles.sort(key=lambda x: sort_profiles_id_func(x[0]))
        for elem in profiles:
            QtWidgets.QTreeWidgetItem(self.trw_profiles, elem)
        self.lne_info.setText(info)

    def on_pbn_open_clicked(self):
        items = self.trw_profiles.selectedItems()

        errmsg = get_errmsg()
        exec_path = get_exec_path(self.browser, errmsg=errmsg)
        if errmsg["err"]:
            QtWidgets.QMessageBox.critical(self, "错误", errmsg["msg"])
            return

        cmd = rf'"{exec_path}" --profile-directory="{{0}}"'

        for item in items:
            profile_id = item.text(0)  # type: str
            # setProgram 不行，不知道为什么，莫名其妙
            if is_compatible:
                self._process.start(cmd.format(profile_id))
            else:
                self._process.startCommand(cmd.format(profile_id))
            self._process.waitForFinished(10000)

    def on_pbn_delete_selected_clicked(self):
        sel_items = self.trw_profiles.selectedItems()
        total = len(sel_items)
        if accept_warning(self, True, "警告", f"确定要删除这 {total} 项吗？"):
            return

        success, fail = 0, 0
        for item in sel_items:
            profile_id = item.text(0)  # type: str
            if self.delete_func(self.profiles_db[profile_id], self.lne_info.text()):
                success += 1
            else:
                fail += 1

        QtWidgets.QMessageBox.information(self, "信息", f"一共选中 {total} 个，成功删除 {success} 个，失败 {fail} 个。")
        self.accept()
