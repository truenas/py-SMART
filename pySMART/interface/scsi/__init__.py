# Copyright (C) 2024 Rafael Leira, Naudit HPCN S.L.
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
This module contains the definition of the `SCSI` device interface type.
Take into account that SAS disks are a kind of scsi devices
"""

import logging
import os
import re
import warnings
from time import time, strptime, mktime, sleep
from typing import Tuple, Union, List, Dict, Optional, Iterator
from enum import Enum
from typing import Optional, Iterator, Union, List

# pySMART module imports
from ..common import CommonIface
from ...smartctl import Smartctl
from ...testentry import TestEntry
from .diagnostics import Diagnostics


class SCSIAttributes(CommonIface):

    """Class to store the SCSI/SAS attributes
    """

    def __init__(self, data: Optional[Iterator[str]] = None, abridged: bool = False, smartEnabled: bool = True, sm: Optional[Smartctl] = None, dev_reference: Optional[str] = None):
        """Initializes the attributes

        Args:
            data (Iterator[str], optional): Iterator of the lines of the output of the command scsi smart-log. Defaults to None.
            abridged (bool, optional): If True, only a subset of the attributes will be parsed. Defaults to False.
            smartEnabled (bool, optional): If True, the SMART attributes will be parsed. Defaults to True.
            sm (Optional[Smartctl], optional): Smartctl reader object. Defaults to None.
            dev_reference (Optional[str], optional): The device reference. Defaults to None.
        """

        self.tests: List[TestEntry] = []
        """
        **(list of `TestEntry`):** Contains the complete SMART self-test log
        for this device, as provided by smartctl.
        """

        self.diagnostics: Diagnostics = Diagnostics()
        """
        **Diagnostics** Contains parsed and processed diagnostic information
        extracted from the SMART information. Currently only populated for
        SAS and SCSI devices, since ATA/SATA SMART attributes are manufacturer
        proprietary.
        """

        if data is not None:
            self.parse(data,
                       abridged=abridged,
                       smartEnabled=smartEnabled,
                       sm=sm,
                       dev_reference=dev_reference)

    @staticmethod
    def has_compatible_data(data: Iterator[str]) -> bool:
        """Checks if the data is compatible with this class

        Args:
            data (Iterator[str]): Iterator of the lines of the output of the command scsi smart-log

        Returns:
            bool: True if compatible, False otherwise
        """

        # TODO: Should think about this

        return True

    def __getstate__(self, all_info=True) -> Dict:
        """
        Allows us to send a pySMART Device object over a serializable
        medium which uses json (or the likes of json) payloads
        """

        state_dict = {
            'legacyDiagnostics': self.diagnostics.__getstate__(),
        }
        return state_dict

    def parse(self, data: Iterator[str], abridged: bool = False, smartEnabled: bool = True, sm: Optional[Smartctl] = None, dev_reference: Optional[str] = None) -> None:
        """Parses the attributes from the raw data

        Args:
            data (Iterator[str]): Iterator of the lines of the output of the command scsi smart-log
            abridged (bool, optional): If True, only a subset of the attributes will be parsed. Defaults to False.
            smartEnabled (bool, optional): If True, the SMART attributes will be parsed. Defaults to True.
            sm (Optional[Smartctl], optional): Smartctl reader object. Defaults to None.
            dev_reference (Optional[str], optional): The device reference. Defaults to None.
        """

        # Control variables for performance
        parse_self_tests = False
        parse_ascq = False

        # Advance data until required things are found
        for line in data:

            #######################################
            #          Test  attributes           #
            #######################################
            if line.strip() == '':  # Blank line stops sub-captures
                if parse_self_tests is True:
                    parse_self_tests = False
                if parse_ascq:
                    parse_ascq = False
                    # self.messages.append(message)
            # if parse_ascq:
            #    message += ' ' + line.lstrip().rstrip()
            if parse_self_tests:
                # Detect Test Format

                ## SCSI/SAS FORMAT ##
                # Example smartctl output
                # SMART Self-test log
                # Num  Test              Status                 segment  LifeTime  LBA_first_err [SK ASC ASQ]
                #      Description                              number   (hours)
                # # 1  Background short  Completed                   -   33124                 - [-   -    -]
                format_scsi = re.compile(
                    r'^[#\s]*(\d+)\s{2,}(.*[^\s])\s{2,}(.*[^\s])\s{2,}(.*[^\s])\s{2,}(.*[^\s])\s{2,}(.*[^\s])\s+\[([^\s]+)\s+([^\s]+)\s+([^\s]+)\]$').match(line)

                if format_scsi is not None:
                    format = 'scsi'
                    parsed = format_scsi.groups()
                    num = int(parsed[0])
                    test_type = parsed[1]
                    status = parsed[2]
                    segment = parsed[3]
                    hours = parsed[4]
                    lba = parsed[5]
                    sense = parsed[6]
                    asc = parsed[7]
                    ascq = parsed[8]
                    self.tests.append(TestEntry(
                        format,
                        num,
                        test_type,
                        status,
                        hours,
                        lba,
                        segment=segment,
                        sense=sense,
                        asc=asc,
                        ascq=ascq
                    ))

            if "Self-test log" in line:
                parse_self_tests = True  # Set flag to capture test entries
                continue

        #######################################
        #    Global / generic  attributes     #
        #######################################
            if 'used endurance' in line:
                pct = int(line.split(':')[1].strip()[:-1])
                self.diagnostics.Life_Left = 100 - pct
                continue

            if 'Specified cycle count' in line:
                self.diagnostics.Start_Stop_Spec = int(
                    line.split(':')[1].strip())
                continue

            if 'Accumulated start-stop cycles' in line:
                self.diagnostics.Start_Stop_Cycles = int(
                    line.split(':')[1].strip())
                if self.diagnostics.Start_Stop_Spec and self.diagnostics.Start_Stop_Spec != 0:
                    self.diagnostics.Start_Stop_Pct_Left = int(round(
                        100 - (self.diagnostics.Start_Stop_Cycles /
                               self.diagnostics.Start_Stop_Spec), 0))
                continue

            if 'Specified load-unload count' in line:
                self.diagnostics.Load_Cycle_Spec = int(
                    line.split(':')[1].strip())
                continue

            if 'Accumulated load-unload cycles' in line:
                self.diagnostics.Load_Cycle_Count = int(
                    line.split(':')[1].strip())
                if self.diagnostics.Load_Cycle_Spec and self.diagnostics.Load_Cycle_Spec != 0:
                    self.diagnostics.Load_Cycle_Pct_Left = int(round(
                        100 - (self.diagnostics.Load_Cycle_Count /
                               self.diagnostics.Load_Cycle_Spec), 0))
                continue

            if 'Elements in grown defect list' in line:
                self.diagnostics.Reallocated_Sector_Ct = int(
                    line.split(':')[1].strip())
                continue

            if 'read:' in line:
                line_ = ' '.join(line.split()).split(' ')
                if line_[1] == '0' and line_[2] == '0' and line_[3] == '0' and line_[4] == '0':
                    self.diagnostics.Corrected_Reads = 0
                elif line_[4] == '0':
                    self.diagnostics.Corrected_Reads = int(
                        line_[1]) + int(line_[2]) + int(line_[3])
                else:
                    self.diagnostics.Corrected_Reads = int(line_[4])
                self.diagnostics._Reads_GB = float(line_[6].replace(',', '.'))
                self.diagnostics._Uncorrected_Reads = int(line_[7])
                continue

            if 'write:' in line:
                line_ = ' '.join(line.split()).split(' ')
                if (line_[1] == '0' and line_[2] == '0' and
                        line_[3] == '0' and line_[4] == '0'):
                    self.diagnostics.Corrected_Writes = 0
                elif line_[4] == '0':
                    self.diagnostics.Corrected_Writes = int(
                        line_[1]) + int(line_[2]) + int(line_[3])
                else:
                    self.diagnostics.Corrected_Writes = int(line_[4])
                self.diagnostics._Writes_GB = float(line_[6].replace(',', '.'))
                self.diagnostics._Uncorrected_Writes = int(line_[7])
                continue

            if 'verify:' in line:
                line_ = ' '.join(line.split()).split(' ')
                if (line_[1] == '0' and line_[2] == '0' and
                        line_[3] == '0' and line_[4] == '0'):
                    self.diagnostics.Corrected_Verifies = 0
                elif line_[4] == '0':
                    self.diagnostics.Corrected_Verifies = int(
                        line_[1]) + int(line_[2]) + int(line_[3])
                else:
                    self.diagnostics.Corrected_Verifies = int(line_[4])
                self.diagnostics._Verifies_GB = float(
                    line_[6].replace(',', '.'))
                self.diagnostics._Uncorrected_Verifies = int(line_[7])
                continue

            if 'non-medium error count' in line:
                self.diagnostics.Non_Medium_Errors = int(
                    line.split(':')[1].strip())
                continue

            if 'Accumulated power on time' in line:
                self.diagnostics.Power_On_Hours = int(
                    line.split(':')[1].split(' ')[1])
                continue

            # Sector sizes
            if 'Sector Sizes' in line:  # ATA
                m = re.match(
                    r'.* (\d+) bytes logical,\s*(\d+) bytes physical', line)
                if m:
                    self.logical_sector_size = int(m.group(1))
                    self.physical_sector_size = int(m.group(2))
                    # set diagnostics block size to physical sector size
                    self.diagnostics._block_size = self.physical_sector_size
                continue
            if 'Logical block size:' in line:  # SCSI 1/2
                self.logical_sector_size = int(
                    line.split(':')[1].strip().split(' ')[0])
                # set diagnostics block size to logical sector size
                self.diagnostics._block_size = self.logical_sector_size
                continue

        if sm is not None and not abridged:
            # If not obtained Power_On_Hours above, make a direct attempt to extract power on
            # hours from the background scan results log.
            if smartEnabled and self.diagnostics.Power_On_Hours is None:
                raw, returncode = sm.generic_call(
                    [
                        '-d',
                        'scsi',
                        '-l',
                        'background',
                        dev_reference
                    ])

                for line in raw:
                    if 'power on time' in line:
                        self.diagnostics.Power_On_Hours = int(
                            line.split(':')[1].split(' ')[1])

        # Now that we have finished the update routine, if we did not find a runnning selftest
        # nuke the self._test_ECD and self._test_progress
        # if self._test_running is False:
        #     self._test_ECD = None
        #     self._test_progress = None


__all__ = ['Device', 'smart_health_assement']
