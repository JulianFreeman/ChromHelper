# coding: utf8
import json
import logging
from pathlib import Path
from config import QtWidgets, QtGui, QtCore, QtSql

from typedict_def import PrfDB, AllExtDB, SgExtInfo, PrfInfo
from utils_qtwidgets import (
    VerticalLine, get_sql_database, ItemIdsRole,
    CopyThread, CopyThreadManager, get_extension_icon
)
from utils_chromium import get_extensions_db
from utils_general import (
    sort_profiles_id_func, path_not_exist,
    get_with_chained_keys,
)
from da_progress_bar import DaProgressBar


class UiWgAppendExtensions(object):

    def __init__(self, window: QtWidgets.QWidget = None):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.pbn_set_temp = QtWidgets.QPushButton("设定模板", window)
        self.pbn_clear_temp = QtWidgets.QPushButton("清空模板", window)
        self.pbn_set_tar_profiles = QtWidgets.QPushButton("设定用户", window)
        self.pbn_clear_tar_profiles = QtWidgets.QPushButton("清空用户", window)
        self.pbn_append = QtWidgets.QPushButton("追加", window)
        self.pbn_update = QtWidgets.QPushButton("更新", window)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.pbn_set_temp)
        self.hly_top.addWidget(self.pbn_clear_temp)
        self.hly_top.addWidget(VerticalLine(window))
        self.hly_top.addWidget(self.pbn_set_tar_profiles)
        self.hly_top.addWidget(self.pbn_clear_tar_profiles)
        self.hly_top.addWidget(VerticalLine(window))
        self.hly_top.addWidget(self.pbn_append)
        self.hly_top.addWidget(self.pbn_update)

        self.hly_cnt = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_cnt)

        self.trw_profiles = QtWidgets.QTreeWidget(window)
        self.trw_profiles.setColumnCount(2)
        self.trw_profiles.setHeaderLabels(["ID", "名称"])
        self.trw_profiles.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self.lw_extensions = QtWidgets.QListWidget(window)
        self.lw_extensions.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self.hly_cnt.addWidget(self.trw_profiles)
        self.hly_cnt.addWidget(self.lw_extensions)

        self.vly_right = QtWidgets.QVBoxLayout()
        self.hly_cnt.addLayout(self.vly_right)

        self.lne_temp_profile_id = QtWidgets.QLineEdit(window)
        self.lne_temp_profile_id.setReadOnly(True)
        self.lw_temp = QtWidgets.QListWidget(window)
        self.lw_temp.setEditTriggers(QtWidgets.QListWidget.EditTrigger.NoEditTriggers)
        self.trw_tar_profiles = QtWidgets.QTreeWidget(window)
        self.trw_tar_profiles.setColumnCount(2)
        self.trw_tar_profiles.setHeaderLabels(["ID", "名称"])
        self.vly_right.addWidget(self.lne_temp_profile_id)
        self.vly_right.addWidget(self.lw_temp)
        self.vly_right.addWidget(self.trw_tar_profiles)


class WgAppendExtensions(QtWidgets.QWidget):

    templates_changed = QtCore.Signal()

    def __init__(self, browser: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.browser = browser
        self.browser_change_lock = False
        self.ui = UiWgAppendExtensions(self)

        self._profiles_dbs: dict[str, PrfDB] = {
            "Chrome": {},
            "Edge": {},
            "Brave": {},
        }
        self._all_ext_db = {}  # type: AllExtDB
        self._temp_exts = []  # type: list[SgExtInfo]
        self._tar_profiles = []  # type: list[PrfInfo]

        self.ui.trw_profiles.itemSelectionChanged.connect(self.on_trw_profiles_item_selection_changed)
        self.ui.pbn_set_temp.clicked.connect(self.on_pbn_set_temp_clicked)
        self.ui.pbn_clear_temp.clicked.connect(self.on_pbn_clear_temp_clicked)
        self.ui.pbn_set_tar_profiles.clicked.connect(self.on_pbn_set_tar_profiles_clicked)
        self.ui.pbn_clear_tar_profiles.clicked.connect(self.on_pbn_clear_tar_profiles_clicked)
        self.ui.pbn_append.clicked.connect(self.on_pbn_append_clicked)
        self.ui.pbn_update.clicked.connect(self.on_pbn_update_clicked)

        self.templates_changed.connect(self.on_self_templates_changed)

    def on_browser_changed(self, browser: str, profiles_db: PrfDB):
        self.browser_change_lock = True
        self.browser = browser
        self._profiles_dbs[browser] = profiles_db

        self.on_pbn_clear_temp_clicked()
        self.on_pbn_clear_tar_profiles_clicked()

        self.load_profiles(profiles_db)
        self.browser_change_lock = False

    def load_profiles(self, profile_db: PrfDB):
        self.ui.trw_profiles.clear()
        self.ui.lw_extensions.clear()

        _, self._all_ext_db = get_extensions_db(profile_db, True)
        display_profiles = [(pid, profile_db[pid]["name"]) for pid in profile_db]
        display_profiles.sort(key=lambda x: sort_profiles_id_func(x[0]))
        for row in display_profiles:
            QtWidgets.QTreeWidgetItem(self.ui.trw_profiles, row)

    def on_pbn_set_temp_clicked(self):
        self.on_pbn_clear_temp_clicked()

        profile_id = self.ui.trw_profiles.currentItem().text(0)
        sel_exts_id = [item.data(ItemIdsRole) for item in self.ui.lw_extensions.selectedItems()]
        exts_info = self._all_ext_db[profile_id]

        for e in exts_info:
            if e["id"] in sel_exts_id:
                self._temp_exts.append(e)
                icon = get_extension_icon(e["icon"])
                item = QtWidgets.QListWidgetItem(icon, e["name"], self.ui.lw_temp)
                item.setData(ItemIdsRole, e["id"])
        self.ui.lne_temp_profile_id.setText(profile_id)

        self.templates_changed.emit()

    def on_pbn_clear_temp_clicked(self):
        self.ui.lw_temp.clear()
        self._temp_exts.clear()
        self.ui.lne_temp_profile_id.clear()

        self.templates_changed.emit()

    def on_pbn_set_tar_profiles_clicked(self):
        self.on_pbn_clear_tar_profiles_clicked()

        profiles_db = self._profiles_dbs[self.browser]
        profile_rows = [(i.text(0), i.text(1)) for i in self.ui.trw_profiles.selectedItems()]
        for row in profile_rows:
            self._tar_profiles.append(profiles_db[row[0]])
            QtWidgets.QTreeWidgetItem(self.ui.trw_tar_profiles, row)

    def on_pbn_clear_tar_profiles_clicked(self):
        self.ui.trw_tar_profiles.clear()
        self._tar_profiles.clear()

    def on_trw_profiles_item_selection_changed(self):
        if self.browser_change_lock:
            return

        self.ui.lw_extensions.clear()
        profile_id = self.ui.trw_profiles.currentItem().text(0)
        exts_info = self._all_ext_db[profile_id]
        exts_id = []  # type: list[str]
        for e in exts_info:
            icon = get_extension_icon(e["icon"])
            item = QtWidgets.QListWidgetItem(icon, e["name"], self.ui.lw_extensions)
            item.setData(ItemIdsRole, e["id"])
            exts_id.append(e["id"])

        for i in range(self.ui.lw_temp.count()):
            item = self.ui.lw_temp.item(i)
            ids = item.data(ItemIdsRole)
            if ids not in exts_id:
                item.setBackground(QtGui.QBrush(QtGui.QColor("lightpink")))
            else:
                item.setBackground(QtGui.QBrush(QtCore.Qt.BrushStyle.NoBrush))

    def on_pbn_update_clicked(self):
        item = self.ui.trw_profiles.currentItem()
        if item is not None:
            idx = self.ui.trw_profiles.indexOfTopLevelItem(item)
        else:
            idx = -1
        v = self.ui.trw_profiles.verticalScrollBar().sliderPosition()

        self.load_profiles(self._profiles_dbs[self.browser])

        item = self.ui.trw_profiles.topLevelItem(idx)
        if item is not None:
            self.ui.trw_profiles.setCurrentItem(item)
        self.ui.trw_profiles.verticalScrollBar().setSliderPosition(v)

        self.on_self_templates_changed()
        QtWidgets.QMessageBox.information(self, "提示", "用户和插件状态已更新。")

    def on_self_templates_changed(self):
        for i in range(self.ui.trw_profiles.topLevelItemCount()):
            item = self.ui.trw_profiles.topLevelItem(i)
            profile_id = item.text(0)

            exts_id = [e["id"] for e in self._all_ext_db[profile_id]]
            num_installed = 0
            for e in self._temp_exts:
                if e["id"] in exts_id:
                    num_installed += 1
            if num_installed == len(self._temp_exts):
                item.setBackground(0, QtGui.QBrush(QtCore.Qt.BrushStyle.NoBrush))
            elif num_installed == 0:
                item.setBackground(0, QtGui.QBrush(QtGui.QColor("lightpink")))
            else:
                item.setBackground(0, QtGui.QBrush(QtGui.QColor("moccasin")))

    def on_pbn_append_clicked(self):
        temp_profile_id = self.ui.lne_temp_profile_id.text()
        if len(temp_profile_id) == 0:
            QtWidgets.QMessageBox.critical(self, "错误", "没有设定模板用户")
            return
        if len(self._tar_profiles) == 0:
            QtWidgets.QMessageBox.critical(self, "错误", "没有设定目标用户")
            return
        profiles_db = self._profiles_dbs[self.browser]
        temp_profile_info = profiles_db[temp_profile_id]

        s_pref_path = temp_profile_info["s_pref_path"]
        if path_not_exist(s_pref_path):
            QtWidgets.QMessageBox.critical(self, "错误", "出现错误，详情查看日志")
            logging.error(f"找不到模板用户的 {s_pref_path}")
            return

        s_pref_data = json.loads(s_pref_path.read_text("utf8"))  # type: dict
        ext_set_data = get_with_chained_keys(s_pref_data, ["extensions", "settings"])  # type: dict
        if ext_set_data is None:
            QtWidgets.QMessageBox.critical(self, "错误", "出现错误，详情查看日志")
            logging.error(f"在模板用户的 {s_pref_path} 中找不到 extensions>settings")
            return

        macs_es_data = get_with_chained_keys(s_pref_data, ["protection", "macs", "extensions", "settings"])  # type: dict
        if macs_es_data is None:
            QtWidgets.QMessageBox.critical(self, "错误", "出现错误，详情查看日志")
            logging.error(f"在模板用户的 {s_pref_path} 中找不到 protection>macs>extensions>settings")
            return

        internal_exts = []  # type: list[tuple[str, str, dict, str]]  # path, ids, info, mac
        external_exts = []  # type: list[tuple[str, dict, str]]  # ids, info, mac

        # 在插件部分检测存在性
        extensions_path_d = temp_profile_info["extensions_path_d"]
        local_ext_settings_path_d = temp_profile_info["local_ext_settings_path_d"]
        ext_cookies_path = temp_profile_info["ext_cookies_path"]
        for ext in self._temp_exts:
            ids = ext["id"]
            if ids not in ext_set_data:
                continue
            if ids not in macs_es_data:
                continue
            ext_info = ext_set_data[ids]
            mac = macs_es_data[ids]
            path = ext_info["path"]  # type: str
            if path.startswith(ids):
                ext_path = Path(extensions_path_d, path)
                is_internal = True
            else:
                ext_path = Path(path)
                is_internal = False
            if path_not_exist(ext_path):
                continue

            if is_internal:
                internal_exts.append((path, ids, ext_info, mac))
            else:
                external_exts.append((ids, ext_info, mac))

        da_pb = DaProgressBar("追加插件进度", self)
        da_pb.show()
        cp_thd_mgr = CopyThreadManager(len(self._tar_profiles), len(self._temp_exts), da_pb.pgb_m, da_pb)

        for profile_info in self._tar_profiles:
            profile_id = profile_info["path"].name
            s_pref_path_i = profile_info["s_pref_path"]
            if path_not_exist(s_pref_path_i):
                logging.error(f"找不到目标用户的 {s_pref_path_i}")
                continue
            s_pref_data_i = json.loads(s_pref_path_i.read_text("utf8"))  # type: dict
            ext_set_data_i = get_with_chained_keys(s_pref_data_i, ["extensions", "settings"])  # type: dict
            if ext_set_data_i is None:
                logging.error(f"在目标用户的 {s_pref_path_i} 中找不到 extensions>settings")
                continue
            macs_es_data_i = get_with_chained_keys(s_pref_data_i, ["protection", "macs", "extensions", "settings"])  # type: dict
            if macs_es_data_i is None:
                logging.error(f"在目标用户的 {s_pref_path_i} 中找不到 protection>macs>extensions>settings")
                continue

            for path, ids, ext_info, mac in internal_exts:
                ext_set_data_i[ids] = ext_info
                macs_es_data_i[ids] = mac
                src_ext_path = Path(extensions_path_d, path)
                dst_extensions_path_d = profile_info["extensions_path_d"]
                dst_ext_path = Path(dst_extensions_path_d, path)
                cp_thd = CopyThread(src_ext_path, dst_ext_path, da_pb)
                cp_thd_mgr.start(cp_thd)

                # 插件数据（只转 Click&Clean）
                if ids == "ghgabhipcejejjmhhchfonmamedcbeod":
                    src_loc_es_path_i = Path(local_ext_settings_path_d, ids)
                    if not path_not_exist(src_loc_es_path_i):
                        dst_local_ext_settings_path_d = profile_info["local_ext_settings_path_d"]
                        dst_loc_es_path_i = Path(dst_local_ext_settings_path_d, ids)
                        cp_d_thd = CopyThread(src_loc_es_path_i, dst_loc_es_path_i, self)
                        cp_d_thd.start()
                if self.browser == "Edge" and ids == "dacknjoogbepndbemlmljdobinliojbk" and not path_not_exist(ext_cookies_path):
                    dst_ext_cookies_path = profile_info["ext_cookies_path"]
                    if path_not_exist(dst_ext_cookies_path):
                        cp_c_thd = CopyThread(ext_cookies_path, dst_ext_cookies_path, self)
                        cp_c_thd.start()
                    else:
                        src_ec_db = get_sql_database(f"{self.browser}_{temp_profile_id}_ec", str(ext_cookies_path))
                        if not src_ec_db.open():
                            logging.error(f"在 Edge 中拷贝插件数据时未能打开 {temp_profile_id} 的 Extension Cookies 文件")
                        else:
                            dst_ec_db = get_sql_database(f"{self.browser}_{profile_id}_ec", str(dst_ext_cookies_path))
                            if not dst_ec_db.open():
                                logging.error(f"在 Edge 中拷贝插件数据时未能打开 {profile_id} 的 Extension Cookies 文件")
                            else:
                                ec_query = QtSql.QSqlQuery(dst_ec_db)
                                ec_query.exec(f"ATTACH DATABASE '{str(ext_cookies_path)}' AS src_ec_db;")
                                ec_query.exec(f"INSERT INTO cookies SELECT * FROM src_ec_db.cookies WHERE host_key='{ids}';")

            for ids, ext_info, mac in external_exts:
                ext_set_data_i[ids] = ext_info
                macs_es_data_i[ids] = mac
                # 离线插件不需要复制目录
                # 做个样子，为了计数
                cp_thd = CopyThread(None, None, da_pb)
                cp_thd_mgr.start(cp_thd)

            s_pref_path_i.write_text(json.dumps(s_pref_data_i, ensure_ascii=False), "utf8")

        self.on_pbn_clear_tar_profiles_clicked()
