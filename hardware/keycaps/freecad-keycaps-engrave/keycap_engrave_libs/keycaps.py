"""
Различные вспомогательные функции для гравировки кейкапов
"""

import ImportGui
import Part
import FreeCAD
from datetime import datetime
import Part, FreeCADGui
from FreeCAD import Vector
from keycap_types import SurfaceInfo, KeycapLabelInfo, KeycapModelInfo
import Draft
from pathlib import Path
from BOPTools import BOPFeatures
from typing import Any
from keycap_config import gc


def create_document() -> FreeCAD.Document:
    "Создаёт новый документ FreeCAD, возвращает его"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    doc_name = f"Import_{timestamp}"
    doc = FreeCAD.newDocument(doc_name)
    return doc


def import_stepfile(model_path: str, label: str) -> Part.Feature:
    "импортирует step-файл в документ FreeCAD. Возвращает импортированный объект"

    # получим список уже существуюших объектов в документе:
    existing_objects = set(gc.doc.Objects)
    ImportGui.insert(model_path, gc.doc.Name)

    new_objects = [obj for obj in gc.doc.Objects if obj not in existing_objects]
    feature = new_objects[0]
    feature.Label = label

    return feature


def clone_object(freecad_object, label: str):
    "Создаёт клон объекта"
    freecad_doc = freecad_object.Document
    clone = freecad_doc.addObject("Part::Feature", label)
    clone.Shape = Part.getShape(freecad_object, "", needSubElement=False, refine=False)
    return clone


def create_group(label: str = "Group"):
    g = gc.doc.addObject("App::DocumentObjectGroup", "Group")
    g.Label = label
    return g


def move_objects_to_group(
    obj: list[Part.Feature],
    group: FreeCAD.DocumentObjectGroup,
):
    "Перемещает объекты в указанную группу"

    for x in obj:
        group.addObject(x)


def find_upper_faces(keycap: Part.Feature) -> list[SurfaceInfo]:
    "Определяет верхние грани кейкапа. Возвращает список имен таких граней"
    # 1. Определяем границы объекта, чтобы знать, где "верх"
    bbox = keycap.Shape.BoundBox
    z_max = bbox.ZMax
    # Допуск: берем грани, которые находятся в пределах 2-3 мм от самой верхней точки
    z_tolerance = 2.0

    top_face_names: list[SurfaceInfo] = []

    # 2. Перебираем все грани (Faces) объекта
    for i, face in enumerate(keycap.Shape.Faces):
        # Получаем нормаль в центре грани
        # (для криволинейных поверхностей лучше брать нормаль в центре масс или в параметрическом центре)
        surface: Part.GeometrySurface = face.Surface  # type: ignore
        uv = surface.parameter(face.CenterOfMass)
        normal = face.normalAt(uv[0], uv[1])

        # Условие 1: Нормаль смотрит вверх (Z > 0.5, где 1.0 - строго вверх)
        # Условие 2: Центр грани находится близко к верхней точке кейкапа
        if normal.z > 0.7 and face.CenterOfMass.z > (z_max - z_tolerance):
            # Формируем имя грани в формате 'Face144'
            # Внимание: индекс в списке начинается с 0, а в именах FreeCAD с 1
            face_name = f"Face{i+1}"
            top_face_names.append(SurfaceInfo(face, face_name, None, None))
    return top_face_names


def find_average_center(centers: list[Vector | None]) -> Vector:
    "Находим среднюю точку среди всех центров граней для расположения общей нормали"

    avg_center = Vector(0, 0, 0)
    for c in centers:
        if c is not None:
            avg_center = avg_center.add(c)
    avg_center = avg_center.multiply(1.0 / len(centers))
    return avg_center


def find_average_normal(normals: list[Vector | None]) -> Vector:
    "ВЫЧИСЛЕНИЕ ОБЩЕЙ УСРЕДНЕННОЙ НОРМАЛИ"

    # Суммируем все векторы
    avg_normal = Vector(0, 0, 0)
    for n in normals:
        if n is not None:
            avg_normal = avg_normal.add(n)

    avg_normal.normalize()  # Итоговый усредненный вектор
    return avg_normal


def find_face_normals(surfaces: list[SurfaceInfo]) -> None:
    for surface in surfaces:
        # Получаем объект грани по имени
        face: Part.Face = surface.face  # obj.Shape.getElement(face_name)

        # 1. Находим параметры U, V для центра масс грани
        # Это нужно, так как normalAt работает в пространстве параметров поверхности
        uv: tuple[float, float] = face.Surface.parameter(face.CenterOfMass)  # type: ignore

        # 2. Вычисляем нормаль в этой точке
        norm: Vector = face.normalAt(uv[0], uv[1])
        norm.normalize()  # Приводим к единичной длине

        surface.face_normal = norm
        surface.face_center = face.CenterOfMass


def draw_all_normals(
    average_center: Vector,
    average_normal: Vector,
    surfaces: list[SurfaceInfo],
    prefix: str,
) -> list[Part.Feature]:
    "Создать визуальные нормали в документе FreeCad. Возвращает список созданных объектов"

    # Настройки визуализации
    vector_length = 5.0  # Длина стрелки нормали

    result: list[Part.Feature] = []
    for surface in surfaces:
        # 3. Визуализируем нормаль конкретной грани (Синим цветом)
        line = draw_normal(
            surface.face_center,
            surface.face_normal,
            f"N_{prefix}_{surface.name}",
            vector_length,
            color=(0.0, 0.3, 1.0),
        )
        result.append(line)
    # Визуализируем общую нормаль (Красным цветом)
    line = draw_normal(
        average_center,
        average_normal,
        f"N_{prefix}_avg",
        vector_length,
        color=(1.0, 0.0, 0.0),
    )
    result.append(line)
    return result


def draw_normal(
    start_point: Vector,
    direction: Vector,
    label: str,
    vector_length: float,
    color: tuple[float, float, float] = (0.0, 0.0, 1.0),
):
    """Вспомогательная функция для отрисовки линии нормали"""
    end_point = start_point.add(direction.multiply(vector_length))
    line_shape = Part.makeLine(start_point, end_point)
    line_obj = gc.doc.addObject("Part::Feature", label)
    line_obj.Shape = line_shape
    line_obj.ViewObject.LineColor = color
    line_obj.ViewObject.LineWidth = 2
    return line_obj


def create_text(
    text_str: str,
    avg_normal: Vector,
    avg_center: Vector,
    font_path: str = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    text_size: float = 3,
):
    "Создаёт текст на плоскости, которая перпендикулярна указанной нормали"

    # Предполагаем, что avg_normal и avg_center уже вычислены в предыдущем шаге
    # Если нет, раскомментируйте строки ниже для теста:
    # avg_normal = App.Vector(0, 0, 1)
    # avg_center = App.Vector(0, 0, 5)
    # 1. Создаем объект ShapeString
    text_obj = Draft.make_shapestring(text_str, font_path, text_size)
    text_obj.Label = f"ShapeString_{text_str}"

    # Вызываем пересчет, чтобы FreeCAD вычислил геометрию и BoundBox
    gc.doc.recompute()

    # 2. Центрируем текст локально
    # По умолчанию точка вставки текста (0,0,0) — это левый нижний угол.
    # Нам нужно сдвинуть его так, чтобы (0,0,0) был центром буквы.
    bbox = text_obj.Shape.BoundBox
    center_offset: Vector = Vector(
        -(bbox.XMax + bbox.XMin) / 2, -(bbox.YMax + bbox.YMin) / 2, 0
    )
    # Применяем локальное смещение
    text_obj.Placement.Base = center_offset

    # 3. Вычисляем ориентацию (Rotation)
    # Нам нужно повернуть стандартную ось Z (0,0,1) так, чтобы она совпала с avg_normal
    standard_z = FreeCAD.Vector(0, 0, 1)
    rotation = FreeCAD.Rotation(standard_z, avg_normal)

    # 4. Устанавливаем итоговое положение (Placement)
    # Мы хотим, чтобы текст находился в avg_center, но был приподнят над поверхностью
    # (например, на 0.1 мм), чтобы избежать ошибок наложения поверхностей при булевых операциях.
    offset_height = 2
    final_pos = avg_center.add(avg_normal.multiply(offset_height))

    # Создаем итоговый Placement: (Позиция, Поворот, Центр вращения)
    # Важно: мы умножаем новый Placement на старый, чтобы сохранить локальное центрирование
    final_placement = FreeCAD.Placement(final_pos, rotation)
    text_obj.Placement = final_placement.multiply(text_obj.Placement)

    gc.doc.recompute()
    return text_obj


def extrude_text(text_obj, depth: float, vector: Vector) -> Part.Feature:
    "Делает текст объёмным на указанную глубину"
    extrusion = gc.doc.addObject("Part::Extrusion", "Text3D")
    extrusion.Base = text_obj

    vec: Vector = Vector(vector.x, vector.y, vector.z)
    vec.multiply(-depth / vec.Length)
    extrusion.Dir = vec  # Направление и длина выдавливания
    extrusion.Solid = True
    gc.doc.recompute()
    return extrusion


def export(objects: list[Part.Feature]) -> None:
    "Экспортирует объекты по списку в step-файлы в указанной директории"
    Path(gc.OUT_DIR).mkdir(exist_ok=True, parents=True)
    for object in objects:
        object.Refine = True
    gc.doc.recompute()
    for object in objects:
        full_path: str = f"{gc.OUT_DIR}/{object.Label}.step"
        ImportGui.export([object], full_path)
        # if hasattr(ImportGui, "exportOptions"):
        #     print("exporting with options")
        #     options = ImportGui.exportOptions(full_path)
        #     ImportGui.export([object], full_path, options)
        # else:
        #     print("exporting without options")
        #     ImportGui.export([object], full_path)


def engrave_single_keycap(key: KeycapLabelInfo) -> Part.Feature:
    def extract_needed_labels() -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        result.append(
            {
                "label": key.label_main,
            }
        )
        return result

    keycap_model: KeycapModelInfo = key.keycap_model
    keycap_template: Part.Feature = keycap_model.template
    label_main: str = key.label_main

    # создадим группу
    group = create_group(f"group_{label_main}")

    # скопируем кейкап
    keycap = clone_object(keycap_template, f"keycap_{label_main}")
    move_objects_to_group([keycap], group)

    engrave_target = keycap

    # create list of requred labels along with their positions:
    labels: list[dict] = extract_needed_labels()

    # создадим facebinder
    selection = [(keycap_template, tuple([x.name for x in keycap_model.surfaces]))]
    fb: Part.Feature = Draft.make_facebinder(selection, f"fb_{label_main}")
    # Draft.autogroup(fb)
    move_objects_to_group([fb], group)

    # создать текст:
    text = create_text(
        label_main, keycap_model.normal, keycap_model.center, gc.FONT_FILE, 3
    )
    move_objects_to_group([text], group)

    extruded_text: Part.Feature = extrude_text(text, 30, keycap_model.normal)
    extruded_text.Label = f"Text3D_{label_main}"
    move_objects_to_group([extruded_text], group)

    # пересечение facebinder с выдавленной надписью:

    bp = BOPFeatures.BOPFeatures(gc.doc)
    projected_text: Part.Feature = bp.make_multi_common(
        [
            fb.Name,
            extruded_text.Name,
        ]
    )
    move_objects_to_group([projected_text], group)

    # Выдавливаем полученный текст на изогнутой поверхностью:
    extruded_text2 = gc.doc.addObject("Part::Extrusion", f"Text3DCurved_{label_main}")
    extruded_text2.Base = projected_text
    extruded_text2.Dir = FreeCAD.Vector(
        0, 0, -gc.ENGRAVE_DEPTH
    )  # Направление и длина выдавливания
    extruded_text2.Solid = True
    move_objects_to_group([extruded_text2], group)

    # Вычитаем полученный объёмный текст из оригинального кейкапа (Part: Cut):
    bp = BOPFeatures.BOPFeatures(gc.doc)
    final_keycap = bp.make_cut([keycap.Name, extruded_text2.Name])
    final_keycap.Label = f"final_keycap_{label_main}"
    # kc.move_objects_to_group([final_keycap], group)
    gc.doc.recompute()
    return final_keycap
