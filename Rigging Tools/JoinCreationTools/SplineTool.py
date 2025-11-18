"""
Spline IK style controls:
- Select a joint chain root (or select several roots) then:
  1) Create a curve through the joint positions
  2) Create one control per joint and attach it to the curve using pointOnCurveInfo
  3) Constrain each joint to its control (point+orient or parent) with optional maintain offset

Usage:
- Select root joint(s) and press "Create Curve + Controls"
- Options: control size, maintain offset
"""
import maya.cmds as cmds

WIN = "splineIKTool_win"

def get_joint_chain(root):
    """Return joints in chain top-down starting at root (fullPath names)."""
    chain = []
    def _walk(j):
        chain.append(j)
        children = cmds.listRelatives(j, children=True, type='joint', fullPath=True) or []
        for c in children:
            _walk(c)
    if cmds.objExists(root) and cmds.nodeType(root) == 'joint':
        _walk(root)
    return chain

def create_curve_from_joints(joints, name="splineCurve", degree=3):
    """Create a nurbs curve through joint world positions. Returns curve transform."""
    if not joints:
        return None
    pts = []
    for j in joints:
        pts.append(cmds.xform(j, q=True, ws=True, t=True))
    # if only 2 points, degree must be 1
    deg = degree
    if len(pts) < 3:
        deg = 1
    curve = cmds.curve(p=pts, degree=deg, name=name)
    # rebuild to have nice parameterization (optional)
    try:
        spans = max(1, len(pts)-1)
        cmds.rebuildCurve(curve, s=(spans), d=deg, replaceOriginal=True)
    except Exception:
        pass
    return curve

def create_ctrl(name, pos, size=1.0, parent=None):
    """Create a simple circle control at pos (world) and return its transform."""
    ctrl_circle = cmds.circle(normal=[0,1,0], radius=size, ch=False)[0]
    # freeze transforms on shape parent, move transform then center pivot
    cmds.xform(ctrl_circle, ws=True, t=pos)
    cmds.makeIdentity(ctrl_circle, apply=True, t=1, r=1, s=1, n=0)
    grp = cmds.group(ctrl_circle, name=name + "_GRP")
    # zero group at control for easier offset handling
    # Move group to same position and parent control under it
    cmds.xform(grp, ws=True, t=pos)
    # unparent control from group (circle created as child of transform) then parent properly:
    # Actually circle returns transform; ensure correct parenting:
    try:
        # place ctrl under group (if not already)
        if cmds.listRelatives(ctrl_circle, parent=True) != [grp]:
            cmds.parent(ctrl_circle, grp)
    except Exception:
        pass
    if parent:
        cmds.parent(grp, parent)
    return ctrl_circle, grp

def attach_ctrls_to_curve(curve, joint_chain, ctrl_size=1.0, maintain_offset=True):
    """
    For each joint in joint_chain create:
      - pointOnCurveInfo node connected to curve
      - a control whose translate is driven by pointOnCurveInfo.position
      - parent/point+orient constrain the joint to the control (maintain offset option)
    Controls are placed at normalized parameter positions along the curve (matching the joint order).
    """
    if not cmds.objExists(curve):
        cmds.error("Curve does not exist.")
        return

    # get shape object
    shapes = cmds.listRelatives(curve, shapes=True, fullPath=True) or []
    if not shapes:
        cmds.error("No curve shape found.")
        return
    curve_shape = shapes[0]

    # spans define parameter domain roughly [0 .. spans]
    try:
        spans = cmds.getAttr(curve_shape + ".spans")
    except Exception:
        spans = max(1, len(joint_chain)-1)

    parent_grp = cmds.group(empty=True, name=curve + "_ctrls_GRP")

    created = []
    n = len(joint_chain)
    for idx, j in enumerate(joint_chain):
        t = 0.0 if n == 1 else float(idx) / float(n - 1)  # normalized 0..1
        param = t * spans

        # create pointOnCurveInfo node
        poci = cmds.createNode('pointOnCurveInfo', name="poci_{}_{}".format(j.split('|')[-1], idx))
        cmds.connectAttr(curve_shape + ".worldSpace[0]", poci + ".inputCurve", f=True)
        cmds.setAttr(poci + ".parameter", float(param))

        # create control and group (control transform will be parented under grp)
        pos = cmds.pointOnCurve(curve, pr=True, position=True, parameter=param) if cmds.objExists(curve) else cmds.xform(j, q=True, ws=True, t=True)
        # fallback if pointOnCurve didn't return point
        if not pos:
            pos = cmds.xform(j, q=True, ws=True, t=True)

        ctrl_name = j.split('|')[-1].replace("_Jnt", "_Ctrl")
        ctrl, ctrl_grp = create_ctrl(ctrl_name, pos, size=ctrl_size, parent=parent_grp)

        # connect poci.position -> ctrl_grp.translate so group follows curve (control remains oriented)
        try:
            cmds.connectAttr(poci + ".position", ctrl_grp + ".translate", f=True)
        except Exception:
            # fallback: set translation explicitly (static)
            cmds.xform(ctrl_grp, ws=True, t=pos)

        # optionally orient the control to the curve tangent using poci.tangent
        # create aim-group to orient control: connect poci.tangent to an aim node would be more work.
        # Instead we place a second helper that is parented and aimConstrained if needed (left as extension)

        # constrain joint to ctrl (parent constraint keeps both transl+rot)
        try:
            cmds.parentConstraint(ctrl, j, mo=maintain_offset, name="pc_{}_to_{}".format(ctrl.split('|')[-1], j.split('|')[-1]))
        except Exception:
            # fallback to point + orient if parent fails
            try:
                cmds.pointConstraint(ctrl, j, mo=maintain_offset)
                cmds.orientConstraint(ctrl, j, mo=maintain_offset)
            except Exception:
                cmds.warning("Failed to constrain {} to {}".format(j, ctrl))

        created.append((j, ctrl, ctrl_grp, poci))

    cmds.select(parent_grp, r=True)
    return created

# UI
def build_ui():
    if cmds.window(WIN, exists=True):
        cmds.deleteUI(WIN)
    cmds.window(WIN, title="Spline IK Controls", widthHeight=(420, 220), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnAlign="center")
    cmds.text(label="Select joint root(s) then create spline curve and controls.", align="center")
    cmds.separator(height=6)

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(130,130,130))
    cmds.button(label="Create Curve + Controls", height=34, command=lambda *a: ui_create_curve_controls())
    cmds.floatSliderGrp('ctrlSize', label='Ctrl Size', field=True, minValue=0.01, maxValue=10.0, value=1.0)
    cmds.checkBox('maintainOffset', label='Maintain Offset', v=True)
    cmds.setParent('..')

    cmds.separator(height=6)
    cmds.text(label="If a curve already exists, select the curve and joint chain root then press 'Attach To Curve'.", align="center")
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(210,210))
    cmds.button(label="Attach Selected Curve -> Create Controls", height=30, command=lambda *a: ui_attach_curve_controls())
    cmds.button(label="Create IK Spline Handle (optional)", height=30, command=lambda *a: ui_create_ik_spline_handle())
    cmds.setParent('..')

    cmds.separator(height=6)
    cmds.button(label="Close", height=26, command=lambda *a: cmds.deleteUI(WIN))
    cmds.showWindow(WIN)

def ui_create_curve_controls():
    sels = cmds.ls(selection=True, long=True) or []
    if not sels:
        cmds.warning("Select joint root(s) (one or more) to build chains.")
        return
    all_created = []
    size = cmds.floatSliderGrp('ctrlSize', q=True, value=True)
    mo = cmds.checkBox('maintainOffset', q=True, v=True)
    for root in sels:
        if cmds.nodeType(root) != 'joint':
            cmds.warning("{} is not a joint, skipping.".format(root))
            continue
        chain = get_joint_chain(root)
        if not chain:
            continue
        curve_name = cmds.ls(root + "_splineCurve", long=False) and root + "_splineCurve" or root.split('|')[-1] + "_splineCurve"
        curve = create_curve_from_joints(chain, name=curve_name)
        created = attach_ctrls_to_curve(curve, chain, ctrl_size=size, maintain_offset=mo)
        all_created.extend(created)
    if all_created:
        cmds.inViewMessage(amg="Spline IK Controls created.", pos='topCenter', fade=True)
    else:
        cmds.warning("No controls created.")

def ui_attach_curve_controls():
    sels = cmds.ls(selection=True, long=True) or []
    if not sels or len(sels) < 2:
        cmds.warning("Select the curve first, then the joint root (curve + jointRoot).")
        return
    # assume first selected is curve and second is joint root
    curve = None
    root = None
    for s in sels:
        if cmds.objectType(s) in ('transform',) and cmds.listRelatives(s, shapes=True):
            shp = cmds.listRelatives(s, shapes=True, fullPath=True)[0]
            if cmds.nodeType(shp) == 'nurbsCurve' and not curve:
                curve = s
                continue
        if cmds.nodeType(s) == 'joint' and not root:
            root = s
    if not curve or not root:
        cmds.warning("Couldn't detect curve + joint root in selection. Select curve then joint root.")
        return
    chain = get_joint_chain(root)
    size = cmds.floatSliderGrp('ctrlSize', q=True, value=True)
    mo = cmds.checkBox('maintainOffset', q=True, v=True)
    attach_ctrls_to_curve(curve, chain, ctrl_size=size, maintain_offset=mo)
    cmds.inViewMessage(amg="Attached controls to curve.", pos='topCenter', fade=True)

def ui_create_ik_spline_handle():
    sels = cmds.ls(selection=True, long=True) or []
    if not sels:
        cmds.warning("Select joint root to create IK spline handle for its chain.")
        return
    for root in sels:
        if cmds.nodeType(root) != 'joint':
            continue
        chain = get_joint_chain(root)
        if len(chain) < 2:
            cmds.warning("Need at least 2 joints for an IK spline.")
            continue
        start = chain[0]
        end = chain[-1]
        curve_name = root.split('|')[-1] + "_splineCurve"
        # try to use existing curve if found, else create one
        curve = None
        if cmds.objExists(curve_name):
            curve = curve_name
        else:
            curve = create_curve_from_joints(chain, name=curve_name)
        try:
            handle = cmds.ikHandle(startJoint=start, endEffector=end, sol="ikSplineSolver", name=root.split('|')[-1] + "_ikSplineHandle", curve=curve, createCurve=False)[0]
            # optionally parent handle under a group for neatness
            grp = cmds.group(handle, name=handle + "_GRP")
            cmds.inViewMessage(amg="IK Spline handle created.", pos='topCenter', fade=True)
        except Exception as e:
            cmds.warning("Failed to create ikSpline: {}".format(e))

if __name__ == "__main__":
    build_ui()