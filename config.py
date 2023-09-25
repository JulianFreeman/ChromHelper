# coding: utf8

is_compatible = False

if is_compatible:
    from PySide2 import QtWidgets as _QtWidgets, QtGui as _QtGui, QtCore as _QtCore, QtSql as _QtSql
    from PySide2.QtWidgets import QAction as _QAction, QActionGroup as _QActionGroup
else:
    from PySide6 import QtWidgets as _QtWidgets, QtGui as _QtGui, QtCore as _QtCore, QtSql as _QtSql
    from PySide6.QtGui import QAction as _QAction, QActionGroup as _QActionGroup


version = [2, 2, 1, 20230925]

ORG_NAME = "JnPrograms"
APP_NAME = "ChromHelper"

QtWidgets = _QtWidgets
QtGui = _QtGui
QtCore = _QtCore
QtSql = _QtSql
QAction = _QAction
QActionGroup = _QActionGroup
