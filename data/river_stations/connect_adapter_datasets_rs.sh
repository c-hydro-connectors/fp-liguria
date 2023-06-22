#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='HYDE DOWNLOADER - GROUND NETWORK WS - REALTIME'
script_version="1.1.0"
script_date='2020/10/30'

virtualenv_folder='/home/fabio/library/fp_libs_python3/'
virtualenv_name='virtualenv_python3'
script_folder='/home/fabio/Desktop/PyCharm_ARPAL/connectors-dev/'

# Execution example:
# python3 hyde_adapter_datasets_rs.py -settings_file configuration.json -time "2020-10-26 03:23"
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get file information
script_file='/home/fabio/Desktop/PyCharm_ARPAL/connectors-dev/data/river_stations/hyde_adapter_datasets_rs.py'
settings_file='/home/fabio/Desktop/PyCharm_ARPAL/connectors-dev/data/river_stations/hyde_adapter_datasets_rs_example.json'

# Get information (-u to get gmt time)
time_now=$(date -u +"%Y-%m-%d %H:00")
# time_now='2018-07-23 00:00' # DEBUG 
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Activate virtualenv
export PATH=$virtualenv_folder/bin:$PATH
source activate $virtualenv_name

# Add path to pythonpath
export PYTHONPATH="${PYTHONPATH}:$script_folder"
#-----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script start
echo " ==================================================================================="
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> START ..."
echo " ==> COMMAND LINE: " python3 $script_file -settings_file $settings_file -time $time_now

# Run python script (using setting and time)
python3 $script_file -settings_file $settings_file -time "$time_now"

# Info script end
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> ... END"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------

