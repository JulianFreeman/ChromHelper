# coding: utf8

is_compatible = False

if is_compatible:
    from PySide2 import QtWidgets as _QtWidgets, QtGui as _QtGui, QtCore as _QtCore
    from PySide2.QtWidgets import QAction as _QAction, QActionGroup as _QActionGroup
else:
    from PySide6 import QtWidgets as _QtWidgets, QtGui as _QtGui, QtCore as _QtCore
    from PySide6.QtGui import QAction as _QAction, QActionGroup as _QActionGroup


version = [2, 0, 0, 20230821]

ORG_NAME = "JnPrograms"
APP_NAME = "ChromHelper"

QtWidgets = _QtWidgets
QtGui = _QtGui
QtCore = _QtCore
QAction = _QAction
QActionGroup = _QActionGroup
