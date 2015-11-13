"""H5View: a light, h5py/IPython-friendly HDF5 viewer in text mode.

Usage:

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
        # access the corresponding h5py object
        item = f.MyDataset.item()
        # get a descendant from its relative path
        print(f.MyGroup4.get('MySubgroup/MyDataset'))

In IPython, tab completion shows all direct children (groups, datasets,
attributes) of the file or any item (group/dataset), making it quite
convenient to interactively explore a HDF5 file.

"""
import h5py
from collections import namedtuple
import operator
import os


ItemInfo = namedtuple('ItemInfo', ['path', 'itemtype', 'shape', 'dtype'])


def format_size(num_bytes):
    """Pretty print a file size."""
    num_bytes = float(num_bytes)
    KiB = 1024
    MiB = KiB * KiB
    GiB = KiB * MiB
    TiB = KiB * GiB
    PiB = KiB * TiB
    EiB = KiB * PiB
    ZiB = KiB * EiB
    YiB = KiB * ZiB
    if num_bytes > YiB:
        output = '%.3g YB' % (num_bytes / YiB)
    elif num_bytes > ZiB:
        output = '%.3g ZB' % (num_bytes / ZiB)
    elif num_bytes > EiB:
        output = '%.3g EB' % (num_bytes / EiB)
    elif num_bytes > PiB:
        output = '%.3g PB' % (num_bytes / PiB)
    elif num_bytes > TiB:
        output = '%.3g TB' % (num_bytes / TiB)
    elif num_bytes > GiB:
        output = '%.3g GB' % (num_bytes / GiB)
    elif num_bytes > MiB:
        output = '%.3g MB' % (num_bytes / MiB)
    elif num_bytes > KiB:
        output = '%.3g KB' % (num_bytes / KiB)
    else:
        output = '%.3g B' % num_bytes
    return output


class Item(object):
    """Represents a group or a dataset in the file."""
    def __init__(self, file, parent, name, itemtype, **kwargs):
        self.file = file
        self.parent = parent
        self.name = name
        self.itemtype = itemtype
        self._children = {}
        # set special keyword arguments as attributes
        self.kwargs = kwargs
        # for n, v in kwargs.iteritems():
            # setattr(self, n, v)
        parentnm = parent.fullname
        if parentnm.endswith('/'):
            parentnm = parentnm[:-1]
        self.fullname = '/'.join([parentnm, name])

    def _add_child(self, name, child):
        """Add a child."""
        self._children[name] = child

    def children(self):
        """Return the list of children."""
        return self._children.keys()


    # Hierarchy methods
    # -----------------
    def get(self, name):
        """Return an attribute, a children, or any descendant from its full
        name."""
        if name in self._attrs():
            return self._attr(name)
        if '/' in name:
            parent, child = os.path.split(name)
            return self.get(parent).get(child)
        else:
            return self._children.get(name)

    def __getattr__(self, name):
        """Access a child."""
        val = self.get(name)
        if val is None:
            val = self.kwargs.get(name)
        return val

    def __dir__(self):
        """Return the list of attributes and children."""
        d = self._children.keys()
        d.extend(self._attrs())
        d.extend(self.kwargs)
        return sorted(d)


    # Item methods
    # ------------
    def item(self):
        """Return the associated h5py object (group or dataset)."""
        return self.file.f.get(self.fullname)

    def __getitem__(self, i):
        """For a dataset, access any part of the array."""
        if self.itemtype == 'dataset':
            return self.item()[i]

    def _attr(self, name):
        """Return an attribute."""
        item = self.item()
        return item.attrs[name]

    def _attrs(self):
        """Return the list of attributes."""
        return sorted(self.item().attrs.keys())


    # Display methods
    # ---------------
    def _get_repr(self):
        """Pretty print this item."""
        if self.itemtype == 'group':
            # s = '<Group   "{0:s}">'.format(self.fullname)
            s = self.fullname
        elif self.itemtype == 'dataset':
            item = self.file.f.get(self.fullname)
            shape, dtype = str(item.shape), str(item.dtype)
            try:
                nbytes = item.dtype.itemsize * item.size
            except:
                nbytes = item.dtype.itemsize * item.len()
            # s = '<Dataset "{0:s}": shape {1:s}, dtype "{2:s}">'.format(
                # self.fullname, shape, dtype)
            s = '{0:s}: shape {1:s}, dtype "{2:s}", {3:s}'.format(
                self.fullname, shape, dtype, format_size(nbytes))
        for attr in self._attrs():
            val = self.get(attr)
            s += '\n  * {0}: {1}'.format(attr, val)
        return s

    def __repr__(self):
        """Pretty print this item and all its descendants recursively."""
        repr = self._get_repr()
        for child in self._children:
            repr = repr + "\n"
            repr += self.get(child).__repr__()
        return repr


class Dataset(Item):
    def __init__(self, file, parent, name):
        super(Dataset, self).__init__(file, parent, name, 'dataset')

class Group(Item):
    def __init__(self, file, parent, name):
        super(Group, self).__init__(file, parent, name, 'group')


class File(Item):
    """Represents a HDF5 file."""
    def __init__(self, filename=None):
        self.fullname = '/'
        super(File, self).__init__(self, self, '', 'group')
        self.filename = filename
        self.f = None
        self.iteminfos = []
        # open and visit the file
        self.open()


    # I/O methods
    # -----------
    def open(self, filename=None):
        """Open the file in read-only mode."""
        if filename is None:
            filename = self.filename
        else:
            self.filename = filename
        if self.f is None and filename is not None:
            self.f = h5py.File(filename, 'r')
            self._visit()

    def close(self):
        """Close the file."""
        if self.f is not None:
            self.f.close()

    def __enter__(self):
        """Enter the file, to use with `with`."""
        # self.open()
        return self

    def __exit__(self, type, value, tb):
        """Exit the file, to use with `with`."""
        self.close()


    # Exploration methods
    # -------------------
    def _visit_item(self, name):
        """Callback function for `visit`: register the item."""
        item = self.f.get(name)
        # add item info
        if isinstance(item, h5py.Dataset):
            itemtype = 'dataset'
            shape, dtype = item.shape, item.dtype
        elif isinstance(item, h5py.Group):
            itemtype = 'group'
            shape, dtype = None, None
        self.iteminfos.append(ItemInfo(name, itemtype, shape, dtype))
        # add child
        if '/' not in name:
            self._children[name] = Item(self, self, name, itemtype, shape=shape, dtype=dtype)
        else:
            parentnm, childnm = os.path.split(name)
            parent = self.get(parentnm)
            child = Item(self, parent, childnm, itemtype, shape=shape, dtype=dtype)
            parent._add_child(childnm, child)

    def _visit(self):
        """Visit the whole hierarchy of groups and datasets in the file."""
        if self.f is not None:
            self.f.visit(self._visit_item)
        self.iteminfos = sorted(self.iteminfos, key=operator.itemgetter(0))
        return self.iteminfos


    # Display methods
    # ---------------
    def __repr__(self):
        """Return a complete pretty print representation of the file and
        all its groups, datasets and attributes."""
        filename = os.path.realpath(self.filename)
        s = '<HDF5 file "{0:s}", {1:s}>\n'.format(
            filename, format_size(os.path.getsize(filename)))
        s += super(File, self).__repr__()
        return s


def open(filename):
    """Open a HDF5 file."""
    return File(filename)


if __name__ == '__main__':
    filename = 'test.h5'
    if not os.path.exists(filename):
        import create
    with open(filename) as f:
        print("Let's display the file.")
        print(f)
        print("")
        print("Now, let's access some attributes, groups, and datasets.")
        print(f.MyAttr)
        print(f.MyGroup2)
        print(f.MyGroup2.MyDataset1[2:4,3:5])
        print(f.MyGroup1.MyGroup11.get('MyGroup111/MyDataset2')[0,0,0,1:3])

