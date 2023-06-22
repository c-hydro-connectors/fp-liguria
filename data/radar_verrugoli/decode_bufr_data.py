"""
Library Features:

Name:          decode_bufr_data
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
               Francesco Silvestro (francesco.silvestro@cimafoundation.org)
Date:          '20211028'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Libraries
import logging
import subprocess
import os
import numpy as np
import pandas as pd

from lib_radar_process import exec_process

# Log
log_stream = logging.getLogger(__name__)
log_format = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=log_format)

# Debug
import matplotlib.pylab as plt
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to decode bufr data
def decode_bufr_data(
        time_reference, time_format='%Y%m%d%H%M%S', folder_name=None, file_name_list=None,
        library_bufr_folder=None, library_bufr_exec='decbufr', table_bufr_folder='',
        file_bufr_header='bufr_header.txt', file_bufr_data='bufr_data.dec', file_bufr_section='section.1.out',
        cmd_bufr_tmpl="{library_bufr_path} -d {table_bufr_folder} {file_bufr_name} {file_bufr_header} {file_bufr_data}"
):

    log_stream.info(' --> Decode bufr ... ')

    if os.path.exists(file_bufr_header):
        os.remove(file_bufr_header)
    if os.path.exists(file_bufr_data):
        os.remove(file_bufr_data)
    if os.path.exists(file_bufr_section):
        os.remove(file_bufr_section)

    if file_name_list is None:
        file_name_list = [
            'T_PABV83_C_LAMM_{time_reference}.bin',
            'T_PAGC83_C_LAMM_{time_reference}.bin',
            'T_PAGE83_C_LAMM_{time_reference}.bin',
            'T_PAGH83_C_LAMM_{time_reference}.bin',
            'T_PAGL83_C_LAMM_{time_reference}.bin'
        ]

    if isinstance(time_reference, str):
        time_reference = pd.Timestamp(time_reference)
        time_reference = time_reference.strftime(format=time_format)
    else:
        log_stream.error(' ===> Time obj not in string format')
        raise NotImplementedError('Case not implemented yet')

    if library_bufr_folder is not None:
        library_bufr_path = os.path.join(library_bufr_folder, library_bufr_exec)
    else:
        library_bufr_path = library_bufr_exec

    if not os.path.exists(library_bufr_path):
        log_stream.error(' ===> Bufr decoder "' + library_bufr_path + '" executable not found')
        raise RuntimeError('Bufr library executable not available in the selected folder.')

    if not os.path.exists(table_bufr_folder):
        log_stream.error(' ===> Bufr decoder "' + table_bufr_folder + '" tables not found')
        raise RuntimeError('Bufr library tables not available in the selected folder.')

    file_data = {}
    for file_name_step in file_name_list:

        if folder_name is not None:
            file_path_step_tmpl = os.path.join(folder_name, file_name_step)
        else:
            file_path_step_tmpl = file_name_step

        file_tags = {'time_reference', time_reference}
        file_path_step_fill = file_path_step_tmpl.format(time_reference=time_reference)
        file_tag_step_fill = os.path.split(file_path_step_fill)[1]

        log_stream.info(' ---> File "' + file_tag_step_fill + '" ... ')
        if os.path.exists(file_path_step_fill):

            cmd_bufr_tags = {
                "library_bufr_path": library_bufr_path, "table_bufr_folder": table_bufr_folder,
                "file_bufr_name": file_path_step_fill,
                "file_bufr_header": file_bufr_header, "file_bufr_data": file_bufr_data}

            cmd_bufr_exec = cmd_bufr_tmpl.format(**cmd_bufr_tags)

            exec_process(cmd_bufr_exec)

            if os.path.exists(file_bufr_header):
                bufr_header = read_file_header(file_bufr_header)
            else:
                log_stream.error(' ===> Bufr file header "' + file_bufr_header + '" not found')
                raise IOError('Bufr file header is mandatory to decode bufr dataset.')

            if os.path.exists(file_bufr_data):
                bufr_data = read_file_data(file_bufr_data, bufr_header=bufr_header)
            else:
                log_stream.error(' ===> Bufr file data "' + file_bufr_data + '" not found')
                raise IOError('Bufr file data is mandatory to decode bufr dataset.')

            log_stream.info(' ---> File "' + file_tag_step_fill + '" ... DONE')

        else:
            bufr_data = None
            log_stream.info(' ---> File "' + file_tag_step_fill + '" ... FAILED. File does not exist.')

        file_data[file_tag_step_fill] = bufr_data

        if os.path.exists(file_bufr_header):
            os.remove(file_bufr_header)
        if os.path.exists(file_bufr_data):
            os.remove(file_bufr_data)
        if os.path.exists(file_bufr_section):
            os.remove(file_bufr_section)

    log_stream.info(' --> Decode bufr ... DONE')

    return file_data

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file data
def read_file_data(file_bufr_data='', bufr_header=None, bufr_dtype='uint8'):

    if 'data_cols' in list(bufr_header.keys()):
        bufr_cols = bufr_header['data_cols']
    else:
        log_stream.error(' ===> Bufr header field "data_cols" is mandatory ')
        raise IOError('Bufr header field not found. Check your settings.')

    if 'data_rows' in list(bufr_header.keys()):
        bufr_rows = bufr_header['data_rows']
    else:
        log_stream.error(' ===> Bufr header field "data_rows" is mandatory ')
        raise IOError('Bufr header field not found. Check your settings.')

    if 'data_alpha' in list(bufr_header.keys()):
        bufr_alpha = bufr_header['data_alpha']
    else:
        log_stream.error(' ===> Bufr header field "data_alpha" is mandatory ')
        raise IOError('Bufr header field not found. Check your settings.')
    if 'data_beta' in list(bufr_header.keys()):
        bufr_beta = bufr_header['data_beta']
    else:
        log_stream.error(' ===> Bufr header field "data_beta" is mandatory ')
        raise IOError('Bufr header field not found. Check your settings.')

    bufr_data_1d = np.fromfile(file_bufr_data, dtype=bufr_dtype)
    bufr_data_2d = np.reshape(bufr_data_1d, [bufr_cols, bufr_rows])
    data_values_2d = (bufr_data_2d + bufr_alpha) * bufr_beta

    return data_values_2d
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file header
def read_file_header(file_name_header, file_header_args=None):
    if file_header_args is None:
        file_header_args = {'data_alpha': 'dBZ-value offset (Alpha)',
                            'data_beta': 'dBZ-value increment (Beta)',
                            'data_cols': 'Number of pixels per column',
                            'data_rows': 'Number of pixels per row'}

    file_handle_header = open(file_name_header, 'r')
    file_header_data = {}
    for file_row in file_handle_header.readlines():
        for field_key, field_str in list(file_header_args.items()):
            if field_str in file_row:
                row_value = file_row.split()[3]
                if (field_key == 'data_cols') or (field_key == 'data_rows'):
                    file_header_data[field_key] = int(float(row_value))
                else:
                    file_header_data[field_key] = float(row_value)

    return file_header_data
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to execute process
def exec_process(command_line=None, command_path=None):

    try:

        # Info command-line start
        log_stream.info(' ---> Process execution: ' + command_line + ' ... ')

        # Execute command-line
        if command_path is not None:
            os.chdir(command_path)
        process_handle = subprocess.Popen(
            command_line, shell=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Read standard output
        while True:
            string_out = process_handle.stdout.readline()
            if isinstance(string_out, bytes):
                string_out = string_out.decode('UTF-8')

            if string_out == '' and process_handle.poll() is not None:

                if process_handle.poll() == 0:
                    break
                else:
                    log_stream.error(' ===> Run failed! Check command-line settings!')
                    raise RuntimeError('Error in executing process')
            if string_out:
                logging.info(str(string_out.strip()))

        # Collect stdout and stderr and exitcode
        std_out, std_err = process_handle.communicate()
        std_exit = process_handle.poll()

        if std_out == b'' or std_out == '':
            std_out = None
        if std_err == b'' or std_err == '':
            std_err = None

        # Check stream process
        stream_process(std_out, std_err)

        # Info command-line end
        log_stream.info(' ---> Process execution: ' + command_line + ' ... DONE')
        return std_out, std_err, std_exit

    except subprocess.CalledProcessError:
        # Exit code for process error
        log_stream.error(' ===> Process execution FAILED! Errors in the called executable!')
        raise RuntimeError('Errors in the called executable')

    except OSError:
        # Exit code for os error
        log_stream.error(' ===> Process execution FAILED!')
        raise RuntimeError('Executable not found!')

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to stream process
def stream_process(std_out=None, std_err=None):

    if std_out is None and std_err is None:
        return True
    else:
        log_stream.warning(' ===> Exception occurred during process execution!')
        return False
# -------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Call script from external library
if __name__ == "__main__":

    # Test parameters
    library_bufr_folder = '/home/fabio/Desktop/PyCharm_Workspace/tmp/read_bufr_radar/bufr_3.2/'
    table_bufr_folder = '/home/fabio/Desktop/PyCharm_Workspace/tmp/read_bufr_radar//tables-OPERA-20121119'
    time_reference = '20210918015000'

    bufr_data_collections = decode_bufr_data(
        time_reference=time_reference, library_bufr_folder=library_bufr_folder, table_bufr_folder=table_bufr_folder)

    print('ciao')
# ----------------------------------------------------------------------------
