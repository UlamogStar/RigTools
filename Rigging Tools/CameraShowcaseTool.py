import maya.cmds as cmds

# ------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------
RIG_GRP   = "CameraRig_Grp"
ORBIT_GRP = "Cam_Orbit_Grp"
ANIM_GRP  = "Cam_Anim_Grp"
ROT_GRP   = "Cam_Rot_Grp"
CAM_NAME  = "Turntable_Cam"
AIM_LOC   = "Cam_Aim_Loc"

SLIDERS = {}
ORBIT_ACCUM = 0.0

# ------------------------------------------------------------
# RIG CREATION
# ------------------------------------------------------------
def create_camera_rig():

    if cmds.objExists(RIG_GRP):
        # Rig already exists — do NOT recreate
        return

    rig_grp = cmds.group(em=True, name=RIG_GRP)

    cmds.addAttr(rig_grp, ln="globalScale", at="double", dv=1, min=0.001)
    cmds.setAttr(rig_grp + ".globalScale", e=True, keyable=True)
    for ax in "XYZ":
        cmds.connectAttr(rig_grp + ".globalScale", f"{rig_grp}.scale{ax}")

    aim = cmds.spaceLocator(name=AIM_LOC)[0]
    cmds.parent(aim, rig_grp)

    orbit_grp = cmds.group(em=True, name=ORBIT_GRP, parent=rig_grp)
    anim_grp  = cmds.group(em=True, name=ANIM_GRP, parent=orbit_grp)
    rot_grp   = cmds.group(em=True, name=ROT_GRP, parent=anim_grp)

    cam = cmds.camera(name=CAM_NAME)[0]
    cmds.parent(cam, rot_grp)

    cmds.aimConstraint(
        aim,
        cam,
        aimVector=(0, 0, -1),
        upVector=(0, 1, 0),
        worldUpType="scene"
    )

    # Lock camera scale only
    for a in ["sx", "sy", "sz"]:
        cmds.setAttr(cam + "." + a, lock=True, keyable=False)

    # Hide rotation channels (do NOT lock)
    for a in ["rx", "ry", "rz"]:
        cmds.setAttr(cam + "." + a, keyable=False, channelBox=False)

    # Default orbit radius
    cmds.setAttr(anim_grp + ".translateZ", 20)

# ------------------------------------------------------------
# SLIDER CALLBACKS
# ------------------------------------------------------------
def set_dolly(val):
    cmds.setAttr(ANIM_GRP + ".translateZ", val)

def set_truck(val):
    cmds.setAttr(ANIM_GRP + ".translateX", val)

def set_pedestal(val):
    cmds.setAttr(ANIM_GRP + ".translateY", val)

def orbit_drag(val):
    """Infinite orbit using delta accumulation"""
    global ORBIT_ACCUM

    ORBIT_ACCUM += val
    cmds.setAttr(ORBIT_GRP + ".rotateY", ORBIT_ACCUM)

    # Reset slider back to center
    cmds.floatSlider(SLIDERS["orbit"], e=True, value=0)

def reset_camera(*_):
    global ORBIT_ACCUM
    ORBIT_ACCUM = 0.0

    cmds.setAttr(ANIM_GRP + ".translate", 0, 0, 20)
    cmds.setAttr(ORBIT_GRP + ".rotate", 0, 0, 0)
    cmds.setAttr(ROT_GRP + ".rotate", 0, 0, 0)

    cmds.floatSlider(SLIDERS["dolly"], e=True, value=20)
    cmds.floatSlider(SLIDERS["truck"], e=True, value=0)
    cmds.floatSlider(SLIDERS["pedestal"], e=True, value=0)
    cmds.floatSlider(SLIDERS["orbit"], e=True, value=0)

# ------------------------------------------------------------
# UI
# ------------------------------------------------------------
def camera_dolly_ui():

    win = "CameraOrbitUI"
    if cmds.window(win, exists=True):
        cmds.deleteUI(win)

    cmds.window(win, title="Camera Orbit / Dolly Controls", widthHeight=(320, 300))
    cmds.columnLayout(adj=True, rowSpacing=8)

    cmds.text(label="Dolly (Radius)")
    SLIDERS["dolly"] = cmds.floatSlider(
        min=1, max=300, value=20, step=0.1,
        dragCommand=set_dolly
    )

    cmds.text(label="Truck")
    SLIDERS["truck"] = cmds.floatSlider(
        min=-150, max=150, value=0, step=0.1,
        dragCommand=set_truck
    )

    cmds.text(label="Pedestal")
    SLIDERS["pedestal"] = cmds.floatSlider(
        min=-150, max=150, value=0, step=0.1,
        dragCommand=set_pedestal
    )

    cmds.separator(h=8, style="in")

    cmds.text(label="Orbit (Infinite)")
    SLIDERS["orbit"] = cmds.floatSlider(
        min=-10, max=10, value=0, step=0.1,
        dragCommand=orbit_drag
    )

    cmds.separator(h=12)
    cmds.button(label="Reset Camera", height=32, command=reset_camera)

    cmds.showWindow(win)

# ------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------
def launch_camera_tool():
    create_camera_rig()
    camera_dolly_ui()

launch_camera_tool()
