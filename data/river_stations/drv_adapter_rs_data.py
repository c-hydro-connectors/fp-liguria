"""
Class Features:

Name:          drv_adapter_rs_data
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20220301'
Version:       '1.0.0'
"""

#######################################################################################
# Libraries
import logging
import os

import numpy as np
import pandas as pd

from copy import deepcopy

from lib_utils_io import write_file_csv, write_obj, read_obj
from lib_utils_system import fill_tags2string, make_folder, get_root_path, list_folder

from lib_utils_rs import get_data_rs, organize_data_rs, order_data
from lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)
#######################################################################################


# -------------------------------------------------------------------------------------
# Class driver dynamic data
class DriverData:

    def __init__(self, time_step, sections_collection=None, src_dict=None, ancillary_dict=None, dst_dict=None,
                 time_dict=None, variable_dict=None, template_dict=None, info_dict=None,
                 flag_updating_ancillary=True, flag_updating_destination=True, flag_cleaning_tmp=True):

        self.time_step = time_step
        self.sections_collection = sections_collection

        self.src_dict = src_dict
        self.ancillary_dict = ancillary_dict
        self.dst_dict = dst_dict
        self.time_dict = time_dict
        self.variable_dict = variable_dict
        self.template_dict = template_dict

        self.tag_folder_name = 'folder_name'
        self.tag_file_name = 'file_name'
        self.tag_file_fields = 'fields'
        self.tag_section_code = 'code'

        self.domain_name = info_dict['domain']
        self.variable_list = list(self.variable_dict.keys())

        self.section_code = self.get_section_code(self.sections_collection, tag_section_code=self.tag_section_code)
        self.time_range = self.collect_file_time()
        # self.time_reference = self.get_time_reference(self.time_step)

        self.folder_name_src_dset_raw = self.src_dict[self.tag_folder_name]
        self.file_name_src_dset_raw = self.src_dict[self.tag_file_name]
        self.file_fields_src_dset = self.src_dict[self.tag_file_fields]
        self.file_path_src_dset_obj = self.collect_file_obj(self.folder_name_src_dset_raw, self.file_name_src_dset_raw,
                                                            extra_args={'section_code': self.section_code})

        self.folder_name_anc_dset_raw = self.ancillary_dict[self.tag_folder_name]
        self.file_name_anc_dset_raw = self.ancillary_dict[self.tag_file_name]
        self.file_path_anc_dset_obj = self.collect_file_obj(self.folder_name_anc_dset_raw, self.file_name_anc_dset_raw)

        self.folder_name_dst_dset_raw = self.dst_dict[self.tag_folder_name]
        self.file_name_dst_dset_raw = self.dst_dict[self.tag_file_name]
        self.file_fields_dst_dset = self.dst_dict[self.tag_file_fields]
        self.file_path_dst_dset_obj = self.collect_file_obj(self.folder_name_dst_dset_raw, self.file_name_dst_dset_raw)

        self.flag_updating_ancillary = flag_updating_ancillary
        self.flag_updating_destination = flag_updating_destination

        self.flag_cleaning_tmp = flag_cleaning_tmp

        self.folder_name_anc_main = get_root_path(self.folder_name_anc_dset_raw)

        self.discharge_filling_method = None

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    @staticmethod
    def get_section_code(section_collections, tag_section_code='code', no_section_code='-'):
        section_code_raw = list(section_collections[tag_section_code].values)
        section_code_filter = [x for x in section_code_raw if x != no_section_code]
        return section_code_filter
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get time reference
    @staticmethod
    def get_time_reference(time_step, time_period=48, time_frequency='H', time_rounding='D'):
        time_step_floor = time_step.floor(time_rounding)
        time_reference = pd.date_range(end=time_step_floor, periods=time_period, freq=time_frequency)[0]
        time_reference_floor = time_reference.floor(time_rounding)
        return time_reference_floor
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect time(s)
    def collect_file_time(self):

        time_period = self.time_dict["time_period"]
        time_frequency = self.time_dict["time_frequency"]
        time_rounding = self.time_dict["time_rounding"]

        time_end = self.time_step.floor(time_rounding)

        time_range = pd.date_range(end=time_end, periods=time_period, freq=time_frequency)

        return time_range
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect file object(s)
    def collect_file_obj(self, folder_name_raw, file_name_raw, extra_args=None):

        domain_name = self.domain_name
        # datetime_reference = self.time_reference

        section_code = None
        if extra_args is not None:
            if 'section_code' in list(extra_args.keys()):
                section_code = extra_args['section_code']

        file_collections_obj = {}
        for variable_step in self.variable_list:
            variable_tag = self.variable_dict[variable_step]['tag']

            file_name_obj = None
            if variable_tag is not None:

                for datetime_step in self.time_range:

                    dateref_step = self.get_time_reference(datetime_step)

                    template_values_step = {
                        'domain_name': domain_name,
                        'ancillary_var_name': variable_step,
                        'destination_var_name': variable_step,
                        'source_datetime_reference': dateref_step,
                        'source_datetime_run': datetime_step,
                        'source_sub_path_time': datetime_step,
                        'ancillary_datetime': datetime_step, 'ancillary_sub_path_time': datetime_step,
                        'destination_datetime': datetime_step, 'destination_sub_path_time': datetime_step}

                    if section_code is not None:
                        if file_name_obj is None:
                            file_name_obj = {}
                        for section_step in section_code:

                            template_values_step['section_code'] = section_step

                            folder_name_def = fill_tags2string(
                                folder_name_raw, self.template_dict, template_values_step)
                            file_name_def = fill_tags2string(
                                file_name_raw, self.template_dict, template_values_step)
                            file_path_def = os.path.join(folder_name_def, file_name_def)

                            if section_step not in list(file_name_obj.keys()):
                                file_name_obj[section_step] = {}
                                file_name_obj[section_step] = [file_path_def]
                            else:
                                file_name_tmp = file_name_obj[section_step]
                                file_name_tmp.append(file_path_def)
                                file_name_obj[section_step] = file_name_tmp

                    else:

                        if file_name_obj is None:
                            file_name_obj = []

                        folder_name_def = fill_tags2string(
                            folder_name_raw, self.template_dict, template_values_step)
                        file_name_def = fill_tags2string(
                            file_name_raw, self.template_dict, template_values_step)
                        file_path_def = os.path.join(folder_name_def, file_name_def)

                        file_name_obj.append(file_path_def)

                file_collections_obj[variable_step] = file_name_obj

        return file_collections_obj

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get datasets
    def get_data(self):

        log_stream.info(' ----> Get dynamic datasets ... ')

        time_range = self.time_range
        sections_data = self.sections_collection
        sections_code = self.section_code

        file_path_src_obj = self.file_path_src_dset_obj
        file_path_anc_obj = self.file_path_anc_dset_obj

        var_dict = self.variable_dict
        var_fields_src = self.file_fields_src_dset
        flag_upd_anc = self.flag_updating_ancillary
        discharge_filling_method = self.discharge_filling_method

        for var_name, var_fields in var_dict.items():

            log_stream.info(' -----> Variable "' + var_name + '" ... ')

            var_tag = var_fields['tag']
            var_type = var_fields['type']
            var_units = var_fields['units']
            var_valid_range = var_fields['valid_range']
            var_min_count = var_fields['min_count']
            var_scale_factor = var_fields['scale_factor']

            if var_tag is not None:

                file_path_src_obj = file_path_src_obj[var_name]
                file_path_anc_list = file_path_anc_obj[var_name]

                section_dframe_collection = {}
                for time_id, time_step in enumerate(time_range):

                    log_stream.info(' ------> Time Step "' + str(time_step) + '" ... ')

                    file_path_anc_step = file_path_anc_list[time_id]

                    if flag_upd_anc:
                        if os.path.exists(file_path_anc_step):
                            os.remove(file_path_anc_step)

                    section_dframe_collection[time_step] = {}
                    if not os.path.exists(file_path_anc_step):

                        log_stream.info(' -------> Section time-series ...')

                        section_collection_time, section_collection_data = {}, {}
                        for section_code in sections_code:

                            log_stream.info(' --------> Section Code "' + str(section_code) + '" ... ')

                            file_path_src_list = file_path_src_obj[section_code]
                            file_path_src_step = file_path_src_list[time_id]

                            if os.path.exists(file_path_src_step):

                                section_ts_discharge, section_ts_water_level = get_data_rs(
                                    file_path_src_step,
                                    method_data_filling=discharge_filling_method,
                                    column_time_in=var_fields_src['time'],
                                    column_discharge_in=var_fields_src['discharge'],
                                    column_level_in=var_fields_src['water_level'])

                                if section_ts_discharge.__len__() > 0:

                                    section_time = section_ts_discharge.index
                                    section_values = section_ts_discharge.values

                                    if var_valid_range[0] is not None:
                                        section_values[section_values < var_valid_range[0]] = np.nan
                                    if var_valid_range[1] is not None:
                                        section_values[section_values > var_valid_range[1]] = np.nan

                                    section_collection_time[section_code] = section_time
                                    section_collection_data[section_code] = section_values

                                    log_stream.info(' --------> Section Code "' + str(section_code) + '" ... DONE')

                                else:
                                    section_collection_time[section_code] = None
                                    section_collection_data[section_code] = None
                                    log_stream.info(' --------> Section Code "' + str(section_code) + '" ... SKIPPED')
                                    log_stream.warning(' ===> Section datasets is undefined')

                            else:
                                section_collection_time[section_code] = None
                                section_collection_data[section_code] = None
                                log_stream.info(' --------> Section Code "' + str(section_code) + '" ... SKIPPED')
                                log_stream.warning(' ===> Section file is not available')

                        log_stream.info(' -------> Section time-series ... DONE')

                        log_stream.info(' -------> Section dataframe ...')
                        section_dframe_index = None
                        for section_key, section_time in section_collection_time.items():

                            if section_time is not None:
                                if section_dframe_index is None:
                                    section_dframe_index = deepcopy(section_time)

                                if section_dframe_index.__len__() != section_time.__len__():
                                    log_stream.error(
                                        ' ===> Dataframe time index must be always the same for each section')
                                    raise NotImplementedError('Case not implemented yet')

                        if section_dframe_index is not None:

                            section_data_default = np.zeros(shape=[section_dframe_index.__len__()])
                            section_data_default[:] = np.nan

                            section_dframe_data = {}
                            for section_key, section_data in section_collection_data.items():
                                if section_data is None:
                                    section_data = deepcopy(section_data_default)
                                section_dframe_data[section_key] = section_data

                            section_dframe_step = pd.DataFrame(index=section_dframe_index, data=section_dframe_data)
                            section_dframe_step.attrs = {
                                'tag': var_tag, 'scale_factor': var_scale_factor,
                                'type': var_type, 'units': var_units,
                                'valid_range': var_valid_range, 'min_count': var_min_count}

                            folder_name_anc_step, file_name_anc_step = os.path.split(file_path_anc_step)
                            make_folder(folder_name_anc_step)

                            write_obj(file_path_anc_step, section_dframe_step)

                            log_stream.info(' -------> Section dataframe ... DONE')

                        else:
                            log_stream.info(' -------> Section dataframe ... FAILED.')
                            log_stream.warning(' ===> All section file are undefined or not available')

                        log_stream.info(' ------> Time Step "' + str(time_step) + '" ... DONE')

                    else:
                        log_stream.info(' ------> Time Step "' + str(time_step) +
                                        '" ... SKIPPED. Ancillary datasets file are previously created.')

                log_stream.info(' -----> Variable "' + var_name + '" ... DONE')

            else:

                log_stream.info(' -----> Variable "' + var_name + '" ... SKIPPED. Variable tag is null.')

        log_stream.info(' ----> Get dynamic datasets ... DONE')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize datasets
    def organize_data(self):

        log_stream.info(' ----> Organize dynamic datasets ... ')

        time_range = self.time_range
        sections_data = self.sections_collection

        file_path_anc_obj = self.file_path_anc_dset_obj
        file_path_dst_obj = self.file_path_dst_dset_obj

        var_dict = self.variable_dict
        var_fields_dst = self.file_fields_dst_dset

        flag_upd_dst = self.flag_updating_destination

        for var_name, var_fields in var_dict.items():

            log_stream.info(' -----> Variable "' + var_name + '" ... ')

            var_tag = var_fields['tag']
            var_type = var_fields['type']
            var_units = var_fields['units']
            var_valid_range = var_fields['valid_range']
            var_min_count = var_fields['min_count']
            var_scale_factor = var_fields['scale_factor']

            if var_tag is not None:

                file_path_anc_list = file_path_anc_obj[var_name]
                file_path_dst_list = file_path_dst_obj[var_name]

                for time_step, file_path_anc_step, file_path_dst_step in zip(
                        time_range, file_path_anc_list, file_path_dst_list):

                    log_stream.info(' ------> Time Step "' + str(time_step) + '" ... ')

                    if flag_upd_dst:
                        if os.path.exists(file_path_dst_step):
                            os.remove(file_path_dst_step)

                    if os.path.exists(file_path_anc_step):

                        if not os.path.exists(file_path_dst_step):

                            section_dframe_anc_step = read_obj(file_path_anc_step)

                            if isinstance(section_dframe_anc_step, pd.DataFrame):

                                section_dframe_tmp_step = organize_data_rs(time_step,
                                                                           section_dframe_anc_step, sections_data)

                                section_dframe_dst_step = order_data(section_dframe_tmp_step,
                                                                     data_fields_expected=var_fields_dst)

                                folder_name_dst_dset, file_name_dst_dset = os.path.split(file_path_dst_step)
                                make_folder(folder_name_dst_dset)

                                write_file_csv(file_path_dst_step, section_dframe_dst_step)

                                log_stream.info(' ------> Time Step "' + str(time_step) + '" ... DONE')

                            else:
                                log_stream.info(' ------> Time Step "' + str(time_step) + '" ... FAILED')

                        else:
                            log_stream.info(' ------> Time Step "' + str(time_step) +
                                            '" ... SKIPPED. Destination datasets file was created previously.')
                    else:
                        log_stream.info(' ------> Time Step "' + str(time_step) +
                                        '" ... SKIPPED. Ancillary datasets file does not exist.')

                log_stream.info(' -----> Variable "' + var_name + '" ... DONE')

            else:

                log_stream.info(' -----> Variable "' + var_name + '" ... SKIPPED. Variable tag is null.')

        log_stream.info(' ----> Organize dynamic datasets ... DONE')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to clean datasets
    def clean_data(self):

        file_path_anc = self.file_path_anc_dset_obj
        clean_tmp = self.flag_cleaning_tmp
        folder_name_anc_main = self.folder_name_anc_main

        if clean_tmp:

            # Remove tmp file and folder(s)
            for var_name, var_file_path_list in file_path_anc.items():
                for var_file_path_step in var_file_path_list:
                    if os.path.exists(var_file_path_step):
                        os.remove(var_file_path_step)
                    var_folder_name_step, var_file_name_step = os.path.split(var_file_path_step)
                    if var_folder_name_step != '':
                        if os.path.exists(var_folder_name_step):
                            if not os.listdir(var_folder_name_step):
                                os.rmdir(var_folder_name_step)

            # Remove empty folder(s)
            folder_name_anc_list = list_folder(folder_name_anc_main)
            for folder_name_anc_step in folder_name_anc_list:
                if os.path.exists(folder_name_anc_step):
                    if not os.listdir(folder_name_anc_step):
                        os.rmdir(folder_name_anc_step)

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
