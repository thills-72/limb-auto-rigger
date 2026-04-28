import math

################functions######################
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
    return locator
    
def skinning_joint_density(ribbon, density):
    locators = []
    for index in range(0, density):
        locators.append(locator_to_surface_cv(ribbon, 0.5, (index / density)))
    return locators
    
def cross_product(vecA, vecB):
    out_vec = [None, None, None]
    out_vec[0] = ((vecA[1] * vecB[2]) - (vecB[1] * vecA[2]))
    out_vec[1] = (-1 * ((vecA[0] * vecB[2]) - (vecB[0] * vecA[2])))
    out_vec[2] = ((vecA[0] * vecB[1]) - (vecB[0] * vecA[1]))
    return out_vec
    
def vector_normalize(vec):
    scaler = 1 / (abs(math.sqrt(math.pow(vec[0], 2) + math.pow(vec[1], 2) + math.pow(vec[2], 2))))
    out_vec = [i * scaler for i in vec]
    return out_vec
    
def move_vector(vecA, vecB):
    out_vec = [None, None, None]
    for index in range(0, 3):
        out_vec[index] = vecA[index] + vecB[index]
    return out_vec

def translates_to_zero(object):
    cmds.setAttr(f"{object}.translateX", 0)
    cmds.setAttr(f"{object}.translateY", 0)
    cmds.setAttr(f"{object}.translateZ", 0)
    return

def shape_circle_cons(con, scale):
    cmds.select(con + ".cv[:]")
    cmds.scale(scale, scale, scale)
    for index in range(0, 4):
        index = index * 2
        cmds.select(con + f".cv[{index}]")
        cmds.scale(scale / 2, scale / 2, scale / 2)
    return
#################################################

################ribbon_creation##################

positions = []
joints = cmds.ls(selection = True)

for jnt in joints:
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

for index in range(0, 3):
    aVector[index] = B[index] - A[index]
aVector = vector_normalize(aVector)

for index in range(0, 3):
    bVector[index] = B[index] - C[index]
bVector  = vector_normalize(bVector)

nVectorPos = cross_product(aVector, bVector)

nVectorPosA = move_vector(nVectorPos, A)
nVectorPosB = move_vector(nVectorPos, B)
nVectorPosC = move_vector(nVectorPos, C)
posCurve = [nVectorPosA, nVectorPosB, nVectorPosC]

nVectorNeg = cross_product(bVector, aVector)

nVectorNegA = move_vector(nVectorNeg, A)
nVectorNegB = move_vector(nVectorNeg, B)
nVectorNegC = move_vector(nVectorNeg, C)
negCurve = [nVectorNegA, nVectorNegB, nVectorNegC]

crv1 = cmds.curve(degree = 1, point = [posCurve[0], posCurve[1]])
crv2 = cmds.curve(degree = 1, point = [negCurve[0], negCurve[1]])
crv3 = cmds.curve(degree = 1, point = [posCurve[1], posCurve[2]])
crv4 = cmds.curve(degree = 1, point = [negCurve[1], negCurve[2]])

surface1 = cmds.loft(crv1, crv2, constructionHistory = True, range = True, autoReverse = True)[0]
surface2 = cmds.loft(crv3, crv4, constructionHistory = True, range = True, autoReverse = True)[0]

cmds.delete(crv1, crv2, crv3, crv4)

ribbon1 = cmds.rebuildSurface(surface1, rebuildType = 0, spansU = 1, spansV = 4, degreeU = 2, degreeV = 3)
ribbon2 = cmds.rebuildSurface(surface2, rebuildType = 0, spansU = 1, spansV = 4, degreeU = 2, degreeV = 3)

"""
twistBlend = cmds.duplicate(ribbon1)
cmds.select(twistBlend)
twist_deformer = cmds.nonLinear(type = "twist")
sineBlend = cmds.duplicate(ribbon1)
cmds.select(sineBlend)
sine_deformer = cmds.nonLinear(type = "sine")
"""

locators = skinning_joint_density(ribbon1, 8)

locators = locators + skinning_joint_density(ribbon2, 8)

cmds.skinCluster(joints[0], joints[1], ribbon1)
cmds.skinCluster(joints[1], joints[2], ribbon2)

skinning_jnts = []
for index, locs in enumerate(locators):
    skinning_jnts.append(cmds.joint())
    cmds.parent(skinning_jnts[index], locators[index])
    translates_to_zero(skinning_jnts[index])

locators_for_controls = locators[1:4] + locators [5:8]
joints_for_controls = skinning_jnts[1:4] + skinning_jnts[5:8]
ribbon_controls = []
control_groups = []
for index, loc in enumerate(locators_for_controls):
    ribbon_controls.append(cmds.circle()[0])
    control_groups.append(cmds.group())
    pConstraint = cmds.parentConstraint(loc, control_groups[index], maintainOffset = False)
    cmds.delete(pConstraint)
    cmds.parentConstraint(ribbon_controls[index], joints_for_controls[index])
    shape_circle_cons(ribbon_controls[index], 3)
    cmds.parentConstraint(loc, ribbon_controls[index])

"""
cmds.parent(twistBlend, twist_deformer, locators[0])
twistBlend_grp = cmds.group(twistBlend, twist_deformer)
cmds.move(0, -3, 0, twistBlend_grp, objectSpace = True, relative = True)

cmds.parent(sineBlend, sine_deformer, locators[0])
sineBlend_grp = cmds.group(sineBlend, sine_deformer)
cmds.move(0, -6, 0, sineBlend_grp, objectSpace = True, relative = True)

cmds.blendShape(twistBlend, sineBlend, surface1)
"""
#################################################

################fk_creation######################
fk_joints = cmds.duplicate(joints[0], renameChildren = True)
for index, jnt in enumerate(fk_joints):
    fk_joints[index] = cmds.rename(fk_joints[index], fk_joints[index] + "_fk")
shoulder = fk_joints[0]
elbow = fk_joints[1]
wrist = fk_joints[2]

#create control
shoulder_con = cmds.circle()
cmds.select(shoulder_con[0] + ".cv[:]")
cmds.rotate(0, "90deg", 0, relative = True)
cmds.scale(4, 4, 4)
elbow_con = cmds.duplicate(shoulder_con[0])
wrist_con = cmds.duplicate(shoulder_con[0])

#parent controls
shoulder_grp = cmds.group(shoulder_con[0])
elbow_grp = cmds.group(elbow_con[0])
wrist_grp = cmds.group(wrist_con[0])

#move grps to joints
cmds.matchTransform(shoulder_grp, shoulder)
cmds.matchTransform(elbow_grp, elbow)
cmds.matchTransform(wrist_grp, wrist)

#parent joints to cons
cmds.parentConstraint(shoulder_con[0], shoulder)
cmds.parentConstraint(elbow_con[0], elbow)
cmds.parentConstraint(wrist_con[0], wrist)

#parent grps to cons
cmds.parent(wrist_grp, elbow_con[0])
cmds.parent(elbow_grp, shoulder_con[0])
#################################################

################ik_creation######################
#select joint chain
ik_joints = cmds.duplicate(joints[0], renameChildren = True)
for index, jnt in enumerate(ik_joints):
    ik_joints[index] = cmds.rename(ik_joints[index], ik_joints[index] + "_ik")
shoulder = ik_joints[0]
elbow = ik_joints[1]
wrist = ik_joints[2]

#build controls: arm ik con + pv con
arm_con = cmds.circle()[0]
cmds.setAttr(arm_con + ".lineWidth", 2)
for index in range(0, 8):
    if index % 2 == 0:
        cmds.select(arm_con + f".cv[{index}]")
        cmds.move(0, 0, 1, objectSpace = True, relative = True)
    if index % 2 == 1:
        cmds.select(arm_con + f".cv[{index}]")
        cmds.move(0, 0, -1, objectSpace = True, relative = True)
arm_grp = cmds.group(arm_con)

pv_con = cmds.circle()[0]
pv_grp = cmds.group(pv_con)

#rotate cvs of arm ik con
cmds.select(arm_con + ".cv[:]")
cmds.rotate(0, "90deg", 0, relative = True)
cmds.scale(5, 5, 5)

#position arm grp
cmds.matchTransform(arm_grp, wrist)

#calculate pv position
shoulder_pos = cmds.xform(shoulder, query = True, worldSpace = True, translation = True)
elbow_pos = cmds.xform(elbow, query = True, worldSpace = True, translation = True)
wrist_pos = cmds.xform(wrist, query = True, worldSpace = True, translation = True)

crv = cmds.curve(degree = 1, p = [shoulder_pos, elbow_pos, wrist_pos])
pv_distance = (aVector[0] + aVector[1] + aVector[2] + bVector[0] + bVector[1] + bVector[2]) / 6
cmds.moveVertexAlongDirection(crv + ".cv[1]", n = 8)
pv_pos = cmds.xform(crv + ".cv[1]", query = True, worldSpace = True, translation = True)

#position pv grp
cmds.xform(pv_grp, worldSpace = True, translation = pv_pos)
cmds.delete(crv)

#create ikHandle
ikh = cmds.ikHandle(startJoint = shoulder, endEffector = wrist)
cmds.setAttr(ikh[0] + ".visibility", False)

#parent ik to con
cmds.parent(ikh[0], arm_con)

#pole vector constraint
cmds.poleVectorConstraint(pv_con, ikh[0])

#orient constraint wrist joint to arm con
cmds.orientConstraint(arm_con, wrist, maintainOffset = True)

#create distance between and distance dimension nodes for forearm and upper arm
####implement-stretch######
dd1 = cmds.distanceDimension(startPoint = (1, 0, 0), endPoint = (0, 0, 0))
dd2 = cmds.distanceDimension(startPoint = (2, 0, 0), endPoint = (0, 2, 0))
cmds.setAttr(dd1 + ".visibility", False)
cmds.setAttr(dd2 + ".visibility", False)
locator1 = cmds.listConnections(dd1)[0]
locator2 = cmds.listConnections(dd1)[1]
locator3 = cmds.listConnections(dd2)[0]
locator4 = cmds.listConnections(dd2)[1]
cmds.parent(locator1, ik_joints[1])
cmds.parent(locator2, arm_con)
cmds.parent(locator3, ik_joints[0])
cmds.parent(locator4, ik_joints[1])
cmds.select(locator1)
cmds.move(0, 0, 0, objectSpace = True)
cmds.select(locator2)
cmds.move(0, 0, 0, objectSpace = True)
cmds.select(locator3)
cmds.move(0, 0, 0, objectSpace = True) 
cmds.select(locator4)
cmds.move(0, 0, 0, objectSpace = True)
base_length = cmds.getAttr(dd1 + ".distance") + cmds.getAttr(dd2 + ".distance")
root_locator_shape = cmds.listRelatives(locator3, children = True)[0]
end_locator_shape = cmds.listRelatives(locator2, children = True)[0]
dd3 = cmds.distanceDimension(startPoint = (0, 0, 0), endPoint = (1, 0, 0))
cmds.setAttr(dd3 + ".visibility", False)
temp_loc1 = cmds.listConnections(dd3)[0]
temp_loc2 = cmds.listConnections(dd3)[1]
cmds.connectAttr(root_locator_shape + ".worldPosition[0]", dd3 + ".startPoint", force = True)
cmds.connectAttr(end_locator_shape + ".worldPosition[0]", dd3 + ".endPoint", force = True)
cmds.delete(temp_loc1)
cmds.delete(temp_loc2)

stretch_condition_node = cmds.createNode("condition")
cmds.setAttr(stretch_condition_node + ".operation", 2)
cmds.connectAttr(dd3 + ".distance", stretch_condition_node + ".firstTerm")
cmds.setAttr(stretch_condition_node + ".secondTerm", base_length)
ratio = cmds.createNode("divide")
cmds.connectAttr(dd3 + ".distance", ratio + ".input1")
cmds.setAttr(ratio + ".input2", base_length)
cmds.connectAttr(ratio + ".output", stretch_condition_node + ".colorIfTrueR")

#create/connect stretch toggle
stretch_switch_node = cmds.createNode("condition")
cmds.addAttr(arm_con, longName = "stretch", attributeType = "float", min = 0, max = 1, keyable = True)
cmds.connectAttr(arm_con + ".stretch", stretch_switch_node + ".firstTerm")
cmds.setAttr(stretch_switch_node + ".secondTerm", 1)
cmds.connectAttr(stretch_condition_node + ".outColorR", stretch_switch_node + ".colorIfTrueR")
cmds.setAttr(stretch_switch_node + ".colorIfFalseR", 1)
cmds.connectAttr(stretch_switch_node + ".outColorR", ik_joints[0] + ".scaleX")
cmds.connectAttr(stretch_switch_node + ".outColorR", ik_joints[1] + ".scaleX")
 
#################################################

##################tie_together###################
shoulder_constraint = cmds.parentConstraint(ik_joints[0], fk_joints[0], joints[0])
elbow_constraint = cmds.parentConstraint(ik_joints[1], fk_joints[1], joints[1])
wrist_constraint = cmds.parentConstraint(ik_joints[2], fk_joints[2], joints[2])

cmds.addAttr(arm_con, longName = "ikfk", attributeType = "float", min = 0, max = 1, keyable = True)
cmds.addAttr(arm_con, longName = "ribbon_Controls", attributeType = "float", min = 0, max = 1, keyable = True)

cmds.connectAttr(arm_con + ".ikfk", shoulder_constraint[0] + f".{fk_joints[0]}W1")
cmds.connectAttr(arm_con + ".ikfk", elbow_constraint[0] + f".{fk_joints[1]}W1")
cmds.connectAttr(arm_con + ".ikfk", wrist_constraint[0] + f".{fk_joints[2]}W1")
cmds.connectAttr(arm_con + ".ikfk", shoulder_con[0] + ".visibility")
cmds.connectAttr(arm_con + ".ikfk", elbow_con[0] + ".visibility")
cmds.connectAttr(arm_con + ".ikfk", wrist_con[0] + ".visibility")

reverse = cmds.shadingNode("reverse", asUtility = True)

cmds.connectAttr(arm_con + ".ikfk", reverse + ".inputX")

cmds.connectAttr(reverse + ".outputX", shoulder_constraint[0] + f".{ik_joints[0]}W0")
cmds.connectAttr(reverse + ".outputX", elbow_constraint[0] + f".{ik_joints[1]}W0")
cmds.connectAttr(reverse + ".outputX", wrist_constraint[0] + f".{ik_joints[2]}W0")
cmds.connectAttr(reverse + ".outputX", pv_con + ".visibility")

for index, con in enumerate(ribbon_controls):
    cmds.connectAttr(arm_con + ".ribbon_Controls", con + ".visibility")

for index, jnt in enumerate(ik_joints):
    cmds.setAttr(jnt + ".visibility", False)

for index, jnt in enumerate(fk_joints):
    cmds.setAttr(jnt + ".visibility", False)
#################################################
