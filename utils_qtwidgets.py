# coding: utf8
from config import QtWidgets, QtCore, QtGui


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
