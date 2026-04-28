from QtCompat import QtCore, QtGui, QtWidgets, QtSvg, QtWebEngineWidgets
import FreeCADGui as Gui
import FreeCAD
from keycap_types import SurfaceInfo, KeycapModelInfo


# Define the Dialog Class
class SimpleDialog(QtGui.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Dialog")
        self.resize(300, 100)

        # Add a widget
        self.layout = QtGui.QVBoxLayout()
        self.label = QtGui.QLabel("Hello from FreeCAD 1.1")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)


def test_dialog():
    print("test_dialog")
    # Create and Show the Dialog
    # Keep a reference to the dialog to prevent garbage collection
    form = SimpleDialog()
    form.show()


def hide_all(doc: FreeCAD.Document | None = FreeCAD.ActiveDocument):
    "Hide all objects in freecad document"
    if doc is None:
        return
    for obj in doc.Objects:
        show_object(obj, False)
    # if hasattr(obj, "ViewObject") and obj.ViewObject is not None:
    #     obj.ViewObject.Visibility = False


def show_object(obj, visibility: bool = True):
    "Показывает или прячет объект"
    # Проверяем наличие ViewObject (у некоторых служебных объектов его может не быть)
    if hasattr(obj, "ViewObject") and obj.ViewObject is not None:
        obj.ViewObject.Visibility = visibility


# **********************************************************
# Выбор граней через GUI: вариант 1, только 1 вызов
# **********************************************************
# class FaceSelectionTask:
#     def __init__(self):
#         # Создаем простой виджет с текстом
#         self.form = QtWidgets.QWidget()
#         layout = QtWidgets.QVBoxLayout(self.form)
#         label = QtWidgets.QLabel(
#             "Выберите грани на кейкапе.\nЗатем нажмите 'OK' вверху."
#         )
#         layout.addWidget(label)

#     def accept(self):
#         # Этот метод вызывается при нажатии кнопки "OK" в панели задач
#         selection = Gui.Selection.getSelectionEx()

#         if not selection:
#             FreeCAD.Console.PrintWarning("Ничего не выбрано!\n")
#             return False  # Не закрывать панель

#         # Логика обработки выбора (ваша автоматизация)
#         process_selection(selection)

#         Gui.Control.closeDialog()
#         return True

#     def reject(self):
#         # При нажатии "Cancel"
#         Gui.Control.closeDialog()
#         return True


# def process_selection(selection):
#     # Здесь ваш код, который берет выбранные грани и делает гравировку
#     print(f"selection: {selection}, len: {len(selection)}")
#     for sel in selection:
#         obj = sel.Object
#         faces = sel.SubElementNames
#         print(f"Объект: {obj.Name}, Грани: {faces}")
#         # Далее ваш код с FaceBinder, Extrude и т.д.
# # Запуск панели
# panel = FaceSelectionTask()
# Gui.Control.showDialog(panel)
# **********************************************************
# /// Выбор граней через GUI: вариант 1, только 1 вызов
# **********************************************************


# **********************************************************
# Выбор граней через GUI: вариант 2, последовательный
# **********************************************************
class SequentialSelectionTask:

    def __init__(self, items: list[KeycapModelInfo], callback):
        self.items = items  # Список имен или объектов
        self.current_index = 0
        self.results = {}
        self.callback = callback

        # Создаем UI
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.form)
        self.label = QtWidgets.QLabel()
        layout.addWidget(self.label)
        self.update_label()

    def update_label(self):
        current_item = self.items[self.current_index]
        show_object(current_item.template, True)
        Gui.runCommand("Std_ViewGroup", 2)
        Gui.SendMsgToActiveView("ViewFit")
        self.label.setText(
            f"Шаг {self.current_index + 1} из {len(self.items)}\n"
            f"Выберите поверхности для:\n{current_item.path}"
        )

    def accept(self):
        """Вызывается при нажатии кнопки OK (Далее)"""
        # Сохраняем текущий выбор
        sel = Gui.Selection.getSelectionEx()
        current_item = self.items[self.current_index]
        self.results[current_item] = sel
        current_item.surfaces = []
        if sel:
            for i in range(0, len(sel[0].SubElementNames)):
                current_item.surfaces.append(
                    SurfaceInfo(sel[0].SubObjects[i], sel[0].SubElementNames[i])
                )

        # print(f"subObjects: {sel[0].SubObjects}")
        # print(f"current_item.faces {current_item.faces}")
        # print(dir(sel))
        # print(dir(sel[0]))
        # sel0 = sel[0]
        # print(f"sel0.Object: {sel0.Object}")
        # print(f"sel0.DocumentName: {sel0.DocumentName}")
        # print(f"sel0.FullName: {sel0.FullName}")
        # print(f"sel0.ObjectName: {sel0.ObjectName}")
        Gui.Selection.clearSelection()

        # Переходим к следующему или завершаем
        show_object(current_item.template, False)
        self.current_index += 1
        if self.current_index < len(self.items):
            self.update_label()
            return False  # Не закрывать панель задач
        else:
            self.finish()
            return True  # Закрыть панель

    def finish(self):
        if self.callback:
            self.callback(self.items)


# Запуск
# panel = kcgui.SequentialSelectionTask(["Верхняя панель", "Боковая грань", "Логотип"])
# Gui.Control.showDialog(panel)
# **********************************************************
# /// Выбор граней через GUI: вариант 2, последовательный
# **********************************************************
