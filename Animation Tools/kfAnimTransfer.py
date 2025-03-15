import maya.cmds as cmds
'''
//////////////////////////////////////////////////////
//kfAnimTransfer
//////////////////////////
//Written by Kiel Figgins
//www.3dfiggins.com
//////////////////////////
//Use to pull transfer the keys from one object or hierarchy to another
//////////////////////////
//Version History
//////////////////////////
//1.00 (12-06-2011) - Original version
//////////////////////////
//Coming Soon

'''

def kfAnimTransfer():
    if cmds.window('kfAnimTransferWin', exists=True):
        cmds.showWindow('kfAnimTransferWin')
        return

    cmds.window('kfAnimTransferWin', width=230, height=600, title='Anim Transfer', tlb=True)
    mainSaveForm = cmds.formLayout()

    # UI pieces
    txAT_Instruct1 = cmds.text(label='Select the object / top of the hierarchy to transfer from,')
    txAT_Instruct2 = cmds.text(label='Then select the object / top of the hierarchies to transfer to:')
    btnAT_Obj = cmds.button(label='Transfer Keys (Object)', width=140, command=lambda x: kfAT_Obj())
    btnAT_Hier = cmds.button(label='Transfer Keys (Hierarchy)', width=140, command=lambda x: kfAT_Hier())

    # UI FormLayout
    cmds.formLayout(mainSaveForm, edit=True,
                    attachForm=[
                        (txAT_Instruct1, 'top', 8),
                        (txAT_Instruct1, 'left', 5),
                        (txAT_Instruct2, 'left', 5),
                        (btnAT_Obj, 'left', 5),
                        (btnAT_Hier, 'left', 5)
                    ],
                    attachControl=[
                        (txAT_Instruct2, 'top', 8, txAT_Instruct1),
                        (btnAT_Obj, 'top', 8, txAT_Instruct2),
                        (btnAT_Hier, 'top', 8, txAT_Instruct2),
                        (btnAT_Hier, 'left', 5, btnAT_Obj)
                    ])

    cmds.showWindow('kfAnimTransferWin')
    cmds.window('kfAnimTransferWin', edit=True, widthHeight=(295, 80))

def kfAT_Obj():
    sel = cmds.ls(selection=True)

    if len(sel) > 1:
        cmds.select(sel[0])
        copySel = cmds.ls(selection=True)

        cmds.select(sel)
        cmds.select(copySel[0], toggle=True)
        pasteSel = cmds.ls(selection=True)

        cmds.copyKey(copySel[0])

        for obj in pasteSel:
            cmds.pasteKey(obj, option='replaceCompletely', copies=1, connect=1, timeOffset=0, floatOffset=0, valueOffset=0)
    else:
        print("\n\nFAIL: Please select at least 2 Objects\n\n")

def kfAT_Hier():
    sel = cmds.ls(selection=True)

    if len(sel) > 1:
        cmds.select(sel[0])
        initHierObj = cmds.ls(selection=True)

        cmds.select(sel)
        cmds.select(initHierObj[0], toggle=True)
        goalHierObj = cmds.ls(selection=True)

        # Find out just the goal name space
        justName = initHierObj[0].split(':')[-1]
        nameSpaceInit = initHierObj[0].replace(justName, '')

        for goalObj in goalHierObj:
            justName = goalObj.split(':')[-1]
            nameSpaceGoal = goalObj.replace(justName, '')

            cmds.select(initHierObj)
            cmds.select(hierarchy=True)
            allInit = cmds.ls(selection=True)

            cmds.select(clear=True)

            for initObj in allInit:
                goalTest = initObj.replace(nameSpaceInit, nameSpaceGoal)

                if cmds.objExists(goalTest):
                    anyDups = cmds.ls(goalTest)

                    cmds.select(anyDups[0])
                    goalObj = cmds.ls(selection=True)

                    anyKeys = cmds.keyframe(initObj, query=True, keyframeCount=True)

                    if anyKeys != 0:
                        cmds.copyKey(initObj)
                        cmds.pasteKey(goalObj, option='replaceCompletely', copies=1, connect=1, timeOffset=0, floatOffset=0, valueOffset=0)

            print(f"\nSUCCESS: Hierarchy Anim Transfer Complete {goalHierObj.index(goalObj) + 1}/{len(goalHierObj)}")
    else:
        print("\n\nFAIL: Please select at least 2 Objects\n\n")

# Run the UI
kfAnimTransfer()