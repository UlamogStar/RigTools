import 
import maya.cmds as cmds

def ControlCreate():
#Command to create control curves at all selected joints
    sel = cmds.ls(selection=True, type='joint')
    for joint in sel:
        #create a group at the position of each joint
        group = cmds.group(empty=True, name=joint + '_grp')
        #Create a control curve for each joint
        control = cmds.circle(name=joint + '_ctrl', normal=[1, 0, 0], radius=1)[0]
        #name each control curve after the joint it is associated with
        cmds.parent(control, group)
        cmds.matchTransform(group, joint)

ControlCreate()