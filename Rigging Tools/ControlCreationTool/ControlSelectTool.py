import maya.cmds as cmds

def selectControls():
    selected_controls = []
    i = 0
    while True:
        control_name = '_ctrl_{}'.format(i)
        if not cmds.objExists(control_name):
            break
        selected_controls.append(control_name)
        i += 1
    cmds.select(selected_controls)

def createUI():
    if cmds.window('controlSelectUI', exists=True):
        cmds.deleteUI('controlSelectUI', window=True)

    cmds.window('controlSelectUI', title='Control Select Tool', widthHeight=(200, 30), sizeable=False)
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label='Select Controls', command='selectControls()')
    cmds.showWindow('controlSelectUI')

createUI()