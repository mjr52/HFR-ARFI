def main():
    p = HFRLoads('u_ax_3ap.mat', 'u_elev_3ap.mat', 'u_lat_3ap.mat', 'axial.mat', 'elev.mat', 'lat.mat')
    p.load_mats()
    p.make_mesh()
    p.load_interp()
    p.make_pointloads()

    pass


class HFRLoads:

    def __init__(self, f_axmat, f_elevmat, f_latmat, axmat, elevmat, latmat,
                 nodesdynfile="nodes.dyn", LCID=1, numElem = (25, 40, 50)):
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

        zforce, xforce, yforce = matload(self.f_axmat), matload(self.f_elevmat), matload(self.f_latmat)
        z, x, y = matload(self.axmat), matload(self.elevmat), matload(self.latmat)

        # SHRINK X AND Y DIRECTIONS FOR Q SYMMETRY
        ylocs, xlocs = np.min(np.where(y>=0)[1]), np.max(np.where(x<=0)[1])
        xlocs = xlocs + 1
        zforce, yforce, xforce = zforce[:, ylocs:, :xlocs], yforce[:, ylocs:, :xlocs], xforce[:, ylocs:, :xlocs]

        # DIVIDE FACE FORCE MAGNITUDES FOR Q SYMMETRY
        xforce[:, :, -1], yforce[:, :, -1], zforce[:, :, -1] = xforce[:, :, -1]/2, yforce[:, :, -1]/2, zforce[:, :, -1]/2
        xforce[:, 0, :], yforce[:, 0, :], zforce[:, 0, :] = xforce[:, 0, :]/2, yforce[:, 0, :]/2, zforce[:, 0, :]/2

        # INVERT FORCE MAGNITUDE
        yforce = -yforce

        x, y = x[x<=0], y[y>=0]
        z = -z

        self.xforce, self.yforce, self.zforce = xforce, yforce, zforce
        self.xmin, self.ymax, self.zmin = np.min(x), np.max(y), np.min(z)

    def make_mesh(self):
        # MAKE MESH
        import sys
        import numpy as np

        sys.path.append("..")
        from fem.mesh import fem_mesh as fm
        from fem.mesh import GenMesh as mesh

        # CHANGE XYZ COORDINATES
        # x = 0 to -x, elev
        # y = 0 to +y, lat
        # z = 0 to -z, ax

        pos = mesh.calc_node_pos((self.xmin, 0.0, 0.0, self.ymax, self.zmin, 0.0), self.numElem)
        mesh.writeNodes(pos)
        mesh.writeElems(self.numElem)

        self.nodeIDs = fm.load_nodeIDs_coords(self.nodesdynfile)
        self.xi = np.array([self.nodeIDs['x'], self.nodeIDs['y'], self.nodeIDs['z']]).T

    def load_interp(self):
        import numpy as np
        import scipy.ndimage

        xforce, yforce, zforce  = self.xforce, self.yforce, self.zforce
        xnode, ynode, znode = self.numElem

        scale = ((znode+1)/np.shape(xforce)[0], (ynode+1)/np.shape(xforce)[1], (xnode+1)/np.shape(xforce)[2])

        xmap = scipy.ndimage.zoom(xforce, scale, order=1)
        ymap = scipy.ndimage.zoom(yforce, scale, order=1)
        zmap = scipy.ndimage.zoom(zforce, scale, order=1)
        self.fmax = np.nanmax(np.abs(([xmap, ymap, zmap])))

        data = np.empty(np.size(xmap),
                        dtype=[('xmap', 'f4'), ('ymap', 'f4'), ('zmap', 'f4')])
        i = 0
        for zp in np.arange(znode + 1):
            for yp in np.arange(ynode + 1):
                for xp in np.arange(xnode + 1):
                    zpr = znode - zp
                    data[i] = (xmap[zpr, yp, xp], ymap[zpr, yp, xp], zmap[zpr, yp, xp])
                    i = i + 1

        self.interps = data

    def make_pointloads(self):
        import numpy as np
        nodeIDs = self.nodeIDs

        with open('PointLoads.dyn', 'w') as NODEFILE:
            NODEFILE.write("*LOAD_NODE_POINT\n")

            def writenode(nodeID, i, maptype, dir):
                val = self.interps[maptype][i]
                if not np.isnan(val) and np.abs(val) > (0.01*self.fmax):
                    NODEFILE.write("%i,%i,%i,%.6f\n" % (nodeID, dir, self.LCID, self.interps[maptype][i]))
                    # NID, [1,2,3], LCID, MAGNITUDE, 0

            for i, nodeID in enumerate(nodeIDs['id']):
                writenode(nodeID, i, 'xmap', 1)
                writenode(nodeID, i, 'ymap', 2)
                writenode(nodeID, i, 'zmap', 3)

            NODEFILE.write("*END\n")

if __name__ == "__main__":
    main()
