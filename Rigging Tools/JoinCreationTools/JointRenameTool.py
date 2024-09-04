import maya.cmds as cmds

def renameLeftJoints(*args):
    selection = cmds.ls(selection=True)
    cmds.rename(selection[0], "L_jnt_")

def renameRightJoints(*args):
    selection = cmds.ls(selection=True)
    cmds.rename(selection[0], "R_jnt_")

def renameRightControls(*args):
    selection = cmds.ls(selection=True)
    cmds.rename(selection[0], "R_ctrl_")

def renameLeftControls(*args):
    selection = cmds.ls(selection=True)
    cmds.rename(selection[0], "L_ctrl_")

def renameFKJoints(*args):
    selection = cmds.ls(selection=True)
    new_name = cmds.rename(selection[0], cmds.ls(selection=True)[0].replace("_", "FK_"))
    cmds.select(new_name)

def renameIKJoints(*args):
    selection = cmds.ls(selection=True)
    new_name = cmds.rename(selection[0], cmds.ls(selection=True)[0].replace("_", "IK_"))
    cmds.select(new_name)

def renameRKJoints(*args):
    selection = cmds.ls(selection=True)
    new_name = cmds.rename(selection[0], cmds.ls(selection=True)[0].replace("_", "RK_"))
    cmds.select(new_name)
    


def createUI():
    windowID = "renameJoints"
    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID, window=True)

    cmds.window(windowID, title="Rename Joints")
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label="Rename Left Joints", command=renameLeftJoints)
    cmds.button(label="Rename Right Joints", command=renameRightJoints)
    cmds.button(label="Rename Left Controls", command=renameLeftControls)
    cmds.button(label="Rename Right Controls", command=renameRightControls)
    cmds.button(label="Rename FK Joints", command=renameFKJoints)
    cmds.button(label="Rename IK Joints", command=renameIKJoints)
    cmds.button(label="Rename RK Joints", command=renameRKJoints)
    cmds.showWindow()

createUI()

