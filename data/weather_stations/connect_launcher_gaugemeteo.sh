#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='FloodPROOFS Liguria Meteo Data download and gridding'
script_version="1.0.0"
script_date='2021/01/20'

script_folder='/home/user/PycharmProjects/fp-hyde-master/'
src_folder=$script_folder'apps/'

virtual_env_folder='/home/user/fp_libs_python3/bin'
virtual_env_name='virtualenv_python3'

script_file='/home/user/PycharmProjects/fp-hyde-master/apps/meteolig2continuum/DownloadMeteoRaster.py'
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get time information
d=$(date -u +"%Y-%m-%d %H")
#-----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
# Add path to pythonpath
export PYTHONPATH="${PYTHONPATH}:$script_folder:$src_folder"
# Activate virtual env
export PATH=$virtual_env_folder:$PATH
source activate $virtual_env_name
#-----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
# Launch script
python3 ${script_file}
#----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
# Terminate    
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> ... END"
echo " ==> Bye, Bye"
echo " ==================================================================================="
#----------------------------------------------------------------------------------------

