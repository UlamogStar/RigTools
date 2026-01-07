"""StretchSystemUI

Small Maya UI to test the `StretchSystemTool`.

Features:
- Pick start/mid/end joints and an IK handle via selection buttons.
- Create the stretch system from the fields or from selection.
- Simple options: toggle `Add Attr` and `Clamp Min`.

Usage (inside Maya):
    import StretchSystemUI
    StretchSystemUI.show_ui()
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

try:
    import maya.cmds as cmds
    IN_MAYA = True
except Exception:
    IN_MAYA = False

from functools import partial


def _set_field_from_selection(field):
    sel = cmds.ls(selection=True) or []
    if not sel:
        cmds.warning('Select an object first to populate the field.')
        return
    cmds.textFieldButtonGrp(field, e=True, text=sel[0])


def _create_from_fields(start_f, mid_f, end_f, ik_f, name_f, add_attr_cb, clamp_cb):
    start = cmds.textFieldButtonGrp(start_f, q=True, text=True)
    mid = cmds.textFieldButtonGrp(mid_f, q=True, text=True)
    end = cmds.textFieldButtonGrp(end_f, q=True, text=True)
    ik = cmds.textFieldButtonGrp(ik_f, q=True, text=True)
    name = cmds.textFieldGrp(name_f, q=True, text=True)
    add_attr = cmds.checkBox(add_attr_cb, q=True, value=True)
    clamp_min = cmds.checkBox(clamp_cb, q=True, value=True)

    if not all([start, mid, end, ik]):
        cmds.warning('Please fill start, mid, end joints and IK handle fields.')
        return

    try:
        import StretchSystemTool
    except Exception:
        cmds.warning('Could not import StretchSystemTool. Ensure it is in your script path.')
        return

    # run inside an undo chunk
    try:
        cmds.undoInfo(openChunk=True)
        StretchSystemTool.create_stretch_ik_chain(ik_handle=ik, start_jnt=start, mid_jnt=mid, end_jnt=end, name=name or None, clamp_min=clamp_min, add_attr=add_attr)
    except Exception as e:
        cmds.warning(f'Error creating stretch system: {e}')
    finally:
        cmds.undoInfo(closeChunk=True)


def show_ui():
    """Show the Stretch System UI in Maya."""
    if not IN_MAYA:
        print('DRY RUN: show_ui only runs inside Maya.')
        return

    win_name = 'StretchSystemToolWin'
    if cmds.window(win_name, exists=True):
        cmds.deleteUI(win_name)

    win = cmds.window(win_name, title='Stretch System Tool', widthHeight=(380, 220))
    main_col = cmds.columnLayout(adjustableColumn=True, rowSpacing=6, columnAlign='center')

    start_f = cmds.textFieldButtonGrp(label='Start Joint', buttonLabel='From Sel', cw3=[110,180,80])
    cmds.textFieldButtonGrp(start_f, e=True, bc=partial(_set_field_from_selection, start_f))

    mid_f = cmds.textFieldButtonGrp(label='Mid Joint', buttonLabel='From Sel', cw3=[110,180,80])
    cmds.textFieldButtonGrp(mid_f, e=True, bc=partial(_set_field_from_selection, mid_f))

    end_f = cmds.textFieldButtonGrp(label='End Joint', buttonLabel='From Sel', cw3=[110,180,80])
    cmds.textFieldButtonGrp(end_f, e=True, bc=partial(_set_field_from_selection, end_f))

    ik_f = cmds.textFieldButtonGrp(label='IK Handle', buttonLabel='From Sel', cw3=[110,180,80])
    cmds.textFieldButtonGrp(ik_f, e=True, bc=partial(_set_field_from_selection, ik_f))

    name_f = cmds.textFieldGrp(label='System Name', text='')

    opts_row = cmds.rowLayout(numberOfColumns=2, columnWidth2=[180,180], adjustableColumn=2)
    add_attr_cb = cmds.checkBox(label='Add Attr on IK', value=True)
    clamp_cb = cmds.checkBox(label='Clamp Min (no squash)', value=True)
    cmds.setParent('..')

    cmds.separator(height=8)

    btn_row = cmds.rowLayout(numberOfColumns=3, columnWidth3=[120,120,120], adjustableColumn=2)
    cmds.button(label='Create From Fields', command=lambda *a: _create_from_fields(start_f, mid_f, end_f, ik_f, name_f, add_attr_cb, clamp_cb))
    cmds.button(label='Create From Selection', command=lambda *a: _create_from_selection_shortcut(name_f, add_attr_cb, clamp_cb))
    cmds.button(label='Close', command=lambda *a: cmds.deleteUI(win))
    cmds.setParent('..')

    cmds.showWindow(win)


def _create_from_selection_shortcut(name_f, add_attr_cb, clamp_cb):
    sel = cmds.ls(selection=True) or []
    if len(sel) < 4:
        cmds.warning('Select start, mid, end joints and an IK handle (4 items) before pressing this.')
        return
    start, mid, end, ik = sel[0:4]

    try:
        import StretchSystemTool
    except Exception:
        cmds.warning('Could not import StretchSystemTool. Ensure it is in your script path.')
        return

    add_attr = cmds.checkBox(add_attr_cb, q=True, value=True)
    clamp_min = cmds.checkBox(clamp_cb, q=True, value=True)
    name = cmds.textFieldGrp(name_f, q=True, text=True) or None

    try:
        cmds.undoInfo(openChunk=True)
        StretchSystemTool.create_stretch_ik_chain(ik_handle=ik, start_jnt=start, mid_jnt=mid, end_jnt=end, name=name, clamp_min=clamp_min, add_attr=add_attr)
    except Exception as e:
        cmds.warning(f'Error creating stretch system: {e}')
    finally:
        cmds.undoInfo(closeChunk=True)


if __name__ == '__main__':
    if IN_MAYA:
        show_ui()
    else:
        print('StretchSystemUI: run inside Maya. This is a dry-run environment.')
