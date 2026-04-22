import maya.cmds as cmds


def replaceRKwithFK(*args):
    searchReplaceNames("_RK_", "_FK_", "selected");

def replaceRKwithIK(*args):
    searchReplaceNames("_RK_", "_IK_", "selected");

def replaceFKwithRK(*args):
    searchReplaceNames("_FK_", "_RK_", "selected");

def replaceFKwithIK(*args):
    searchReplaceNames("_FK_", "_IK_", "selected");

def replaceIKwithFK(*args):
    searchReplaceNames("_IK_", "_FK_", "selected");

def replaceIKwithRK(*args):
    searchReplaceNames("_IK_", "_RK_", "selected");

def createUI():
    windowID = "renameJoints"
    if cmds.window('renameJoints', exists=True):
        cmds.deleteUI('renameJoints', window=True)
    cmds.window(windowID, title="Rename Joints", sizeable=False, widthHeight=(240, 150))
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label="RK → FK (joints)", command=replaceRKwithFK)
    cmds.button(label="RK → IK (joints)", command=replaceRKwithIK)
    cmds.button(label="FK → RK (joints)", command=replaceFKwithRK)
    cmds.button(label="FK → IK (joints)", command=replaceFKwithIK)
    cmds.button(label="IK → FK (joints)", command=replaceIKwithFK)
    cmds.button(label="IK → RK (joints)", command=replaceIKwithRK)

    cmds.showWindow(windowID)

createUI()
