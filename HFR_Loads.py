def main():
    import os
    os.environ['HOME'] = 'C:/Users/mringel/Desktop/Projects_US/'
    p = HFRLoads('u_ax_3ap.mat', 'u_elev_3ap.mat', 'u_lat_3ap.mat', 'axial.mat', 'elev.mat', 'lat.mat')
    p.load_mats()
    p.make_mesh()
    p.load_interp()
    p.make_pointloads()

    '''
    from pointloads import PointLoads
    s = PointLoads('PointLoads.dyn')
    s.show_image_plane(ele_coord=0)
    '''
    pass


class HFRLoads:

    def __init__(self, f_axmat, f_elevmat, f_latmat, axmat, elevmat, latmat,
                 nodesdynfile="nodes.dyn", LCID=1, numElem = (10, 10, 10)):
        import os

        args = locals()
        for k,v in args.items():
            if type(v) is str:
                try:
                    os.path.isfile(v)
                except FileNotFoundError:
                    print("File doesn't exist")
            setattr(self, k, v)

        self.nodeIDs = None
        self.xi = None
        self.xforce = None
        self.yforce = None
        self.zforce = None
        self.xmax = None
        self.ymax = None
        self.zmin = None
        self.interps = None

    def load_mats(self):
        #LOAD MATLAB FORCE DATA
        import scipy.io as sio
        import numpy as np

        zforce = sio.loadmat(self.f_axmat, matlab_compatible=True)[self.f_axmat[:-4]]
        yforce = sio.loadmat(self.f_elevmat, matlab_compatible=True)[self.f_elevmat[:-4]]
        xforce = sio.loadmat(self.f_latmat, matlab_compatible=True)[self.f_latmat[:-4]]

        z = sio.loadmat(self.axmat, matlab_compatible=True)[self.axmat[:-4]]
        y = sio.loadmat(self.elevmat, matlab_compatible=True)[self.elevmat[:-4]]
        x = sio.loadmat(self.latmat, matlab_compatible=True)[self.latmat[:-4]]

        # SHRINK X AND Y DIRECTIONS FOR Q SYMMETRY
        ylocs = np.where(y>=0)[1]
        xlocs = np.where(x>=0)[1]
        zforce = zforce[0::1, xlocs, :]
        zforce = zforce[:, 0::1, ylocs]
        yforce = yforce[0::1, xlocs, :]
        yforce = yforce[:, 0::1, ylocs]
        xforce = xforce[0::1, xlocs, :]
        xforce = xforce[:, 0::1, ylocs]
        x = x[x>=0]
        y = y[y>=0]
        z = z.flatten()
        x = x[0::1]
        z = z[0::1]
        z = z - max(z)

        self.xforce = xforce
        self.yforce = yforce
        self.zforce = zforce
        self.xmax = np.max(x)
        self.ymax = np.max(y)
        self.zmin = np.min(z)


    def make_mesh(self):
        # MAKE MESH
        import sys
        import os
        import numpy as np

        HOME = os.getenv('HOME')
        sys.path.append(HOME)
        from fem.mesh import fem_mesh as fm
        from fem.mesh import GenMesh as mesh

        pos = mesh.calc_node_pos((0.0, self.xmax, 0.0, self.ymax, self.zmin, 0.0), self.numElem)
        mesh.writeNodes(pos)
        mesh.writeElems(self.numElem)

        self.nodeIDs = fm.load_nodeIDs_coords(self.nodesdynfile)
        self.xi = np.array([self.nodeIDs['x'], self.nodeIDs['y'], self.nodeIDs['z']]).T

    def load_interp(self):
        import numpy as np
        import scipy.ndimage
        '''
        # THIS IS TOO SLOW
        # ans = scipy.interpolate.griddata(points, xforce, xi, method='linear')

        vtx, wts = Fast_Interp.interp_weights(self.points, self.xi)

        self.xmap = Fast_Interp.interpolate(self.xforce, vtx, wts)
        self.ymap = Fast_Interp.interpolate(self.yforce, vtx, wts)
        self.zmap = Fast_Interp.interpolate(self.zforce, vtx, wts)

        # data = {'xmap': xmap, 'ymap': ymap, 'zmap': zmap}
        # sio.savemat('newloads', data)
        '''

        xforce = self.xforce
        yforce = self.yforce
        zforce = self.zforce
        xnode, ynode, znode = self.numElem

        scale = ((znode+1)/np.shape(xforce)[0], (xnode+1)/np.shape(xforce)[1], (ynode+1)/np.shape(xforce)[2])

        xmap = scipy.ndimage.zoom(xforce, scale, order=1)
        ymap = scipy.ndimage.zoom(yforce, scale, order=1)
        zmap = scipy.ndimage.zoom(zforce, scale, order=1)

        data = np.empty(np.size(xmap),
                        dtype=[('xmap', 'f4'), ('ymap', 'f4'), ('zmap', 'f4')])
        i = 0
        for zp in np.arange(znode + 1):
            for yp in np.arange(ynode + 1):
                for xp in np.arange(xnode + 1):
                    zpr = znode - zp
                    data[i] = (xmap[zpr, xp, yp], ymap[zpr, xp, yp], zmap[zpr, xp, yp])
                    i = i + 1

        self.interps = data

    def make_pointloads(self):
        # Check NodeIDs and xmaps the same size??

        nodeIDs = self.nodeIDs

        NODEFILE = open('PointLoads.dyn', 'w')
        NODEFILE.write("*LOAD_NODE_POINT\n")

        for i, nodeID in enumerate(nodeIDs['id']):
            NODEFILE.write("%i,%i,%i,%.6f,%i\n" % (nodeID, 1, self.LCID, self.interps['xmap'][i], 0))
            NODEFILE.write("%i,%i,%i,%.6f,%i\n" % (nodeID, 2, self.LCID, self.interps['ymap'][i], 0))
            NODEFILE.write("%i,%i,%i,%.6f,%i\n" % (nodeID, 3, self.LCID, self.interps['zmap'][i], 0))
            # NID, [1,2,3], LCID, MAGNITUDE, 0

        NODEFILE.write("*END\n")
        NODEFILE.close()

if __name__ == "__main__":
    main()
