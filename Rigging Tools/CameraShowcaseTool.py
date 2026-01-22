import maya.cmds as cmds

# ---------------------------------
# Utility
# ---------------------------------

def get_target_data():
    sel = cmds.ls(sl=True)
    if not sel:
        return [0, 0, 0], 10.0

    bbox = cmds.exactWorldBoundingBox(sel[0])

    center = [
        (bbox[0] + bbox[3]) / 2.0,
        (bbox[1] + bbox[4]) / 2.0,
        (bbox[2] + bbox[5]) / 2.0
    ]

    size = max(
        bbox[3] - bbox[0],
        bbox[4] - bbox[1],
        bbox[5] - bbox[2]
    )

    return center, size * 1.5


def ensure_group(name, parent=None):
    if cmds.objExists(name):
        return name
    grp = cmds.group(em=True, name=name)
    if parent:
        cmds.parent(grp, parent)
    return grp


# ---------------------------------
# Rig Creation
# ---------------------------------

def add_global_scale_attr(grp):
    if not cmds.attributeQuery("globalScale", node=grp, exists=True):
        cmds.addAttr(grp, ln="globalScale", at="double", min=0.001, dv=1)
        cmds.setAttr(grp + ".globalScale", e=True, keyable=True)
        for axis in "XYZ":
            cmds.connectAttr(grp + ".globalScale", grp + ".scale" + axis, f=True)


def create_camera():
    rig_grp = ensure_group("CameraRig_Grp")
    add_global_scale_attr(rig_grp)

    if cmds.objExists("Turntable_Cam"):
        return

    cam, _ = cmds.camera(name="Turntable_Cam")
    cam_grp = cmds.group(cam, name="Turntable_Cam_Grp")
    cmds.parent(cam_grp, rig_grp)

    cmds.makeIdentity(cam, apply=True, t=1, r=1, s=1, n=0)

    # Lock scale only
    for attr in ["sx", "sy", "sz"]:
        cmds.setAttr(cam + "." + attr, lock=True, keyable=False)


def create_or_move_locator(name, parent, position, rotation):
    if not cmds.objExists(name):
        loc = cmds.spaceLocator(name=name)[0]
        cmds.parent(loc, parent)
    else:
        loc = name

    cmds.xform(loc, ws=True, t=position, ro=rotation)
    return loc


def setup_scene():
    center, distance = get_target_data()

    rig_grp = ensure_group("CameraRig_Grp")
    create_camera()

    # View locators with explicit rotations
    create_or_move_locator(
        "Cam_Front_Loc",
        rig_grp,
        [center[0], center[1], center[2] + distance],
        [0, 0, 0]
    )

    create_or_move_locator(
        "Cam_Back_Loc",
        rig_grp,
        [center[0], center[1], center[2] - distance],
        [0, 180, 0]
    )

    create_or_move_locator(
        "Cam_Right_Loc",
        rig_grp,
        [center[0] + distance, center[1], center[2]],
        [0, 90, 0]
    )

    create_or_move_locator(
        "Cam_Left_Loc",
        rig_grp,
        [center[0] - distance, center[1], center[2]],
        [0, -90, 0]
    )


# ---------------------------------
# Snapping Logic
# ---------------------------------

def snap_camera_to(locator):
    cam_grp = "Turntable_Cam_Grp"

    if not cmds.objExists(cam_grp) or not cmds.objExists(locator):
        cmds.warning("Camera group or locator missing.")
        return

    # Snap position
    constraint = cmds.parentConstraint(locator, cam_grp, mo=False)[0]
    cmds.delete(constraint)

    # Match rotation AFTER snap
    cmds.matchTransform(
        cam_grp,
        locator,
        pos=False,
        rot=True,
        scl=False
    )


# ---------------------------------
# UI
# ---------------------------------

def build_ui():
    win = "CameraViewTool_UI"
    if cmds.window(win, exists=True):
        cmds.deleteUI(win)

    cmds.window(win, title="Scalable Camera Rig", widthHeight=(260, 300))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8)

    cmds.button(
        label="Create / Update Camera Rig",
        height=36,
        command=lambda *_: setup_scene()
    )

    cmds.separator(height=12)

    cmds.button(label="Front View", command=lambda *_: snap_camera_to("Cam_Front_Loc"))
    cmds.button(label="Back View",  command=lambda *_: snap_camera_to("Cam_Back_Loc"))
    cmds.button(label="Left View",  command=lambda *_: snap_camera_to("Cam_Left_Loc"))
    cmds.button(label="Right View", command=lambda *_: snap_camera_to("Cam_Right_Loc"))

    cmds.separator(height=12)
    cmds.text(label="Camera orientation driven by locator rotations")

    cmds.showWindow(win)


# ---------------------------------
# Run
# ---------------------------------

build_ui()
