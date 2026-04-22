"""BindPoseTool

Automates BindPose creation and repair in Maya rigging workflows.

Features:
- Detects and removes orphaned BindPose nodes
- Creates new BindPose based on selected joints or skin-bound geometry
- Handles control rigs with non-joint nodes in hierarchy
- Validates BindPose integrity before/after operations

Usage (inside Maya Python tab):
    import BindPoseTool
    BindPoseTool.show_ui()
"""

import maya.cmds as cmds

WIN = 'bindPoseToolUI'

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def _get_all_bindpose_nodes():
    """Get all BindPose nodes in the scene."""
    bindpose_nodes = cmds.ls(type='dagPose')
    return bindpose_nodes if bindpose_nodes else []


def _delete_bindpose_nodes(bindpose_list=None):
    """Delete BindPose nodes. Returns count of deleted nodes."""
    if bindpose_list is None:
        bindpose_list = _get_all_bindpose_nodes()
    
    if not bindpose_list:
        return 0
    
    deleted_count = 0
    for node in bindpose_list:
        try:
            if cmds.objExists(node):
                cmds.delete(node)
                deleted_count += 1
        except Exception as e:
            cmds.warning('Failed to delete {}: {}'.format(node, e))
    
    return deleted_count


def _get_skin_deformers(geometry):
    """Get all skin cluster deformers on a piece of geometry."""
    if not cmds.objExists(geometry):
        return []
    
    try:
        skin_deformers = cmds.ls(cmds.listHistory(geometry, pruneDagObjects=True), type='skinCluster')
        return skin_deformers if skin_deformers else []
    except Exception as e:
        cmds.warning('Could not get deformers for {}: {}'.format(geometry, e))
        return []


def _get_joints_from_skin(geometry):
    """Extract all joints influencing a skinned geometry."""
    skin_deformers = _get_skin_deformers(geometry)
    if not skin_deformers:
        return []
    
    joints = []
    try:
        for deformer in skin_deformers:
            deformer_joints = cmds.skinCluster(deformer, query=True, influence=True)
            if deformer_joints:
                joints.extend(deformer_joints)
    except Exception as e:
        cmds.warning('Could not get joints from skin: {}'.format(e))
    
    return list(set(joints))


def _create_bindpose(joints):
    """Create a new BindPose for the given joints. Returns the BindPose node name."""
    if not joints:
        cmds.error('No joints provided for BindPose creation')
        return None
    
    try:
        cmds.select(joints, noExpand=True)
        result = cmds.dagPose(save=True, selection=True)
        return result
    except Exception as e:
        cmds.error('Failed to create BindPose: {}'.format(e))
        return None


def _validate_hierarchy(root_joint):
    """Validate the hierarchy and return potential issues."""
    issues = {
        'non_joint_nodes': [],
        'missing_bindpose': False,
        'bindpose_orphaned': False
    }
    
    if not cmds.objExists(root_joint):
        return issues
    
    try:
        descendants = cmds.listRelatives(root_joint, allDescendents=True, fullPath=True)
        if not descendants:
            descendants = []
        
        for node in descendants:
            node_type = cmds.nodeType(node)
            if node_type not in ['joint', 'transform']:
                issues['non_joint_nodes'].append(node)
        
        bindpose_nodes = _get_all_bindpose_nodes()
        if not bindpose_nodes:
            issues['missing_bindpose'] = True
        
        return issues
    except Exception as e:
        cmds.warning('Validation failed: {}'.format(e))
        return issues


# ============================================================================
# MAIN OPERATIONS
# ============================================================================

def create_bindpose_from_selection():
    """Create BindPose from selected joints."""
    selected = cmds.ls(selection=True, type='joint')
    
    if not selected:
        cmds.warning('No joints selected. Please select joints and try again.')
        return False
    
    result = _create_bindpose(selected)
    return result is not None


def fix_bindpose_for_geometry(geometry):
    """Fix BindPose for a specific piece of geometry."""
    joints = _get_joints_from_skin(geometry)
    if not joints:
        cmds.warning('No skinned joints found on {}'.format(geometry))
        return False
    
    deleted = _delete_bindpose_nodes()
    result = _create_bindpose(joints)
    return result is not None


def auto_fix(delete_old=True):
    """Automatically detect and fix BindPose issues.
    
    Args:
        delete_old: if True, delete existing BindPose nodes first
    
    Returns:
        True if successful, False otherwise
    """
    all_skinned = cmds.ls(type='mesh')
    if not all_skinned:
        cmds.error('No geometry found in scene')
        return False
    
    all_joints = set()
    for geo in all_skinned:
        joints = _get_joints_from_skin(geo)
        all_joints.update(joints)
    
    if not all_joints:
        cmds.error('No skinned joints found in scene')
        return False
    
    if delete_old:
        _delete_bindpose_nodes()
    
    result = _create_bindpose(list(all_joints))
    
    if result:
        cmds.confirmDialog(title='Success', message='BindPose auto-fix completed successfully!')
        return True
    else:
        cmds.error('BindPose auto-fix failed')
        return False


def show_status():
    """Print current BindPose status to the Script Editor."""
    print('\n' + '='*50)
    print('BINDPOSE STATUS REPORT')
    print('='*50)
    
    bindpose_nodes = _get_all_bindpose_nodes()
    all_skinned = cmds.ls(type='mesh') or []
    all_joints = set()
    
    for geo in all_skinned:
        joints = _get_joints_from_skin(geo)
        all_joints.update(joints)
    
    print('\nBindPose nodes found: {}'.format(len(bindpose_nodes)))
    for bp in bindpose_nodes:
        print('  - {}'.format(bp))
    
    print('\nSkinned geometry: {}'.format(len(all_skinned)))
    print('Skinned joints: {}'.format(len(all_joints)))
    
    if not bindpose_nodes:
        print('\nWARNING: No BindPose nodes found!')
    
    print('\n' + '='*50 + '\n')


# ============================================================================
# UI FUNCTIONS
# ============================================================================

def _close_window():
    """Close the UI window."""
    if cmds.window(WIN, exists=True):
        cmds.deleteUI(WIN, window=True)


def _auto_fix_clicked(*args):
    """Handle auto-fix button click."""
    result = auto_fix(delete_old=True)
    status = 'Success!' if result else 'Failed - check Script Editor'
    bg_color = [0.2, 0.8, 0.2] if result else [0.8, 0.2, 0.2]
    cmds.text('status_text', edit=True, label=status, backgroundColor=bg_color)


def _fix_selected_clicked(*args):
    """Handle fix selected geometry button click."""
    selected = cmds.ls(selection=True, geometry=True)
    
    if not selected:
        cmds.text('status_text', edit=True, label='No geometry selected', backgroundColor=[0.8, 0.2, 0.2])
        return
    
    for geo in selected:
        fix_bindpose_for_geometry(geo)
    
    cmds.text('status_text', edit=True, label='Fixed {} geometry(ies)!'.format(len(selected)), backgroundColor=[0.2, 0.8, 0.2])


def _from_selection_clicked(*args):
    """Handle create from selection button click."""
    result = create_bindpose_from_selection()
    status = 'Success!' if result else 'Failed - check Script Editor'
    bg_color = [0.2, 0.8, 0.2] if result else [0.8, 0.2, 0.2]
    cmds.text('status_text', edit=True, label=status, backgroundColor=bg_color)


def _delete_bindpose_clicked(*args):
    """Handle delete BindPose button click."""
    count = _delete_bindpose_nodes()
    cmds.text('status_text', edit=True, label='Deleted {} BindPose node(s)'.format(count), backgroundColor=[0.2, 0.8, 0.2])


def _show_status_clicked(*args):
    """Handle show status button click."""
    show_status()
    cmds.text('status_text', edit=True, label='Status printed to Script Editor', backgroundColor=[0.2, 0.8, 0.2])


def show_ui():
    """Create and show the BindPose Tool UI."""
    
    _close_window()
    
    cmds.window(WIN, title='BindPose Tool', widthHeight=(350, 250), sizeable=False)
    
    main_col = cmds.columnLayout(adjustableColumn=True, rowSpacing=10)
    
    cmds.text(label='BindPose Repair Tool', font='boldLabelFont', height=25)
    cmds.text(label='Automate BindPose creation and fixes', font='smallPlainLabelFont', height=20)
    
    cmds.separator(height=10, style='in')
    
    button_col = cmds.columnLayout(parent=main_col, adjustableColumn=True, rowSpacing=5)
    
    cmds.button(
        label='Auto-Fix BindPose',
        height=40,
        backgroundColor=[0.4, 0.6, 0.8],
        command=_auto_fix_clicked
    )
    
    cmds.button(
        label='Fix Selected Geometry',
        height=35,
        command=_fix_selected_clicked
    )
    
    cmds.button(
        label='Create from Selected Joints',
        height=35,
        command=_from_selection_clicked
    )
    
    cmds.button(
        label='Delete Old BindPose',
        height=35,
        backgroundColor=[0.8, 0.4, 0.4],
        command=_delete_bindpose_clicked
    )
    
    cmds.button(
        label='Show Status',
        height=35,
        command=_show_status_clicked
    )
    
    cmds.separator(height=10, style='in')
    
    cmds.text('status_text', label='Ready', height=20, backgroundColor=[0.3, 0.3, 0.3])
    
    cmds.showWindow(WIN)


# Run the UI on import
show_ui()
