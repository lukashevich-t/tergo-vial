import FreeCAD
from keycap_types import KeycapLabelInfo


class KeycapSettings:
    """Class for storing global constants and variables"""

    FONT_FILE: str = None  # type: ignore
    KEYCAP_DIR: str = None  # type: ignore
    OUT_DIR: str = None  # type: ignore
    ENGRAVE_DEPTH: float = 0.2
    KEYS: list[KeycapLabelInfo] = []
    MAIN_LABEL_SIZE: float = 4.5
    OTHER_LABEL_SIZE: float = 3
    doc: FreeCAD.Document = None  # type: ignore
    LABEL_HRZ_OFFSET: float = 3
    """Horizontal offset (to the left and to the right) from the center of main label to the centers of secondary labels"""
    LABEL_VERT_OFFSET: float = 3.5
    """Vertical offset (to up and to down) from the center of main label to the centers of secondary labels"""

    def __repr__(self):
        return f"{self.__class__}: {dir(self)}"


# global config
gc = KeycapSettings()
