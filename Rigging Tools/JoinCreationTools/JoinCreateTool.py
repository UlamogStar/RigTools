import maya.cmds as cmds
import maya.mel as mel

created_joints = []  # Store created joints for hierarchy
side_option = "None"
part_option = "Arm"

def create_joints_at_selected(match_rotation=False):
    """Creates joints at the selected objects' positions with optional rotation matching."""
    global created_joints
    selected_objects = cmds.ls(selection=True, type='transform')

    if not selected_objects:
        cmds.warning("Select at least one object.")
        return

    created_joints = []  # Reset joint list

    for obj in selected_objects:
        cmds.select(clear=True)  # Avoid parenting issues
        joint = cmds.joint(name=obj + "_Jnt")
        cmds.matchTransform(joint, obj, position=True, rotation=match_rotation)
        created_joints.append(joint)

    cmds.select(created_joints)  # Select newly created joints
    cmds.inViewMessage(amg="Joints created successfully!", pos='midCenter', fade=True)

def rename_joints():
    """Renames created joints following user-defined naming conventions using MEL."""
    global created_joints, side_option, part_option

    if not created_joints:
        cmds.warning("No joints to rename.")
        return

    prefix = ""
    if side_option == "Left":
        prefix = "L_"
    elif side_option == "Right":
        prefix = "R_"

    for i, joint in enumerate(created_joints):
        new_name = f"{prefix}{part_option}_FK_{i:02d}_Jnt"
        mel.eval(f'rename "{joint}" "{new_name}"')
        created_joints[i] = new_name  # Update list with new names

    cmds.select(created_joints)
    cmds.inViewMessage(amg="Joints renamed successfully!", pos='midCenter', fade=True)

def group_and_parent_joints():
    """Groups and parents joints in proper hierarchy."""
    global created_joints, side_option, part_option

    if not created_joints:
        cmds.warning("No joints to group.")
        return

    prefix = ""
    if side_option == "Left":
        prefix = "L_"
    elif side_option == "Right":
        prefix = "R_"

    group_name = f"{prefix}{part_option}_Grp"

    if cmds.objExists(group_name):
        cmds.warning(f"Group {group_name} already exists.")
        return

    # Create group at the position of the first joint
    top_joint = created_joints[0]
    group_node = cmds.group(empty=True, name=group_name)
    cmds.matchTransform(group_node, top_joint, position=True)
    cmds.parent(top_joint, group_node)  # Parent first joint to the group

    # Parent joints in order
    for i in range(len(created_joints) - 1):
        cmds.parent(created_joints[i + 1], created_joints[i])

    cmds.select(group_node)
    cmds.inViewMessage(amg="Joints grouped & parented successfully!", pos='midCenter', fade=True)

def create_naming_ui():
    """Creates a UI for renaming settings."""
    global side_option, part_option

    naming_window = "jointNamingUI"
    if cmds.window(naming_window, exists=True):
        cmds.deleteUI(naming_window)

    cmds.window(naming_window, title="Joint Naming Settings", widthHeight=(300, 140), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    cmds.text(label="Select Side:")
    side_menu = cmds.optionMenu()
    cmds.menuItem(label="None")
    cmds.menuItem(label="Left")
    cmds.menuItem(label="Right")

    cmds.text(label="Select Part:")
    part_menu = cmds.optionMenu()
    cmds.menuItem(label="Arm")
    cmds.menuItem(label="Leg")
    cmds.menuItem(label="Tail")
    cmds.menuItem(label="Hand")
    cmds.menuItem(label="Foot")

    def update_options(*args):
        """Updates global variables based on UI selection."""
        global side_option, part_option
        side_option = cmds.optionMenu(side_menu, query=True, value=True)
        part_option = cmds.optionMenu(part_menu, query=True, value=True)
        cmds.inViewMessage(amg=f"Naming updated: {side_option}_{part_option}", pos='midCenter', fade=True)

    cmds.button(label="Apply Naming Settings", command=update_options, bgc=(0.5, 0.5, 0.7))
    cmds.showWindow(naming_window)

def create_main_ui():
    """Creates the main UI for the joint creation tool."""
    window_name = "jointCreationUI"

    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    cmds.window(window_name, title="Joint Creation Tool", widthHeight=(300, 250), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    cmds.text(label="Select objects and create joints at their positions.")

    cmds.button(label="Create Joints (Position Only)",
                command=lambda *args: create_joints_at_selected(match_rotation=False),
                bgc=(0.3, 0.6, 0.3))

    cmds.button(label="Create Joints (Match Position & Rotation)",
                command=lambda *args: create_joints_at_selected(match_rotation=True),
                bgc=(0.3, 0.3, 0.6))

    cmds.separator(height=10, style='in')

    cmds.button(label="Set Joint Naming Convention",
                command=lambda *args: create_naming_ui(),
                bgc=(0.5, 0.5, 0.7))

    cmds.button(label="Rename Joints",
                command=lambda *args: rename_joints(),
                bgc=(0.6, 0.4, 0.2))

    cmds.separator(height=10, style='in')

    cmds.button(label="Group & Parent Joints (Per Chain)",
                command=lambda *args: group_and_parent_joints(),
                bgc=(0.6, 0.3, 0.3))

    cmds.showWindow(window_name)

# Run the UI
create_main_ui()
