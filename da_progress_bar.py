# coding: utf8
from config import QtWidgets, QtCore


class DaProgressBar(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("删除书签进度")
        self.resize(400, 30)
        self.vly_m = QtWidgets.QVBoxLayout()
        self.setLayout(self.vly_m)

        self.pgb_m = QtWidgets.QProgressBar(self)
        self.pgb_m.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.vly_m.addWidget(self.pgb_m)
