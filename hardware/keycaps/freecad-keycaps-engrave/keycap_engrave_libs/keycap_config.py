import FreeCAD
from keycap_types import KeycapLabelInfo


class KeycapSettings:
    """Class for storing global constants and variables"""

    FONT_FILE: str = None  # type: ignore
    KEYCAP_DIR: str = None  # type: ignore
    OUT_DIR: str = None  # type: ignore
    ENGRAVE_DEPTH: float = 0.2
    KEYS: list[KeycapLabelInfo] = []
    MAIN_LABEL_SIZE: float = 3
    OTHER_LABEL_SIZE: float = 2
    doc: FreeCAD.Document = None  # type: ignore

    def __repr__(self):
        return f"{self.__class__}: {dir(self)}"


# global config
gc = KeycapSettings()
