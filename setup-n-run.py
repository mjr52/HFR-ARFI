import os
import time

#locs = [-1.0, -2.5, -3.5] # Axial locs of spherical lesion, in units -cm
locs = [-2.5]
#sizes = [0.1, 0.3, 0.5]  # Radius of spherical lesion, in units cm
sizes = [0.3]
#lesion_yms = [10000, 30000, 90000, 180000] # Units 10*Pa
lesion_yms = [180000]

for loc in locs:
    for size in sizes:

        # Create lesion elems
        os.system('python3 HFR_Loads.py')
        os.system('PYTHONPATH=/work/mjr52 python3 /work/mjr52/fem/mesh/CreateStructure.py --nefile elems.dyn \
                    --partid 3 --sphere --sopts 0.0 0.0 {} {}'.format(str(loc), str(size)))

        # Rerun boundary conditions
        os.system('python3 gen_bc.py')

        for lesion_ym in lesion_yms:
            # Create new dyna_deck
            #cp filename destination
            os.system('cp hfr_arfi_original.dyn hfr_arfi.dyn')
            os.system("sed -i -e 's/LESION_E/{}/' {}".format(str(lesion_ym), 'hfr_arfi.dyn'))

            filename = str(loc)[1] + str(loc)[3] + "_" + str(size)[2] + "_"+str(lesion_ym)[0:-4] +"kPa"
            # Submit batch job
            os.system('PYTHONPATH=/work/mjr52 sbatch slurm.py')
            while not os.path.exists('res_sim.mat'):
                os.system('squeue -p ultrasound -u mjr52')
                time.sleep(60)


            if os.path.exists('res_sim.mat'):
                time.sleep(10)
                # Extract files and move to directory
                os.system('mkdir {}'.format(filename))
                os.system('mv d3* {}'.format(filename))
                # Extract res_sim.mat
                os.system('mv res_sim.mat res_sim_{}.mat'.format(filename))
                os.system('mv res_sim_{}.mat {}'.format(filename, filename))
















