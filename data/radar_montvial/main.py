import os
import h5py


class H5ls:
    """ 
    The H5ls class is a callable object that adds the name of an HDF5 object to its list of names if the
    object has a dtype attribute and the name is not already in the list.
    """
    
    def __init__(self):
        self.names = []

    def __call__(self, name, h5obj):
        if hasattr(h5obj,'dtype') and not name in self.names:
            self.names += [name]


def main():
    """
    This function reads a specific HDF5 file and prints the contents of all datasets within it.
    """
   
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    FOLDER = 'data'
    FILENAME = 'odim.20230412_000016.766_to_20230412_000023.766_Vial_radar_SEC.h5'
    
    path = os.path.join(BASEDIR, FOLDER, FILENAME)
 
    with h5py.File(path,'r') as f:    
        h5ls = H5ls()
        f.visititems(h5ls)
        
        for ds in h5ls.names:
            print(f[ds][()])
   

if __name__ == "__main__":
    main()