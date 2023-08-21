# coding: utf8
from config import QtWidgets, QtCore
from utils_qtwidgets import PushButtonWithId


class DaChromSettings(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.resize(540, 140)
        self.setWindowTitle("设置")

        self.vly_m = QtWidgets.QVBoxLayout()
        self.setLayout(self.vly_m)

        self.gbx_exec = QtWidgets.QGroupBox("执行文件路径", self)
        self.vly_m.addWidget(self.gbx_exec)

        self.gly_gbx_exec = QtWidgets.QGridLayout()
        self.gbx_exec.setLayout(self.gly_gbx_exec)

        self.lb_exec_chrome = QtWidgets.QLabel("Chrome", self)
        self.lb_exec_edge = QtWidgets.QLabel("Edge", self)
        self.lb_exec_brave = QtWidgets.QLabel("Brave", self)
        self.lne_exec_chrome = QtWidgets.QLineEdit(self)
        self.lne_exec_edge = QtWidgets.QLineEdit(self)
        self.lne_exec_brave = QtWidgets.QLineEdit(self)
        self.pbn_exec_chrome = PushButtonWithId("ChromeExec", self, "选择")
        self.pbn_exec_edge = PushButtonWithId("EdgeExec", self, "选择")
        self.pbn_exec_brave = PushButtonWithId("BraveExec", self, "选择")

        self.gly_gbx_exec.addWidget(self.lb_exec_chrome, 0, 0)
        self.gly_gbx_exec.addWidget(self.lb_exec_edge, 1, 0)
        self.gly_gbx_exec.addWidget(self.lb_exec_brave, 2, 0)
        self.gly_gbx_exec.addWidget(self.lne_exec_chrome, 0, 1)
        self.gly_gbx_exec.addWidget(self.lne_exec_edge, 1, 1)
        self.gly_gbx_exec.addWidget(self.lne_exec_brave, 2, 1)
        self.gly_gbx_exec.addWidget(self.pbn_exec_chrome, 0, 2)
        self.gly_gbx_exec.addWidget(self.pbn_exec_edge, 1, 2)
        self.gly_gbx_exec.addWidget(self.pbn_exec_brave, 2, 2)

        self.gbx_data = QtWidgets.QGroupBox("用户数据路径", self)
        self.vly_m.addWidget(self.gbx_data)

        self.gly_gbx_data = QtWidgets.QGridLayout()
        self.gbx_data.setLayout(self.gly_gbx_data)

        self.lb_data_chrome = QtWidgets.QLabel("Chrome", self)
        self.lb_data_edge = QtWidgets.QLabel("Edge", self)
        self.lb_data_brave = QtWidgets.QLabel("Brave", self)
        self.lne_data_chrome = QtWidgets.QLineEdit(self)
        self.lne_data_edge = QtWidgets.QLineEdit(self)
        self.lne_data_brave = QtWidgets.QLineEdit(self)
        self.pbn_data_chrome = PushButtonWithId("ChromeData", self, "选择")
        self.pbn_data_edge = PushButtonWithId("EdgeData", self, "选择")
        self.pbn_data_brave = PushButtonWithId("BraveData", self, "选择")

        self.gly_gbx_data.addWidget(self.lb_data_chrome, 0, 0)
        self.gly_gbx_data.addWidget(self.lb_data_edge, 1, 0)
        self.gly_gbx_data.addWidget(self.lb_data_brave, 2, 0)
        self.gly_gbx_data.addWidget(self.lne_data_chrome, 0, 1)
        self.gly_gbx_data.addWidget(self.lne_data_edge, 1, 1)
        self.gly_gbx_data.addWidget(self.lne_data_brave, 2, 1)
        self.gly_gbx_data.addWidget(self.pbn_data_chrome, 0, 2)
        self.gly_gbx_data.addWidget(self.pbn_data_edge, 1, 2)
        self.gly_gbx_data.addWidget(self.pbn_data_brave, 2, 2)

        self.gbx_others = QtWidgets.QGroupBox("其他", self)
        self.vly_m.addWidget(self.gbx_others)

        self.gly_gbx_others = QtWidgets.QGridLayout()
        self.gbx_others.setLayout(self.gly_gbx_others)

        self.lb_plg_db = QtWidgets.QLabel("预存库", self)
        self.lne_plg_db = QtWidgets.QLineEdit(self)
        self.pbn_plg_db = QtWidgets.QPushButton("选择", self)

        self.gly_gbx_others.addWidget(self.lb_plg_db, 0, 0)
        self.gly_gbx_others.addWidget(self.lne_plg_db, 0, 1)
        self.gly_gbx_others.addWidget(self.pbn_plg_db, 0, 2)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.pbn_save = QtWidgets.QPushButton("保存", self)
        self.pbn_remove = QtWidgets.QPushButton("清除", self)
        self.pbn_cancel = QtWidgets.QPushButton("取消", self)

        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_save)
        self.hly_bot.addWidget(self.pbn_remove)
        self.hly_bot.addWidget(self.pbn_cancel)

        self.vly_m.addLayout(self.hly_bot)
        self.vly_m.addStretch(1)

        self.pbn_save.clicked.connect(self.on_pbn_save_clicked)
        self.pbn_remove.clicked.connect(self.on_pbn_remove_clicked)
        self.pbn_cancel.clicked.connect(self.on_pbn_cancel_clicked)

        self.pbn_exec_chrome.clicked_with_id.connect(self.on_pbn_exec_n_clicked_with_id)
        self.pbn_exec_edge.clicked_with_id.connect(self.on_pbn_exec_n_clicked_with_id)
        self.pbn_exec_brave.clicked_with_id.connect(self.on_pbn_exec_n_clicked_with_id)

        self.pbn_data_chrome.clicked_with_id.connect(self.on_pbn_data_n_clicked_with_id)
        self.pbn_data_edge.clicked_with_id.connect(self.on_pbn_data_n_clicked_with_id)
        self.pbn_data_brave.clicked_with_id.connect(self.on_pbn_data_n_clicked_with_id)

        self.pbn_plg_db.clicked.connect(self.on_pbn_plg_db_clicked)

        self._read_settings()

    def _read_settings(self):
        us = QtCore.QSettings()
        chrome_exec = us.value("chrome_exec", "")  # type: str
        edge_exec = us.value("edge_exec", "")  # type: str
        brave_exec = us.value("brave_exec", "")  # type: str

        chrome_data = us.value("chrome_data", "")  # type: str
        edge_data = us.value("edge_data", "")  # type: str
        brave_data = us.value("brave_data", "")  # type: str

        plg_db = us.value("plg_db", "")  # type: str

        self.lne_exec_chrome.setText(chrome_exec)
        self.lne_exec_edge.setText(edge_exec)
        self.lne_exec_brave.setText(brave_exec)

        self.lne_data_chrome.setText(chrome_data)
        self.lne_data_edge.setText(edge_data)
        self.lne_data_brave.setText(brave_data)

        self.lne_plg_db.setText(plg_db)

    def on_pbn_exec_n_clicked_with_id(self, ids: str):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, f"选择 {ids}")
        if len(filename) == 0:
            return
        match ids:
            case "ChromeExec":
                self.lne_exec_chrome.setText(filename)
            case "EdgeExec":
                self.lne_exec_edge.setText(filename)
            case "BraveExec":
                self.lne_exec_brave.setText(filename)

    def on_pbn_data_n_clicked_with_id(self, ids: str):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, f"选择 {ids}")
        if len(dirname) == 0:
            return
        match ids:
            case "ChromeData":
                self.lne_data_chrome.setText(dirname)
            case "EdgeData":
                self.lne_data_edge.setText(dirname)
            case "BraveData":
                self.lne_data_brave.setText(dirname)

    def on_pbn_plg_db_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择预存库文件",
                                                            filter="JSON 文件 (*.json);;所有文件(*)")
        if len(filename) == 0:
            return
        self.lne_plg_db.setText(filename)

    def on_pbn_save_clicked(self):
        us = QtCore.QSettings()
        us.setValue("chrome_exec", self.lne_exec_chrome.text())
        us.setValue("edge_exec", self.lne_exec_edge.text())
        us.setValue("brave_exec", self.lne_exec_brave.text())

        us.setValue("chrome_data", self.lne_data_chrome.text())
        us.setValue("edge_data", self.lne_data_edge.text())
        us.setValue("brave_data", self.lne_data_brave.text())

        us.setValue("plg_db", self.lne_plg_db.text())
        self.accept()

    def on_pbn_remove_clicked(self):
        us = QtCore.QSettings()
        us.clear()
        self.accept()

    def on_pbn_cancel_clicked(self):
        self.reject()
