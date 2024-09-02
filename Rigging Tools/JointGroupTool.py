import maya.cmds as cmds

def parent_joints():
    # Get the selected joints
    selected_joints = cmds.ls(selection=True)
    
    if len(selected_joints) < 2:
        cmds.warning("Select at least two joints.")
        return
    
    # Parent the joints in order of selection
    for i in range(1, len(selected_joints)):
        cmds.parent(selected_joints[i], selected_joints[i - 1])

def create_ui():
    # Check if the window exists, and if so, delete it
    if cmds.window("jointParentingUI", exists=True):
        cmds.deleteUI("jointParentingUI")
    
    # Create a new window
    window = cmds.window("jointParentingUI", title="Joint Parenting Tool", widthHeight=(200, 30))
    
    # Create a column layout
    cmds.columnLayout(adjustableColumn=False)
    
    # Add a button that calls the parent_joints function
    cmds.button(label="Parent Joints", command=lambda *args: parent_joints())
    
    # Show the window
    cmds.showWindow(window)

# Run the UI
create_ui()
