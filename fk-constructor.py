#select joints
sel = cmds.ls(selection = True)
shoulder = sel[0]
elbow = sel[1]
wrist = sel[2]

#create control
shoulder_con = cmds.circle(name = shoulder.replace("JNT", "CON"))
cmds.select(shoulder_con[0] + ".cv[:]")
cmds.rotate(0, "90deg", 0, relative = True)
elbow_con = cmds.duplicate(shoulder_con[0], name = elbow.replace("JNT", "CON"))
wrist_con = cmds.duplicate(shoulder_con[0], name = wrist.replace("JNT", "CON"))

#parent controls
shoulder_grp = cmds.group(shoulder_con[0], name = shoulder.replace("JNT", "GRP"))
elbow_grp = cmds.group(elbow_con[0], name = elbow.replace("JNT", "GRP"))
wrist_grp = cmds.group(wrist_con[0], name = wrist.replace("JNT", "GRP"))

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