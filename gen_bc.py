import sys
sys.path.append("..")
from fem.mesh import bc
import fem_mesh as fm
import GenMesh as mesh

'''
numElem = (75, 75, 150)
pos = mesh.calc_node_pos((-1.5, 0.0, 0.0, 1.5, -3.0, 0.0), numElem)
mesh.writeNodes(pos)
mesh.writeElems(numElem)
'''

# setup quarter symmetry condition
pml_elems = ((5, 0), (0, 5), (5, 5))
face_constraints = (('1,1,1,1,1,1', '1,0,0,0,1,1'),
                    ('0,1,0,1,0,1', '1,1,1,1,1,1'),
                    ('1,1,1,1,1,1', '1,1,1,1,1,1'))
edge_constraints = (((0, 1), (1, 0), (0, 0)), '1,1,0,1,1,1')

bc.apply_pml(pml_elems, face_constraints, edge_constraints)
