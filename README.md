H5View: a light, h5py/IPython-friendly HDF5 viewer in text mode
===============================================================

This light Python module lets you explore interactively any HDF5 file in
a Python console or in IPython. Pretty print the file structure and get the
shape, data type, and size of any dataset. Tab completion works in IPython
to let you access any subgroup or dataset.

H5View is based on the h5py package.

Usage
=====

    import h5view
    with h5view.open('test.h5') as f:
        # display the whole structure of the file
        print(f)
        # access a group and display its information
        print(f.MyGroup1.SubGroup)
        # access a dataset
        X = f.MyGroup2.MyDataset[0,:]
        # access an attribute
        val = f.MyGroup3.myAttr
        # access to the corresponding h5py object
        item = f.MyDataset.item()
        # get a descendant from its relative path
        print(f.MyGroup4.get('MySubgroup/MyDataset'))

In IPython, tab completion shows all direct children (groups, datasets,
attributes) of the file or any item (group/dataset), making it quite
convenient to interactively explore a HDF5 file.

Installation
============

The code is only in `h5view.py`. The `create.py` file is used to create
a test HDF5 file.

Download the package and type in a shell (a test HDF5 file is created
automatically in the same folder):

    $ python h5view.py
    Let's display the file.
    <HDF5 file "/home/me/h5view/test.h5", 50.2 KB>
    /
      * MyAttr: 23.0
    /MyGroup1
      * MyAttr2: my string
    /MyGroup1/MyGroup11
    /MyGroup1/MyGroup11/MyGroup111
    /MyGroup1/MyGroup11/MyGroup111/MyDataset2: shape (2, 3, 4, 5), dtype "float32", 480 B
    /MyGroup2
    /MyGroup2/MyDataset1: shape (100, 100), dtype "int32", 39.1 KB

    Now, let's access some attributes, groups, and datasets.
    23.0
    /MyGroup2
    /MyGroup2/MyDataset1: shape (100, 100), dtype "int32", 39.1 KB
    [[42 42]
     [42 42]]
    [ 0.  0.]

    
