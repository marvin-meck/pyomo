#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2008-2022
#  National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

import os.path

from pyomo.common.collections import Bunch
from pyomo.dataportal.factory import DataManagerFactory
from pyomo.dataportal.process_data import _process_include
from pyomo.core import (
    Set,
    Param
)

@DataManagerFactory.register("dat", "Pyomo data command file interface")
class PyomoDataCommands(object):
    def __init__(self):
        self._info = []
        self.options = Bunch()

    def available(self):
        return True

    def initialize(self, **kwds):
        self.filename = kwds.pop('filename')
        self.add_options(**kwds)

    def add_options(self, **kwds):
        self.options.update(kwds)

    def open(self):
        if self.filename is None:  # pragma:nocover
            raise IOError("No filename specified")

    def close(self):
        pass

    def read(self):
        """
        This function does nothing, since executing Pyomo data commands
        both reads and processes the data all at once.
        """
        if not os.path.exists(self.filename):  # pragma:nocover
            raise IOError("Cannot find file '%s'" % self.filename)

    def write(self, model, data):  # pragma:nocover
        """
        This function does nothing, because we cannot write to a *.dat file.
        """
        with open(self.filename, 'w') as OUTPUT:
            
            for ns in data.keys():
                if ns is not None:
                    OUTPUT.write(f"namespace {ns}"+"{")

                for the_set in model.component_map(Set):
                    _write_set(OUTPUT,data[ns],the_set)

                for the_param in model.component_map(Param):
                    raise NotImplementedError

                if ns is not None:
                    OUTPUT.write("}")

    def process(self, model, data, default):
        """
        Read Pyomo data commands and process the data.
        """
        _process_include(['include', self.filename], model, data, default, self.options)

    def clear(self):
        self._info = []

def  _write_set(ostream, data, name):
    """writes set component to ostream
    """
    for key,vals in data[name].items():
        if key is None:
            # regular set
            ostream.write("set {} := ".format(name))
        else:
            # indexed set
            ostream.write("set {}[{}] := ".format(name,key))

        for val in vals:
            ostream.write(f"{val} \n")
        else:
            ostream.write(";\n\n")