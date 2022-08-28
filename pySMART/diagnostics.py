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
represent SMART SCSI attributes associated with a `Device`.
"""

import copy
from typing import Dict


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

        self.Uncorrected_Reads: int = None
        """**(float):** Total number of read operations that had an uncorrectable error."""
        self.Uncorrected_Writes: int = None
        """**(float):** Total number of write operations that had an uncorrectable error."""
        self.Uncorrected_Verifies: int = None

        self.Reads_GB: float = None
        """**(float):** Total number of GBs readed in the disk life."""
        self.Writes_GB: float = None
        """**(float):** Total number of GBs written in the disk life."""
        self.Verifies_GB: float = None

        self.Non_Medium_Errors: int = None
        """**(int):** Other errors not caused by this disk."""

    def get_classic_format(self) -> Dict[str, str]:
        """This method pretends to generate the previously/depreceted diag dictionary structure

        Returns:
            Dict[str,str]: the <1.1.0 PySMART diags structure
        """
        ret_dict = copy.deepcopy(vars(self))

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
