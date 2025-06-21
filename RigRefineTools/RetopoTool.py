import maya.cmds as cmds
from RigTools.RigRefineTools.RetopoTool import apply_poly_reduce, apply_poly_remesh, apply_poly_retopo
from RigTools.RiggingTools.JoinCreationTools.jntSelectTool import selectRight, selectLeft, selectGeo
from RigTools.RiggingTools.ControlCreationTool.ControlCreateTool import create_controls_at_selected, create_groups_at_selected
from RigTools.RigRefineTools.TexturePathTool import update_texture_paths

def launch_unified_tool_ui():
    if cmds.window("unifiedToolWin", exists=True):
        cmds.deleteUI("unifiedToolWin")

    win = cmds.window("unifiedToolWin", title="Unified Rigging Tool", widthHeight=(500, 400))
    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

    # --- Retopology Tab ---
    retopo_tab = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, parent=tabs)
    cmds.text(label="Retopology Tools", align="center", height=20)
    cmds.separator(height=10, style='in')
    cmds.text(label="Reduce Polygon Count (%)")
    reduce_slider = cmds.intSliderGrp(field=True, minValue=1, maxValue=99, value=50, label='Target %')
    cmds.button(label="Apply polyReduce", command=lambda *_: apply_poly_reduce(cmds.intSliderGrp(reduce_slider, q=True, value=True)))
    cmds.separator(height=10, style='in')
    cmds.text(label="Remesh Edge Length")
    edge_length_field = cmds.floatFieldGrp(numberOfFields=1, label='Edge Length', value1=0.5)
    cmds.button(label="Apply polyRemesh", command=lambda *_: apply_poly_remesh(cmds.floatFieldGrp(edge_length_field, q=True, value1=True)))
    cmds.separator(height=10, style='in')
    cmds.button(label="Apply polyRetopo", command=lambda *_: apply_poly_retopo())

    # --- Joint Tools Tab ---
    joint_tab = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, parent=tabs)
    cmds.text(label="Joint Tools", align="center", height=20)
    cmds.separator(height=10, style='in')
    cmds.button(label="Select Right Joints", command=lambda *_: selectRight())
    cmds.button(label="Select Left Joints", command=lambda *_: selectLeft())
    cmds.button(label="Select Geometry", command=lambda *_: selectGeo())

    # --- Control Tools Tab ---
    control_tab = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, parent=tabs)
    cmds.text(label="Control Tools", align="center", height=20)
    cmds.separator(height=10, style='in')
    cmds.button(label="Create Groups at Selected", command=lambda *_: create_groups_at_selected())
    cmds.button(label="Create Controls at Selected", command=lambda *_: create_controls_at_selected())

    # --- Texture Path Tools Tab ---
    texture_tab = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, parent=tabs)
    cmds.text(label="Texture Path Tools", align="center", height=20)
    cmds.separator(height=10, style='in')
    path_field = cmds.textFieldButtonGrp("pathField", label='New Texture Folder', buttonLabel='Browse',
                                         buttonCommand=lambda *_: browse_and_set_path())
    cmds.button(label="Update Texture Paths", command=lambda *_: update_texture_paths(
        cmds.textFieldButtonGrp("pathField", query=True, text=True)))

    cmds.tabLayout(tabs, edit=True, tabLabel=[
        (retopo_tab, 'Retopology'),
        (joint_tab, 'Joint Tools'),
        (control_tab, 'Control Tools'),
        (texture_tab, 'Texture Paths')
    ])

    cmds.showWindow(win)

def browse_and_set_path():
    new_path = cmds.fileDialog2(fm=3, dialogStyle=2)
    if new_path:
        cmds.textFieldButtonGrp("pathField", edit=True, text=new_path[0])

# Launch the unified UI
launch_unified_tool_ui()