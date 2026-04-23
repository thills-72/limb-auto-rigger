positions = []

for jnt in cmds.ls(selection = True):
    position = cmds.xform(jnt, query = True, worldSpace = True, translation = True)
    positions.append(position)

print(positions)
crv1 = cmds.curve(degree = 1, point = positions)
crv2 = cmds.duplicate(crv)[0]

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

bVector[0] = B[0] - C[0]
bVector[1] = B[1] - C[1]
bVector[2] = B[2] - C[2]

nVectorPos[0] = ((aVector[1] * bVector[2]) - (bVector[1] * aVector[2]))
nVectorPos[1] = (-1 * ((aVector[0] * bVector[2]) - (bVector[0] * aVector[2])))
nVectorPos[2] = ((aVector[0] * bVector[1]) - (bVector[0] * aVector[1]))

nVectorPosB = [nVectorPos[0] + B[0], nVectorPos[1] + B[1], nVectorPos[2] + B[2]]
nVectorPosA = [nVectorPos[0] + A[0], nVectorPos[1] + A[1], nVectorPos[2] + A[2]]
nVectorPosC = [nVectorPos[0] + C[0], nVectorPos[1] + C[1], nVectorPos[2] + C[2]]

nVectorNeg[0] = ((bVector[1] * aVector[2]) - (aVector[1] * bVector[2]))
nVectorNeg[1] = (-1 * ((bVector[0] * aVector[2]) - (aVector[0] * bVector[2])))
nVectorNeg[2] = ((bVector[0] * aVector[1]) - (aVector[0] * bVector[1]))

nVectorNegB = [nVectorNeg[0] + B[0], nVectorNeg[1] + B[1], nVectorNeg[2] + B[2]]
nVectorNegA = [nVectorNeg[0] + A[0], nVectorNeg[1] + A[1], nVectorNeg[2] + A[2]]
nVectorNegC = [nVectorNeg[0] + C[0], nVectorNeg[1] + C[1], nVectorNeg[2] + C[2]]

cmds.xform(crv1 + ".cv[0]", worldSpace = True, translation = nVectorPosA)
cmds.xform(crv1 + ".cv[1]", worldSpace = True, translation = nVectorPosB)
cmds.xform(crv1 + ".cv[2]", worldSpace = True, translation = nVectorPosC)
cmds.xform(crv2 + ".cv[0]", worldSpace = True, translation = nVectorNegA)
cmds.xform(crv2 + ".cv[1]", worldSpace = True, translation = nVectorNegB)
cmds.xform(crv2 + ".cv[2]", worldSpace = True, translation = nVectorNegC)