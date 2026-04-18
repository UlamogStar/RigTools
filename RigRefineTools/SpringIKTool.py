import maya.cmds as cmds

def enableSpringIK():
    maya.cmds.ikSpringSolver( edit=True, enable=True )


def jointCreate():
    sel = cmds.ls(selection=True, long=True) or []
    if not sel:
        cmds.warning("Select one or more joints to create spring IK handles on.")
        return []

    created = []
    for node in sel:
        if cmds.objectType(node) != 'joint':
            cmds.warning(f"Skipping '{node}': not a joint.")
            continue

        ik_handle_name = f"{node}_SpringIKHandle"
        try:
            ik_handle, effector = cmds.ikHandle(name=ik_handle_name, startJoint=node, solver='ikSpringSolver')
            created.append(ik_handle)
        except Exception as e:
            cmds.warning(f"Failed to create IK handle for '{node}': {e}")

    return created