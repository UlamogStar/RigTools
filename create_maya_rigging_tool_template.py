import os

base = "maya_rigging_tool"
submodules = [
    "ikfk_rk_rig",
    "squash_stretch",
    "follow_switch",
    "twist_system",
    "spring_ik",      # Added
    "spline_ik"       # Added
]
files = {
    "__init__.py": 'from .main_ui import show_main_rigging_tool_hub\n',
    "main_ui.py": '''import maya.cmds as cmds

def open_ikfk_rk_ui(*_):
    from maya_rigging_tool.ikfk_rk_rig.ui import show_ikfk_rk_window
    show_ikfk_rk_window()

def open_squash_stretch_ui(*_):
    from maya_rigging_tool.squash_stretch.ui import show_squash_stretch_window
    show_squash_stretch_window()

def open_follow_switch_ui(*_):
    from maya_rigging_tool.follow_switch.ui import show_follow_switch_window
    show_follow_switch_window()

def open_twist_system_ui(*_):
    from maya_rigging_tool.twist_system.ui import show_twist_system_window
    show_twist_system_window()

def open_spring_ik_ui(*_):
    from maya_rigging_tool.spring_ik.ui import show_spring_ik_window
    show_spring_ik_window()

def open_spline_ik_ui(*_):
    from maya_rigging_tool.spline_ik.ui import show_spline_ik_window
    show_spline_ik_window()

def show_main_rigging_tool_hub():
    win = "riggingToolHubWin"
    if cmds.window(win, exists=True):
        cmds.deleteUI(win)
    cmds.window(win, title="Rigging Tool Hub", widthHeight=(300, 300))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)
    cmds.text(label="Rigging Tool Hub", align="center", height=30)
    cmds.separator(height=10, style='in')
    cmds.button(label="IK/FK/RK Rig Setup", command=open_ikfk_rk_ui)
    cmds.button(label="Squash & Stretch Setup", command=open_squash_stretch_ui)
    cmds.button(label="Follow Switching Setup", command=open_follow_switch_ui)
    cmds.button(label="Twist System Setup", command=open_twist_system_ui)
    cmds.button(label="Spring IK Setup", command=open_spring_ik_ui)
    cmds.button(label="Spline IK Setup", command=open_spline_ik_ui)
    cmds.setParent('..')
    cmds.showWindow(win)
'''
}

submodule_ui = '''import maya.cmds as cmds

def show_{name}_window():
    win = "{name}Window"
    if cmds.window(win, exists=True):
        cmds.deleteUI(win)
    window = cmds.window(win, title="{title}", widthHeight=(350, 250))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="{title} Tool", align="center")
    cmds.separator(height=10, style='in')
    cmds.button(label="Run {title} Logic", command="maya_rigging_tool.{name}.logic.run_logic()")
    cmds.setParent('..')
    cmds.showWindow(window)
'''

submodule_logic = '''import maya.cmds as cmds

def run_logic():
    cmds.confirmDialog(title="Info", message="{title} logic goes here.")
'''

os.makedirs(base, exist_ok=True)
for fname, content in files.items():
    with open(os.path.join(base, fname), "w") as f:
        f.write(content)

for sub in submodules:
    subdir = os.path.join(base, sub)
    os.makedirs(subdir, exist_ok=True)
    with open(os.path.join(subdir, "__init__.py"), "w") as f:
        f.write("")
    # UI
    title = sub.replace("_", " ").title()
    with open(os.path.join(subdir, "ui.py"), "w") as f:
        f.write(submodule_ui.format(name=sub, title=title))
    # Logic
    with open(os.path.join(subdir, "logic.py"), "w") as f:
        f.write(submodule_logic.format(title=title))

print("maya_rigging_tool workspace template created!")