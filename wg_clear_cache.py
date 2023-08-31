# coding: utf8
import os
from config import QtWidgets, QtCore, QtGui

from typedict_def import PrfDB
from utils_general import path_not_exist, sort_profiles_id_func
from utils_qtwidgets import ItemSizeRole, TrwiSortBySize, ClearThread, accept_warning


class UiWgClearCache(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.lb_total_size = QtWidgets.QLabel("总缓存大小：", window)
        self.lne_total_size = QtWidgets.QLineEdit(window)
        self.lne_total_size.setReadOnly(True)
        self.pbn_refresh = QtWidgets.QPushButton("刷新", window)
        self.pbn_clear = QtWidgets.QPushButton("清理所选", window)
        self.hly_top.addWidget(self.lb_total_size)
        self.hly_top.addWidget(self.lne_total_size)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.pbn_refresh)
        self.hly_top.addWidget(self.pbn_clear)

        self.trw_cache = QtWidgets.QTreeWidget(window)
        self.vly_m.addWidget(self.trw_cache)
        self.trw_cache.setHeaderLabels(["ID", "名称", "缓存大小", "已清理"])
        self.trw_cache.setSelectionMode(QtWidgets.QTreeWidget.SelectionMode.ExtendedSelection)


class WgClearCache(QtWidgets.QWidget):

    def __init__(self, browser: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.browser = browser
        self._profiles_dbs: dict[str, PrfDB] = {
            "Chrome": {},
            "Edge": {},
            "Brave": {},
        }
        self._cache_db = {}  # type: dict[str, int]  # id: size
        self.ui = UiWgClearCache(self)

        self.ui.pbn_refresh.clicked.connect(self.on_pbn_refresh_clicked)
        self.ui.pbn_clear.clicked.connect(self.on_pbn_clear_clicked)

    @staticmethod
    def _simplify_size(b: int) -> str:
        if b == -1:
            return "-1"

        b = float(b)
        kb = b / 1024
        if kb < 1:
            return f"{b:.0f} B"
        mb = kb / 1024
        if mb < 1:
            return f"{kb:.2f} KB"
        gb = mb / 1024
        if gb < 1:
            return f"{mb:.2f} MB"
        tb = gb / 1024
        if tb < 1:
            return f"{gb:.2f} GB"
        return f"{tb:.2f} TB"

    def on_browser_changed(self, browser: str, profiles_db: PrfDB):
        self.browser = browser
        self._profiles_dbs[browser] = profiles_db
        self.update_cache(profiles_db)

    def update_cache(self, profiles_db: PrfDB):
        self.ui.trw_cache.setSortingEnabled(False)
        self.ui.trw_cache.clear()
        self._cache_db.clear()

        display_profiles = []  # type: list[tuple[str, str, str]]  # type: id, name, h_size
        total_size = 0
        for profile_id in profiles_db:
            profile_info = profiles_db[profile_id]
            cache_data_path_d = profile_info["cache_data_path_d"]
            if path_not_exist(cache_data_path_d):
                size = -1
            else:
                size = 0
                for file in cache_data_path_d.glob("*"):
                    if file.is_file():
                        size += os.stat(file).st_size
                total_size += size
            h_size = self._simplify_size(size)
            self._cache_db[profile_id] = size

            display_profiles.append((profile_id, profile_info["name"], h_size))

        display_profiles.sort(key=lambda x: sort_profiles_id_func(x[0]))
        i = 0
        for pid, name, h_size in display_profiles:
            item = TrwiSortBySize(self.ui.trw_cache, (pid, name, h_size))
            item.setData(0, ItemSizeRole, i)
            item.setData(2, ItemSizeRole, self._cache_db[pid])
            item.setTextAlignment(2, QtCore.Qt.AlignmentFlag.AlignRight)

            i += 1

        self.ui.trw_cache.setSortingEnabled(True)
        self.ui.lne_total_size.setText(self._simplify_size(total_size))

    def on_pbn_refresh_clicked(self):
        self.update_cache(self._profiles_dbs[self.browser])
        QtWidgets.QMessageBox.information(self, "信息", "浏览器缓存已刷新。")

    def on_pbn_clear_clicked(self):
        total = len(self.ui.trw_cache.selectedItems())
        if accept_warning(self, True, "提示", f"确定清理所选的 {total} 个用户吗？"):
            return

        profile_db = self._profiles_dbs[self.browser]
        for item in self.ui.trw_cache.selectedItems():
            profile_id = item.text(0)
            profile_info = profile_db[profile_id]
            cache_data_path_d = profile_info["cache_data_path_d"]
            if path_not_exist(cache_data_path_d):
                continue

            clt = ClearThread(cache_data_path_d, item, self)
            clt.cleared.connect(self.on_clt_cleared)
            clt.start()

    def on_clt_cleared(self, item: TrwiSortBySize):
        item.setBackground(3, QtGui.QBrush(QtGui.QColor("lightgreen")))
