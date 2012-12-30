"""Create a mock HDF5 file."""
import h5py

with h5py.File('test.h5') as f:
    g1 = f.create_group('MyGroup1')
    g2 = f.create_group('MyGroup2')
    g11 = g1.create_group('MyGroup11')
    g111 = g11.create_group('MyGroup111')
    f.attrs['MyAttr'] = 23.
    dset = g2.create_dataset("MyDataset1", (100, 100), 'i')
    dset[...] = 42
    g111.create_dataset("MyDataset2", (2,3,4,5), 'f')
    g1.attrs['MyAttr2'] = 'my string'
