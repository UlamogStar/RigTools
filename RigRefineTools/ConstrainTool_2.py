import maya.cmds as cmds
import fnmatch


def match_controls_to_joints(suffix_joint='_Jnt', suffix_ctrl='_Ctrl', maintain_offset=False, ignore_constrained=True, ignore_ik_joints=False):
    """
    Finds joints and controls by name suffix, matches them by the base name
    (name without the suffix) and applies point, orient and scale constraints
    from the control -> joint.

    Args:
        suffix_joint (str): joint name suffix (default '_Jnt')
        suffix_ctrl (str): control name suffix (default '_Ctrl')
        maintain_offset (bool): whether to maintain offset when creating constraints
        ignore_constrained (bool): skip joints that already have constraints
        ignore_ik_joints (bool): skip joints with 'IK' in their name
    Returns:
        list of (control, joint) pairs constrained
    """
    # collect joints
    joints = cmds.ls('*' + suffix_joint, type='joint') or []

    # collect transforms that look like controls (ending with suffix)
    all_transforms = cmds.ls(type='transform') or []
    ctrls = [t for t in all_transforms if t.endswith(suffix_ctrl)]

    def base_name(name, suffix):
        if name.endswith(suffix):
            return name[:-len(suffix)]
        return None

    joint_map = {base_name(j, suffix_joint): j for j in joints if base_name(j, suffix_joint)}
    ctrl_map = {base_name(c, suffix_ctrl): c for c in ctrls if base_name(c, suffix_ctrl)}

    pairs = []
    for b, j in joint_map.items():
        c = ctrl_map.get(b)
        if c:
            pairs.append((c, j))

    if not pairs:
        cmds.warning('No matching control/joint pairs found using suffixes: %s, %s' % (suffix_joint, suffix_ctrl))
        return []

    def is_joint_constrained(jnt):
        """Return True if the joint already has constraint nodes connected to it."""
        constraint_types = ['parentConstraint', 'pointConstraint', 'orientConstraint', 'scaleConstraint', 'aimConstraint']
        for ct in constraint_types:
            conns = cmds.listConnections(jnt, type=ct) or []
            if conns:
                return True
        return False

    created = []
    cmds.undoInfo(openChunk=True)
    try:
        for c, j in pairs:
            if ignore_constrained and is_joint_constrained(j):
                # skip joints that already have constraints
                continue
            if ignore_ik_joints and 'IK' in j:
                # skip IK joints
                continue
            # create translation (point), rotation (orient) and scale constraints from control -> joint
            # use explicit names to make it easy to find them; Maya will uniquify if needed
            point_name = j + '_pointConstraint'
            orient_name = j + '_orientConstraint'
            scale_name = j + '_scaleConstraint'

            # create constraints
            pc = cmds.pointConstraint(c, j, maintainOffset=maintain_offset, name=point_name)
            oc = cmds.orientConstraint(c, j, maintainOffset=maintain_offset, name=orient_name)
            sc = cmds.scaleConstraint(c, j, maintainOffset=maintain_offset, name=scale_name)

            created.append({'joint': j, 'control': c, 'point': pc, 'orient': oc, 'scale': sc})

        cmds.inViewMessage(amg='%d control->joint constraint pairs created.' % len(created), pos='topCenter', fade=True)
    finally:
        cmds.undoInfo(closeChunk=True)

    return [(c['control'], c['joint']) for c in created]


if __name__ == '__main__':
    match_controls_to_joints()