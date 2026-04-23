#select joint chain
sel = cmds.ls(selection = True)
shoulder = sel[0]
elbow = sel[1]
wrist = sel[2]

#build controls: arm ik con + pv con
arm_con = cmds.circle(name = wrist.replace("_JNT", "_CON"))
arm_grp = cmds.group(arm_con[0], name = wrist.replace("_JNT", "_GRP"))

pv_con = cmds.circle(name = wrist.replace("_JNT", "_PV_CON"))
pv_grp = cmds.group(pv_con[0], name = wrist.replace("_JNT", "_PV_GRP"))

#rotate cvs of arm ik con
cmds.select(arm_con[0] + ".cv[:]")
cmds.rotate(0, "90deg", 0, relative = True)

#position arm grp
cmds.matchTransform(arm_grp, wrist)

#calculate pv position
shoulder_pos = cmds.xform(shoulder, query = True, worldSpace = True, translation = True)
elbow_pos = cmds.xform(elbow, query = True, worldSpace = True, translation = True)
wrist_pos = cmds.xform(wrist, query = True, worldSpace = True, translation = True)

crv = cmds.curve(degree = 1, p = [shoulder_pos, elbow_pos, wrist_pos])
cmds.moveVertexAlongDirection(crv + ".cv[1]", n = 8)
pv_pos = cmds.xform(crv + ".cv[1]", query = True, worldSpace = True, translation = True)

#position pv grp
cmds.xform(pv_grp, worldSpace = True, translation = pv_pos)
cmds.delete(crv)

#create ikHandle
ikh = cmds.ikHandle(startJoint = shoulder, endEffector = wrist, name = wrist.replace("_JNT", "_IKH"))

#parent ik to con
cmds.parent(ikh[0], arm_con)

#pole vector constraint
cmds.poleVectorConstraint(pv_con, ikh[0])

#orient constraint wrist joint to arm con
cmds.orientConstraint(arm_con[0], wrist, maintainOffset = True)