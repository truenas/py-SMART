# Copyright (C) 2014 Marc Herndon
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.
#
################################################################
"""
This module contains generic utilities and configuration information for use
by the other submodules of the `pySMART` package.
"""

import copy
import io
import logging
import logging.handlers
import os
import traceback
from typing import Dict, Any, Optional
from shutil import which

_srcfile = __file__
TRACE = logging.DEBUG - 5


class TraceLogger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name)
        logging.addLevelName(TRACE, 'TRACE')
        return

    def trace(self, msg, *args, **kwargs):
        self.log(TRACE, msg, *args, **kwargs)

    def findCaller(self, stack_info=False, stacklevel=1):
        """
        Overload built-in findCaller method
        to omit not only logging/__init__.py but also the current file
        """
        f = logging.currentframe()
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        orig_f = f
        while f and stacklevel > 1:
            f = f.f_back
            stacklevel -= 1
        if not f:
            f = orig_f
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename in (logging._srcfile, _srcfile):
                f = f.f_back
                continue
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
            break
        return rv


def configure_trace_logging():
    if getattr(logging.handlers.logging.getLoggerClass(), 'trace', None) is None:
        logging.setLoggerClass(TraceLogger)


def any_in(search_in, *searched_items):
    """
    return True if any of searched_items is in search_in otherwise False.
    raise
    """
    assert len(searched_items) > 0
    return any(map(lambda one: one in search_in, searched_items))


def all_in(search_in, *searched_items):
    """
    return True if all of searched_items are in search_in otherwise False
    does not care about duplicates in searched_items potentially evaluates all of them,
    """
    assert len(searched_items) > 0
    return all(map(lambda one: one in search_in, searched_items))


smartctl_type_dict = {
    'ata': 'ata',
    'csmi': 'ata',
    'nvme': 'nvme',
    'sas': 'scsi',
    'sat': 'sat',
    'sata': 'ata',
    'scsi': 'scsi',
    'atacam': 'atacam'
}
"""
**(dict of str):** Contains actual interface types (ie: sas, csmi) as keys and
the corresponding smartctl interface type (ie: scsi, ata) as values.
"""

SMARTCTL_PATH = which('smartctl')


def smartctl_isvalid_type(interface_type: str) -> bool:
    """Tests if the interface_type is supported

    Args:
        interface_type (str): An internal interface_type

    Returns:
        bool: True if the type is supported, false z
    """
    if interface_type in smartctl_type_dict:
        return True
    elif 'megaraid,' in interface_type:
        return True
    else:
        return False


def smartctl_type(interface_type: Optional[str]) -> Optional[str]:
    """This method basically searchs on smartctl_type_dict to convert from internal
       smartctl interface type to an understable type for smartctl. However, further
       transforms may be performed for some special interfaces

    Args:
        interface_type (str): An internal representation of an smartctl interface type

    Returns:
        str: Returns the corresponding smartctl interface_type that matches with the internal interface representation.
             In case it is not supported, None would be returned
    """
    if interface_type is None:
        return None

    if interface_type in smartctl_type_dict:
        return smartctl_type_dict[interface_type]
    elif 'megaraid,' in interface_type:
        return interface_type
    else:
        return None


def get_object_properties(obj: Any, deep_copy: bool = True, remove_private: bool = False, recursive: bool = True) -> Optional[Dict[str, Any]]:
    if obj is None:
        return None

    if not hasattr(obj, '__dict__'):
        return obj

    prop_names = dir(obj)

    if deep_copy:
        ret = copy.deepcopy(vars(obj))
    else:
        ret = vars(obj)

    available_types = ['dict', 'str', 'int', 'float', 'list', 'NoneType']
    recursion_types = ['object', 'NvmeError']

    for prop_name in prop_names:
        prop_val = getattr(obj, prop_name)
        prop_val_type_name = type(prop_val).__name__

        if (prop_name[0] != '_'):
            # Get properties from objects
            if (prop_val_type_name in available_types) and (prop_name not in ret):
                ret[prop_name] = prop_val

            # Do recursion
            if recursive:
                if prop_val_type_name in recursion_types:
                    ret[prop_name] = get_object_properties(
                        prop_val, deep_copy, remove_private, recursive)
                elif prop_val_type_name == 'list':
                    ret[prop_name] = []
                    for item in prop_val:
                        if type(item).__name__ in recursion_types:
                            ret[prop_name].append(get_object_properties(
                                item, deep_copy, remove_private, recursive))
                        else:
                            ret[prop_name].append(item)
                elif prop_val_type_name == 'dict':
                    ret[prop_name] = {}
                    for key, value in prop_val.items():
                        if type(value).__name__ in recursion_types:
                            ret[prop_name][key] = get_object_properties(
                                value, deep_copy, remove_private, recursive)
                        else:
                            ret[prop_name][key] = value

    if remove_private:
        for key in ret.keys():
            if key[0] == '_':
                del ret[key]

    return ret


__all__ = ['smartctl_type', 'SMARTCTL_PATH',
           'all_in', 'any_in', 'get_object_properties']
