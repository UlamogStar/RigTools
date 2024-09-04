import maya.cmds as cmds

def createParentConstraint():
    selection = cmds.ls(selection=True)
    if len(selection) != 2:
        cmds.error('Please select two objects')
        return
    cmds.parentConstraint(selection[0], selection[1], mo=True, weight=1)
def createScaleConstraint():
    selection = cmds.ls(selection=True)
    if len(selection) != 2:
        cmds.error('Please select two objects')
        return
    cmds.scaleConstraint(selection[0], selection[1], mo=True, weight=1)
def createOrientConstraint():
    selection = cmds.ls(selection=True)
    if len(selection) != 2:
        cmds.error('Please select two objects')
        return
    cmds.orientConstraint(selection[0], selection[1], mo=True, weight=1)
    

def createUI():
    if cmds.window('constrainUI', exists=True):
        cmds.deleteUI('constrainUI', window=True)
    
    cmds.window('constrainUI', title='Constrain Tool', widthHeight=(200, 100), sizeable=False)
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label='Parent Constraint', command='createParentConstraint()')
    cmds.button(label='Scale Constraint', command='createScaleConstraint()')
    cmds.button(label='Orient Constraint', command='createOrientConstraint()')

    cmds.showWindow('constrainUI')

createUI()