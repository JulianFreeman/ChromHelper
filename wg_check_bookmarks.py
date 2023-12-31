# coding: utf8
from config import QtWidgets, QtCore, QtGui, is_compatible

from typedict_def import PrfDB, BmxDB
from utils_qtwidgets import accept_warning, ItemUrlRole, DeleteThread, DeleteThreadManager
from utils_chromium import get_bookmarks_db, delete_bookmarks
from utils_general import sort_profiles_id_func

from da_show_profiles import DaShowProfiles
from da_export_bookmarks import DaExportBookmarks
from da_progress_bar import DaProgressBar


class UiWgCheckBookmarks(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.lb_filter = QtWidgets.QLabel("输入关键词：", window)
        self.lne_filter = QtWidgets.QLineEdit(window)
        self.pbn_update = QtWidgets.QPushButton("更新", window)
        self.pbn_export_sel = QtWidgets.QPushButton("导出所选", window)
        self.pbn_delete_sel = QtWidgets.QPushButton("删除所选", window)
        self.hly_top.addWidget(self.lb_filter)
        self.hly_top.addWidget(self.lne_filter)
        self.hly_top.addWidget(self.pbn_update)
        self.hly_top.addWidget(self.pbn_export_sel)
        self.hly_top.addWidget(self.pbn_delete_sel)

        self.hly_mid = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_mid)

        self.cbx_filter_by_url = QtWidgets.QCheckBox("搜索 URL", window)
        self.cbx_exclude_search = QtWidgets.QCheckBox("排除 Google Search", window)
        self.lb_search_profile = QtWidgets.QLabel("搜索用户：", window)
        self.cmbx_search_profile = QtWidgets.QComboBox(window)
        self.lb_cur_amount = QtWidgets.QLabel("当前书签个数：", window)
        self.sbx_cur_amount = QtWidgets.QSpinBox(window)
        self.sbx_cur_amount.setReadOnly(True)
        self.sbx_cur_amount.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.sbx_cur_amount.setMaximum(9999)
        self.hly_mid.addWidget(self.lb_search_profile)
        self.hly_mid.addWidget(self.cmbx_search_profile)
        self.hly_mid.addWidget(self.cbx_filter_by_url)
        self.hly_mid.addWidget(self.cbx_exclude_search)
        self.hly_mid.addStretch(1)
        self.hly_mid.addWidget(self.lb_cur_amount)
        self.hly_mid.addWidget(self.sbx_cur_amount)

        self.lw_bookmarks = QtWidgets.QListWidget(window)
        self.lw_bookmarks.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self.vly_m.addWidget(self.lw_bookmarks)


class WgCheckBookmarks(QtWidgets.QWidget):

    def __init__(self, browser: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.ui = UiWgCheckBookmarks(self)
        self.browser = browser
        self._profiles_dbs: dict[str, PrfDB] = {
            "Chrome": {},
            "Edge": {},
            "Brave": {},
        }
        self._bmx_db = {}  # type: BmxDB

        self.ui.pbn_update.clicked.connect(self.on_pbn_update_clicked)
        self.ui.pbn_export_sel.clicked.connect(self.on_pbn_export_sel_clicked)
        self.ui.pbn_delete_sel.clicked.connect(self.on_pbn_delete_sel_clicked)
        self.ui.lne_filter.textEdited.connect(self.on_lne_filter_text_edited)
        self.ui.cbx_filter_by_url.stateChanged.connect(self.on_cbx_filter_by_url_state_changed)
        self.ui.cbx_exclude_search.stateChanged.connect(self.on_cbx_exclude_search_state_changed)
        self.ui.cmbx_search_profile.currentIndexChanged.connect(self.on_cmbx_search_profile_current_index_changed)
        self.ui.lw_bookmarks.itemDoubleClicked.connect(self.on_lw_bookmarks_item_double_clicked)

    def filter_bookmarks(self, *,
                         keyword: str = None,
                         by_url: bool = None,
                         exclude_search: bool = None,
                         search_profile: str = None):
        num_visible = 0
        if keyword is None:
            keyword = self.ui.lne_filter.text()
        if by_url is None:
            by_url = self.ui.cbx_filter_by_url.isChecked()
        if exclude_search is None:
            exclude_search = self.ui.cbx_exclude_search.isChecked()
        if search_profile is None:
            search_profile = self.ui.cmbx_search_profile.currentData()

        for i in range(self.ui.lw_bookmarks.count()):
            item = self.ui.lw_bookmarks.item(i)
            name = item.text().lower()
            url = item.data(ItemUrlRole)
            keyword = keyword.lower()  # 空字符串 in 任意字符串  都为 True

            filtered = False
            if by_url:
                filtered = filtered or (keyword not in url)
            else:
                filtered = filtered or (keyword not in name)
            if exclude_search:
                filtered = filtered or (url.startswith("https://www.google.com/search"))
            if search_profile != "all":
                filtered = filtered or search_profile not in self._bmx_db[url]["profiles"]

            item.setHidden(filtered)
            if not filtered:
                num_visible += 1
        self.ui.sbx_cur_amount.setValue(num_visible)

    def update_bookmarks(self, profiles_db: PrfDB):
        self._bmx_db = get_bookmarks_db(profiles_db)
        self.ui.lw_bookmarks.clear()
        for url in self._bmx_db:
            name = self._bmx_db[url]["name"]

            item = QtWidgets.QListWidgetItem(name, self.ui.lw_bookmarks)
            item.setData(ItemUrlRole, url)

        # 触发过滤
        self.filter_bookmarks()

    def on_browser_changed(self, browser: str, profiles_db: PrfDB):
        self.browser = browser
        self._profiles_dbs[browser] = profiles_db
        self.update_bookmarks(profiles_db)

        self.ui.cmbx_search_profile.clear()
        profiles_list = [(pid, profiles_db[pid]["name"]) for pid in profiles_db]
        profiles_list.sort(key=lambda x: sort_profiles_id_func(x[0]))
        self.ui.cmbx_search_profile.addItem("全部", "all")
        for pid, name in profiles_list:
            self.ui.cmbx_search_profile.addItem(f"{pid} - {name}", pid)

    def on_pbn_update_clicked(self):
        self.update_bookmarks(self._profiles_dbs[self.browser])
        QtWidgets.QMessageBox.information(self, "提示", "书签信息已更新。")

    def on_pbn_delete_sel_clicked(self):
        sel_items = self.ui.lw_bookmarks.selectedItems()
        total = len(sel_items)
        if accept_warning(self, True, "警告", f"确定删除这 {total} 项吗？"):
            return

        inst = 0
        id_urls = {}  # type: dict[str, list[str]]
        for item in sel_items:
            url = item.data(ItemUrlRole)
            profiles = self._bmx_db[url]["profiles"]

            for profile_id in profiles:
                id_urls.setdefault(profile_id, [])
                id_urls[profile_id].append(url)
                inst += 1

        da_pb = DaProgressBar("删除书签进度", self)
        da_pb.show()
        del_thd_mgr = DeleteThreadManager(inst, da_pb.pgb_m, da_pb)

        for profile_id in id_urls:
            del_thd = DeleteThread(delete_bookmarks, self._profiles_dbs[self.browser][profile_id],
                                   id_urls[profile_id], da_pb)
            del_thd_mgr.start(del_thd)

    def on_pbn_export_sel_clicked(self):
        bmx_db = {}  # type: BmxDB
        for item in self.ui.lw_bookmarks.selectedItems():
            url = item.data(ItemUrlRole)
            bmx_db[url] = self._bmx_db[url]

        da_eb = DaExportBookmarks(bmx_db, self)
        da_eb.setWindowTitle("导出书签")
        da_eb.setWindowIcon(QtGui.QIcon(":/img/ebk_16.png"))
        da_eb.resize(640, 360)
        da_eb.exec()

    def on_lne_filter_text_edited(self, text: str):
        self.filter_bookmarks(keyword=text)

    def on_cbx_filter_by_url_state_changed(self, state: int):
        if is_compatible:
            by_url = state == int(QtCore.Qt.CheckState.Checked)
        else:
            by_url = state == QtCore.Qt.CheckState.Checked.value
        self.filter_bookmarks(by_url=by_url)

    def on_cbx_exclude_search_state_changed(self, state: int):
        if is_compatible:
            exclude_search = state == int(QtCore.Qt.CheckState.Checked)
        else:
            exclude_search = state == QtCore.Qt.CheckState.Checked.value
        self.filter_bookmarks(exclude_search=exclude_search)

    def on_cmbx_search_profile_current_index_changed(self, index: int):
        if index == -1:
            return
        profile_id = self.ui.cmbx_search_profile.itemData(index)
        self.filter_bookmarks(search_profile=profile_id)

    def on_lw_bookmarks_item_double_clicked(self, item: QtWidgets.QListWidgetItem):
        bookmark = item.text()
        url = item.data(ItemUrlRole)
        if len(bookmark) > 40:
            title = bookmark[:37] + "..."
        else:
            title = bookmark

        da_sp = DaShowProfiles(self.browser, self._profiles_dbs[self.browser], delete_bookmarks, self)
        da_sp.setWindowTitle(f"{title} - {self.browser}")
        profiles = self._bmx_db[url]["profiles"]

        display_profiles = [(pid, name, pos) for pid, (name, pos) in profiles.items()]

        da_sp.update_list(display_profiles, url)
        da_sp.show()
