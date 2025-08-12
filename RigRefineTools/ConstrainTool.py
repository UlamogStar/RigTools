import maya.cmds as cmds

WIN = 'constrainToolUI'

def _get_parent_and_children():
    sels = cmds.ls(selection=True) or []
    if len(sels) < 2:
        cmds.warning('Select parent first, then one or more children.')
        return None, []
    return sels[0], sels[1:]

def createParentConstraint(*args):
    parent, children = _get_parent_and_children()
    if not parent or not children:
        return
    mo = cmds.checkBox('ct_mo', q=True, v=True)
    for child in children:
        try:
            cmds.parentConstraint(parent, child, mo=mo)
        except Exception as e:
            cmds.warning('ParentConstraint failed: {} -> {} | {}'.format(parent, child, e))

def createOrientConstraint(*args):
    parent, children = _get_parent_and_children()
    if not parent or not children:
        return
    mo = cmds.checkBox('ct_mo', q=True, v=True)
    for child in children:
        try:
            cmds.orientConstraint(parent, child, mo=mo)
        except Exception as e:
            cmds.warning('OrientConstraint failed: {} -> {} | {}'.format(parent, child, e))

def createScaleConstraint(*args):
    parent, children = _get_parent_and_children()
    if not parent or not children:
        return
    for child in children:
        try:
            cmds.scaleConstraint(parent, child)
        except Exception as e:
            cmds.warning('ScaleConstraint failed: {} -> {} | {}'.format(parent, child, e))

def clearConstraintsOnChildren(*args):
    _, children = _get_parent_and_children()
    if not children:
        return
    for child in children:
        cons = []
        # Constraints living under the child transform (typical)
        cons += cmds.listRelatives(child, type='parentConstraint') or []
        cons += cmds.listRelatives(child, type='orientConstraint') or []
        cons += cmds.listRelatives(child, type='scaleConstraint') or []
        # Also check connected constraints just in case
        cons += cmds.listConnections(child, type='parentConstraint') or []
        cons += cmds.listConnections(child, type='orientConstraint') or []
        cons += cmds.listConnections(child, type='scaleConstraint') or []
        cons = list(set(cons))
        if cons:
            cmds.delete(cons)

def createUI(*args):
    if cmds.window(WIN, exists=True):
        cmds.deleteUI(WIN, window=True)

    cmds.window(WIN, title='Constrain Tool', sizeable=False)
    cmds.columnLayout(adj=True, rs=6)

    cmds.text(label='Select parent, then child(ren).')
    cmds.checkBox('ct_mo', label='Maintain Offset (Parent/Orient)', v=True)

    cmds.rowLayout(numberOfColumns=3, adj=1,
                   columnAttach=[(1,'both',0),(2,'both',0),(3,'both',0)],
                   columnWidth=[(1,140),(2,140),(3,140)])
    cmds.button(label='Parent Constraint', c='createParentConstraint()')
    cmds.button(label='Orient Constraint', c='createOrientConstraint()')
    cmds.button(label='Scale Constraint', c='createScaleConstraint()')
    cmds.setParent('..')

    cmds.separator(h=6, style='none')
    cmds.button(label='Clear Constraints on Selected Children', c='clearConstraintsOnChildren()')

    cmds.separator(h=6, style='none')
    cmds.button(label='Refresh Selection', c='cmds.select(cmds.ls(sl=True))')

    cmds.showWindow(WIN)

createUI()