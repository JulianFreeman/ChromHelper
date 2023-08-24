# coding: utf8
import json
from pathlib import Path

from typedict_def import PrfDB, ExtDB
from config import QtWidgets, QtGui
from utils_qtwidgets import accept_warning, ItemStatusRole, ItemIdsRole, get_extension_icon
from utils_chromium import get_extensions_db, delete_extensions

from da_show_profiles import DaShowProfiles
from pbn_colored_button import PbnColoredButton


class UiWgCheckPlugins(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.pbn_safe = self.create_status_button("安全", 1, "pbn_safe", window)
        self.pbn_unsafe = self.create_status_button("不安全", -1, "pbn_unsafe", window)
        self.pbn_unknown = self.create_status_button("未知", 0, "pbn_unknown", window)
        self.pbn_update = QtWidgets.QPushButton("更新", window)
        self.pbn_export_unknown = QtWidgets.QPushButton("导出未知", window)

        self.hly_top.addWidget(self.pbn_safe)
        self.hly_top.addWidget(self.pbn_unsafe)
        self.hly_top.addWidget(self.pbn_unknown)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.pbn_update)
        self.hly_top.addWidget(self.pbn_export_unknown)

        self.lw_plugins = QtWidgets.QListWidget(window)
        self.vly_m.addWidget(self.lw_plugins)

        self.pbn_safe.setChecked(True)
        self.pbn_unsafe.setChecked(True)
        self.pbn_unknown.setChecked(True)

    @staticmethod
    def create_status_button(text: str, status: int, obj_name: str,
                             parent: QtWidgets.QWidget) -> PbnColoredButton:
        if status > 0:
            color = "green"
        elif status < 0:
            color = "red"
        else:
            color = "gray"
        pbn_s = PbnColoredButton(color, obj_name, parent)
        pbn_s.setText(text)
        pbn_s.setCheckable(True)

        return pbn_s


class WgCheckPlugins(QtWidgets.QWidget):

    def __init__(self, browser: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.browser = browser
        self.ui = UiWgCheckPlugins(self)

        self._profiles_dbs: dict[str, PrfDB] = {
            "Chrome": {},
            "Edge": {},
            "Brave": {},
        }
        self._ext_db = {}  # type: ExtDB

        self.ui.lw_plugins.itemDoubleClicked.connect(self.on_lw_plugins_item_double_clicked)
        self.ui.pbn_update.clicked.connect(self.on_pbn_update_clicked)
        self.ui.pbn_export_unknown.clicked.connect(self.on_pbn_export_unknown_clicked)

        self.ui.pbn_safe.toggled.connect(self.on_pbn_safe_toggled)
        self.ui.pbn_unsafe.toggled.connect(self.on_pbn_unsafe_toggled)
        self.ui.pbn_unknown.toggled.connect(self.on_pbn_unknown_toggled)

    def update_extensions(self, profiles_db: PrfDB):
        self.ui.lw_plugins.clear()
        self._ext_db, _ = get_extensions_db(profiles_db, False)

        for ext_id in self._ext_db:
            ext_info = self._ext_db[ext_id]
            icon = get_extension_icon(ext_info["icon"])
            item = QtWidgets.QListWidgetItem(icon, ext_info["name"], self.ui.lw_plugins)
            match ext_info["safe"]:
                case True:
                    item.setBackground(QtGui.QBrush(QtGui.QColor("lightgreen")))
                    item.setData(ItemStatusRole, 1)
                    item.setHidden(not self.ui.pbn_safe.isChecked())
                case False:
                    item.setBackground(QtGui.QBrush(QtGui.QColor("lightpink")))
                    item.setData(ItemStatusRole, -1)
                    item.setHidden(not self.ui.pbn_unsafe.isChecked())
                case None:
                    item.setData(ItemStatusRole, 0)
                    item.setHidden(not self.ui.pbn_unknown.isChecked())
            item.setData(ItemIdsRole, ext_id)
            item.setToolTip(ext_info["note"])

    def on_browser_changed(self, browser: str, profiles_db: PrfDB):
        self.browser = browser
        self._profiles_dbs[browser] = profiles_db
        self.update_extensions(profiles_db)

    def on_pbn_update_clicked(self):
        self.update_extensions(self._profiles_dbs[self.browser])
        QtWidgets.QMessageBox.information(self, "提示", "插件信息已更新。")

    def on_pbn_safe_toggled(self, checked: bool):
        for i in range(self.ui.lw_plugins.count()):
            item = self.ui.lw_plugins.item(i)
            if item.data(ItemStatusRole) > 0:
                item.setHidden(not checked)

    def on_pbn_unsafe_toggled(self, checked: bool):
        for i in range(self.ui.lw_plugins.count()):
            item = self.ui.lw_plugins.item(i)
            if item.data(ItemStatusRole) < 0:
                item.setHidden(not checked)

    def on_pbn_unknown_toggled(self, checked: bool):
        for i in range(self.ui.lw_plugins.count()):
            item = self.ui.lw_plugins.item(i)
            if item.data(ItemStatusRole) == 0:
                item.setHidden(not checked)

    def on_pbn_export_unknown_clicked(self):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "导出未知")
        if len(dirname) == 0:
            return
        ex_file = Path(dirname, f"unknown_extensions_{self.browser}.json")
        if accept_warning(self, ex_file.exists(), "警告", "文件已存在，确认覆盖吗？"):
            return

        unknown_ext = {e: v["name"] for e, v in self._ext_db.items() if v["safe"] is None}
        with open(ex_file, "w", encoding="utf8") as f:
            json.dump(unknown_ext, f, indent=4, ensure_ascii=False)
        QtWidgets.QMessageBox.information(self, "提示", f"已导出到 {ex_file}")

    def on_lw_plugins_item_double_clicked(self, item: QtWidgets.QListWidgetItem):
        ext_id = item.data(ItemIdsRole)  # type: str
        ext_info = self._ext_db[ext_id]

        da_sp = DaShowProfiles(self.browser, self._profiles_dbs[self.browser], delete_extensions, self)
        da_sp.setWindowTitle(f"{ext_info['name']} - {self.browser}")
        da_sp.setWindowIcon(item.icon())

        display_profiles = [(i, n) for i, n in ext_info["profiles"].items()]
        da_sp.update_list(display_profiles, ext_id)
        da_sp.show()
