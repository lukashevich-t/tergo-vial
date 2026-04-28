try:
    # print("Importing from PySide2...")
    from PySide2 import QtCore, QtGui, QtWidgets, QtSvg

    try:
        from PySide2 import QtWebEngineWidgets

        HAS_QT_WEBENGINE = True
    except ImportError:
        QtWebEngineWidgets = None
        HAS_QT_WEBENGINE = False
except ImportError:
    try:
        # print("failed. Importing from PySide...")
        from PySide import QtCore, QtGui, QtSvg

        QtWidgets = QtGui
        QtWebEngineWidgets = None
        HAS_QT_WEBENGINE = False
    except ImportError:
        # print("failed. Importing from PySide6...")
        from PySide6 import QtCore, QtGui, QtWidgets, QtSvg, QtSvgWidgets

        if not hasattr(QtSvg, "QSvgWidget"):
            QtSvg.QSvgWidget = QtSvgWidgets.QSvgWidget

        try:
            from PySide6 import QtWebEngineWidgets

            HAS_QT_WEBENGINE = True
        except ImportError:
            QtWebEngineWidgets = None
            HAS_QT_WEBENGINE = False


if not hasattr(QtSvg, "QSvgWidget"):

    class QSvgWidget(QtWidgets.QWidget):
        def __init__(self, path: str = None, parent=None):
            super().__init__(parent)
            self._renderer = QtSvg.QSvgRenderer(self)
            if path:
                self.load(path)

        def renderer(self):
            return self._renderer

        def load(self, data):
            if hasattr(data, "toString"):
                data = data.toString()

            if isinstance(data, str):
                self._renderer.load(data)
            else:
                self._renderer.load(data)
            self.update()

        def sizeHint(self):
            return self._renderer.defaultSize()

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            self._renderer.render(painter, self.rect())

    QtSvg.QSvgWidget = QSvgWidget
