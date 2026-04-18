import maya.cmds as cmds



def create_joints_at_clusters(match_rotation=False):
   
    sel = cmds.ls(selection=True, long=True) or []
    if not sel:
        cmds.warning("Select one or more cluster handle transforms.")
        return []

    created = []
    for node in sel:
        node_type = cmds.nodeType(node)
        transform = node

        if node_type != 'transform':
            parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
            if not parents:
                cmds.warning(f"Skipping '{node}': not a transform and no parent found.")
                continue
            transform = parents[0]

        shapes = cmds.listRelatives(transform, shapes=True, fullPath=True) or []
        if not any(cmds.nodeType(s) == 'clusterHandle' for s in shapes):
            cmds.warning(f"Skipping '{transform}': no cluster handle shape found.")
            continue

        cmds.select(clear=True)
        short = transform.split('|')[-1]
        j = cmds.joint(name=f"{short}_Jnt")
        cmds.matchTransform(j, transform, position=True, rotation=match_rotation)
        created.append(j)
        
    return created


def create_joints_at_selected_clusters(match_rotation=False):
    """Compatibility wrapper used by the UI/button.
    Calls `create_joints_at_clusters` so existing UI commands keep working.
    """
    return create_joints_at_clusters(match_rotation=match_rotation)


def show_ui():
   
    win = 'joinCreateClusterUI'
    if cmds.window(win, exists=True):
        cmds.deleteUI(win)

    cmds.window(win, title='Create Joints From Clusters', widthHeight=(320, 120), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnAlign='center')
    cmds.text(label='Select cluster handle transforms and use the buttons below.')

    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.button(label='Create (Position)', command=lambda *a: create_joints_at_selected_clusters(match_rotation=False), bgc=(0.3, 0.6, 0.3))
    cmds.setParent('..')



show_ui()
