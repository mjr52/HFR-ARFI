# HFR-ARFI
To run sims - `python3 setup-n-run.py`

## Necessary Matlab Files
* `I_ax_34ap.mat` - Intensity matrix (axial direction) in W/cm^2
* `I_lat_34ap.mat` - Intensity matrix (lat direction) in W/cm^2
* `I_elev_34ap.mat` - Intensity matrix (elev direction) in W/cm^2
* `axial.mat` - axial depths in mm
* `lat.mat` - lateral depths in mm
* `elev.mat` - elevation depths in mm

* All `I_*.mat` matricies should be the same size. [axial X lat X elev]
* `axial.mat` should be [1 X axial]
* `lat.mat` should be [1 X lat]
* `elev.mat` should be [1 X elev]

## Setup hfr_arfi_original.dyn
* Can edit mesh stiffness, timesteps, DYNA setup here

## Setup HFR_Loads.py
* Line 2 will coorespond to the 6 Matlab file names
* Line 14 will set mesh dimensions (elev, lat, axial)

## Setup setup-n-run.py
* Enter axial locations, sizes, and lesion stiffnesses in lists at beginning of file
