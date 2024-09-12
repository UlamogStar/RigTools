import maya.cmds as cmds

# Make viewport selection, parent control, then child control
sels = cmds.ls(selection=True)

# Ensure exactly two objects are selected
if len(sels) < 2:
    raise ValueError('Please select 2 objects. First parent, then child.')

parent_Ctrl = sels[0]
child_Ctrl = sels[1]

# Get the parent group of the child control
child_Ctrl_Grp = cmds.listRelatives(child_Ctrl, parent=True)[0]  # Returns the list of the child's parent

# Create constraints
p_constraint_T = cmds.parentConstraint(parent_Ctrl, child_Ctrl_Grp, mo=True, skipRotate=['x', 'y', 'z'], weight=1)[0]  # Translate
p_constraint_R = cmds.parentConstraint(parent_Ctrl, child_Ctrl_Grp, mo=True, skipTranslate=['x', 'y', 'z'], weight=1)[0]  # Rotate
p_constraint_S = cmds.scaleConstraint(parent_Ctrl, child_Ctrl_Grp, mo=True, weight=1)[0]  # Scale

# Create attributes on the child control
if not cmds.attributeQuery('FollowTranslate', node=child_Ctrl, exists=True):
    cmds.addAttr(child_Ctrl, longName='FollowTranslate', attributeType='double', minValue=0, maxValue=1, defaultValue=1, keyable=True)
    cmds.setAttr('%s.FollowTranslate' % child_Ctrl, e=True, keyable=True, channelBox=True)

if not cmds.attributeQuery('FollowRotate', node=child_Ctrl, exists=True):
    cmds.addAttr(child_Ctrl, longName='FollowRotate', attributeType='double', minValue=0, maxValue=1, defaultValue=1, keyable=True)
    cmds.setAttr('%s.FollowRotate' % child_Ctrl, e=True, keyable=True, channelBox=True)

# Connect attributes from the child control to constraint weights
cmds.connectAttr('%s.FollowTranslate' % child_Ctrl, '%s.w0' % p_constraint_T, f=True)
cmds.connectAttr('%s.FollowRotate' % child_Ctrl, '%s.w0' % p_constraint_R, f=True)
