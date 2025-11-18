"""
Simple Maya utility: enable override on curve shapes / joints and set their color.
- Run in Maya Script Editor (Python tab) or save as a module and import.
- Select controls and use the UI to enable overrides / change colors.
"""
import maya.cmds as cmds

WINDOW = "colorToCurveUI"


def enable_color_override_on_selection():
    sel = cmds.ls(sl=True, long=True) or []
    for node in sel:
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
        if shapes:
            for shp in shapes:
                try:
                    cmds.setAttr(shp + ".overrideEnabled", 1)
                except Exception:
                    pass
        else:
            try:
                cmds.setAttr(node + ".overrideEnabled", 1)
            except Exception:
                pass


def select_curve_transforms():
    """Select transforms that have nurbsCurve shapes (full paths)."""
    curves = cmds.ls(type="nurbsCurve", long=True) or []
    if not curves:
        cmds.warning("No nurbsCurve shapes found.")
        return
    parents = list(set(cmds.listRelatives(curves, parent=True, fullPath=True) or []))
    if parents:
        cmds.select(parents, r=True)


def _find_curve_shapes_by_markers(include_markers, exclude_markers=None):
    """Return nurbsCurve shape names that match include/exclude markers (case-insensitive)."""
    all_shapes = cmds.ls(type="nurbsCurve", long=True) or []
    include = [m.lower() for m in (include_markers or [])]
    exclude = [m.lower() for m in (exclude_markers or [])]
    matched = []
    for shp in all_shapes:
        s = shp.lower()
        if all(m in s for m in include) and not any(m in s for m in exclude):
            matched.append(shp)
    return list(set(matched))


def apply_color_to_shapes(shapes, color_index):
    if not shapes:
        return
    for shp in shapes:
        try:
            cmds.setAttr(shp + ".overrideEnabled", 1)
            # use index color
            cmds.setAttr(shp + ".overrideColor", int(color_index))
            # disable rgb override if present
            if cmds.attributeQuery("overrideRGBColors", node=shp, exists=True):
                try:
                    cmds.setAttr(shp + ".overrideRGBColors", 0)
                except Exception:
                    pass
        except Exception as e:
            cmds.warning("Failed to set color on {}: {}".format(shp, e))
    cmds.select(shapes, r=True)


def apply_index_to_selection(color_index):
    """Apply overrideColor index to selected curves/joints/transforms."""
    sel = cmds.ls(sl=True, long=True) or []
    if not sel:
        cmds.warning("Nothing selected.")
        return
    for node in sel:
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
        if shapes:
            for shp in shapes:
                if cmds.objectType(shp) == "nurbsCurve":
                    try:
                        cmds.setAttr(shp + ".overrideEnabled", 1)
                        cmds.setAttr(shp + ".overrideColor", int(color_index))
                        if cmds.attributeQuery("overrideRGBColors", node=shp, exists=True):
                            try:
                                cmds.setAttr(shp + ".overrideRGBColors", 0)
                            except Exception:
                                pass
                    except Exception as e:
                        cmds.warning("Failed on {}: {}".format(shp, e))
        else:
            # maybe a joint or transform
            try:
                if cmds.nodeType(node) == "joint" or cmds.attributeQuery("overrideColor", node=node, exists=True):
                    cmds.setAttr(node + ".overrideEnabled", 1)
                    cmds.setAttr(node + ".overrideColor", int(color_index))
                    if cmds.attributeQuery("overrideRGBColors", node=node, exists=True):
                        try:
                            cmds.setAttr(node + ".overrideRGBColors", 0)
                        except Exception:
                            pass
            except Exception:
                pass


def apply_rgb_to_selection(rgb):
    """Set RGB override on selection (uses overrideRGBColors + overrideColorRGB)."""
    if not rgb or len(rgb) != 3:
        cmds.warning("Invalid RGB color.")
        return
    sel = cmds.ls(sl=True, long=True) or []
    if not sel:
        cmds.warning("Nothing selected.")
        return
    r, g, b = rgb
    for node in sel:
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
        if shapes:
            for shp in shapes:
                try:
                    cmds.setAttr(shp + ".overrideEnabled", 1)
                    if cmds.attributeQuery("overrideRGBColors", node=shp, exists=True):
                        cmds.setAttr(shp + ".overrideRGBColors", 1)
                    # set double3 rgb attr if available
                    if cmds.attributeQuery("overrideColorRGB", node=shp, exists=True):
                        cmds.setAttr(shp + ".overrideColorRGB", float(r), float(g), float(b), type="double3")
                    else:
                        # fallback to index if rgb attrs not present
                        cmds.warning("RGB override not available on {}; using nearest index instead.".format(shp))
                except Exception as e:
                    cmds.warning("Failed to set RGB on {}: {}".format(shp, e))
        else:
            # joints / transforms
            try:
                if cmds.attributeQuery("overrideRGBColors", node=node, exists=True):
                    cmds.setAttr(node + ".overrideEnabled", 1)
                    cmds.setAttr(node + ".overrideRGBColors", 1)
                    if cmds.attributeQuery("overrideColorRGB", node=node, exists=True):
                        cmds.setAttr(node + ".overrideColorRGB", float(r), float(g), float(b), type="double3")
            except Exception:
                pass


# Example presets (includes FK detection)
def preset_left_ik_ctrls():
    shapes = _find_curve_shapes_by_markers(['|l_', '_ik_', '_ctrl'], exclude_markers=['|r_'])
    apply_color_to_shapes(shapes, 6)


def preset_right_ik_ctrls():
    shapes = _find_curve_shapes_by_markers(['|r_', '_ik_', '_ctrl'], exclude_markers=['|l_'])
    apply_color_to_shapes(shapes, 13)


def preset_general_ctrls():
    shapes = _find_curve_shapes_by_markers(['_ctrl'])
    apply_color_to_shapes(shapes, 17)


def select_fk_controls():
    """Select transforms that look like FK controls (contain '_fk_')."""
    shapes = _find_curve_shapes_by_markers(['_fk_'])
    if not shapes:
        # try looser match for 'fk' if no exact marker found
        shapes = _find_curve_shapes_by_markers(['fk'])
    if not shapes:
        cmds.warning("No FK curve shapes found.")
        return
    parents = list(set(cmds.listRelatives(shapes, parent=True, fullPath=True) or []))
    if parents:
        cmds.select(parents, r=True)


def preset_fk_left(color_index=13):
    shapes = _find_curve_shapes_by_markers(['|l_', '_fk_', '_ctrl'], exclude_markers=['|r_'])
    if not shapes:
        shapes = _find_curve_shapes_by_markers(['|l_', '_fk_'])
    apply_color_to_shapes(shapes, color_index)


def preset_fk_right(color_index=6):
    shapes = _find_curve_shapes_by_markers(['|r_', '_fk_', '_ctrl'], exclude_markers=['|l_'])
    if not shapes:
        shapes = _find_curve_shapes_by_markers(['|r_', '_fk_'])
    apply_color_to_shapes(shapes, color_index)


def apply_all_presets():
    preset_left_ik_ctrls()
    preset_right_ik_ctrls()
    preset_general_ctrls()


# UI
def create_ui():
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW, window=True)
    cmds.window(WINDOW, title="Color To Curve", widthHeight=(360, 320), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

    cmds.button(label="Enable Color Override (selection)", height=28, command=lambda *a: enable_color_override_on_selection())

    cmds.frameLayout(label="Presets", collapsable=True, collapse=False, mw=6, mh=6)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(115,115,115))
    cmds.button(label="Left IK -> 6", command=lambda *a: preset_left_ik_ctrls())
    cmds.button(label="Right IK -> 13", command=lambda *a: preset_right_ik_ctrls())
    cmds.button(label="General -> 17", command=lambda *a: preset_general_ctrls())
    cmds.setParent("..")

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(115,115,115))
    cmds.button(label="Select FK Controls", command=lambda *a: select_fk_controls())
    cmds.button(label="FK Left -> Blue", command=lambda *a: preset_fk_left(color_index=6))
    cmds.button(label="FK Right -> Red", command=lambda *a: preset_fk_right(color_index=13))
    cmds.setParent("..")
    cmds.setParent("..")  # end frame

    cmds.separator(h=6, style='none')
    cmds.text(label="Apply custom color index to selection (1-31)")
    # int slider for color index
    slider = cmds.intSliderGrp(field=True, label="Color Index", min=1, max=31, value=17)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(220,120))
    cmds.button(label="Apply Index to Selection", command=lambda *a: apply_index_to_selection(cmds.intSliderGrp(slider, q=True, value=True)))
    cmds.button(label="Pick RGB and Apply", command=lambda *a: _open_color_editor_and_apply())
    cmds.setParent("..")

    cmds.separator(h=6, style='none')
    cmds.text(label="Utilities")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.button(label="Select Curves", command=lambda *a: select_curve_transforms())
    cmds.button(label="Re-select Objects", command=lambda *a: cmds.select(cmds.ls(sl=True), r=True))
    cmds.setParent("..")

    cmds.showWindow(WINDOW)


def _open_color_editor_and_apply():
    # Open color editor and apply chosen rgb to selection
    try:
        # open dialog
        cmds.colorEditor()
        rgb = cmds.colorEditor(query=True, rgb=True)
        if rgb:
            apply_rgb_to_selection(rgb)
    except Exception as e:
        cmds.warning("Color editor failed: {}".format(e))


# Auto-launch
if __name__ == "__main__":
    create_ui()