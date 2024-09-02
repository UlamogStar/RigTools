import maya.cmds as cmds

def renameLeftJoints(*args):
    cmds.ls(selection=True)
    cmds.rename('L_jnt_')

def renameRightJoints(*args):
    cmds.ls(selection=True)
    cmds.rename('R_jnt_')

def renameRightControls(*args):
    cmds.ls(selection=True)
    cmds.rename('R_ctrl_')

def renameLeftControls(*args):
    cmds.ls(selection=True)
    cmds.rename('L_ctrl_')

def createUI():
    windowID = "renameJoints"
    if cmds.window('renameJoints', exists=True):
        cmds.deleteUI('renameJoints', window=True)

    cmds.window('renameJoints', title="Rename Joints", sizeable=False, widthHeight=(200, 100))
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label="Rename Left Joints", command=renameLeftJoints)
    cmds.button(label="Rename Right Joints", command=renameRightJoints)
    cmds.button(label="Rename Left Controls", command=renameLeftControls)
    cmds.button(label="Rename Right Controls", command=renameRightControls)
    
    cmds.showWindow()

createUI()
