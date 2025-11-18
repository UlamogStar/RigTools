import re
import maya.cmds as cmds

def _ensure_attr(node, attr, attrType='double', default=1.0, minValue=0.0, maxValue=1.0):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, attributeType=attrType, minValue=minValue, maxValue=maxValue, defaultValue=default, keyable=True)
    else:
        try:
            cmds.setAttr('{}.{}'.format(node, attr), e=True, keyable=True)
        except Exception:
            pass

def _find_joint_for_ctrl(ctrl):
    """Try common name conversions and loose matching to find a corresponding joint."""
    short = ctrl.split('|')[-1]
    # candidate replacements
    candidates = []
    candidates += [short.replace('_Ctrl', '_Jnt'), short.replace('_ctrl', '_Jnt'),
                   short.replace('Ctrl', 'Jnt'), short.replace('ctrl', 'Jnt'),
                   short + '_Jnt', short + '_jnt']
    # try direct candidates
    for c in candidates:
        if cmds.objExists(c) and cmds.nodeType(c) == 'joint':
            return c
        # also try full path style names
        if cmds.objExists('|' + c) and cmds.nodeType('|' + c) == 'joint':
            return '|' + c
    # fallback: loose base name match (strip common ctrl suffixes)
    base = re.sub(r'(_ctrl$|_Ctrl$|Ctrl$|ctrl$)', '', short)
    all_joints = cmds.ls(type='joint', long=True) or []
    if not base:
        return None
    # prefer exact contains match
    for j in all_joints:
        if base.lower() in j.split('|')[-1].lower():
            return j
    # last resort: any joint with same start token
    token = base.split('_')[0]
    for j in all_joints:
        if j.split('|')[-1].lower().startswith(token.lower()):
            return j
    return None

def setup_follow_on_selection():
    """
    For each selected control transform, try to find a matching joint (by name)
    and create translate/rotate/scale constraints on that joint driven by the control.
    Adds FollowTranslate / FollowRotate / FollowScale attributes on the control
    and connects them to the constraint weight attributes.
    Operates only on the current selection.
    """
    sels = cmds.ls(selection=True, long=True) or []
    if not sels:
        cmds.warning("Select control transform(s) to setup follow system.")
        return

    processed = []
    for ctrl in sels:
        if not cmds.objExists(ctrl):
            continue
        # find the joint that corresponds to this control
        joint = _find_joint_for_ctrl(ctrl)
        if not joint:
            cmds.warning("No matching joint found for control: {}".format(ctrl))
            continue

        # create attributes on the control
        _ensure_attr(ctrl, 'FollowTranslate', default=1.0)
        _ensure_attr(ctrl, 'FollowRotate', default=1.0)
        _ensure_attr(ctrl, 'FollowScale', default=1.0)

        # create translate-only parentConstraint (skipRotate)
        try:
            # If a constraint already exists from this ctrl to the joint, we still create a new one
            p_constraint_T = cmds.parentConstraint(ctrl, joint, mo=True, skipRotate=['x', 'y', 'z'], weight=1)[0]
        except Exception as e:
            cmds.warning("Failed to create translate constraint for {} -> {}: {}".format(ctrl, joint, e))
            p_constraint_T = None

        # create rotate-only parentConstraint (skipTranslate)
        try:
            p_constraint_R = cmds.parentConstraint(ctrl, joint, mo=True, skipTranslate=['x', 'y', 'z'], weight=1)[0]
        except Exception as e:
            cmds.warning("Failed to create rotate constraint for {} -> {}: {}".format(ctrl, joint, e))
            p_constraint_R = None

        # create scale constraint
        try:
            p_constraint_S = cmds.scaleConstraint(ctrl, joint, mo=True, weight=1)[0]
        except Exception as e:
            cmds.warning("Failed to create scale constraint for {} -> {}: {}".format(ctrl, joint, e))
            p_constraint_S = None

        # connect control attributes to the constraint weights (if present)
        try:
            if p_constraint_T and cmds.objExists("{}.w0".format(p_constraint_T)):
                cmds.connectAttr("{}.FollowTranslate".format(ctrl), "{}.w0".format(p_constraint_T), force=True)
        except Exception as e:
            cmds.warning("Connect failed (Translate) for {}: {}".format(ctrl, e))
        try:
            if p_constraint_R and cmds.objExists("{}.w0".format(p_constraint_R)):
                cmds.connectAttr("{}.FollowRotate".format(ctrl), "{}.w0".format(p_constraint_R), force=True)
        except Exception as e:
            cmds.warning("Connect failed (Rotate) for {}: {}".format(ctrl, e))
        try:
            if p_constraint_S and cmds.objExists("{}.w0".format(p_constraint_S)):
                cmds.connectAttr("{}.FollowScale".format(ctrl), "{}.w0".format(p_constraint_S), force=True)
        except Exception as e:
            cmds.warning("Connect failed (Scale) for {}: {}".format(ctrl, e))

        processed.append((ctrl, joint))

    if processed:
        msg = "Setup follow on {} control(s).".format(len(processed))
        cmds.inViewMessage(amg=msg, pos='topCenter', fade=True)
    else:
        cmds.warning("No follow setups were created.")

# If this file is run directly, run the setup on current selection
if __name__ == "__main__":
    setup_follow_on_selection()
