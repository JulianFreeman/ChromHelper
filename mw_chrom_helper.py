# coding: utf8
import sys
import shutil

from config import QtWidgets, QtGui, QtCore, QAction, QActionGroup, is_compatible
from utils_general import get_log_dir, get_errmsg
from utils_chromium import (
    get_data_path,
    get_profiles_db,
)

from da_chrom_settings import DaChromSettings
from wg_check_plugins import WgCheckPlugins
from wg_check_bookmarks import WgCheckBookmarks
from wg_check_settings import WgCheckSettings
from wg_append_extensions import WgAppendExtensions
from wg_clear_cache import WgClearCache

import chrom_helper_rc


class UiMwChromHelper(object):

    def __init__(self, window: QtWidgets.QMainWindow):
        icons = {
            "chrome": ":/img/chrome_32.png",
            "edge": ":/img/edge_32.png",
            "brave": ":/img/brave_32.png",
            "bsc": ":/img/bsc_16.png",
            "bpc": ":/img/bpc_16.png",
            "bmc": ":/img/bmc_16.png",
            "aex": ":/img/aex_16.png",
            "cbc": ":/img/cbc_16.png",
        }

        window.resize(860, 680)
        window.setWindowTitle("Chromium 核心浏览器辅助工具")
        window.setWindowIcon(QtGui.QIcon(":/img/chrom_helper_64.png"))

        self.tw_cw = QtWidgets.QTabWidget(window)
        window.setCentralWidget(self.tw_cw)
        self.menu_bar = window.menuBar()

        # ========== Menu Bar =====================
        self.menu_browsers = self.menu_bar.addMenu("浏览器")
        self.act_browser_chrome = QAction(QtGui.QIcon(icons["chrome"]), "Chrome", window)
        self.act_browser_edge = QAction(QtGui.QIcon(icons["edge"]), "Edge", window)
        self.act_browser_brave = QAction(QtGui.QIcon(icons["brave"]), "Brave", window)
        self.act_browser_chrome.setCheckable(True)
        # 保证子窗口的初始化成功
        self.act_browser_chrome.setChecked(True)
        self.act_browser_edge.setCheckable(True)
        self.act_browser_brave.setCheckable(True)
        self.acg_browsers = QActionGroup(window)
        self.acg_browsers.setExclusive(True)
        self.acg_browsers.addAction(self.act_browser_chrome)
        self.acg_browsers.addAction(self.act_browser_edge)
        self.acg_browsers.addAction(self.act_browser_brave)
        self.menu_browsers.addActions([self.act_browser_chrome,
                                       self.act_browser_edge,
                                       self.act_browser_brave])
        self.menu_browsers.addSeparator()
        self.act_update_browser_data = QAction("更新用户数据", window)
        self.menu_browsers.addAction(self.act_update_browser_data)

        self.menu_help = self.menu_bar.addMenu("帮助")
        self.act_settings = QAction("偏好设置", window)
        self.act_clear_log = QAction("清空日志", window)
        self.act_about = QAction("关于", window)
        self.act_about_qt = QAction("关于 Qt", window)
        self.menu_help.addAction(self.act_settings)
        self.menu_help.addSeparator()
        self.menu_help.addAction(self.act_clear_log)
        self.menu_help.addSeparator()
        self.menu_help.addAction(self.act_about)
        self.menu_help.addAction(self.act_about_qt)

        # =============== Central Widget ==============
        browser = self.acg_browsers.checkedAction().text()
        self.wg_check_plugins = WgCheckPlugins(browser, self.tw_cw)
        self.wg_check_bookmarks = WgCheckBookmarks(browser, self.tw_cw)
        self.wg_check_settings = WgCheckSettings(browser, self.tw_cw)
        self.wg_append_extensions = WgAppendExtensions(browser, self.tw_cw)
        self.wg_clear_cache = WgClearCache(browser, self.tw_cw)

        if sys.platform == "win32":
            self.tw_cw.addTab(self.wg_check_plugins, "")
            self.tw_cw.addTab(self.wg_check_bookmarks, "")
            self.tw_cw.addTab(self.wg_check_settings, "")
            self.tw_cw.addTab(self.wg_append_extensions, "")
            self.tw_cw.addTab(self.wg_clear_cache, "")
            self.tw_cw.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
            tbb_tw_cw = self.tw_cw.tabBar()
            lb_tbb_wg_check_plugins = self.create_tab_label(icons["bpc"], "插件", tbb_tw_cw)
            lb_tbb_wg_check_bookmarks = self.create_tab_label(icons["bmc"], "书签", tbb_tw_cw)
            lb_tbb_wg_check_settings = self.create_tab_label(icons["bsc"], "设置", tbb_tw_cw)
            lb_tbb_wg_append_extensions = self.create_tab_label(icons["aex"], "追加插件", tbb_tw_cw)
            lb_tbb_wg_clear_cache = self.create_tab_label(icons["cbc"], "清理缓存", tbb_tw_cw)
            tbb_tw_cw.setTabButton(0, QtWidgets.QTabBar.ButtonPosition.RightSide, lb_tbb_wg_check_plugins)
            tbb_tw_cw.setTabButton(1, QtWidgets.QTabBar.ButtonPosition.RightSide, lb_tbb_wg_check_bookmarks)
            tbb_tw_cw.setTabButton(2, QtWidgets.QTabBar.ButtonPosition.RightSide, lb_tbb_wg_check_settings)
            tbb_tw_cw.setTabButton(3, QtWidgets.QTabBar.ButtonPosition.RightSide, lb_tbb_wg_append_extensions)
            tbb_tw_cw.setTabButton(4, QtWidgets.QTabBar.ButtonPosition.RightSide, lb_tbb_wg_clear_cache)
        else:
            self.tw_cw.addTab(self.wg_check_plugins, QtGui.QIcon(icons["bpc"]), "插件")
            self.tw_cw.addTab(self.wg_check_bookmarks, QtGui.QIcon(icons["bmc"]), "书签")
            self.tw_cw.addTab(self.wg_check_settings, QtGui.QIcon(icons["bsc"]), "设置")
            self.tw_cw.addTab(self.wg_append_extensions, QtGui.QIcon(icons["aex"]), "追加插件")
            self.tw_cw.addTab(self.wg_clear_cache, QtGui.QIcon(icons["cbc"]), "清理缓存")

    @staticmethod
    def create_tab_label(icon: str, title: str, tab_bar: QtWidgets.QTabBar) -> QtWidgets.QLabel:
        lb_i = QtWidgets.QLabel(tab_bar)
        lb_i.setTextFormat(QtCore.Qt.TextFormat.RichText)
        title_wz_span = [f"<span>{s}</span>" for s in title]
        title_span_wz_br = "<br>".join(title_wz_span)
        lb_i.setText(f"""<html><head/><body><span><img src="{icon}"/></span><br>{title_span_wz_br}</body></html>""")
        lb_i.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        return lb_i


class MwChromHelper(QtWidgets.QMainWindow):

    def __init__(self, parent: QtWidgets.QWidget = None,
                 *, org_name: str, app_name: str, version: list[int]):
        super().__init__(parent)
        self.version = version
        self.org_name = org_name
        self.app_name = app_name
        self.ui = UiMwChromHelper(self)

        # ====== Menu Bar =========
        self.ui.act_settings.triggered.connect(self.on_act_settings_triggered)
        self.ui.act_clear_log.triggered.connect(self.on_act_clear_log_triggered)
        self.ui.act_about.triggered.connect(self.on_act_about_triggered)
        self.ui.act_about_qt.triggered.connect(self.on_act_about_qt_triggered)
        self.ui.acg_browsers.triggered.connect(self.on_acg_browsers_triggered)

        self.ui.act_update_browser_data.triggered.connect(self.on_act_update_browser_data_triggered)

        # 为了触发槽函数
        self.ui.act_browser_chrome.trigger()

    def update_browser_data(self, browser: str):
        errmsg = get_errmsg()
        data_path = get_data_path(browser, errmsg=errmsg)
        if errmsg["err"]:
            QtWidgets.QMessageBox.critical(self, "错误", errmsg["msg"])
            return

        profiles_db = get_profiles_db(data_path, errmsg=errmsg)
        if errmsg["err"]:
            QtWidgets.QMessageBox.critical(self, "错误", errmsg["msg"])
            return

        self.ui.wg_check_plugins.on_browser_changed(browser, profiles_db)
        self.ui.wg_check_bookmarks.on_browser_changed(browser, profiles_db)
        self.ui.wg_check_settings.on_browser_changed(browser, profiles_db)
        self.ui.wg_append_extensions.on_browser_changed(browser, profiles_db)
        self.ui.wg_clear_cache.on_browser_changed(browser, profiles_db)

    def on_act_update_browser_data_triggered(self):
        browser = self.ui.acg_browsers.checkedAction().text()
        self.update_browser_data(browser)

    def on_acg_browsers_triggered(self, action: QAction):
        browser = action.text()
        self.update_browser_data(browser)

    def on_act_settings_triggered(self):
        da_cs = DaChromSettings(self)
        da_cs.exec()

    def on_act_clear_log_triggered(self):
        errmsg = get_errmsg()
        app_log_dir = get_log_dir(self.org_name, self.app_name, errmsg=errmsg)
        if errmsg["err"]:
            return
        shutil.rmtree(app_log_dir, ignore_errors=True)

    def on_act_about_triggered(self):
        version = self.version
        about_text = ("Chromium 核心浏览器辅助工具\n\n旨在更方便地对以 Chromium 为核心的浏览器"
                      "进行快速设置、插件检查、书签检查、书签导出、追加插件等操作。\n\n"
                      f"当前版本：v{version[0]}.{version[1]}.{version[2]}，发布日期：{version[-1]}")
        QtWidgets.QMessageBox.about(self, "关于", about_text)

    def on_act_about_qt_triggered(self):
        QtWidgets.QMessageBox.aboutQt(self, "关于 Qt")


def launch(org_name: str, app_name: str, has_log: bool, log_err: str, version: list[int]):
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName(org_name)
    app.setApplicationName(app_name)

    win = MwChromHelper(org_name=org_name, app_name=app_name, version=version)
    win.show()
    if not has_log:
        QtWidgets.QMessageBox.information(win, "提示", f"日志记录未开启：{log_err}")
    if is_compatible:
        return app.exec_()
    else:
        return app.exec()
