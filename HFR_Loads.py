def main():
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
                 nodesdynfile="nodes.dyn", LCID=1, numElem = (40, 25, 50)):
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
        self.fmax = None

    def load_mats(self):
        #LOAD MATLAB FORCE DATA
        import numpy as np

        def matload(filename):
            import scipy.io as sio
            return sio.loadmat(filename)[filename[:-4]]

        zforce, yforce, xforce = matload(self.f_axmat), matload(self.f_elevmat), matload(self.f_latmat)
        z, y, x = matload(self.axmat), matload(self.elevmat), matload(self.latmat)

        # SHRINK X AND Y DIRECTIONS FOR Q SYMMETRY
        ylocs, xlocs = np.min(np.where(y>=0)[1]), np.min(np.where(x>=0)[1])
        zforce, yforce, xforce = zforce[:, xlocs:, ylocs:], yforce[:, xlocs:, ylocs:], xforce[:, xlocs:, ylocs:]

        x, y = x[x>=0], y[y>=0]
        z = z[:] - np.max(z[:])

        self.xforce, self.yforce, self.zforce = xforce, yforce, zforce
        self.xmax, self.ymax, self.zmin = np.max(x), np.max(y), np.min(z)

    def make_mesh(self):
        # MAKE MESH
        import sys
        import numpy as np

        sys.path.append("..")
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

        xforce, yforce, zforce  = self.xforce, self.yforce, self.zforce
        xnode, ynode, znode = self.numElem

        scale = ((znode+1)/np.shape(xforce)[0], (xnode+1)/np.shape(xforce)[1], (ynode+1)/np.shape(xforce)[2])

        xmap = scipy.ndimage.zoom(xforce, scale, order=1)
        ymap = scipy.ndimage.zoom(yforce, scale, order=1)
        zmap = scipy.ndimage.zoom(zforce, scale, order=1)
        self.fmax = np.nanmax([xmap, ymap, zmap])

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
        import numpy as np
        nodeIDs = self.nodeIDs

        with open('PointLoads.dyn', 'w') as NODEFILE:
            NODEFILE.write("*LOAD_NODE_POINT\n")

            def writenode(nodeID, i, maptype, dir):
                val = self.interps[maptype][i]
                if not np.isnan(val) and val > (0.01*self.fmax):
                    NODEFILE.write("%i,%i,%i,%.6f,%i\n" % (nodeID, dir, self.LCID, self.interps[maptype][i], 0))
                    # NID, [1,2,3], LCID, MAGNITUDE, 0

            for i, nodeID in enumerate(nodeIDs['id']):
                writenode(nodeID, i, 'xmap', 1)
                writenode(nodeID, i, 'ymap', 2)
                writenode(nodeID, i, 'zmap', 3)

            NODEFILE.write("*END\n")

if __name__ == "__main__":
    main()
