import importlib
import MayaUtils
importlib.reload(MayaUtils)

from MayaUtils import *
from PySide2.QtWidgets import QLabel, QPushButton, QVBoxLayout
import maya.cmds as mc

class ProxyGenerator:
    def __init__(self):
        self.skin = ""
        self.model = ""
        self.jnts = []

    def BuildProxyForSelectedMesh(self):
        model = mc.ls(sl=True)[0]
        if not IsMesh(model):
            print(f"{model} is not a mesh")
            return
        
        self.model = model
        print(f"Found Model{model}")

        modelShape = mc.listRelatives(self.model, s=True)[0]
        skin = GetallConnectionsIn(modelShape, GetUpperStream, IsSkin)
        if not skin:
            print(f"{self.model} is not boumd!")
            return
        
        jnts = GetallConnectionsIn(modelShape, GetUpperStream, IsJoint)
        if not jnts:
            print(f"{self.model} is not boumd with any joints!")
            return
        self.skin = skin[0]
        self.jnts = jnts
        print(f"found model {self.model} with skin {self.skin} and joints: {self.jnts}")

        jntVertDict = self.GenerateJntVertsDict()
        chunks = []
        ctrls = []
        for jnt, verts in jntVertDict.items():
            newChunk = self.CreateProxyModleForJntsAndVerts(jnt, verts)

    def CreateProxyModleForJntsAndVerts(self, jnt, verts):
        if not verts:
            return None
        
        faces = mc.polyListComponentConversion(verts, fromVertex=True, toFace=True)
        faces = mc.ls(faces, fl=True)

        FaceNames = set()
        for face in faces:
            FaceNames.add(face.replace(self.model, ""))

        dup = mc.duplicate(self.model)[0]
        AllDupFaces = mc.ls(f"{dup}.f[*]", fl=True)
        facesToDelete = []
        for dupFace in AllDupFaces:
            if dupFace.replace(dup, "") not in FaceNames:
                facesToDelete.append(dupFace)

        mc.delete(facesToDelete)

        dupeName = self.model + "_" + jnt + "_proxy"
        mc.rename(dup, dupeName)
        return dupeName

            
    def GenerateJntVertsDict(self):
        dict = {}
        for jnt in self.jnts:
            dict[jnt] = []

        verts = mc.ls(f"{self.model}.vtx[*]", fl=True)
        for vert in verts:
            owningJnt = self.GetJntWithMaxInfuence(vert, self.skin)
            dict[owningJnt].append(vert)

        return dict

    def GetJntWithMaxInfuence(self, vert, skin):
        weights = mc.skinPercent(skin, vert, q=True, v=True)
        jnts = mc.skinBindCtx(skin, vert, q=True, t=None)

        maxWeightIndex = 0
        maxWeight = weights[0]
        for i in range(1, len(weights)):
            if weights[i] > maxWeight:
                maxWeight = weights[1]
                maxWeightIndex = 1

        return jnts[maxWeightIndex]

class ProxyGeneratorWidget(MayaWindow):
    def __init__(self):
        super().__init__()
        self.generator = ProxyGenerator()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.masterLayout.addWidget(QLabel("Please select the rigged model, and press the buld button"))
        buildBtn = QPushButton("Build")
        self.masterLayout.addWidget(buildBtn)
        buildBtn.clicked.connect(self.generator.BuildProxyForSelectedMesh)
        self.setWindowTitle("Proxy Generator")
        
    def GetWudgetYbuqyeBane(self):
        return "ProxyGeneratorCL4152025212"
    
ProxyGeneratorWidget().show()