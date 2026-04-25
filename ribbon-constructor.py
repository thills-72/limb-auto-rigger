"""
takes a surface and a UV ratio position and pins a locator that follows the surface to that point, surface variable is a string and U and V are floats
""" 
def locator_to_surface_cv(surf, U, V):
    #create point on surface node
    infoNode = cmds.pointOnSurface(surf, parameterU = U, parameterV = V, constructionHistory = True)
    #create four by four matrix and decompose matrix node
    matrix = cmds.createNode("fourByFourMatrix")
    decompose = cmds.createNode("decomposeMatrix")
    #connect point on surface node vector information to four by four matrix inputs
    cmds.connectAttr(f"{infoNode}.normalizedTangentUX", f"{matrix}.in00")
    cmds.connectAttr(f"{infoNode}.normalizedTangentUY", f"{matrix}.in01")
    cmds.connectAttr(f"{infoNode}.normalizedTangentUZ", f"{matrix}.in02")
    cmds.setAttr(f"{matrix}.in03", 0)
    cmds.connectAttr(f"{infoNode}.normalX", f"{matrix}.in10")
    cmds.connectAttr(f"{infoNode}.normalY", f"{matrix}.in11")
    cmds.connectAttr(f"{infoNode}.normalZ", f"{matrix}.in12")
    cmds.setAttr(f"{matrix}.in13", 0)
    cmds.connectAttr(f"{infoNode}.normalizedTangentVX", f"{matrix}.in20")
    cmds.connectAttr(f"{infoNode}.normalizedTangentVY", f"{matrix}.in21")
    cmds.connectAttr(f"{infoNode}.normalizedTangentVZ", f"{matrix}.in22")
    cmds.setAttr(f"{matrix}.in23", 0)
    cmds.connectAttr(f"{infoNode}.positionX", f"{matrix}.in30")
    cmds.connectAttr(f"{infoNode}.positionY", f"{matrix}.in31")
    cmds.connectAttr(f"{infoNode}.positionZ", f"{matrix}.in32")
    cmds.setAttr(f"{matrix}.in33", 1)
    #connect output of 4x4 matrix to decompose node
    cmds.connectAttr(f"{matrix}.output", f"{decompose}.inputMatrix")
    #connect output position and rotation of decompose to position and rotation of locator
    locator = cmds.spaceLocator()[0]
    cmds.connectAttr(f"{decompose}.outputTranslate", f"{locator}.translate")
    cmds.connectAttr(f"{decompose}.outputRotate", f"{locator}.rotate")


positions = []

for jnt in cmds.ls(selection = True):
    position = cmds.xform(jnt, query = True, worldSpace = True, translation = True)
    positions.append(position)

"""
need to get perpendicular vector direction from the plane that the three joints are sitting within
could do this by creating geo but am going to do it with matrix math
need cross product of the two vectors that are created with the three points
to accomplish this: consider the three joints as points in 3d space as A, B, C and their matrix locations as subscript X, Y, Z
get the vector from B to A and B to C: <BX - AX, BY - AY, BZ - AZ> and <BX - CX, BY - CY, BZ - CZ>, consider these vectors a and b respectively
note that the vector positions that this solves for are from the origin, meaning that a and b have to be added to the original positions of A and B
to get the normal vector take the cross product of a and b
a x b = |i  j  k | = |aY aZ|i - |aX aZ|j + |aX aY|k = ((aY * bZ) - (aZ * bY))i - ((aX * bZ) - (bX * aZ))j + ((aX * bY) - (bX * aY))k
        |aX aY aZ|   |bY bZ|    |bX bZ|    |bX bY|
        |bX bY bZ|

consider i j k as x y z 
this solves out the normal vector and can then be added and subtracted from each of the joint locations (aka translation vectors) to get the normal direction
adjusting the height of the ribbon will be multiplying the normal vector solve by a flat value to change how far out the curve is shifted when they two vectors are added and subtracted
"""

A = positions[0]
B = positions[1]
C = positions[2]

aVector = [None, None, None]
bVector = [None, None, None]
nVectorPos = [None, None, None]
nVectorNeg = [None, None, None]

aVector[0] = B[0] - A[0]
aVector[1] = B[1] - A[1]
aVector[2] = B[2] - A[2]
aVector = [i * 0.1 for i in aVector]

bVector[0] = B[0] - C[0]
bVector[1] = B[1] - C[1]
bVector[2] = B[2] - C[2]
bVector = [i * 0.1 for i in bVector]

nVectorPos[0] = ((aVector[1] * bVector[2]) - (bVector[1] * aVector[2]))
nVectorPos[1] = (-1 * ((aVector[0] * bVector[2]) - (bVector[0] * aVector[2])))
nVectorPos[2] = ((aVector[0] * bVector[1]) - (bVector[0] * aVector[1]))

nVectorPosB = [nVectorPos[0] + B[0], nVectorPos[1] + B[1], nVectorPos[2] + B[2]]
nVectorPosA = [nVectorPos[0] + A[0], nVectorPos[1] + A[1], nVectorPos[2] + A[2]]
nVectorPosC = [nVectorPos[0] + C[0], nVectorPos[1] + C[1], nVectorPos[2] + C[2]]
posCurve = [nVectorPosA, nVectorPosB, nVectorPosC]

nVectorNeg[0] = ((bVector[1] * aVector[2]) - (aVector[1] * bVector[2]))
nVectorNeg[1] = (-1 * ((bVector[0] * aVector[2]) - (aVector[0] * bVector[2])))
nVectorNeg[2] = ((bVector[0] * aVector[1]) - (aVector[0] * bVector[1]))

nVectorNegB = [nVectorNeg[0] + B[0], nVectorNeg[1] + B[1], nVectorNeg[2] + B[2]]
nVectorNegA = [nVectorNeg[0] + A[0], nVectorNeg[1] + A[1], nVectorNeg[2] + A[2]]
nVectorNegC = [nVectorNeg[0] + C[0], nVectorNeg[1] + C[1], nVectorNeg[2] + C[2]]
negCurve = [nVectorNegA, nVectorNegB, nVectorNegC]

crv1 = cmds.curve(degree = 1, point = [posCurve[0], posCurve[1]])
crv2 = cmds.curve(degree = 1, point = [negCurve[0], negCurve[1]])
crv3 = cmds.curve(degree = 1, point = [posCurve[1], posCurve[2]])
crv4 = cmds.curve(degree = 1, point = [negCurve[1], negCurve[2]])

surface1 = cmds.loft(crv1, crv2, constructionHistory = True, range = True, autoReverse = True)[0]
surface2 = cmds.loft(crv3, crv4, constructionHistory = True, range = True, autoReverse = True)[0]

cmds.delete(crv1, crv2, crv3, crv4)

ribbon1 = cmds.rebuildSurface(surface1, rebuildType = 0, spansU = 1, spansV = 4, degreeU = 2, degreeV = 1)
ribbon2 = cmds.rebuildSurface(surface2, rebuildType = 0, spansU = 1, spansV = 4, degreeU = 2, degreeV = 1)

locator_to_surface_cv(ribbon1, 0.5, 0.5)