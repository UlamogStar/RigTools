"""
    Simple Maya utility: enable override on curve shapes / joints and set their color.
    Run in Maya Script Editor (Python tab) or save as a module and import.
    Select controls and use the UI to enable overrides / change colors.
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


# UI
def create_ui():
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW, window=True)
    cmds.window(WINDOW, title="Color To Curve", widthHeight=(240, 120), sizeable=True)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8)

    cmds.button(label="Enable Color Override (selection)", height=36, command=lambda *a: enable_color_override_on_selection())
    cmds.separator(h=6, style='none')
    cmds.button(label="Pick RGB and Apply", height=36, command=lambda *a: _open_color_editor_and_apply())

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


create_ui()