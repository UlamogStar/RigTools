import maya.cmds as cmds

def searchReplaceNames(find, replace, scope='selected'):
    if scope == 'selected':
        nodes = cmds.ls(selection=True, long=True) or []
    else:
        nodes = cmds.ls(long=True) or []

    replaced = 0
    for node in nodes:
        if find in node:
            try:
                new_name = node.replace(find, replace)
                cmds.rename(node, new_name)
                replaced += 1
            except Exception as e:
                cmds.warning(f"Failed to rename '{node}': {e}")

    cmds.inViewMessage(amg=f'Replaced {replaced} names.', pos='topCenter', fade=True)
    return replaced

def replaceRKwithFK(*args):
    sel = cmds.ls(selection=True, long=True) or []
    if not sel:
        cmds.warning("Select one or more joints to rename.")
        return []

    renamed = []
    for node in sel:
        if cmds.objectType(node) != 'joint':
            cmds.warning(f"Skipping '{node}': not a joint.")
            continue
        if "_RK_" in node:
            try:
                new_name = node.replace("_RK_", "_FK_")
                renamed_node = cmds.rename(node, new_name)
                renamed.append(renamed_node)
            except Exception as e:
                cmds.warning(f"Failed to rename '{node}': {e}")

    cmds.inViewMessage(amg=f'Renamed {len(renamed)} nodes', pos='topCenter', fade=True)
    return renamed

def replaceRKwithIK(*args):
    sel = cmds.ls(selection=True, long=True) or []
    if not sel:
        cmds.warning("Select one or more joints to rename.")
        return []

    renamed = []
    for node in sel:
        if cmds.objectType(node) != 'joint':
            cmds.warning(f"Skipping '{node}': not a joint.")
            continue
        if "_RK_" in node:
            try:
                new_name = node.replace("_RK_", "_IK_")
                renamed_node = cmds.rename(node, new_name)
                renamed.append(renamed_node)
            except Exception as e:
                cmds.warning(f"Failed to rename '{node}': {e}")

    cmds.inViewMessage(amg=f'Renamed {len(renamed)} nodes', pos='topCenter', fade=True)
    return renamed

def replaceFKwithRK(*args):
    sel = cmds.ls(selection=True, long=True) or []
    if not sel:
        cmds.warning("Select one or more joints to rename.")
        return []

    renamed = []
    for node in sel:
        if cmds.objectType(node) != 'joint':
            cmds.warning(f"Skipping '{node}': not a joint.")
            continue
        if "_FK_" in node:
            try:
                new_name = node.replace("_FK_", "_RK_")
                renamed_node = cmds.rename(node, new_name)
                renamed.append(renamed_node)
            except Exception as e:
                cmds.warning(f"Failed to rename '{node}': {e}")

    cmds.inViewMessage(amg=f'Renamed {len(renamed)} nodes', pos='topCenter', fade=True)
    return renamed

def replaceFKwithIK(*args):
    sel = cmds.ls(selection=True, long=True) or []
    if not sel:
        cmds.warning("Select one or more joints to rename.")
        return []

    renamed = []
    for node in sel:
        if cmds.objectType(node) != 'joint':
            cmds.warning(f"Skipping '{node}': not a joint.")
            continue
        if "_FK_" in node:
            try:
                new_name = node.replace("_FK_", "_IK_")
                renamed_node = cmds.rename(node, new_name)
                renamed.append(renamed_node)
            except Exception as e:
                cmds.warning(f"Failed to rename '{node}': {e}")

    cmds.inViewMessage(amg=f'Renamed {len(renamed)} nodes', pos='topCenter', fade=True)
    return renamed

def replaceIKwithFK(*args):
    sel = cmds.ls(selection=True, long=True) or []
    if not sel:
        cmds.warning("Select one or more joints to rename.")
        return []

    renamed = []
    for node in sel:
        if cmds.objectType(node) != 'joint':
            cmds.warning(f"Skipping '{node}': not a joint.")
            continue
        if "_IK_" in node:
            try:
                new_name = node.replace("_IK_", "_FK_")
                renamed_node = cmds.rename(node, new_name)
                renamed.append(renamed_node)
            except Exception as e:
                cmds.warning(f"Failed to rename '{node}': {e}")

    cmds.inViewMessage(amg=f'Renamed {len(renamed)} nodes', pos='topCenter', fade=True)
    return renamed

def replaceIKwithRK(*args):
    sel = cmds.ls(selection=True, long=True) or []
    if not sel:
        cmds.warning("Select one or more joints to rename.")
        return []

    renamed = []
    for node in sel:
        if cmds.objectType(node) != 'joint':
            cmds.warning(f"Skipping '{node}': not a joint.")
            continue
        if "_IK_" in node:
            try:
                new_name = node.replace("_IK_", "_RK_")
                renamed_node = cmds.rename(node, new_name)
                renamed.append(renamed_node)
            except Exception as e:
                cmds.warning(f"Failed to rename '{node}': {e}")

    cmds.inViewMessage(amg=f'Renamed {len(renamed)} nodes', pos='topCenter', fade=True)
    return renamed

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

    cmds.showWindow()

createUI()
