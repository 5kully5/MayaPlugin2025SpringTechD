import importlib
import MayaUtils
importlib.reload(MayaUtils)

from MayaUtils import MayaWindow
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QColorDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSlider, QVBoxLayout, QWidget # type: ignore
from PySide2.QtCore import Qt, Signal
from maya.OpenMaya import MVector
import maya.cmds as mc
import maya.mel as mel

class LimbRigger:
    def __init__(self):
        self.root = ""
        self.mid = ""
        self.end = ""
        self.controllerSize = 5
        self.ControllerColor = [0,0,0]
        #getting limb and controller name and size

    def FindJntsBasedOnSelections(self):
        try:
            self.root = mc.ls(sl=True, type="joint")[0]
            self.mid = mc.listRelatives(self.root, c=True, type="joint")[0]
            self.end = mc.listRelatives(self.mid, c=True, type="joint")[0]
        except Exception as e:
            raise Exception("Wrong Selection, please selection the first joint of the limb")
        #calling instances in which to tell the user if they did everyting correctly or not
        

    def CreateFKControllerForJnts(self, jntName):
        ctrlName = "ac_l_fk_" + jntName
        ctrlGrpName = ctrlName + "_grp"
        mc.circle(name = ctrlName, radius = self.controllerSize, normal = (1,0,0))
        mc.group(ctrlName, n=ctrlName)
        mc.matchTransform(ctrlGrpName, jntName)
        mc.orientConstraint(ctrlName, jntName)
        return ctrlName, ctrlGrpName
        #making controller and making the grp and name


    def CreateBoxController(self, name):
        #copy the mel code you get from maya and import it into here after name
        mel.eval(f"curve -n {name} -d 1 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p 0.5 -0.5 0.5 -p 0.5 0.5 0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 -0.5 -0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 ;")
        mc.scale(self.controllerSize, self.controllerSize, self.controllerSize, name)
        mc.makeIdentity(name, apply=True) #freeze tranformation
        grpName = name + "_grp"
        mc.group(name, n = grpName)
        return name, grpName
    
    def CreatePlusController(self, name):
        #paste mel code for plus controller shape
        mel.eval(f"curve -n {name} -d 1 -p 3.998356 0 3.001427 -p 3.998356 0 3.001427 -p 3.998356 0 3.001427 -p 3.998356 0 3.001427 -p 5.000584 0 3.007831 -p 5.000584 0 3.007831 -p 5.000584 0 3.007831 -p 5.001627 0 4.014998 -p 6.027885 0 4.001211 -p 6.012511 0 4.997947 -p 5.012602 0 5.034713 -p 5.02592 0 5.999881 -p 3.989075 0 6.000681 -p 3.994619 0 5.003642 -p 2.996706 0 5.029282 -p 3.009883 0 3.989389 -p 3.988429 0 4.00692 -p 3.998356 0 3.001427 -p 5.000584 0 3.007831 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 ; ")
        grpName = name + "_grp"
        mc.group(name, n = grpName)
        return name, grpName
    
    def GetObjectLocation(self, ObjectName):
        x, y, z = mc.xform(ObjectName, q=True, ws=True, t=True) #quires the translation of the object in world space
        return MVector(x, y, z)
    
    
    def PrintMVector(self, vector):
        print(f"<{vector.x}, {vector.y}, {vector.z}>")

    def RigLimb(self):
        rootCtrl, rootCtrlGrp = self.CreateFKControllerForJnts(self.root)
        midCtrl, midCtrlGrp = self.CreateFKControllerForJnts(self.root)
        endCtrl, endCtrlGrp = self.CreateFKControllerForJnts(self.root)

        mc.parent(midCtrlGrp, rootCtrl)
        mc.parent(endCtrlGrp, midCtrl)
        #making the bones link to the controller

        ikEndCtrl = "ac_ik_" + self.end
        ikEndCtrl, ikEndCtrlGrp = self.CreateBoxController(ikEndCtrl)
        mc.matchTransformation(ikEndCtrlGrp, self.end)
        endOrientConstraint = mc.orientConstraint(ikEndCtrl, self.end)[0]

        rootJntLoc = self.GetObjectLocation(self.root)
        self.PrintMVector(rootJntLoc)

        ikHandleName = "ikHandle_" + self.end
        mc.ikHandle(n=ikHandleName, sol="IkRPsolver", sj=self.root, ee=self.end)

        poleVectorLocationValues = mc.getAttr(ikHandleName + ".poleVector")[0]
        poleVector = MVector(poleVectorLocationValues[0], poleVectorLocationValues[1], poleVectorLocationValues[2])
        poleVector.normal()

        endJntLoc = self.GetObjectLocation(self.end)
        rootToEndVector = endJntLoc - rootJntLoc

        poleVectorCtrlLoc = rootJntLoc + rootToEndVector / 2 + poleVector * rootToEndVector.length()
        poleVectorCtrl = "ac_ik" + self.mid
        mc.spaceLocator(n=poleVectorCtrl)
        poleVectorCtrlGrp = poleVectorCtrl + "_grp"
        mc.group(poleVectorCtrl, n= poleVectorCtrlGrp)
        mc.setAttr(poleVectorCtrlGrp+"t", poleVectorCtrlLoc.x, poleVectorCtrlLoc.y, poleVectorCtrlLoc.z, typ="double3")

        mc.poleVectorConstraint(poleVectorCtrl, ikHandleName)

        ikfkBlendCtrl = "ac_ikfk_blend_" + self.root
        ikfkBlendCtrl, ikfkBlendCtrlGrp = self.CreatePlusController(ikfkBlendCtrl)
        mc.seltAttr(ikfkBlendCtrlGrp+ ".t", rootJntLoc.x*2, rootJntLoc.y, rootJntLoc.z*2, typ="double3")

        ikfkBlendAttrName = "ikfkBlend"
        mc.addAttr(ikfkBlendCtrl, ln=ikfkBlendAttrName, min = 0, max = 1, k=True)
        ikfkBlendAttr = ikfkBlendCtrl + "." + ikfkBlendAttrName

        mc.expression(s=f"{ikHandleName}.ikBlend={ikfkBlendAttr}")
        mc.expression(s=f"{ikEndCtrlGrp}.v={poleVectorCtrlGrp}.v={ikfkBlendAttr}")
        mc.expression(s=f"{rootCtrlGrp}.v=1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{endCtrl}w0 = 1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{ikEndCtrl}w0 = {ikfkBlendAttr}")

        topGrpName = f"{self.root}_rig_grp"
        mc.group([rootCtrlGrp, ikEndCtrlGrp, poleVectorCtrlGrp, ikfkBlendCtrlGrp], n=topGrpName)
        mc.parent(ikHandleName, ikEndCtrl)

        mc.setAttr(topGrpName+".overrideEnable", 1)
        mc.setAttr(topGrpName+".overrideRGBColors", 1)
        mc.setAttr(topGrpName+".overrideRGBColors", self.ControllerColor[0], self.ControllerColor[1], self.ControllerColor[2], type="double3")

class ColorPicker(QWidget):
    colorChanged = Signal(QColor)
    def __init__(self):
        super().__init__()
        self.masterLayout = QVBoxLayout()
        self.color = QColor()
        self.setLayout(self.masterLayout)
        self.pickColorBtn = QPushButton()
        self.pickColorBtn.setStyleSheet(f"background-color:black")
        self.pickColorBtn.clicked.connect(self.PickColorBtnClicked)
        self.masterLayout.addWidget(self.pickColorBtn)

    def PickColorBtnClicked(self):
        self.color = QColorDialog.getColor()
        self.pickColorBtn.setStyleSheet(f"background-Color:{self.color.name()}")
        self.colorChanged.emit(self.color)

class LimbRiggerWidget(MayaWindow):
    def __init__(self):
        super().__init__()
        self.rigger = LimbRigger()
        self.setWindowTitle("Limb Rigger")
        #name of window

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        #window layout

        toolTipLable = QLabel("Select the first joint of the limb, and press the auto find button")
        self.masterLayout.addWidget(toolTipLable)
        #telling user what to do first

        self.jntsListLineEdit = QLineEdit()
        self.masterLayout.addWidget(self.jntsListLineEdit)
        self.jntsListLineEdit.setEnabled(False)
        #grabbing and showing that the second limb was found

        autoFindJntBtn = QPushButton("Auto Find")
        autoFindJntBtn.clicked.connect(self.autoFindJntBtnClicked)
        self.masterLayout.addWidget(autoFindJntBtn)
        #auto finding bones/constraints

        ctrlSizeSlider = QSlider()
        ctrlSizeSlider.setOrientation(Qt.Horizontal)
        ctrlSizeSlider.setRange(1, 30)
        ctrlSizeSlider.setValue(self.rigger.controllerSize)
        self.ctrlSizeLabel = QLabel(f"{self.rigger.controllerSize}")
        ctrlSizeSlider.valueChanged.connect(self.CtrlSizeSliderChanged)
        
        ctrlSizeLayout = QHBoxLayout()
        ctrlSizeLayout.addWidget(ctrlSizeSlider)
        ctrlSizeLayout.addWidget(self.ctrlSizeLabel)
        self.masterLayout.addLayout(ctrlSizeLayout)

        colorPicker = ColorPicker()
        colorPicker.colorChanged.connect(self.UpdateRig)
        self.masterLayout.addWidget(colorPicker)

        UpdateColor = QPushButton("Update Rig")
        UpdateColor.clicked.connect(self.UpdateRig)
        self.masterLayout.addWidget(UpdateColor)

        rigLimbBtn = QPushButton("Rig Limb")
        rigLimbBtn.clicked.connect(lambda : self.rigger.RigLimb())
        self.masterLayout.addWidget(rigLimbBtn)
        #returning that the limb has been rigger 

    def UpdateRig(self):
        ColorUpdate = self.ColorPickerChange
        try:
            if self.rigger:
                ColorUpdate()
        except Exception as a:
            print(self, "error", f"[{a}]")
        pass
        

    def ColorPickerChange(self, newColor: QColor):
        self.rigger.ControllerColor[0] = newColor.redF()
        self.rigger.ControllerColor[1] = newColor.greenF()
        self.rigger.ControllerColor[2] = newColor.blueF()

    def CtrlSizeSliderChanged(self, newvalue):
        self.ctrlSizeLabel.setText(f"{newvalue}")
        self.rigger.controllerSize = newvalue
    
    def autoFindJntBtnClicked(self):
        try:
            self.rigger.FindJntsBasedOnSelections()
            self.jntsListLineEdit.setText(f"{self.rigger.root},{self.rigger.mid},{self.rigger.end}")
        except Exception as e:
            QMessageBox.critical(self, "error", f"[{e}]")
        #button that the user will press in order to rig the bones

LimbRiggerWidget = LimbRiggerWidget()
LimbRiggerWidget.show()

LimbRiggerWidget = LimbRiggerWidget()
LimbRiggerWidget.show()