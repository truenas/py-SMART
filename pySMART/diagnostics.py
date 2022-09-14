# Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.
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
This module contains the definition of the `Diagnostics` class/structure, used to
represent different kinds of SMART SCSI health and attributes associated with a `Device`.

Currently it merges the nvme (v2) and scsi diagnostics structures.
"""

import copy
from typing import Dict, Union


class Diagnostics(object):
    """
    Contains all of the information associated with every SMART SCSI/SAS attribute
    in a `Device`'s SMART table. This class pretends to provide a better view
    of the data recolected from smartctl and its types.

    Values set to None reflects that disk does not support such info
    """

    def __init__(self):
        """Initialize the structure with every field set to None
        """
        # Extra useful fields
        self._block_size = 512
        """The block size of the device in Bytes (512 for most disks)"""

        # Generic counters
        self.Reallocated_Sector_Ct: int = None
        """**(int):** Reallocated sector count."""

        self.Start_Stop_Spec: int = None
        self.Start_Stop_Cycles: int = None
        self.Start_Stop_Pct_Left: int = None
        """**(int):** Percent left of the life-time start-stop cycles."""

        self.Load_Cycle_Spec: int = None
        self.Load_Cycle_Count: int = None
        self.Load_Cycle_Pct_Left: int = None
        """**(int):** Percent left of the life-time load cycles."""

        self.Power_On_Hours: int = None
        """**(int):** Number of hours the device have been powered on."""
        self.Life_Left: int = None
        """**(int):** Percent left of the whole disk life."""

        # Error counters
        self.Corrected_Reads: int = None
        """**(float):** Total number of read operations that had an error but were corrected."""
        self.Corrected_Writes: int = None
        """**(float):** Total number of write operations that had an error but were corrected."""
        self.Corrected_Verifies: int = None

        self._Uncorrected_Reads: int = None
        """**(float):** Total number of read operations that had an uncorrectable error."""
        self._Uncorrected_Writes: int = None
        """**(float):** Total number of write operations that had an uncorrectable error."""
        self._Uncorrected_Verifies: int = None

        self._Reads_GB: float = None
        """**(float):** Total number of GBs readed in the disk life."""
        self._Writes_GB: float = None
        """**(float):** Total number of GBs written in the disk life."""
        self._Verifies_GB: float = None
        """**(float):** Total number of GBs verified in the disk life."""

        self._Reads_count: int = None
        """**(int):** Total number of blocks readed in the disk life."""
        self._Writes_count: int = None
        """**(int):** Total number of blocks written in the disk life."""
        self._Verifies_count: int = None
        """**(int):** Total number of blocks verified in the disk life."""

        self.Non_Medium_Errors: int = None
        """**(int):** Other errors not caused by this disk."""

    # Properties

    @property
    def Uncorrected_Reads(self):
        return self._Uncorrected_Reads

    @property
    def Uncorrected_Writes(self):
        return self._Uncorrected_Writes

    @property
    def Uncorrected_Verifies(self):
        return self._Uncorrected_Verifies

    @property
    def Reads_GB(self) -> Union[float, None]:
        if self._Reads_GB is not None:
            return self._Reads_GB
        elif self._Reads_count is not None:
            return (self._Reads_count * self.block_size) / (1024.0 * 1024 * 1024)
        else:
            return None

    @property
    def Writes_GB(self) -> Union[float, None]:
        if self._Writes_GB is not None:
            return self._Writes_GB
        elif self._Writes_count is not None:
            return (self._Writes_count * self.block_size) / (1024.0 * 1024 * 1024)
        else:
            return None

    @property
    def Verifies_GB(self) -> Union[float, None]:
        if self._Verifies_GB is not None:
            return self._Verifies_GB
        elif self._Verifies_count is not None:
            return (self._Verifies_count * self.block_size) / (1024.0 * 1024 * 1024)
        else:
            return None

    @property
    def Reads_count(self) -> Union[int, None]:
        if self._Reads_count is not None:
            return self._Reads_count
        elif self._Reads_GB is not None:
            return int((self._Reads_GB * 1024 * 1024 * 1024) / self.block_size)
        else:
            return None

    @property
    def Writes_count(self) -> Union[int, None]:
        if self._Writes_count is not None:
            return self._Writes_count
        elif self._Writes_GB is not None:
            return (int)((self._Writes_GB * 1024 * 1024 * 1024) / self.block_size)
        else:
            return None

    @property
    def Verifies_count(self) -> Union[int, None]:
        if self._Verifies_count is not None:
            return self._Verifies_count
        elif self._Verifies_GB is not None:
            return (int)((self._Verifies_GB * 1024 * 1024 * 1024) / self.block_size)
        else:
            return None

    @property
    def block_size(self) -> int:
        return self._block_size

    # Methods

    def get_classic_format(self) -> Dict[str, str]:
        """This method pretends to generate the previously/depreceted diag dictionary structure

        Returns:
            Dict[str,str]: the <1.1.0 PySMART diags structure
        """

        # Copy all the fields to a new dictionary that are not hidden
        ret_dict = {k: v for k, v in vars(
            self).items() if not k.startswith('_')}

        # Add all the properties
        ret_dict.update({k:  getattr(self, k) for k, v in vars(
            Diagnostics).items() if type(v) is property})

        # replace Non_Medium_Errors -> Non-Medium_Errors
        ret_dict['Non-Medium_Errors'] = ret_dict['Non_Medium_Errors']
        del ret_dict['Non_Medium_Errors']

        # replace None with '-'
        for value in ret_dict:
            if ret_dict[value] is None:
                ret_dict[value] = '-'

        # ensure everything is a string
        for value in ret_dict:
            ret_dict[value] = str(ret_dict[value])

        # include percent %
        percent_values = [
            'Life_Left',
            'Start_Stop_Pct_Left',
            'Load_Cycle_Pct_Left'
        ]
        for pv in percent_values:
            if ret_dict[pv] != '-':
                ret_dict[pv] = ret_dict[pv] + '%'

        return ret_dict

    def __getstate__(self, all_info=True):
        """
        Allows us to send a pySMART diagnostics object over a serializable
        medium which uses json (or the likes of json) payloads
        """
        return vars(self)

    def __setstate__(self, state):
        self.__dict__.update(state)


__all__ = ['Diagnostics']
