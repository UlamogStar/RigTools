import maya.cmds as cmds


def setup_prop_follow(prop_group, left_target, right_target, attr_name='followHand'):
    # -------------------------
    # Validation
    # -------------------------
    for obj, label in (
        (prop_group, "Prop group"),
        (left_target, "Left target"),
        (right_target, "Right target"),
    ):
        if not cmds.objExists(obj):
            raise RuntimeError(f"{label} '{obj}' does not exist.")

    # -------------------------
    # Buffer group (NO movement)
    # -------------------------
    buffer_grp = f"{prop_group}_followBuffer"
    if not cmds.objExists(buffer_grp):
        buffer_grp = cmds.group(empty=True, name=buffer_grp)
        cmds.delete(cmds.parentConstraint(prop_group, buffer_grp))
        parent = cmds.listRelatives(prop_group, parent=True)
        if parent:
            cmds.parent(buffer_grp, parent[0])
        cmds.parent(prop_group, buffer_grp)

    # -------------------------
    # Enum attribute
    # -------------------------
    if not cmds.attributeQuery(attr_name, node=prop_group, exists=True):
        cmds.addAttr(
            prop_group,
            ln=attr_name,
            at='enum',
            en='Off:Left:Right',
            keyable=True
        )
        cmds.setAttr(f"{prop_group}.{attr_name}", 0)

    # -------------------------
    # Constraints on buffer
    # -------------------------
    constr_left = cmds.parentConstraint(
        left_target, buffer_grp, mo=False,
        name=f"{prop_group}_follow_left_parentConstraint"
    )[0]

    constr_right = cmds.parentConstraint(
        right_target, buffer_grp, mo=False,
        name=f"{prop_group}_follow_right_parentConstraint"
    )[0]

    # Force weights
    cmds.setAttr(constr_left + ".target[0].targetWeight", 1)
    cmds.setAttr(constr_right + ".target[0].targetWeight", 1)

    # Disable initially
    cmds.setAttr(constr_left + ".enable", 0)
    cmds.setAttr(constr_right + ".enable", 0)

    # -------------------------
    # Condition nodes to drive target weights
    # -------------------------
    cond_left = cmds.createNode('condition', name=f"{prop_group}_cond_left")
    cond_right = cmds.createNode('condition', name=f"{prop_group}_cond_right")

    for cond, term in ((cond_left, 1), (cond_right, 2)):
        cmds.setAttr(cond + ".operation", 2)  # equal
        cmds.setAttr(cond + ".firstTerm", term)
        cmds.setAttr(cond + ".colorIfTrueR", 1)
        cmds.setAttr(cond + ".colorIfFalseR", 0)
        cmds.connectAttr(
            f"{prop_group}.{attr_name}",
            cond + ".secondTerm",
            force=True
        )

    # Connect condition outputs to constraint target weights (not enable)
    cmds.connectAttr(cond_left + ".outColorR", constr_left + ".target[0].targetWeight", force=True)
    cmds.connectAttr(cond_right + ".outColorR", constr_right + ".target[0].targetWeight", force=True)

    # -------------------------
    # Force SNAP on enum change using matchTransform
    # -------------------------
    def snap_on_switch():
        val = cmds.getAttr(f"{prop_group}.{attr_name}")
        if val == 1:
            cmds.matchTransform(buffer_grp, left_target, pos=True, rot=True)
        elif val == 2:
            cmds.matchTransform(buffer_grp, right_target, pos=True, rot=True)
        # val == 0 (Off): leave buffer_grp where it is

    cmds.scriptJob(
        attributeChange=[f"{prop_group}.{attr_name}", snap_on_switch],
        protected=True
    )

    return constr_left, constr_right


# --------------------------------------------------------------------
# UI (unchanged)
# --------------------------------------------------------------------

def show_ui():
    win = 'propFollowUI'
    if cmds.window(win, exists=True):
        cmds.deleteUI(win)

    cmds.window(win, title='Prop Follow Setup', widthHeight=(360, 220), sizeable=True)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8)

    cmds.text(label='Select objects in the scene then use Load Selection.')

    cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'))
    cmds.text(label='Prop Control:')
    prop_field = cmds.textField()
    cmds.button(label='Load', command=lambda *_: cmds.textField(
        prop_field, e=True, text=_get_sel_first()
    ))
    cmds.setParent('..')

    cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'))
    cmds.text(label='Left Target:')
    left_field = cmds.textField()
    cmds.button(label='Load', command=lambda *_: cmds.textField(
        left_field, e=True, text=_get_sel_first()
    ))
    cmds.setParent('..')

    cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'))
    cmds.text(label='Right Target:')
    right_field = cmds.textField()
    cmds.button(label='Load', command=lambda *_: cmds.textField(
        right_field, e=True, text=_get_sel_first()
    ))
    cmds.setParent('..')

    cmds.separator(h=10)

    cmds.rowLayout(numberOfColumns=2, columnAlign=(1, 'center'))
    cmds.button(
        label='Setup Follow',
        height=30,
        bgc=(0.3, 0.6, 0.3),
        command=lambda *_: _ui_do_setup(prop_field, left_field, right_field)
    )
    cmds.button(
        label='Close',
        height=30,
        bgc=(0.6, 0.3, 0.3),
        command=lambda *_: cmds.deleteUI(win)
    )
    cmds.setParent('..')

    cmds.showWindow(win)


def _get_sel_first():
    sel = cmds.ls(selection=True, long=False) or []
    return sel[0] if sel else ''


def _ui_do_setup(prop_field, left_field, right_field):
    prop = cmds.textField(prop_field, q=True, text=True)
    left = cmds.textField(left_field, q=True, text=True)
    right = cmds.textField(right_field, q=True, text=True)

    if not prop or not left or not right:
        cmds.warning('Please fill all fields.')
        return

    try:
        setup_prop_follow(prop, left, right)
    except Exception as e:
        cmds.warning(str(e))
        return

    cmds.inViewMessage(amg='Prop follow setup complete.', pos='midCenter', fade=True)


if __name__ == '__main__':
    show_ui()
