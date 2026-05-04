import math

################functions######################
"""
takes a surface and a UV ratio position and pins a locator that follows 
the surface to that point
surf: string
U, V: float
""" 

def locator_to_surface_cv(surf, U, V):
    #create point on surface node
    infoNode = cmds.pointOnSurface(surf, parameterU = U, parameterV = V, 
                                   constructionHistory = True)
    #create four by four matrix and decompose matrix node
    matrix = cmds.createNode("fourByFourMatrix")
    decompose = cmds.createNode("decomposeMatrix")
    #connect point on surface node vector information to four by 
    #four matrix inputs
    cmds.connectAttr(f"{infoNode}.normalizedTangentUX", 
                     f"{matrix}.in00")
    cmds.connectAttr(f"{infoNode}.normalizedTangentUY", 
                     f"{matrix}.in01")
    cmds.connectAttr(f"{infoNode}.normalizedTangentUZ", 
                     f"{matrix}.in02")
    cmds.setAttr(f"{matrix}.in03", 0)
    cmds.connectAttr(f"{infoNode}.normalX", f"{matrix}.in10")
    cmds.connectAttr(f"{infoNode}.normalY", f"{matrix}.in11")
    cmds.connectAttr(f"{infoNode}.normalZ", f"{matrix}.in12")
    cmds.setAttr(f"{matrix}.in13", 0)
    cmds.connectAttr(f"{infoNode}.normalizedTangentVX", 
                     f"{matrix}.in20")
    cmds.connectAttr(f"{infoNode}.normalizedTangentVY", 
                     f"{matrix}.in21")
    cmds.connectAttr(f"{infoNode}.normalizedTangentVZ", 
                     f"{matrix}.in22")
    cmds.setAttr(f"{matrix}.in23", 0)
    cmds.connectAttr(f"{infoNode}.positionX", f"{matrix}.in30")
    cmds.connectAttr(f"{infoNode}.positionY", f"{matrix}.in31")
    cmds.connectAttr(f"{infoNode}.positionZ", f"{matrix}.in32")
    cmds.setAttr(f"{matrix}.in33", 1)
    #connect output of 4x4 matrix to decompose node
    cmds.connectAttr(f"{matrix}.output", f"{decompose}.inputMatrix")
    #connect output position and rotation of decompose to position and 
    #rotation of locator
    locator = cmds.spaceLocator()[0]
    cmds.connectAttr(f"{decompose}.outputTranslate", 
                     f"{locator}.translate")
    cmds.connectAttr(f"{decompose}.outputRotate", f"{locator}.rotate")
    return locator
    
#amount of joints pinned to the ribbon that will be skinned to mesh
def skinning_joint_density(ribbon, density):
    locators = []
    for index in range(0, density + 1):
        locators.append(locator_to_surface_cv(ribbon, 0.5, (index / density)))
    return locators

#vector algebra, used for normal calculation
def cross_product(vecA, vecB):
    out_vec = [None, None, None]
    out_vec[0] = ((vecA[1] * vecB[2]) - (vecB[1] * vecA[2]))
    out_vec[1] = (-1 * ((vecA[0] * vecB[2]) - (vecB[0] * vecA[2])))
    out_vec[2] = ((vecA[0] * vecB[1]) - (vecB[0] * vecA[1]))
    return out_vec

#returns base unit vector in direction of original vector
def vector_normalize(vec):
    scaler = 1 / (abs(math.sqrt(math.pow(vec[0], 2) + math.pow(vec[1], 2) + math.pow(vec[2], 2))))
    out_vec = [i * scaler for i in vec]
    return out_vec
    
#moves vecB to the end of vecA
def move_vector(vecA, vecB):
    out_vec = [None, None, None]
    for index in range(0, 3):
        out_vec[index] = vecA[index] + vecB[index]
    return out_vec

#zeroes out translation matrix in object space
def translates_to_zero(object):
    cmds.move(0, 0, 0, object, objectSpace = True)
    return

#creates square controls
def shape_circle_cons(con, scale):
    cmds.select(con + ".cv[:]")
    cmds.scale(scale, scale, scale)
    for index in range(0, 4):
        index = index * 2
        cmds.select(con + f".cv[{index}]")
        cmds.scale(scale / 2, scale / 2, scale / 2)
    return

#creates a child joints underneath each parent location in a list
def create_child_joints(root):
    joint_list = []
    for index, locs in enumerate(root):
        joint_list.append(cmds.joint(radius = 0.3))
        cmds.parent(joint_list[index], root[index])
        translates_to_zero(joint_list[index])
    return joint_list
    
#creates ribbon by lofting between two curves
def create_ribbon(point1, point2, point3, point4):
    crv1 = cmds.curve(degree = 1, point = [point1, point2])
    crv2 = cmds.curve(degree = 1, point = [point3, point4])
    ribbon = cmds.loft(crv1, crv2, constructionHistory = True, 
                       range = True, autoReverse = True)[0]
    cmds.delete(crv1, crv2)
    return ribbon

#creates ribbon skinning joints aligned with ribbon position parented
#underneath a root joint
def ribbon_skinning_joints(ribbon, root_joint, density):
    joint_list = []
    info_node = cmds.pointOnSurface(ribbon, parameterU = 0.5, 
                                    parameterV = 0.5, 
                                    constructionHistory = True)
    for index in range(0, density):
        control_position = index / (density - 1)
        joint_list.append(cmds.joint())
        cmds.parent(joint_list[index], root_joint)
        cmds.setAttr(info_node + ".parameterV", control_position)
        position = cmds.getAttr(info_node + ".position")[0]
        cmds.move(position[0], position[1], position[2], 
                  joint_list[index], worldSpace = True)
    cmds.skinCluster(joint_list, ribbon, toSelectedBones = True)
    cmds.delete(info_node)
    return joint_list

#create controls for ribbon joints
def ribbon_controls(ribbon_control_jnts):
    ribbon_control_groups = []
    for index, jnt in enumerate(ribbon_control_jnts):
        ribbon_controls.append(cmds.circle()[0])
        shape_circle_cons(ribbon_controls[index], 3)
        ribbon_control_groups.append(cmds.group(ribbon_controls[index]))
        pConstraint = cmds.pointConstraint(jnt, ribbon_control_groups[index], maintainOffset = False)
        cmds.delete(pConstraint)
        root_joint = cmds.listConnections(ribbon_control_jnts[index])[0]
        oConstraint = cmds.orientConstraint(root_joint, ribbon_control_groups[index], maintainOffset = False, offset = [0, 90, 0])
        cmds.delete(oConstraint)
        cmds.parentConstraint(ribbon_controls[index], ribbon_control_jnts[index], maintainOffset = True)
        cmds.parent(ribbon_control_groups[index], root_joint) 
    return ribbon_control_groups
    
#creates wave arm ik control shape
def arm_ik_control():    
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
    return arm_grp, arm_con

#creates pv control
def arm_ik_pv_control():
    pv_con = cmds.circle()[0]
    pv_grp = cmds.group(pv_con)

    cmds.select(arm_con + ".cv[:]")
    cmds.rotate(0, "90deg", 0, relative = True)
    cmds.scale(5, 5, 5)
    return pv_grp, pv_con

#calculate pv control position
def calculate_pv_pos(shoulder, elbow, wrist):
    shoulder_pos = cmds.xform(shoulder, query = True, worldSpace = True, 
                              translation = True)
    elbow_pos = cmds.xform(elbow, query = True, worldSpace = True, 
                           translation = True)
    wrist_pos = cmds.xform(wrist, query = True, worldSpace = True, 
                           translation = True)

    crv = cmds.curve(degree = 1, p = [shoulder_pos, elbow_pos, 
                                      wrist_pos])
    cmds.moveVertexAlongDirection(crv + ".cv[1]", n = 8)
    pv_pos = cmds.xform(crv + ".cv[1]", query = True, worldSpace = True, 
                        translation = True)
    cmds.delete(crv)
    return pv_pos

#################################################

################ribbon_creation##################

#save joints and duplicate chain for ik/fk switch
positions = []
joints = cmds.ls(selection = True)

ik_joints = cmds.duplicate(joints[0], renameChildren = True)
for index in range(0, 3):
    ik_joints[index] = cmds.rename(ik_joints[index], 
                                   ik_joints[index] + "_ik")

fk_joints = cmds.duplicate(joints[0], renameChildren = True)
for index in range(0, 3):
    fk_joints[index] = cmds.rename(fk_joints[index], 
                                   fk_joints[index] + "_fk")

#extract joint positions for normal calculation
for jnt in joints:
    position = cmds.xform(jnt, query = True, worldSpace = True, 
                          translation = True)
    positions.append(position)

A = positions[0]
B = positions[1]
C = positions[2]

#initialize vectors between joints and positive/negative normals
aVector = [None, None, None]
bVector = [None, None, None]
nVectorPos = [None, None, None]
nVectorNeg = [None, None, None]

#calculate vectors
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

#create ribbons using the curves created from the positive and negative
#normal vectors
surface1 = create_ribbon(posCurve[0], posCurve[1], negCurve[0], 
                         negCurve[1])
surface2 = create_ribbon(posCurve[1], posCurve[2], negCurve[1], 
                         negCurve[2])

#rebuild ribbons to useful formats
ribbon1 = cmds.rebuildSurface(surface1, rebuildType = 0, spansU = 1, 
                              spansV = 4, degreeU = 2, degreeV = 3)
ribbon2 = cmds.rebuildSurface(surface2, rebuildType = 0, spansU = 1, 
                              spansV = 4, degreeU = 2, degreeV = 3)

#create locators that move with ribbon deformation
locators = skinning_joint_density(ribbon1, 16)
locators = locators + skinning_joint_density(ribbon2, 16)

#create joints that follow those locators
geo_skinning_jnts = create_child_joints(locators)

#create skinned ribbon control joints that follow the base joint chain
ribbon_control_jnts = []
ribbon_control_jnts = ribbon_skinning_joints(ribbon1, joints[0], 3)
ribbon_control_jnts = ribbon_control_jnts + 
ribbon_skinning_joints(ribbon2, joints[1], 3)

#create controls for the ribbon deformation joints
ribbon_control_groups = []
ribbon_control_groups = ribbon_controls(ribbon_control_jnts)

#################################################

################fk_creation######################

shoulder = fk_joints[0]
elbow = fk_joints[1]
wrist = fk_joints[2]

#create control
shoulder_con = cmds.circle()
cmds.select(shoulder_con[0] + ".cv[:]")
cmds.rotate(0, "90deg", 0, relative = True)
cmds.scale(3.5, 3.5, 3.5)
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

shoulder = ik_joints[0]
elbow = ik_joints[1]
wrist = ik_joints[2]

#build controls: arm ik con + pv con
arm_grp, arm_con = arm_ik_control()
pv_grp, pv_con = arm_ik_pv_control()

#position arm grp
cmds.matchTransform(arm_grp, wrist)

#position pv grp
pv_pos = calculate_pv_pos(shoulder, elbow, wrist)
cmds.xform(pv_grp, worldSpace = True, translation = pv_pos)

#create ikHandle
ikh = cmds.ikHandle(startJoint = shoulder, endEffector = wrist)
cmds.setAttr(ikh[0] + ".visibility", False)

#parent ik to con
cmds.parent(ikh[0], arm_con)

#pole vector constraint
cmds.poleVectorConstraint(pv_con, ikh[0])

#orient constraint wrist joint to arm con
cmds.orientConstraint(arm_con, wrist, maintainOffset = True)
 
#################################################

##################tie_together###################
#constrain base joint chain
shoulder_constraint = cmds.parentConstraint(ik_joints[0], 
                                            fk_joints[0], joints[0])
elbow_constraint = cmds.parentConstraint(ik_joints[1], fk_joints[1], 
                                         joints[1])
wrist_constraint = cmds.parentConstraint(ik_joints[2], fk_joints[2], 
                                         joints[2])

#add switch attributes
cmds.addAttr(arm_con, longName = "ikfk", attributeType = "float", 
             min = 0, max = 1, keyable = True)
cmds.addAttr(arm_con, longName = "ribbon_Controls", 
             attributeType = "float", min = 0, max = 1, keyable = True)

#connect constraints to switch attributes
cmds.connectAttr(arm_con + ".ikfk", 
                 shoulder_constraint[0] + f".{fk_joints[0]}W1")
cmds.connectAttr(arm_con + ".ikfk", 
                 elbow_constraint[0] + f".{fk_joints[1]}W1")
cmds.connectAttr(arm_con + ".ikfk", 
                 wrist_constraint[0] + f".{fk_joints[2]}W1")
cmds.connectAttr(arm_con + ".ikfk", shoulder_con[0] + ".visibility")
cmds.connectAttr(arm_con + ".ikfk", elbow_con[0] + ".visibility")
cmds.connectAttr(arm_con + ".ikfk", wrist_con[0] + ".visibility")

reverse = cmds.shadingNode("reverse", asUtility = True)

cmds.connectAttr(arm_con + ".ikfk", reverse + ".inputX")

cmds.connectAttr(reverse + ".outputX", 
                 shoulder_constraint[0] + f".{ik_joints[0]}W0")
cmds.connectAttr(reverse + ".outputX", 
                 elbow_constraint[0] + f".{ik_joints[1]}W0")
cmds.connectAttr(reverse + ".outputX", 
                 wrist_constraint[0] + f".{ik_joints[2]}W0")
cmds.connectAttr(reverse + ".outputX", pv_con + ".visibility")

for con in ribbon_controls:
    cmds.connectAttr(arm_con + ".ribbon_Controls", con + ".visibility")

#turn joint visibility off for any but the base chain
for jnt in ik_joints:
    cmds.setAttr(jnt + ".visibility", False)

for jnt in fk_joints:
    cmds.setAttr(jnt + ".visibility", False)
    
for jnt in ribbon_control_jnts:
    cmds.setAttr(jnt + ".visibility", False)
#################################################