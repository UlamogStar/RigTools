import maya.cmds as cmds

def freezeTransforms():
    selection = cmds.ls(selection=True)
    for obj in selection:
        cmds.DeleteHistory(obj)
        cmds.FreezeTransformations(obj)

def attributesSetZero():
    selection = cmds.ls(selection=True)
    for obj in selection:
        cmds.setAttr('{}.rx'.format(obj), 0)
        cmds.setAttr('{}.ry'.format(obj), 0)
        cmds.setAttr('{}.rz'.format(obj), 0)
        cmds.setAttr('{}.sx'.format(obj), 1)
        cmds.setAttr('{}.sy'.format(obj), 1)
        cmds.setAttr('{}.sz'.format(obj), 1)
        

def matchTransforms():
    selection = cmds.ls(selection=True)
    if len(selection) != 2:
        cmds.error('Please select two objects')
        return
    cmds.MatchTransform(selection[0], selection[1], pos=True, rot=True, scl=True)

def createControl():
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.error('Please select at least one object')
        return
    
    for obj in selection:
        cmds.select(obj)
        cmds.CreateNURBSCircle()
        cmds.move(0, 0, 0, relative=True)
        cmds.rename('_ctrl_0')
    
def createGroup():
    selection = cmds.ls(selection=True)
    if selection:
        cmds.group(selection, name='{}_grp'.format(selection[0]))
    else:
        selection = cmds.ls(selection=True)
        if selection:
            cmds.group(selection, name='{}_grp'.format(selection[0]))
        cmds.error('Please select an object')


def createUI():
    if cmds.window('matchTransformUI', exists=True):
        cmds.deleteUI('matchTransformUI', window=True)
    cmds.window('matchTransformUI', title='Match Transform Tool', widthHeight=(200, 180), sizeable=False)
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label='Freeze Transforms', command='freezeTransforms()')
    cmds.button(label='Set Attributes to Zero', command='attributesSetZero()')
    cmds.button(label='Match Transforms', command='matchTransforms()')
    cmds.button(label='Create Control', command= 'createControl()')
    cmds.button(label='Create Group', command='createGroup()')
    cmds.showWindow('matchTransformUI')

createUI()

