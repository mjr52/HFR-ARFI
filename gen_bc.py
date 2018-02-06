import sys
import os
import bc
import fem_mesh as fm
import GenMesh as mesh


'''
numElem = (50, 200, 300)
pos = mesh.calc_node_pos((-2.5, 0.0, -5.0, 5.0, -15.0, 0.0), numElem)
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
