positions = []

for jnt in cmds.ls(selection = True):
    position = cmds.xform(jnt, query = True, worldSpace = True, translation = True)
    positions.append(position)

print(positions)
#crv = cmds.curve(degree = 1, point = positions)

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

print(A, B, C)

Ax = A[0]
Ay = A[1]
Az = A[2]

Bx = B[0]
By = B[1]
Bz = B[2]

Cx = C[0]
Cy = C[1]
Cz = C[2]

print(Ax, Ay, Az, Bx, By, Bz, Cx, Cy, Cz)

ax = Bx - Ax
ay = By - Ay
az = Bz - Az

bx = Bx - Cx
by = By - Cy
bz = Bz - Cz

aVector = [ax, ay, az]
bVector = [bx, by, bz]
#correctedAVector = [B[0] + aVector[0], B[1] + aVector[1], B[2] + aVector[2]]
#correctedBVector = [B[0] + bVector[0], B[1] + bVector[1], B[2] + bVector[2]]

#cmds.curve(degree = 1, point = [positions[1], correctedAVector])
#cmds.curve(degree = 1, point = [positions[1], correctedBVector])

#nx = ((correctedAVector[1] * correctedBVector[2]) - (correctedBVector[1] * correctedAVector[2]))
#ny = (-1 * ((correctedAVector[0] * correctedBVector[2]) - (correctedBVector[0] * correctedAVector[2])))
#nz = ((correctedAVector[0] * correctedBVector[1]) - (correctedBVector[1] * correctedAVector[0]))

nx = ((aVector[1] * bVector[2]) - (bVector[1] * aVector[2]))
ny = (-1 * ((aVector[0] * bVector[2]) - (bVector[0] * aVector[2])))
nz = ((aVector[0] * bVector[1]) - (bVector[0] * aVector[1]))

normalVector = [nx, ny, nz]
correctedNormalVectorB = [normalVector[0] + B[0], normalVector[1] + B[1], normalVector[2] + B[2]]
correctedNormalVectorA = [normalVector[0] + A[0], normalVector[1] + A[1], normalVector[2] + A[2]]
correctedNormalVectorC = [normalVector[0] + C[0], normalVector[1] + C[1], normalVector[2] + C[2]]
cmds.curve(degree = 1, point = [positions[1], correctedNormalVectorB])
cmds.curve(degree = 1, point = [positions[0], correctedNormalVectorA])
cmds.curve(degree = 1, point = [positions[2], correctedNormalVectorC])
print(normalVector)