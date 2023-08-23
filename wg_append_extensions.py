# coding: utf8
import shutil
import logging
from pathlib import Path
from config import QtWidgets, QtGui, QtCore, QtSql

from typedict_def import PrfDB, AllExtDB, SgExtInfo, PrfInfo
from utils_qtwidgets import VerticalLine, get_sql_database, CopyThread, ItemIdsRole
from utils_chromium import get_extensions_db
from utils_general import sort_profiles_id_func


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

        self.lne_temp_profile = QtWidgets.QLineEdit(window)
        self.lne_temp_profile.setReadOnly(True)
        self.lw_temp = QtWidgets.QListWidget(window)
        self.lw_temp.setEditTriggers(QtWidgets.QListWidget.EditTrigger.NoEditTriggers)
        self.trw_tar_profiles = QtWidgets.QTreeWidget(window)
        self.trw_tar_profiles.setColumnCount(2)
        self.trw_tar_profiles.setHeaderLabels(["ID", "名称"])
        self.vly_right.addWidget(self.lne_temp_profile)
        self.vly_right.addWidget(self.lw_temp)
        self.vly_right.addWidget(self.trw_tar_profiles)


class WgAppendExtensions(QtWidgets.QWidget):

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
        self._current_temp = []  # type: list[SgExtInfo]
        self._tar_profiles = []  # type: list[PrfInfo]

        self.ui.trw_profiles.itemSelectionChanged.connect(self.on_trw_profiles_item_selection_changed)
        self.ui.pbn_set_temp.clicked.connect(self.on_pbn_set_temp_clicked)
        self.ui.pbn_clear_temp.clicked.connect(self.on_pbn_clear_temp_clicked)
        self.ui.pbn_set_tar_profiles.clicked.connect(self.on_pbn_set_tar_profiles_clicked)
        self.ui.pbn_clear_tar_profiles.clicked.connect(self.on_pbn_clear_tar_profiles_clicked)
        self.ui.pbn_append.clicked.connect(self.on_pbn_append_clicked)
        self.ui.pbn_update.clicked.connect(self.on_pbn_update_clicked)

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
        profile_name = self.ui.trw_profiles.currentItem().text(1)
        sel_exts_id = [item.data(ItemIdsRole) for item in self.ui.lw_extensions.selectedItems()]
        exts_info = self._all_ext_db[profile_id]

        for e in exts_info:
            if e["id"] in sel_exts_id:
                self._current_temp.append(e)
                if e["icon"]:
                    icon = QtGui.QIcon(e["icon"])
                else:
                    icon = QtGui.QIcon(":/img/none_128.png")
                self.ui.lw_temp.addItem(QtWidgets.QListWidgetItem(icon, e["name"]))
        self.ui.lne_temp_profile.setText(profile_name)

    def on_pbn_clear_temp_clicked(self):
        self.ui.lw_temp.clear()
        self._current_temp.clear()
        self.ui.lne_temp_profile.clear()

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

        for e in exts_info:
            if e["icon"]:
                icon = QtGui.QIcon(e["icon"])
            else:
                icon = QtGui.QIcon(":/img/none_128.png")
            item = QtWidgets.QListWidgetItem(icon, e["name"], self.ui.lw_extensions)
            item.setData(ItemIdsRole, e["id"])

    def on_pbn_update_clicked(self):
        # idx = self.ui.trw_profiles.ro
        self.load_profiles(self._profiles_dbs[self.browser])
        # self.ui.trw_profiles.setCurrentIndex(idx)
        # self.ui.trw_profiles.scr

        QtWidgets.QMessageBox.information(self, "提示", "用户和插件状态已更新。")

    def on_pbn_append_clicked(self):
        return 0
        profile_name = self.ui.lne_temp_profile.text()
        if len(profile_name) == 0:
            QtWidgets.QMessageBox.critical(self, "错误", "没有设定模板用户")
            return
        data_path = get_data_path(self.browser)
        if data_path is None:
            QtWidgets.QMessageBox.critical(self, "错误", "未找到用户数据文件夹")
            return

        profile_id = profile_name.split(" - ")[0]
        s_pref_db = get_secure_preferences_db(self.browser, profile_id)
        ext_settings = get_extension_settings(self.browser, profile_id, s_pref_db)
        internal_exts = []  # type: list[tuple[Path, str, dict, str]]  # Path, ids, info, mac
        external_exts = []  # type: list[tuple[str, dict, str]]  # ids, info, mac

        for e in self._current_temp:
            ids = e["ids"]
            if ids not in ext_settings:
                continue
            ext_info = ext_settings[ids]  # type: dict
            path = ext_info["path"]  # type: str
            if path.startswith(ids):
                path_p = Path(data_path, profile_id, "Extensions", path)
                is_internal = True
            else:
                path_p = Path(path)
                is_internal = False
            if not path_p.exists():
                continue

            macs_es = get_protection_macs_es(self.browser, profile_id, s_pref_db)
            mac = macs_es.get(ids, "")

            if is_internal:
                internal_exts.append((path_p, ids, ext_info, mac))
            else:
                external_exts.append((ids, ext_info, mac))

        for p in self._tar_profiles:
            prf = p.split(" - ")[0]
            s_pref_db_i = get_secure_preferences_db(self.browser, prf)
            pref_db_i = get_preferences_db(self.browser, prf)
            ext_settings_i = get_extension_settings(self.browser, prf, s_pref_db_i, pref_db_i)
            macs_es_i = get_protection_macs_es(self.browser, prf, s_pref_db_i)

            # 已存在的插件会覆盖
            for path_p, ids, ext_info, mac in internal_exts:
                ext_settings_i[ids] = ext_info
                macs_es_i[ids] = mac
                ext_path = Path(data_path, prf, "Extensions", ids, path_p.name)

                thd_i = CopyThread(path_p, ext_path, self)
                thd_i.start()

                # CC特殊处理
                if ids == "ghgabhipcejejjmhhchfonmamedcbeod":
                    src_path = Path(data_path, profile_id, "Local Extension Settings", ids)
                    dst_path = Path(data_path, prf, "Local Extension Settings", ids)
                    if src_path.exists():
                        thd_c = CopyThread(src_path, dst_path, self)
                        thd_c.start()
                elif self.browser == "Edge" and ids == "dacknjoogbepndbemlmljdobinliojbk":
                    # Edge 的 CC 的配置数据在 Extension Cookies 文件中
                    src_ec_path = Path(data_path, profile_id, "Extension Cookies")
                    if src_ec_path.exists():
                        dst_ec_path = Path(data_path, prf, "Extension Cookies")
                        if not dst_ec_path.exists():
                            thd_c = CopyThread(src_ec_path, dst_ec_path, self)
                            thd_c.start()
                        else:
                            src_ec_db = get_sql_database(f"{self.browser}_{profile_id}_ec", str(src_ec_path))
                            if not src_ec_db.open():
                                logging.error(f"在 Edge 中拷贝 CC 插件时未能打开 {profile_id} 的 Extension Cookies 文件")
                            else:
                                dst_ec_db = get_sql_database(f"{self.browser}_{prf}_ec", str(dst_ec_path))
                                if not dst_ec_db.open():
                                    logging.error(f"在 Edge 中拷贝 CC 插件时未能打开 {prf} 的 Extension Cookies 文件")
                                else:
                                    ec_query = QtSql.QSqlQuery(dst_ec_db)
                                    ec_query.exec(f"ATTACH DATABASE '{str(src_ec_path)}' AS src_ec_db;")
                                    ec_query.exec(f"INSERT INTO cookies SELECT * FROM src_ec_db.cookies WHERE host_key='{ids}';")
                                    logging.info(f"以从 {profile_id} 向 {prf} 的 Extension Cookies 插入 CC 配置")

            for ids, ext_info, mac in external_exts:
                ext_settings_i[ids] = ext_info
                macs_es_i[ids] = mac
                # 离线插件不需要复制目录

            overwrite_preferences_db(pref_db_i, self.browser, prf)
            overwrite_secure_preferences_db(s_pref_db_i, self.browser, prf)

        total = len(self._tar_profiles)
        self.on_pbn_clear_tar_profiles_clicked()

        QtWidgets.QMessageBox.information(
            self, "信息",
            f"已为 {total} 个用户追加 {len(internal_exts)} 个在线插件和 {len(external_exts)} 个离线插件。"
        )
