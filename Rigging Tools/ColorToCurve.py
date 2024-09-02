import maya.cmds as cmds
def enableColorOveride():
    sel = cmds.ls(sl=True)
    for obj in sel:
        cmds.setAttr(obj + '.overrideEnabled', 1)

def selectCurvesObj():
    cmds.select(clear=True)
    cmds.select(cmds.ls(type='nurbsCurve'))

def selectObj():
    cmds.select(clear=True)
    cmds.select(cmds.ls(sl=True))
    
def changeCurveColor(color):
    if color < 0 or color > 31:
        print("Value outside range, please enter value 0-31")
    else:
        sel = cmds.ls(sl=True)
        for obj in sel:
            shapes = cmds.listRelatives(obj, shapes=True)
            if shapes:
                for shape in shapes:
                    cmds.setAttr(shape + '.overrideEnabled', 1)
                    cmds.setAttr(shape + '.overrideColor', color)
    changeObjColor
def changeJointColor(color):
    sel = cmds.ls(sl=True)
    for obj in sel:
        cmds.setAttr(obj + '.overrideEnabled', 1)
        cmds.setAttr(obj + '.overrideColor', color)
                    

def createUI():
    if cmds.window('colorToCurveUI', exists=True):
        cmds.deleteUI('colorToCurveUI', window=True)

    cmds.window('colorToCurveUI', title='Color to Curve', widthHeight=(200, 100), sizeable=False)
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label='Enable Color Override', command='enableColorOveride()')
    cmds.intSlider('colorSlider', minValue=0, maxValue=31, value=0, step=1, cc='changeCurveColor(cmds.intSlider("colorSlider", query=True, value=True))')
    cmds.button(label='Change Color', command='changeObjColor(cmds.intSlider("colorSlider", query=True, value=True))')
    cmds.intSlider('jointColorSlider', minValue=0, maxValue=31, value=0, step=1, cc='changeJointColor(cmds.intSlider("jointColorSlider", query=True, value=True))')
    cmds.button(label='Change Joint Color', command='changeJointColor(cmds.intSlider("jointColorSlider", query=True, value=True))')
    cmds.button(label='Select Object', command='selectObj()')
    cmds.button(label='Select Curves', command='selectCurvesObj()')
    cmds.showWindow('colorToCurveUI')

createUI()
