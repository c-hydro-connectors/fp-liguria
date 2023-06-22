"""
Library Features:

Name:          decode_hdf5_data
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
               Francesco Silvestro (francesco.silvestro@cimafoundation.org)
Date:          '20230413'
Version:       '1.0.1'
"""


# ----------------------------------------------------------------------------
# libraries
import os
import h5py
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# method to read hdf5 odim
def read_hdf5_odim(file_name):

    file_handle = h5py.File(file_name, 'r')

    workspace = {}
    for group in file_handle:
    
        obj = file_handle[group]
        group = str(group)
    
        workspace[group] = {}
        workspace[group]['dset_value'] = {}
        workspace[group]['dset_attrs'] = {}

        for k, a in obj.attrs.items():
            k = str(k)
            workspace[group]['dset_attrs'][k] = {}
            workspace[group]['dset_attrs'][k] = a
    
        for m in obj:
    
            member = obj[m]
            m = str(m)
    
            workspace[group]['dset_value'][m] = {}
            workspace[group]['dset_value'][m]['var_value'] = {}
            workspace[group]['dset_value'][m]['var_attrs'] = {}
            for kk, aa in member.attrs.items():
                kk = str(kk)
                workspace[group]['dset_value'][m]['var_attrs'][kk] = {}
                workspace[group]['dset_value'][m]['var_attrs'][kk] = aa
    
            for d in member:

                data = member[d]
                if hasattr(data, 'size'):
                    values = data[()]
                else:
                    values = None

                workspace[group]['dset_value'][m]['var_value'][d] = {}
                workspace[group]['dset_value'][m]['var_value'][d]['values'] = {}
                workspace[group]['dset_value'][m]['var_value'][d]['attrs'] = {}

                workspace[group]['dset_value'][m]['var_value'][d]['values'] = values
                for kk, aa in data.attrs.items():
                    kk = str(aa)
                    workspace[group]['dset_value'][m]['var_value'][d]['attrs'][str(kk)] = {}
                    workspace[group]['dset_value'][m]['var_value'][d]['attrs'][str(kk)] = aa

    values = workspace['dataset1']['dset_value']['data1']['var_value']['data']['values']
    attrs = workspace['dataset1']['dset_value']['data1']['var_value']['data']['attrs']
    
    startazA = workspace['dataset1']['dset_value']['how']['var_attrs']['startazA']
    startazT = workspace['dataset1']['dset_value']['how']['var_attrs']['startazT']
    elangles = workspace['dataset1']['dset_value']['how']['var_attrs']['elangles']

    return workspace
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# call script from external
if __name__ == "__main__":

    # Test parameters
    folder_name = '/home/fabio/Desktop/PyCharm_ARPAL/connectors-dev/data/radar_montvial/data/'
    file_name = 'odim.20230412_000517.619_to_20230412_000524.619_Vial_radar_SEC.h5'

    if not os.path.exists(os.path.join(folder_name, file_name)):
        raise FileNotFoundError('File "' + os.path.join(folder_name, file_name) + '" not found! Exit.')

    hdf5_data_collection = read_hdf5_odim(os.path.join(folder_name, file_name))

    print('ciao')
# ----------------------------------------------------------------------------
