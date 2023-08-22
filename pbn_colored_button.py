# coding: utf8
from config import QtWidgets, QtCore, QtGui


class PbnColoredButton(QtWidgets.QPushButton):

    def __init__(self, base_color: str | QtGui.QColor,
                 obj_name: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.obj_name = obj_name
        self.setObjectName(obj_name)
        self.base_color = QtGui.QColor(base_color)
        self.lighter_color = self.base_color.lighter(125)

        self.white = QtGui.QColor("#FFFFFF")

        self._ss = """
        #{obj_name} {{
            color: {color};
            background-color: {bg_color};
            border: 1px solid {bd_color};
            border-radius: 4px;
        }}

        #{obj_name}:checked {{
            color: {checked_color};
            background-color: {checked_bg_color};
            border: 1px solid {checked_bd_color};
            border-radius: 4px;
        }}
        """

        self._color = self.base_color
        self._bg_color = self.white

        self.anim_color = QtCore.QPropertyAnimation(self, b"color", self)
        self.anim_bg_color = QtCore.QPropertyAnimation(self, b"bg_color", self)
        self.anim_group = QtCore.QParallelAnimationGroup(self)
        self.anim_group.addAnimation(self.anim_color)
        self.anim_group.addAnimation(self.anim_bg_color)

        self._update_stylesheet()

        self.installEventFilter(self)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(75, 21)

    def _update_stylesheet(self):
        self.setStyleSheet(
            self._ss.format(
                color=self._color.name(),
                bg_color=self._bg_color.name(),
                checked_color=self.white.name(),
                bd_color=self.base_color.name(),
                checked_bg_color=self.base_color.name(),
                checked_bd_color=self.base_color.name(),
                obj_name=self.obj_name,
            )
        )

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        match event.type():
            case QtCore.QEvent.Type.HoverEnter:
                self.hover_enter_event()
            case QtCore.QEvent.Type.HoverLeave:
                self.hover_leave_event()

        return False

    def hover_enter_event(self):
        self.anim_group.stop()
        self.anim_color.setDuration(250)
        self.anim_bg_color.setDuration(250)
        self.anim_color.setStartValue(self.base_color)
        self.anim_color.setEndValue(self.white)
        self.anim_bg_color.setStartValue(self.white)
        self.anim_bg_color.setEndValue(self.lighter_color)
        self.anim_group.start()

    def hover_leave_event(self):
        self.anim_group.stop()
        self.anim_color.setDuration(250)
        self.anim_bg_color.setDuration(250)
        self.anim_color.setStartValue(self.white)
        self.anim_color.setEndValue(self.base_color)
        self.anim_bg_color.setStartValue(self.lighter_color)
        self.anim_bg_color.setEndValue(self.white)
        self.anim_group.start()

    def get_color(self):
        return self._color

    def set_color(self, color: QtGui.QColor):
        self._color = color
        self._update_stylesheet()

    def get_bg_color(self):
        return self._bg_color

    def set_bg_color(self, bg_color: QtGui.QColor):
        self._bg_color = bg_color
        self._update_stylesheet()

    color = QtCore.Property(QtGui.QColor, fget=get_color, fset=set_color)
    bg_color = QtCore.Property(QtGui.QColor, fget=get_bg_color, fset=set_bg_color)
