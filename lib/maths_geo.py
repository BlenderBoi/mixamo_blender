from math import *
from mathutils import *


def mat3_to_vec_roll(mat):
    vec = mat.col[1]
    vecmat = vec_roll_to_mat3(mat.col[1], 0)
    vecmatinv = vecmat.inverted()
    rollmat = vecmatinv @ mat
    roll = atan2(rollmat[0][2], rollmat[2][2])
    return roll


def vec_roll_to_mat3(vec, roll):
    target = Vector((0, 0.1, 0))
    nor = vec.normalized()
    axis = target.cross(nor)
    if axis.dot(axis) > 0.0000000001: # this seems to be the problem for some bones, no idea how to fix
        axis.normalize()
        theta = target.angle(nor)
        bMatrix = Matrix.Rotation(theta, 3, axis)
    else:
        updown = 1 if target.dot(nor) > 0 else -1
        bMatrix = Matrix.Scale(updown, 3)
        bMatrix[2][2] = 1.0

    rMatrix = Matrix.Rotation(roll, 3, nor)
    mat = rMatrix @ bMatrix
    return mat


def align_bone_x_axis(edit_bone, new_x_axis):
    new_x_axis = new_x_axis.cross(edit_bone.y_axis)
    new_x_axis.normalize()
    dot = max(-1.0, min(1.0, edit_bone.z_axis.dot(new_x_axis)))
    angle = acos(dot)
    edit_bone.roll += angle
    dot1 = edit_bone.z_axis.dot(new_x_axis)
    edit_bone.roll -= angle * 2.0
    dot2 = edit_bone.z_axis.dot(new_x_axis)
    if dot1 > dot2:
        edit_bone.roll += angle * 2.0


def align_bone_z_axis(edit_bone, new_z_axis):
    new_z_axis = -(new_z_axis.cross(edit_bone.y_axis))
    new_z_axis.normalize()
    dot = max(-1.0, min(1.0, edit_bone.x_axis.dot(new_z_axis)))
    angle = acos(dot)
    edit_bone.roll += angle
    dot1 = edit_bone.x_axis.dot(new_z_axis)
    edit_bone.roll -= angle * 2.0
    dot2 = edit_bone.x_axis.dot(new_z_axis)
    if dot1 > dot2:
        edit_bone.roll += angle * 2.0


def signed_angle(u, v, normal):
    nor = normal.normalized()
    a = u.angle(v)    
    
    c = u.cross(v)
    
    if c.magnitude == 0.0:
        c = u.normalized().cross(v)
    if c.magnitude == 0.0:
        return 0.0
        
    if c.angle(nor) < 1:
        a = -a
    return a


def project_point_onto_plane(q, p, n):
    n = n.normalized()
    return q - ((q - p).dot(n)) * n


def get_pole_angle(base_bone, ik_bone, pole_location):
    pole_normal = (ik_bone.tail - base_bone.head).cross(pole_location - base_bone.head)
    projected_pole_axis = pole_normal.cross(base_bone.tail - base_bone.head)
    return signed_angle(base_bone.x_axis, projected_pole_axis, base_bone.tail - base_bone.head)
    
    
def get_pose_matrix_in_other_space(mat, pose_bone):
    rest = pose_bone.bone.matrix_local.copy()
    rest_inv = rest.inverted()

    if pose_bone.parent and pose_bone.bone.use_inherit_rotation:
        par_mat = pose_bone.parent.matrix.copy()
        par_inv = par_mat.inverted()
        par_rest = pose_bone.parent.bone.matrix_local.copy()

    else:
        par_mat = Matrix()
        par_inv = Matrix()
        par_rest = Matrix()

    smat = rest_inv @ (par_rest @ (par_inv @ mat))

    return smat


def get_ik_pole_pos(b1, b2, method=1, axis=None): 
   
    if method == 1:
        # IK pole position based on real IK bones vector
        plane_normal = (b1.head - b2.tail)
        midpoint = (b1.head + b2.tail) * 0.5
        prepole_dir = b2.head - midpoint#prepole_fk.tail - prepole_fk.head
        pole_pos = b2.head + prepole_dir.normalized()# * 4
        pole_pos = project_point_onto_plane(pole_pos, b2.head, plane_normal)
        pole_pos = b2.head + ((pole_pos - b2.head).normalized() * (b2.head - b1.head).magnitude * 1.7)
        
    elif method == 2:    
        # IK pole position based on bone2 Z axis vector      
        pole_pos = b2.head + (axis.normalized() * (b2.tail-b2.head).magnitude)
    
    return pole_pos
    
    
def rotate_point(point, angle, origin, axis):
    rot_mat = Matrix.Rotation(angle, 4, axis.normalized())
    # rotate in world origin space
    offset_vec = -origin
    offset_knee = point + offset_vec
    # rotate
    rotated_point = rot_mat @ offset_knee
    # bring back to original space
    rotated_point = rotated_point -offset_vec
    return rotated_point
    
    
def dot_product(x, y):
    return sum([x[i] * y[i] for i in range(len(x))])

    
def norm(x):
    return sqrt(dot_product(x, x))

    
def normalize(x):
    return [x[i] / norm(x) for i in range(len(x))]

    
def project_vector_onto_plane(x, n):
    d = dot_product(x, n) / norm(n)
    p = [d * normalize(n)[i] for i in range(len(n))]
    vec_list = [x[i] - p[i] for i in range(len(x))]
    return Vector((vec_list[0], vec_list[1], vec_list[2]))
    