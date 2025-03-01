import maya.cmds as cmds
import re

created_joints = []  # Store created joints for grouping

def create_joints_at_selected(match_rotation=False):
    """Creates joints at the selected objects' positions with optional rotation matching."""
    global created_joints
    selected_objects = cmds.ls(selection=True, type='transform')
    
    if not selected_objects:
        cmds.warning("Select at least one object.")
        return
    
    created_joints = []  # Reset joint list
    
    for obj in selected_objects:
        cmds.select(clear=True)  # Avoids parenting issues
        
        joint_name = obj + "_Jnt"
        
        # Ensure unique joint names
        if cmds.objExists(joint_name):
            joint_name = cmds.rename(joint_name, obj + "_Jnt1")

        joint = cmds.joint(name=joint_name)
        cmds.matchTransform(joint, obj, position=True, rotation=match_rotation)
        
        created_joints.append(joint)

    cmds.select(created_joints)  # Select the created joints for user convenience
    cmds.inViewMessage(amg="Joints created successfully!", pos='midCenter', fade=True)

def extract_group_name(name):
    """Extracts the main joint group name (e.g., 'L_Hand' from 'L_Hand_Jnt_01')."""
    match = re.match(r"([A-Za-z]+_[A-Za-z]+)", name)
    return match.group(1) if match else None

def extract_number(name):
    """Extracts the numerical part of a name for sorting, defaults to high value if no number."""
    numbers = re.findall(r'\d+', name)
    return int(numbers[-1]) if numbers else float('inf')  # Sort names without numbers last

def group_and_parent_joints():
    """Groups the created joints and parents them hierarchically within their respective chains."""
    global created_joints
    
    if not created_joints:
        cmds.warning("No joints have been created yet.")
        return
    
    # Organize joints into groups based on their prefix (e.g., 'L_Hand')
    joint_groups = {}
    for joint in created_joints:
        group_name = extract_group_name(joint)
        if group_name:
            if group_name not in joint_groups:
                joint_groups[group_name] = []
            joint_groups[group_name].append(joint)

    # Process each group separately
    for group_name, joints in joint_groups.items():
        sorted_joints = sorted(joints, key=extract_number)

        # Create a group for the joint chain
        group_node = f"{group_name}_Grp"
        if cmds.objExists(group_node):
            group_node = cmds.rename(group_node, group_name + "_Grp1")

        cmds.group(sorted_joints, name=group_node)

        # Parent joints in order within their respective group
        for i in range(len(sorted_joints) - 1):
            cmds.parent(sorted_joints[i + 1], sorted_joints[i])  # Parent next joint to the current one

    cmds.inViewMessage(amg="Joints grouped & parented within their chains!", pos='midCenter', fade=True)

def create_ui():
    """Creates a UI for the joint creation tool."""
    window_name = "jointCreationUI"

    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    cmds.window(window_name, title="Joint Creation Tool", widthHeight=(300, 180), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    cmds.text(label="Select objects and create joints at their position.")
    
    cmds.button(label="Create Joints (Position Only)", 
                command=lambda *args: create_joints_at_selected(match_rotation=False),
                bgc=(0.3, 0.6, 0.3))

    cmds.button(label="Create Joints (Match Position & Rotation)", 
                command=lambda *args: create_joints_at_selected(match_rotation=True),
                bgc=(0.3, 0.3, 0.6))

    cmds.separator(height=10, style='in')

    cmds.button(label="Group & Parent Joints (Per Chain)", 
                command=lambda *args: group_and_parent_joints(),
                bgc=(0.6, 0.3, 0.3))

    cmds.showWindow(window_name)

# Run the UI
create_ui()
