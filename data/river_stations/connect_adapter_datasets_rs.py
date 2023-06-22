#!/usr/bin/python3

"""
HYDE Adapting Tool - River Stations

__date__ = '20210512'
__version__ = '1.0.0'
__author__ = 'Fabio Delogu (fabio.delogu@cimafoundation.org'
__library__ = 'HyDE'

General command line:
python3 hyde_adapter_datasets_rs.py -settings_file configuration.json -time "YYYY-MM-DD HH:MM"

Version:
20220228 (1.5.0) --> Pre-operational Release
20210512 (1.0.0) --> Beta Release
"""
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Complete library
import logging
import os
import time

from lib_utils_io import read_file_settings
from lib_utils_logging import set_logging_file
from lib_utils_time import set_time
from lib_info_args import logger_name, logger_format, time_format_algorithm

from drv_adapter_rs_geo import DriverGeo
from drv_adapter_rs_data import DriverData

from argparse import ArgumentParser

# Logging
log_stream = logging.getLogger(logger_name)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Algorithm information
alg_name = 'HYDE ADAPTING TOOL - RIVER STATIONS'
alg_version = '1.5.0'
alg_release = '2022-02-28'
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Script Main
def main():

    # -------------------------------------------------------------------------------------
    # Get algorithm settings
    alg_settings, alg_time = get_args()

    # Set algorithm settings
    data_settings = read_file_settings(alg_settings)

    # Set algorithm logging
    set_logging_file(
        logger_name=logger_name,
        logger_formatter=logger_format,
        logger_file=os.path.join(data_settings['log']['folder_name'], data_settings['log']['file_name']))
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Info algorithm
    log_stream.info(' ============================================================================ ')
    log_stream.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_release + ')')
    log_stream.info(' ==> START ... ')
    log_stream.info(' ')

    # Time algorithm information
    start_time = time.time()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Organize time run
    time_now, time_run, time_range = set_time(
        time_run_args=alg_time,
        time_run_file=data_settings['time']['time_now'],
        time_format=time_format_algorithm,
        time_period=data_settings['time']['time_period'],
        time_frequency=data_settings['time']['time_frequency'],
        time_rounding=data_settings['time']['time_rounding']
    )
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Get geographical information
    driver_geo = DriverGeo(src_dict=data_settings['data']['static'])
    sections_collections = driver_geo.read_data()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Iterate over time(S)
    for time_step in time_range:

        # -------------------------------------------------------------------------------------
        # Info time
        log_stream.info(' ---> TIME STEP: ' + str(time_step) + ' ... ')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get datasets information
        driver_data = DriverData(time_step,
                                 sections_collection=sections_collections,
                                 src_dict=data_settings['data']['dynamic']['source'],
                                 ancillary_dict=data_settings['data']['dynamic']['ancillary'],
                                 dst_dict=data_settings['data']['dynamic']['destination'],
                                 time_dict=data_settings['time'],
                                 variable_dict=data_settings['variable'],
                                 template_dict=data_settings['template'],
                                 info_dict=data_settings['info'],
                                 flag_updating_ancillary=data_settings['flags']['update_dynamic_data_ancillary'],
                                 flag_updating_destination=data_settings['flags']['update_dynamic_data_destination'],
                                 flag_cleaning_tmp=data_settings['flags']['clean_dynamic_data_tmp'])
        # Get datasets
        driver_data.get_data()
        # Organize and save datasets
        driver_data.organize_data()

        # Clean temporary file(s)
        driver_data.clean_data()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Info time
        log_stream.info(' ---> TIME STEP: ' + str(time_step) + ' ... DONE')
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Info algorithm
    time_elapsed = round(time.time() - start_time, 1)

    log_stream.info(' ')
    log_stream.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_release + ')')
    log_stream.info(' ==> TIME ELAPSED: ' + str(time_elapsed) + ' seconds')
    log_stream.info(' ==> ... END')
    log_stream.info(' ==> Bye, Bye')
    log_stream.info(' ============================================================================ ')
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get script argument(s)
def get_args():
    parser_handle = ArgumentParser()
    parser_handle.add_argument('-settings_file', action="store", dest="alg_settings")
    parser_handle.add_argument('-time', action="store", dest="alg_time")
    parser_values = parser_handle.parse_args()

    if parser_values.alg_settings:
        alg_settings = parser_values.alg_settings
    else:
        alg_settings = 'configuration.json'

    if parser_values.alg_time:
        alg_time = parser_values.alg_time
    else:
        alg_time = None

    return alg_settings, alg_time

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to set logging information
def set_logging(logger_file='log.txt', logger_format=None):
    if logger_format is None:
        logger_format = '%(asctime)s %(name)-12s %(levelname)-8s ' \
                        '%(filename)s:[%(lineno)-6s - %(funcName)20s()] %(message)s'

    # Remove old logging file
    if os.path.exists(logger_file):
        os.remove(logger_file)

    # Set level of root debugger
    logging.root.setLevel(logging.DEBUG)

    # Open logging basic configuration
    logging.basicConfig(level=logging.DEBUG, format=logger_format, filename=logger_file, filemode='w')

    # Set logger handle
    logger_handle_1 = logging.FileHandler(logger_file, 'w')
    logger_handle_2 = logging.StreamHandler()
    # Set logger level
    logger_handle_1.setLevel(logging.DEBUG)
    logger_handle_2.setLevel(logging.DEBUG)
    # Set logger formatter
    logger_formatter = logging.Formatter(logger_format)
    logger_handle_1.setFormatter(logger_formatter)
    logger_handle_2.setFormatter(logger_formatter)

    # Add handle to logging
    logging.getLogger('').addHandler(logger_handle_1)
    logging.getLogger('').addHandler(logger_handle_2)

# -------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Call script from external library
if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------------
