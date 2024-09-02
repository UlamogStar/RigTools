import maya.cmds as cmds

def create_joints_at_selected():
    # Get the selected objects
    selected_objects = cmds.ls(selection=True, type='transform')
    
    if not selected_objects:
        cmds.warning("Select at least one object.")
        return
    
    # Create joints at each selected object's position
    for obj in selected_objects:
        # Clear the selection to avoid parenting the joint to the object
        cmds.select(clear=True)
        
        # Create a joint at the origin
        joint = cmds.joint(name=obj + "_jnt")
        
        # Match the joint's transform to the selected object's transform
        cmds.matchTransform(joint, obj, position=True, rotation=False)

def create_ui():
    # Check if the window exists, and if so, delete it
    if cmds.window("jointCreationUI", exists=True):
        cmds.deleteUI("jointCreationUI")
    
    # Create a new window
    window = cmds.window("jointCreationUI", title="Joint Creation Tool", widthHeight=(200, 200))
    
    # Create a column layout
    cmds.columnLayout(adjustableColumn=False)
    
    # Add a button that calls the create_joints_at_selected function
    cmds.button(label="Create Joints at Selected", command=lambda *args: create_joints_at_selected())
    
    # Show the window
    cmds.showWindow(window)

# Run the UI
create_ui()

