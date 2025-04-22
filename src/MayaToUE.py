from MayaUtils import *
from PySide2.QtGui import QIntValidator, QRegExpValidator
from PySide2.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QVBoxLayout
import maya.cmds as mc

def TryAction(actionFunc):
    def wrapper(*args, **kwargs):
        try:
            actionFunc(*args, **kwargs)
        except Exception as e:
            QMessageBox().critical(None, "Error", f"{e}")
    return wrapper

class AnimClip:
    def __init__(self):
        self.subfix = ""
        self.frameMin = mc.playbackOptions(q=True, min=True)
        self.frameMax = mc.playbackOptions(q=True, max=True)
        self.shouldExport = True

class MayaToUE:
    def __init__(self):
        self.rootJnt = ""
        self.models = set()
        self.animations : list[AnimClip] = []
        self.fileName = ""
        self.saveDif = ""

    def AddSelectedMeshes(self):
        selection = mc.ls(sl=True)

        if not selection:
            raise Exception("No Mesh Seleted, please select all meshes of your rig")
        
        meshes = []
        for sel in selection:
            if IsMesh(sel):
                self.append(sel)
        if len(meshes) == 0:
            raise Exception("No Mesh Seleted, please select all meshes of your rig")
        
        self.models = meshes

    def AddRootJoint(self):
        if not self.rootJnt:
            raise Exception("No Root Joint Assigned, please set the root joint of your rig first")
        
        if mc.objExists(self.rootJnt):
            currentRootPos = mc.xform(self.rootJnt, q=True, ws=True, t=True)
            if currentRootPos[0] == 0 and currentRootPos[1] == 0 and currentRootPos[2] == 0:
                    raise Exception("Current rot joint is at origin already, no need to make a new one")
            
        self.meshList = QListWidget()
        self.masterlayout.addWidget(self.meshList)
        self.meshList.setMaximumHeight(100)

        addMeshesBtn = QPushButton("Add Meshes")
        addMeshesBtn.clicked.connect(self.AddMeshesBtnClicked)
        self.masterlayout.addWidget(addMeshesBtn)
        
    @TryAction
    def AddMeshesBtnClicked(self):
        self.mayaToUE.AddSelectedMeshes()
        self.meshList.clear()
        self.meshList.addItems(self.mayaToUE.models)
            
        mc.select(cl=True)
        rootJntName = self.rootJnt + "_root"
        mc.joint(n=rootJntName)
        mc.parent(self.rootJnt, rootJntName)
        self.rootJnt = rootJntName
            

    def setSelectedJntAsRoot(self):
        selection = mc.ls(sl=True, type="joint")
        if not selection:
            raise Exception("Wrong Selection please select the roon joint of the rig")
        
        self.root = selection[0]

class AnimClipWidget(MayaWindow):
    def __init__(self, animClip: AnimClip):
        super().__init__()
        self.animClip = animClip
        self.masterlayout = QHBoxLayout()
        self.setLayout(self.masterlayout)

        shouldExportCheckBox = QCheckBox()
        shouldExportCheckBox.setChecked(self.animClip.shouldExport)
        self.masterlayout.addWidget(shouldExportCheckBox)
        shouldExportCheckBox.toggled.connect(self.ShouldExportCheckboxToggled)

        subfixLable = QLabel("SubFix: ")
        self.masterlayout.addWidget(subfixLable)

        subfixLineEdit = QLineEdit()
        subfixLineEdit.setValidator(QRegExpValidator("\w+"))
        subfixLineEdit.setText(self.animClip.subfix)
        subfixLineEdit.textChanged.connect(self.SubfixTextChange)
        self.masterlayout.addWidget(subfixLineEdit)

        minFrameLabel = QLabel("Min: ")
        self.masterlayout.addWidget(minFrameLabel)
        minFrameLibelEdit = QLineEdit()
        minFrameLibelEdit.setValidator(QIntValidator())
        minFrameLibelEdit.setText(str(int(self.animClip.frameMin)))
        minFrameLibelEdit.textChanged.connect(self.minFrameChange)
        self.masterlayout.addWidget(minFrameLibelEdit)

        maxFrameLabel = QLabel("Max: ")
        self.masterlayout.addWidget(maxFrameLabel)
        maxFrameLibelEdit = QLineEdit()
        maxFrameLibelEdit.setValidator(QIntValidator())
        maxFrameLibelEdit.setText(str(int(self.animClip.frameMax)))
        maxFrameLibelEdit.textChanged.connect(self.maxFrameChange)
        self.masterlayout.addWidget(maxFrameLibelEdit)

        setRangeBtn = QPushButton("[-]")
        setRangeBtn.clicked.connect(self.setRangeBtnClicked)
        self.masterlayout.addWidget(setRangeBtn)

    def setRangeBtnClicked(self):
        mc.playbackOptions(e=True, min= self.animClip.frameMin, max = self.animClip.frameMax)
        mc.playbackOptions(e=True, ast= self.animClip.frameMin, aet = self.animClip.frameMax)

    def maxFrameChange(self, newVal):
        self.animClip.frameMax = int(newVal)

    def minFrameChange(self, newVal):
        self.animClip.frameMin = int(newVal)

    def SubfixTextChange(self, newText):
        self.animClip.subfix = newText

    def ShouldExportCheckboxToggled(self):
        self.animClip.shouldExport = not self.animClip.shouldExport

class MayaToUEWidget(MayaWindow):
    def GetWidgetUniqueName(self):
        return "MayaToUEWidgetJL4172025407"
    
    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()

        self.setWindowTitle("Maya To UE")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.rootjntText = QLineEdit()
        self.rootjntText.setEnabled(False)
        self.masterLayout.addWidget(self.rootjntText)

        setSelectedASRootJntBtn = QPushButton("Set Root Joint")
        setSelectedASRootJntBtn.clicked.connect(self.setSelectedAsRootJntBtnClicked)
        self.masterLayout.addWidget(setSelectedASRootJntBtn)

        addRootJntBtn = QPushButton("Add Root Joint")
        addRootJntBtn.clicked.connect(self.AddRootJntBtnClicked)
        self.masterLayout.addWidget(addRootJntBtn)

    @TryAction
    def AddRootJntBtnClicked(self):
        self.mayaToUE.AddRootJnt()
        self.rootjntText.setText(self.mayaToUE.rootJnt)
        
    @TryAction
    def setSelectedAsRootJntBtnClicked(self):
            self.mayaToUE.setSelectedJntAsRoot
            self.rootjntText.setText(self.mayaToUE.rootJnt)

#MayaToUEWidget().show()
AnimClipWidget(AnimClip()).show()