from FreeCAD import Vector
import Part


class SurfaceInfo:
    """Storage of face information"""

    face: Part.Face
    """FreeCAD's face object"""

    name: str
    """name of surface"""

    face_normal: Vector
    """normal to the face in it's center of mass"""

    face_center: Vector
    """center of mass for the face"""

    def __init__(
        self,
        face: Part.Face,
        name: str,
        norm: Vector = Vector(),
        center: Vector = Vector(),
    ):
        self.face = face
        self.name = name
        self.face_normal = norm
        self.face_center = center

    def __str__(self) -> str:
        return f"{self.__class__}: name={self.name}, face={self.face}, face_normal={self.face_normal}, face_center={self.face_center}"

    def __repr__(self) -> str:
        return self.__str__()


class KeycapModelInfo:
    """Info about keycap's 3d-model"""

    path: str
    """Path to keycap's .step file1"""

    name: str
    """Name of keycap for use in Freecad interface. Initially derived from the path"""

    normal: Vector
    """Average normal to keycap's top surface"""

    center: Vector
    """detected center of keycap's top surface"""

    center_correction = Vector(0, 0, 0)
    """manual correction for automatically detected center of mass"""

    template: Part.Feature
    """FreeCad's Part.Feature object. Filled after loading the model from .step file"""

    surfaces: list[SurfaceInfo] = []
    """List of the faces that make up the top face of the keycap"""

    def __init__(
        self,
        path: str,
        normal: Vector = Vector(0, 0, 0),
        center: Vector = Vector(0, 0, 0),
        center_correction: Vector = Vector(0, 0, 0),
    ):
        self.path = path
        self.name = path.replace("\\", "/").split("/")[-1]
        self.normal = normal
        self.center = center
        self.center_correction = center_correction

    def __repr__(self) -> str:
        return f"""
{self.__class__}: name={self.name},
path={self.path},
face_normal={self.normal},
center={self.center}
surfaces={self.surfaces}        
        """


class KeycapLabelInfo:
    "Contains info about labels on keycap and link to keycap 3d-model info"

    keycap_model: KeycapModelInfo
    "Main keycap label (center)"
    label_main: str
    "Label for top-left side"
    label_tl: str
    "Label for top-right side"
    label_tr: str
    "Label for bottom-left side"
    label_bl: str
    "Label for bottom-right side"
    label_br: str

    def __init__(
        self,
        keycap_model: KeycapModelInfo,
        label_main: str,
        label_tl: str = "",
        label_tr: str = "",
        label_bl: str = "",
        label_br: str = "",
    ):
        """
        Constructor

        Args:
            keycap_model(KeycapModelInfo): Reference for keycap geometry (3d-model, normals, center of keycap etc)
            label_main: Main keycap label (center)
            label_tl(str): Label for top-left side
            label_tr(str): Label for top-right side
            label_bl(str): Label for bottom-left side
            label_br(str): Label for bottom-right side

        Returns:
            KeycapLabelInfo: constructed object
        """
        self.keycap_model = keycap_model
        self.label_main = label_main
        self.label_tl = label_tl
        self.label_tr = label_tr
        self.label_bl = label_bl
        self.label_br = label_br
