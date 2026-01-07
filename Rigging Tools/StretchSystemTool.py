"""StretchSystemTool

Lightweight Maya Python tool to add a node-based stretch system to a two-segment IK chain.

Features:
- Creates locators driven by the chain joints and a distanceBetween node to measure current length.
- Computes a scale factor relative to the rest length using a multiplyDivide node.
- Uses a condition node to prevent squash (clamps to minimum 1.0) optionally.
- Provides a blendColors node driven by a `stretch` attribute on the IK handle transform so stretch can be toggled.
- Connects output to the joint scaleX attributes so the joint lengths stretch proportionally.

Usage (inside Maya Python tab):
    import StretchSystemTool
    StretchSystemTool.create_stretch_ik_chain(ik_handle='ikHandle1', start_jnt='joint1', mid_jnt='joint2', end_jnt='joint3')

The module will print the node creation plan when not run inside Maya (dry-run mode).
"""

from __future__ import annotations
import math
import logging
logger = logging.getLogger(__name__)

try:
    import maya.cmds as cmds
    IN_MAYA = True
except Exception:
    IN_MAYA = False


def _maya(cmd, *args, **kwargs):
    """Helper: run maya command or print if not in Maya."""
    if IN_MAYA:
        return getattr(cmds, cmd)(*args, **kwargs)
    else:
        # simple dry-run message
        print(f"DRY RUN: cmds.{cmd}(*{args}, **{kwargs})")
        return None


def create_stretch_ik_chain(ik_handle: str, start_jnt: str, mid_jnt: str, end_jnt: str, *, name: str = None, clamp_min: bool = True, add_attr: bool = True):
    """Create a node-based stretch system for a two-segment IK chain.

    Args:
        ik_handle: name of existing IK handle transform (or shape) to attach the stretch attribute to.
        start_jnt: root joint of the chain.
        mid_jnt: middle joint of the chain.
        end_jnt: end joint of the chain.
        name: optional base name for created nodes (defaults to '<start>_stretch').
        clamp_min: if True, joints won't squash (minimum scale = 1.0).
        add_attr: if True, adds a `stretch` float attribute on the IK handle (0..1) to blend stretch.

    Returns:
        dict: mapping of created node names for convenience.

    Note: This does not reorient joints or alter joint setups — it only connects scaleX on the provided joints.
    It expects the joints to be oriented such that their length sits on the X axis.
    """
    if name is None:
        name = f"{start_jnt}_stretch"

    # Resolve IK handle transform: if an IK handle shape was provided, get its transform
    ik_transform = ik_handle
    if IN_MAYA:
        # if shape name or handle is a shape, try to find the parent transform
        if cmds.objExists(ik_handle):
            shapes = cmds.listRelatives(ik_handle, parent=True, fullPath=False) or []
            if shapes:
                ik_transform = shapes[0]

    created = {}

    # create locators and position them at joints
    loc_start = f"{name}_loc_start_loc"
    loc_end = f"{name}_loc_end_loc"
    if IN_MAYA:
        if not cmds.objExists(loc_start):
            loc_start = cmds.spaceLocator(name=loc_start)[0]
        if not cmds.objExists(loc_end):
            loc_end = cmds.spaceLocator(name=loc_end)[0]
        # point constrain locators to joints so they follow
        cmds.pointConstraint(start_jnt, loc_start, maintainOffset=False)
        cmds.pointConstraint(end_jnt, loc_end, maintainOffset=False)
    else:
        _maya('spaceLocator', name=loc_start)
        _maya('spaceLocator', name=loc_end)
    created['locators'] = (loc_start, loc_end)

    # create distanceBetween node (Maya node is 'distanceBetween')
    dist_node = f"{name}_distance"
    if IN_MAYA:
        if not cmds.objExists(dist_node):
            dist_node = cmds.createNode('distanceBetween', name=dist_node)
        # connect locator worldMatrix to distance node
        cmds.connectAttr(f"{loc_start}.worldMatrix[0]", f"{dist_node}.inMatrix1", force=True)
        cmds.connectAttr(f"{loc_end}.worldMatrix[0]", f"{dist_node}.inMatrix2", force=True)
        current_dist = cmds.getAttr(f"{dist_node}.distance")
    else:
        _maya('createNode', 'distanceBetween', name=dist_node)
        current_dist = None
    created['distance'] = dist_node

    # compute rest lengths of segments (vector distance between start->mid and mid->end)
    def _segment_length(a, b):
        if IN_MAYA:
            pa = cmds.xform(a, q=True, ws=True, t=True)
            pb = cmds.xform(b, q=True, ws=True, t=True)
            return math.dist(pa, pb)
        else:
            return 1.0

    len1 = _segment_length(start_jnt, mid_jnt)
    len2 = _segment_length(mid_jnt, end_jnt)
    rest_length = len1 + len2

    # multiplyDivide node to compute scale factor = currentDist / rest_length
    md_node = f"{name}_md_divide"
    if IN_MAYA:
        if not cmds.objExists(md_node):
            md_node = cmds.createNode('multiplyDivide', name=md_node)
        cmds.setAttr(f"{md_node}.operation", 2)  # divide
        cmds.connectAttr(f"{dist_node}.distance", f"{md_node}.input1X", force=True)
        cmds.setAttr(f"{md_node}.input2X", rest_length)
    else:
        _maya('createNode', 'multiplyDivide', name=md_node)
    created['md_divide'] = md_node

    # condition node to prevent squash (clamp min to 1.0)
    cond_node = f"{name}_cond"
    if IN_MAYA:
        if not cmds.objExists(cond_node):
            cond_node = cmds.createNode('condition', name=cond_node)
        # Compare md.outputX to 1.0
        cmds.connectAttr(f"{md_node}.outputX", f"{cond_node}.firstTerm", force=True)
        cmds.setAttr(f"{cond_node}.secondTerm", 1.0)
        cmds.setAttr(f"{cond_node}.operation", 2)  # Greater
        # If greater: use md.outputX, else: 1.0
        cmds.connectAttr(f"{md_node}.outputX", f"{cond_node}.colorIfTrueR", force=True)
        cmds.setAttr(f"{cond_node}.colorIfFalseR", 1.0)
        out_attr = f"{cond_node}.outColorR"
    else:
        _maya('createNode', 'condition', name=cond_node)
        out_attr = f"{cond_node}.outColorR"
    created['condition'] = cond_node

    # blendColors node driven by an attribute (stretch slider 0..1)
    blend_node = f"{name}_blend"
    if IN_MAYA:
        if not cmds.objExists(blend_node):
            blend_node = cmds.createNode('blendColors', name=blend_node)
        # color1 = 1 (no stretch), color2 = condition result
        cmds.setAttr(f"{blend_node}.color1R", 1.0)
        cmds.connectAttr(out_attr, f"{blend_node}.color2R", force=True)
    else:
        _maya('createNode', 'blendColors', name=blend_node)
    created['blend'] = blend_node

    # add attribute on IK handle transform to control blend (0..1)
    stretch_attr = f"{ik_transform}.stretch"
    if IN_MAYA and add_attr:
        if not cmds.attributeQuery('stretch', node=ik_transform, exists=True):
            cmds.addAttr(ik_transform, longName='stretch', attributeType='double', min=0.0, max=1.0, defaultValue=1.0)
            cmds.setAttr(f"{ik_transform}.stretch", keyable=True)
        # connect attribute to blend
        cmds.connectAttr(f"{ik_transform}.stretch", f"{blend_node}.blender", force=True)
    else:
        if not IN_MAYA:
            print(f"DRY RUN: create attr {stretch_attr} and connect to {blend_node}.blender")
    created['stretch_attr'] = stretch_attr

    # connect blend output to joints' scaleX (both start and mid get the same scale)
    # Note: some rigs expect scaleY/scaleZ driven or joint scale compensation — this keeps it simple.
    if IN_MAYA:
        # connect blend.outputR -> start_jnt.scaleX and mid_jnt.scaleX
        cmds.connectAttr(f"{blend_node}.outputR", f"{start_jnt}.scaleX", force=True)
        cmds.connectAttr(f"{blend_node}.outputR", f"{mid_jnt}.scaleX", force=True)
    else:
        _maya('connectAttr', f"{blend_node}.outputR", f"{start_jnt}.scaleX")
        _maya('connectAttr', f"{blend_node}.outputR", f"{mid_jnt}.scaleX")
    created['driven_joints'] = (start_jnt, mid_jnt)

    # store metadata attributes so the system can be queried later
    meta_attr = f"{start_jnt}.stretchSystem_{name}"
    if IN_MAYA:
        try:
            if not cmds.attributeQuery('stretchSystem', node=start_jnt, exists=True):
                cmds.addAttr(start_jnt, longName='stretchSystem', dataType='string')
            cmds.setAttr(f"{start_jnt}.stretchSystem", name, type='string')
        except Exception:
            # non-critical
            pass

    # summary
    logger.info('Created stretch system: %s', created)
    return created


def create_from_selection(name: str = None):
    """Small helper: use a selection to build a stretch system.

    Selection rules (common one): select start joint, mid joint, end joint, then IK handle.
    If selection order differs, the function will attempt to find an IK handle in the selection.
    """
    if not IN_MAYA:
        print('create_from_selection only works inside Maya.')
        return

    sel = cmds.ls(selection=True) or []
    if len(sel) < 4:
        raise RuntimeError('Select start, mid, end joints and an IK handle (4 items).')

    # assume first 3 are joints and last is IK handle by default
    start_jnt, mid_jnt, end_jnt = sel[0:3]
    ik = sel[3]
    return create_stretch_ik_chain(ik_handle=ik, start_jnt=start_jnt, mid_jnt=mid_jnt, end_jnt=end_jnt, name=name)


if __name__ == '__main__':
    print('StretchSystemTool: run inside Maya or import functions in script editor.')
