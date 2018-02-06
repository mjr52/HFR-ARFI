# HFR-ARFI

## How to Setup Sims
* Run `HFR_Loads.py` to generate `PointLoads.dyn`.
* Run `gen_bc.py` to generate boundary condition files:
  + `bc.dyn`
  + `elems_pml.dyn`
* `hfr_arfi.dyn` will include all of the individual `*.dyn` files into the sim.

## How to Run LS-DYNA
* On the DCC, run the following: `PYTHONPATH=/work/mjr52 sbatch slurm.py`
* This will create a `res_sim.mat` file from `nodout`.
