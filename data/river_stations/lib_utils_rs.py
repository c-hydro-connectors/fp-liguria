"""
Library Features:

Name:          lib_utils_rs
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20220301'
Version:       '1.0.0'
"""

#######################################################################################
# Libraries
import logging
from copy import deepcopy

import numpy as np
import pandas as pd

from lib_info_args import logger_name

# Logging
pd.options.mode.chained_assignment = None
log_stream = logging.getLogger(logger_name)
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to order ground network data
def order_data(data_frame, data_fields_expected):

    data_fields_raw = list(data_frame.columns.values)

    columns_result = all(elem in data_fields_raw for elem in data_fields_expected)
    if columns_result:
        data_frame_ordered = data_frame[data_fields_expected]
    else:
        log_stream.warning(' ===> Dataframe ordering failed because all expected columns are not in original dataframe')
        data_frame_ordered = data_frame

    return data_frame_ordered

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read hydro observed file in mat and txt format
def get_data_rs(file_name,
                column_time_in='a1sDateVet', column_discharge_in='a1dQOss', column_level_in='a1dLivOssMean',
                column_time_out='time', column_discharge_out='discharge', column_level_out='water_level',
                method_data_filling='ffill'):

    # Check file format and extension
    if file_name.endswith('.txt'):

        file_table = pd.read_table(file_name, sep=' ')

        if column_time_in in list(file_table.columns):
            file_time = file_table[column_time_in].values
        else:
            log_stream.error(' ===> File column "' + column_time_in + '" observed not available in the datasets')
            raise IOError('Check your input file "' + file_name + '" to control the available fields')

        if column_discharge_in in list(file_table.columns):
            file_discharge = file_table[column_discharge_in].values
        else:
            log_stream.error(' ===> File column "' + column_discharge_in + '" observed not available in the datasets')
            raise IOError('Check your input file "' + file_name + '" to control the available fields')

        if column_level_in is not None:
            if column_level_in in list(file_table.columns):
                file_water_level = file_table[column_level_in].values
            else:
                log_stream.warning(' ===> File column "' + column_level_in + '" observed not available in the datasets')
                file_water_level = np.zeros(shape=file_discharge.shape[0])
                file_water_level[:] = -9999.0
        else:
            log_stream.warning(' ===> File column for water level observed variable is undefined')
            file_water_level = np.zeros(shape=file_discharge.shape[0])
            file_water_level[:] = -9999.0

        time_list = file_time.tolist()
        discharge_list = file_discharge.tolist()
        water_level_list = file_water_level.tolist()

        section_period = []
        section_data_discharge = []
        section_data_water_level = []
        for time_step, discharge_step, water_level_step in zip(time_list, discharge_list, water_level_list):

            section_time = pd.Timestamp(pd.Timestamp(str(time_step)))
            section_point_discharge = float(discharge_step)
            section_point_water_level = float(water_level_step)

            section_period.append(section_time)
            section_data_discharge.append(section_point_discharge)
            section_data_water_level.append(section_point_water_level)

        section_series_discharge = pd.Series(index=section_period, data=section_data_discharge)
        section_series_water_level = pd.Series(index=section_period, data=section_data_water_level)

        section_series_discharge = fill_data_rs(
            obj_hydro=section_series_discharge, obj_method_filling=method_data_filling)

    else:
        log_stream.error(' ===> File "' + file_name + '" unsupported format')
        raise NotImplementedError('Case not implemented yet')

    return section_series_discharge, section_series_water_level

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to fill obj hydro
def fill_data_rs(obj_hydro, obj_method_filling=None, obj_method_filtering=None, obj_limit_filling=10,
                 obj_value_min=0.0, obj_value_max=None, obj_nodata=-9999.0):

    if obj_value_min is not None:
        obj_hydro[obj_hydro < obj_value_min] = np.nan
    if obj_value_max is not None:
        obj_hydro[obj_hydro > obj_value_max] = np.nan

    time_valid_first = obj_hydro.first_valid_index()
    time_valid_last = obj_hydro.last_valid_index()

    if obj_method_filling is not None:
        if obj_method_filling == 'ffill':
            obj_hydro_filled = obj_hydro.ffill(axis='rows', limit=obj_limit_filling)
        elif obj_method_filling == 'bfill':
            obj_hydro_filled = obj_hydro.bfill(axis='rows', limit=obj_limit_filling)
        elif obj_method_filling == 'interpolate':
            obj_hydro_filled = obj_hydro.interpolate(method='values', limit=obj_limit_filling)
        else:
            log_stream.error(' ===> Method to fill data "' + obj_method_filling + '" is not suppoerted')
            raise NotImplementedError('Case not implemented yet')
    else:
        obj_hydro_filled = deepcopy(obj_hydro)

    obj_hydro_filled = obj_hydro_filled.fillna(obj_nodata)

    if obj_method_filtering:
        obj_hydro_filtered = obj_hydro_filled[time_valid_first:time_valid_last]
    else:
        obj_hydro_filtered = deepcopy(obj_hydro_filled)

    return obj_hydro_filtered

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to organize river stations data into a dataframe
def organize_data_rs(time_reference, data_df, sections_df, no_data=-9999.0,
                     column_code_data='code', column_discharge_data='discharge', column_time_data='time'):

    section_times = list(data_df.index)
    section_codes = list(data_df.columns)
    section_datasets = list(data_df.values)
    section_attrs = data_df.attrs

    if 'units' in list(section_attrs.keys()):
        data_units = section_attrs['units']
    else:
        data_units = ''

    section_df_collection = {}
    for time_id, time_step in enumerate(section_times):

        section_values = list(section_datasets[time_id])
        section_obj = dict(zip(section_codes, section_values))

        section_df_merged = None
        for section_key, section_data in section_obj.items():
            section_df_step = sections_df.loc[sections_df[column_code_data] == section_key, :]

            if np.isnan(section_data):
                section_data = no_data

            section_df_step[column_discharge_data] = section_data
            section_df_step[column_time_data] = time_step

            if 'units' not in list(section_df_step.columns):
                section_df_step['units'] = data_units

            if section_df_merged is None:
                section_df_merged = deepcopy(section_df_step)
            else:
                section_df_merged = pd.concat([section_df_merged, section_df_step])

        section_df_collection[time_step] = section_df_merged

    if time_reference in list(section_df_collection.keys()):
        section_df_select = section_df_collection[time_reference]
    else:
        section_df_select = None

    return section_df_select

# -------------------------------------------------------------------------------------
