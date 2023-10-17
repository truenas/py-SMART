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
This module contains the definition of the `Test_Entry` class, used to
represent individual entries in a `Device`'s SMART Self-test Log.
"""

from typing import Optional


class TestEntry(object):
    """
    Contains all of the information associated with a single SMART Self-test
    log entry. This data is intended to exactly mirror that obtained through
    smartctl.
    """

    def __init__(self, format, num: Optional[int], test_type, status, hours, lba,
                 remain=None,
                 segment=None,
                 sense=None,
                 asc=None,
                 ascq=None,
                 nsid=None,
                 sct=None,
                 code=None):

        self._format = format
        """
        **(str):** Indicates whether this entry was taken from an 'ata' or
        'scsi' self-test log. Used to display the content properly.
        """
        self.num: Optional[int] = num
        """
        **(int):** Entry's position in the log from 1 (most recent) to 21
        (least recent).  ATA logs save the last 21 entries while SCSI logs
        only save the last 20.
        """
        self.type = test_type
        """
        **(str):** Type of test run.  Generally short, long (extended), or
        conveyance, plus offline (background) or captive (foreground).
        """
        self.status = status
        """
        **(str):** Self-test's status message, for example 'Completed without
        error' or 'Completed: read failure'.
        """
        self.hours = hours
        """
        **(str):** The device's power-on hours at the time the self-test
        was initiated.
        """
        self.LBA = lba
        """
        **(str):** Indicates the first LBA at which an error was encountered
        during this self-test. Presented as a decimal value for ATA/SATA
        devices and in hexadecimal notation for SAS/SCSI devices.
        """
        self.remain = remain
        """
        **(str):** Percentage value indicating how much of the self-test is
        left to perform. '00%' indicates a complete test, while any other
        value could indicate a test in progress or one that failed prior to
        completion. Only reported by ATA devices.
        """
        self.segment = segment
        """
        **(str):** A manufacturer-specific self-test segment number reported
        by SCSI devices on self-test failure. Set to '-' otherwise.
        """
        self.sense = sense
        """
        **(str):** SCSI sense key reported on self-test failure. Set to '-'
        otherwise.
        """
        self.ASC = asc
        """
        **(str):** SCSI 'Additonal Sense Code' reported on self-test failure.
        Set to '-' otherwise.
        """
        self.ASCQ = ascq
        """
        **(str):** SCSI 'Additonal Sense Code Quaifier' reported on self-test
        failure. Set to '-' otherwise.
        """
        self.nsid = nsid
        """
        **(str):** NVMe 'Name Space Identifier' reported on self-test failure.
        Set to '-' if no namespace is defined.
        """
        self.sct = sct
        """
        **(str):** NVMe 'Status Code Type' reported on self-test failure.
        Set to '-' if undefined.
        """
        self.code = code
        """
        **(str):** NVMe 'Status Code' reported on self-test failure.
        Set to '-' if undefined.
        """

    def __getstate__(self):
        return {
            'num': self.num,
            'type': self.type,
            'status': self.status,
            'hours': self.hours,
            'lba': self.LBA,
            'remain': self.remain,
            'segment': self.segment,
            'sense': self.sense,
            'asc': self.ASC,
            'ascq': self.ASCQ,
            'nsid': self.nsid,
            'sct': self.sct,
            'code': self.code
        }

    def __repr__(self):
        """Define a basic representation of the class object."""
        return "<SMART Self-test [%s|%s] hrs:%s LBA:%s>" % (
            self.type, self.status, self.hours, self.LBA)

    def __str__(self):
        """
        Define a formatted string representation of the object's content.
        Looks nearly identical to the output of smartctl, without overflowing
        80-character lines.
        """
        if self._format == 'ata':
            return "{0:>2} {1:17}{2:30}{3:5}{4:7}{5:17}".format(
                self.num, self.type, self.status, self.remain, self.hours,
                self.LBA)
        elif self._format == 'scsi':
            # 'Segment' could not be fit on the 80-char line. It's of limited
            # utility anyway due to it's manufacturer-proprietary nature...
            return ("{0:>2} {1:17}{2:23}{3:7}{4:14}[{5:4}{6:5}{7:4}]".format(
                self.num,
                self.type,
                self.status,
                self.hours,
                self.LBA,
                self.sense,
                self.ASC,
                self.ASCQ
            ))
        elif self._format == 'nvme':
            ## NVME FORMAT ##
            # Example smartctl output
            # Self-test Log (NVMe Log 0x06)
            # Self-test status: Extended self-test in progress (28% completed)
            # Num  Test_Description  Status                       Power_on_Hours  Failing_LBA  NSID Seg SCT Code
            #  0   Extended          Completed without error                3441            -     -   -   -    -
            return ("{0:^4} {1:<18}{2:<29}{3:>14}{4:>13}{5:>6}{6:>4}{7:>4}{8:>5}".format(
                self.num,
                self.type,
                self.status,
                self.hours,
                self.LBA if self.LBA is not None else '-',
                self.nsid if self.LBA is not None else '-',
                self.segment if self.segment is not None else '-',
                self.sct if self.LBA is not None else '-',
                self.code if self.LBA is not None else '-'
            ))
        else:
            return "Unknown test format: %s" % self._format


__all__ = ['TestEntry']
