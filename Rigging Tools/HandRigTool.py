import maya.cmds as cmds

def createLocator():
    cmds.spaceLocator()

def createJoint():
    cmds.joint()

def renameHand():
    sels = cmds.ls(sl=True)
    for each in sels:
        cmds.rename(each, '_Finger_0')
        def createJointsAndRename(locators):
            for i, locator in enumerate(locators):
                joint = cmds.joint()
                cmds.rename(joint, f'_Finger_{i}')