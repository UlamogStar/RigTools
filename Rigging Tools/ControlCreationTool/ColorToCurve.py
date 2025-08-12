import maya.cmds as cmds

def enableColorOverride():
    sel = cmds.ls(sl=True)
    for obj in sel:
        cmds.setAttr(obj + '.overrideEnabled', 1)

def selectCurvesObj():
    cmds.select(clear=True)
    curves = cmds.ls(type='nurbsCurve')
    if curves:
        parents = list(set(cmds.listRelatives(curves, parent=True, fullPath=True) or []))
        cmds.select(parents)
    else:
        cmds.warning("No nurbsCurve shapes found.")

def selectObj():
    cmds.select(clear=True)
    cmds.select(cmds.ls(sl=True))

def changeCurveColor(color):
    if color < 1 or color > 31:
        print("Value outside range, please enter value 1-31")
        return
    sel = cmds.ls(sl=True)
    for obj in sel:
        shapes = cmds.listRelatives(obj, shapes=True)
        if shapes:
            for shape in shapes:
                if cmds.objectType(shape) == "nurbsCurve":
                    cmds.setAttr(shape + '.overrideEnabled', 1)
                    cmds.setAttr(shape + '.overrideColor', color)

def changeJointColor(color):
    if color < 1 or color > 31:
        print("Value outside range, please enter value 1-31")
        return
    sel = cmds.ls(sl=True)
    for obj in sel:
        if cmds.objectType(obj) == "joint":
            cmds.setAttr(obj + '.overrideEnabled', 1)
            cmds.setAttr(obj + '.overrideColor', color)

def updateCurveSwatch(*args):
    colorIdx = cmds.intSlider('colorSlider', query=True, value=True)
    cmds.symbolButton('curveColorSwatch', edit=True, image='colorIndex{}'.format(colorIdx))

def updateJointSwatch(*args):
    colorIdx = cmds.intSlider('jointColorSlider', query=True, value=True)
    cmds.symbolButton('jointColorSwatch', edit=True, image='colorIndex{}'.format(colorIdx))

def createUI():
    if cmds.window('colorToCurveUI', exists=True):
        cmds.deleteUI('colorToCurveUI', window=True)

    cmds.window('colorToCurveUI', title='Color to Curve', widthHeight=(220, 180), sizeable=False)
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label='Enable Color Override', command='enableColorOverride()')

    cmds.rowLayout(numberOfColumns=2)
    cmds.intSlider('colorSlider', minValue=1, maxValue=31, value=1, step=1,
                   cc='changeCurveColor(cmds.intSlider("colorSlider", query=True, value=True));updateCurveSwatch()')
    cmds.symbolButton('curveColorSwatch', width=40, height=20, image='colorIndex1', enable=False)
    cmds.setParent('..')

    cmds.button(label='Change Curve Color', command='changeCurveColor(cmds.intSlider("colorSlider", query=True, value=True))')

    cmds.rowLayout(numberOfColumns=2)
    cmds.intSlider('jointColorSlider', minValue=1, maxValue=31, value=1, step=1,
                   cc='changeJointColor(cmds.intSlider("jointColorSlider", query=True, value=True));updateJointSwatch()')
    cmds.symbolButton('jointColorSwatch', width=40, height=20, image='colorIndex1', enable=False)
    cmds.setParent('..')

    cmds.button(label='Change Joint Color', command='changeJointColor(cmds.intSlider("jointColorSlider", query=True, value=True))')
    cmds.button(label='Select Object', command='selectObj()')
    cmds.button(label='Select Curves', command='selectCurvesObj()')
    cmds.showWindow('colorToCurveUI')

createUI()
