from PySide2.QtWidgets import  QMainWindow, QWidget # type: ignore
from PySide2.QtCore import Qt
import maya.OpenMayaUI as omui
import shiboken2
import maya.cmds as mc

def IsMesh(obj):
    shapes = mc.listRelatives(obj, s=True)
    if not shapes:
        return False
        
    for s in shapes:
        if mc.objectType(s) == "mesh":
            return True
        
    return False

def IsSkin(obj):
    return mc.objectType(obj) == "skinCluster"
def IsJoint(obj):
    return mc.objectType(obj) == "joint"

def GetUpperStream(obj):
    return mc.listConnections(obj, s=True, d=False, sh=True)

def GetLowerStream(obj):
    return mc.listConnections(obj, s=False, d=True, sh=True)


def GetallConnectionsIn(obj, nextFunc, filter = None):
    allFound = set()
    nexts = nextFunc(obj)
    searchDepth = 100
    while nexts and searchDepth > 0:
        searchDepth -= 1
        for next in nexts:
            allFound.add(next)

        nexts = nextFunc(nexts)
        if nexts:
            nexts = [x for x in nexts if x not in allFound]

    if not filter:
        return list(allFound)
    
    filtered = []
    for found in allFound:
        if filter(found):
            filtered.append(found)

    return filtered

def GetMayaMainWindow()->QMainWindow:
    mainWindow = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(mainWindow), QMainWindow) #telling to make another maya window

def DeleteWidgetWithName(name):
    for widget in GetMayaMainWindow().findChildren(QWidget, name):  #adding new window and deleting new window when reseted
        widget.deleteLater()

import maya.cmds as mc

class MayaWindow(QWidget):
    def __init__(self):
        super().__init__(parent = GetMayaMainWindow())
        DeleteWidgetWithName(self.GetWidgetUniqueName())
        self.setWindowFlags(Qt.WindowType.Window)
        self.setObjectName(self.GetWidgetUniqueName())
        #maya window being able to show instances of stuff
    
    def GetWidgetUniqueName(self):
        return "dsfsdfsdfisdsdhjd1234315315fi9"

GetMayaMainWindow().show