import bpy

def add_copy_transf(p_bone, tgt, subtgt):  
    cns_transf = p_bone.constraints.get("Copy Transforms")
    if cns_transf == None:
        cns_transf = p_bone.constraints.new("COPY_TRANSFORMS")
        cns_transf.name = "Copy Transforms"
    cns_transf.target = tgt
    cns_transf.subtarget = subtgt
    

def set_constraint_inverse_matrix(cns):
    # set the inverse matrix of Child Of constraint
    tar_obj = cns.target
    subtarget_pbone = tar_obj.pose.bones.get(cns.subtarget)
    if subtarget_pbone:
        #cns.inverse_matrix = tar_obj.matrix_world.inverted() @ subtarget_pbone.matrix_basis.inverted()
        print("reset child of cns", cns.name, cns.subtarget)
        cns.inverse_matrix = subtarget_pbone.bone.matrix_local.to_4x4().inverted()