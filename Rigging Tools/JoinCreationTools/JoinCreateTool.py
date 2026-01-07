import maya.cmds as cmds
import maya.mel as mel


def create_joints_at_clusters(match_rotation=False):
    """Create joints at selected cluster handle transforms.

    This function looks at the current selection and for each selected transform
    that has a shape of type 'clusterHandle' it creates a joint at the transform's
    world position. Optionally it matches rotation as well.

    Returns a list of created joint names.
    """
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
        j = cmds.joint(name=f"{transform}_Jnt")
        cmds.matchTransform(j, transform, position=True, rotation=match_rotation)
        created.append(j)

    if created:
        cmds.select(created)
        try:
            cmds.inViewMessage(amg="Joints created at clusters.", pos='midCenter', fade=True)
        except Exception:
            pass
    else:
        cmds.warning("No joints were created.")

    return created


def create_joints_at_selected_clusters(match_rotation=False):
    """Convenience wrapper kept for clarity and backward compatibility."""
    return create_joints_at_clusters(match_rotation=match_rotation)


def create_shelf_button(shelf_name=None, match_rotation=False):
    """Create a shelf button that runs this tool.

    If `shelf_name` is None, the user will be prompted for a shelf/tab name.
    The function attempts to create a Python-command shelf button that calls
    `create_joints_at_selected_clusters`.
    """
    if shelf_name is None:
        res = cmds.promptDialog(
            title='Shelf name',
            message='Enter target shelf/tab name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')

        if res != 'OK':
            cmds.warning('Shelf creation cancelled.')
            return None

        shelf_name = cmds.promptDialog(query=True, text=True)

    # Build a robust python command string that imports this module and runs the function
    py_cmd = (
        "import importlib, sys\n"
        "from JoinCreateTool import create_joints_at_selected_clusters as _run\n"
        "_run(match_rotation=%s)" % (True if match_rotation else False)
    )

    try:
        cmds.shelfButton(parent=shelf_name,
                         annotation='Create joints at selected cluster handles',
                         command=py_cmd,
                         image='commandButton.png')
        cmds.inViewMessage(amg='Shelf button created.', pos='midCenter', fade=True)
    except Exception as e:
        cmds.warning(f"Failed to create shelf button on '{shelf_name}': {e}\nTry creating the button manually or pass a valid shelf/tab name.")
        return None


def show_ui():
    """Show a small UI to run the cluster->joint tool or add a shelf button."""
    win = 'joinCreateClusterUI'
    if cmds.window(win, exists=True):
        cmds.deleteUI(win)

    cmds.window(win, title='Create Joints From Clusters', widthHeight=(320, 120), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnAlign='center')
    cmds.text(label='Select cluster handle transforms and use the buttons below.')

    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.button(label='Create (Position)', command=lambda *a: create_joints_at_selected_clusters(match_rotation=False), bgc=(0.3, 0.6, 0.3))
    cmds.button(label='Create (Match Rot)', command=lambda *a: create_joints_at_selected_clusters(match_rotation=True), bgc=(0.3, 0.3, 0.6))
    cmds.setParent('..')

    cmds.button(label='Create Shelf Button...', command=lambda *a: create_shelf_button(), bgc=(0.6, 0.5, 0.2))
    cmds.showWindow(win)


if __name__ == '__main__':
    show_ui()
