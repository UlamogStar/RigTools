import maya.cmds as cmds

# ======================================================
# IK FOLLOW SYSTEM
# Improved: condition -> multDoubleLinear -> constraint weight
# Ensures each constraint weight has an explicit node chain
# visible in the Connection Editor and gives full weight
# when selected via the FollowTarget enum.
# ======================================================


def _safe_short_name(obj):
    sn = cmds.ls(obj, sn=True)
    return sn[0] if sn else obj


def _sanitize_node_name(name):
    # Replace characters that are unsafe in node names
    for ch in ['|', ':', ' ', '-', '.']:
        name = name.replace(ch, '_')
    return name


def addIKFollowSystem(ik_ctrl, cog_ctrl, trans_ctrl, world_ctrl):

    for obj in [ik_ctrl, cog_ctrl, trans_ctrl, world_ctrl]:
        if not cmds.objExists(obj):
            cmds.error(f"{obj} does not exist.")

    parent = cmds.listRelatives(ik_ctrl, parent=True)
    if not parent:
        cmds.error("IK control must be grouped.")
    grp = parent[0]

    # ---------------------------
    # ATTRIBUTE
    # ---------------------------
    if not cmds.attributeQuery("FollowTarget", node=ik_ctrl, exists=True):
        cmds.addAttr(
            ik_ctrl,
            ln="FollowTarget",
            at="enum",
            en="None:COG:Transform:World",
            k=True
        )
        cmds.setAttr(f"{ik_ctrl}.FollowTarget", 0)

    # ---------------------------
    # CONSTRAINT
    # ---------------------------
    pcon = cmds.parentConstraint(
        cog_ctrl,
        trans_ctrl,
        world_ctrl,
        grp,
        mo=True,
        n=f"{_sanitize_node_name(ik_ctrl)}_Follow_PCon"
    )[0]

    weights = cmds.parentConstraint(pcon, q=True, wal=True)
    # Try to get the ordered list of targets for robust mapping
    try:
        targets = cmds.parentConstraint(pcon, q=True, tl=True)
    except Exception:
        try:
            targets = cmds.parentConstraint(pcon, q=True, t=True)
        except Exception:
            targets = None

    # ---------------------------
    # TARGET ENUM VALUES
    # ---------------------------
    enum_map = {
        "COG": 1,
        "TRANSFORM": 2,
        "WORLD": 3
    }

    # get short names for matching
    cog_sn = _safe_short_name(cog_ctrl).lower()
    trans_sn = _safe_short_name(trans_ctrl).lower()
    world_sn = _safe_short_name(world_ctrl).lower()

    # ---------------------------
    # EXCLUSIVE WEIGHT LOGIC (robust mapping)
    # Map each weight to its corresponding target by index when possible.
    # Build explicit node chains: condition -> multDoubleLinear -> weight
    # ---------------------------
    for idx, weight in enumerate(weights):
        # Determine the target this weight corresponds to
        target_obj = None
        if targets and idx < len(targets):
            target_obj = targets[idx]

        label = weight.split("W")[0]
        label_clean = label.upper()

        enum_val = None
        # Prefer explicit target mapping if available
        if target_obj:
            target_sn = _safe_short_name(target_obj).lower()
            if target_sn == cog_sn:
                enum_val = enum_map["COG"]
            elif target_sn == trans_sn:
                enum_val = enum_map["TRANSFORM"]
            elif target_sn == world_sn:
                enum_val = enum_map["WORLD"]
        else:
            # Fallback to substring matching on the weight label
            if cog_sn in label.lower():
                enum_val = enum_map["COG"]
            elif trans_sn in label.lower():
                enum_val = enum_map["TRANSFORM"]
            elif world_sn in label.lower():
                enum_val = enum_map["WORLD"]

        if enum_val is None:
            # Could not match weight to any provided source; skip
            continue

        safe_label = _sanitize_node_name(f"{_sanitize_node_name(ik_ctrl)}_{label_clean}")

        # Create condition node
        cond = cmds.createNode(
            "condition",
            n=f"{safe_label}_Follow_COND"
        )

        cmds.setAttr(f"{cond}.operation", 0)      # Equal
        cmds.setAttr(f"{cond}.secondTerm", enum_val)
        cmds.setAttr(f"{cond}.colorIfTrueR", 1)
        cmds.setAttr(f"{cond}.colorIfFalseR", 0)

        # Connect enum attr to condition.firstTerm
        try:
            cmds.connectAttr(
                f"{ik_ctrl}.FollowTarget",
                f"{cond}.firstTerm",
                force=True
            )
        except Exception:
            # If the enum is already connected elsewhere, leave it
            pass

        # Create a simple multiplier node so the Connection Editor shows
        # an explicit chain (and to allow future scaling if needed).
        mdl = cmds.createNode('multDoubleLinear', n=f"{safe_label}_Follow_MDL")
        # Ensure it multiplies by 1
        try:
            cmds.setAttr(f"{mdl}.input2", 1)
        except Exception:
            pass

        # Connect condition output to multiplier input1
        try:
            cmds.connectAttr(f"{cond}.outColorR", f"{mdl}.input1", force=True)
        except Exception:
            pass

        # If the constraint weight has existing incoming connections, break them
        existing = cmds.listConnections(f"{pcon}.{weight}", s=True, d=False, plugs=True)
        if existing:
            for src in existing:
                try:
                    cmds.disconnectAttr(src, f"{pcon}.{weight}")
                except Exception:
                    pass

        # Connect final output to the constraint weight
        try:
            cmds.connectAttr(f"{mdl}.output", f"{pcon}.{weight}", force=True)
        except Exception:
            # Fallback: connect condition directly
            try:
                cmds.connectAttr(f"{cond}.outColorR", f"{pcon}.{weight}", force=True)
            except Exception:
                pass

    print(f"Follow system added to {ik_ctrl}")


# ======================================================
# UI (CLEANED UP)
# ======================================================

def _loadSelection(field):
    sel = cmds.ls(sl=True)
    if sel:
        cmds.textField(field, e=True, text=sel[0])


def _applyFromUI():
    addIKFollowSystem(
        cmds.textField("ikField", q=True, text=True),
        cmds.textField("cogField", q=True, text=True),
        cmds.textField("transField", q=True, text=True),
        cmds.textField("worldField", q=True, text=True)
    )


def buildIKFollowUI():

    if cmds.window("IKFollowUI", exists=True):
        cmds.deleteUI("IKFollowUI")

    cmds.window("IKFollowUI", title="IK Follow (Simple)", w=360)
    cmds.columnLayout(adj=True, rs=6)

    for label, field in [
        ("IK Control", "ikField"),
        ("COG Control", "cogField"),
        ("Transform Control", "transField"),
        ("World Group", "worldField")
    ]:
        cmds.rowLayout(nc=3, adj=2)
        cmds.text(label=label)
        cmds.textField(field)
        cmds.button(
            label="Load",
            c=lambda _, f=field: _loadSelection(f)
        )
        cmds.setParent("..")

    cmds.separator(h=10)

    cmds.button(
        label="Add Follow System",
        h=40,
        bgc=(0.25, 0.45, 0.25),
        c=lambda *_: _applyFromUI()
    )

    cmds.showWindow("IKFollowUI")


if __name__ == '__main__':
    buildIKFollowUI()
