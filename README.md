# LO_user
This repo is identical to Parker MacCready's, except for a few modifications:
- [get_lo_info.py](https://github.com/LukeABobay/LO_user/blob/main/get_lo_info.py):
  - Initial modifications outlined in Parker's LO repo were made to personalize file paths
  - Additional modifications were made to use lo_env = 'lb_pc' if (str(HOME) == '/home/bobayl') and ('DESKTOP' in HOSTNAME)
  - Updated on 2025-05-19 to include a wrapper that looks for ROMS output files in /dat2/parker/LO_roms/cas7_t0_x4b if they are not found in /dat1/parker/LO_roms/cas7_t0_x4b because Parker split /dat1/parker/LO_roms/cas7_t0_x4b into the two directories.
- [job_definitions.py](https://github.com/LukeABobay/LO_user/blob/main/extract/box/job_definitions.py):
  - Defined a primary job, "bobay," which extracts bottom depth, northward component of wind speed, eastward component of wind speed, vertical momentum component, rho points where no data are available, dissolved oxygen, phytoplankton, and zooplankton for the entire horizontal domain of the LiveOcean model. This was updated on 2025-05-17 to eliminate variables redundant with those extracted from GLORYS12V1.
  - Defined a secondary job, "bobay_test," which extracts variables of interest from a much smaller horizontal domain as a test data set.
- [run_extractions_and_stage.py](https://github.com/LukeABobay/LO_user/blob/main/extract/box/run_extractions_and_stage.py):
  - I created this script to loop through all available LiveOcean hindcasts (2013-01-01 to 2025-05-20 as of 2025-05-20) to extract them in monthly chunks to directories in /dat1/bobayl/LO_output/extract/cas7_t0_x4b/box/, then move the monthly output .nc files to a temporary directory at /home/bobayl/tmp_transfer/. The temporary directory is necessary because /dat1/ can't be accessed by SSH to transfer files to the Novus custer, so instead, I will pull LiveOcean output files to Novus from bobayl@apogee.ocean.washington.edu:/home/bobayl/tmp_transfer, then delete them from tmp_transfer/.
