#!/bin/env python
#SBATCH --mem=128G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --partition=ultrasound
#SBATCH --mail-user=mjr52@duke.edu
#SBATCH --mail-type=END

from time import ctime
import os
from socket import gethostname
from fem.post.create_disp_dat import create_dat as create_disp_dat
from fem.post.create_res_sim_mat import run as create_res_sim_mat

print('STARTED: {}'.format(ctime()))
print('HOST: {}'.format(gethostname()))

DYNADECK = "hfr_arfi.dyn"
NTASKS = os.getenv('SLURM_NTASKS', '8')

os.system("ls-dyna-d ncpu={} i={}".format(NTASKS, DYNADECK))

#os.system("rm d3*")

create_disp_dat()

create_res_sim_mat(DYNADECK)
create_res_sim_mat(DYNADECK, disp_comp=1, disp_scale=1e4, ressim="res_sim_radial.mat")

#if os.path.isfile("res_sim.mat"):
#    os.system("rm nodout")

os.system('xz -T0 -v disp.dat')

print("FINISHED: {}".format(ctime()))

