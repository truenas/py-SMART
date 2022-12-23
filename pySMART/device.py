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
This module contains the definition of the `Device` class, used to represent a
physical storage device connected to the system.
Once initialized, class members contain all relevant information about the
device, including its model, serial number, firmware version, and all SMART
attribute data.

Methods are provided for initiating self tests and querying their results.
"""
# Python built-ins
from __future__ import print_function

import logging
import os
import re
import warnings
from time import time, strptime, mktime, sleep
from typing import Tuple, Union, List, Dict, Optional

# pySMART module imports
from .attribute import Attribute
from .diagnostics import Diagnostics
from .interface import *
from .smartctl import Smartctl, SMARTCTL
from .testentry import TestEntry
from .utils import smartctl_type, smartctl_isvalid_type, any_in, all_in

logger = logging.getLogger('pySMART')


def smart_health_assement(disk_name: str, interface: Optional[str] = None, smartctl: Smartctl = SMARTCTL) -> Optional[str]:
    """
    This function gets the SMART Health Status of the disk (IF the disk
    is SMART capable and smart is enabled on it else returns None).
    This function is to be used only in abridged mode and not otherwise,
    since in non-abridged mode update gets this information anyways.

    Args:
        disk_name (str): name of the disk
        interface (str, optional): interface type of the disk (e.g. 'sata', 'scsi', 'nvme',... Defaults to None.)

    Returns:
        str: SMART Health Status of the disk. Returns None if the disk is not SMART capable or smart is not enabled on it.
             Possible values are 'PASS', 'FAIL' or None.
    """
    assessment = None
    raw = smartctl.health(os.path.join(
        '/dev/', disk_name.replace('nvd', 'nvme')), interface)
    line = raw[4]  # We only need this line
    if 'SMART overall-health self-assessment' in line:  # ATA devices
        if line.split(':')[1].strip() == 'PASSED':
            assessment = 'PASS'
        else:
            assessment = 'FAIL'
    if 'SMART Health Status' in line:  # SCSI devices
        if line.split(':')[1].strip() == 'OK':
            assessment = 'PASS'
        else:
            assessment = 'FAIL'
    return assessment


class Device(object):
    """
    Represents any device attached to an internal storage interface, such as a
    hard drive or DVD-ROM, and detected by smartmontools. Includes eSATA
    (considered SATA) but excludes other external devices (USB, Firewire).
    """

    def __init__(self, name: str, interface: Optional[str] = None, abridged: bool = False, smart_options: Union[str, List[str], None] = None, smartctl: Smartctl = SMARTCTL):
        """Instantiates and initializes the `pySMART.device.Device`."""
        if not (
                interface is None or
                smartctl_isvalid_type(interface.lower())
        ):
            raise ValueError(
                'Unknown interface: {0} specified for {1}'.format(interface, name))
        self.abridged = abridged or interface == 'UNKNOWN INTERFACE'
        if smart_options is not None:
            if isinstance(smart_options,  str):
                smart_options = smart_options.split(' ')
            smartctl.add_options(smart_options)
        self.smartctl = smartctl
        """
        """
        self.name: str = name.replace('/dev/', '').replace('nvd', 'nvme')
        """
        **(str):** Device's hardware ID, without the '/dev/' prefix.
        (ie: sda (Linux), pd0 (Windows))
        """
        self.model: Optional[str] = None
        """**(str):** Device's model number."""
        self.serial: Optional[str] = None
        """**(str):** Device's serial number."""
        self.vendor: Optional[str] = None
        """**(str):** Device's vendor (if any)."""
        self._interface: Optional[str] = None if interface == 'UNKNOWN INTERFACE' else interface
        """
        **(str):** Device's interface type. Must be one of:
            * **ATA** - Advanced Technology Attachment
            * **SATA** - Serial ATA
            * **SCSI** - Small Computer Systems Interface
            * **SAS** - Serial Attached SCSI
            * **SAT** - SCSI-to-ATA Translation (SATA device plugged into a
            SAS port)
            * **CSMI** - Common Storage Management Interface (Intel ICH /
            Matrix RAID)
        Generally this should not be specified to allow auto-detection to
        occur. Otherwise, this value overrides the auto-detected type and could
        produce unexpected or no data.
        """
        self._capacity: Optional[int] = None
        """**(str):** Device's user capacity as reported directly by smartctl (RAW)."""
        self._capacity_human: Optional[str] = None
        """**(str):** Device's user capacity (human readable) as reported directly by smartctl (RAW)."""
        self.firmware: Optional[str] = None
        """**(str):** Device's firmware version."""
        self.smart_capable: bool = 'nvme' in self.name
        """
        **(bool):** True if the device has SMART Support Available.
        False otherwise. This is useful for VMs amongst other things.
        """
        self.smart_enabled: bool = 'nvme' in self.name
        """
        **(bool):** True if the device supports SMART (or SCSI equivalent) and
        has the feature set enabled. False otherwise.
        """
        self.assessment: Optional[str] = None
        """
        **(str):** SMART health self-assessment as reported by the device.
        """
        self.messages: List[str] = []
        """
        **(list of str):** Contains any SMART warnings or other error messages
        reported by the device (ie: ascq codes).
        """
        self.is_ssd: bool = True if 'nvme' in self.name else False
        """
        **(bool):** True if this device is a Solid State Drive.
        False otherwise.
        """
        self.rotation_rate: Optional[int] = None
        """
        **(int):** The Roatation Rate of the Drive if it is not a SSD.
        The Metric is RPM.
        """
        self.attributes: List[Optional[Attribute]] = [None] * 256
        """
        **(list of `Attribute`):** Contains the complete SMART table
        information for this device, as provided by smartctl. Indexed by
        attribute #, values are set to 'None' for attributes not suported by
        this device.
        """
        self.test_capabilities = {
            'offline': False,  # SMART execute Offline immediate (ATA only)
            'short': 'nvme' not in self.name,  # SMART short Self-test
            'long': 'nvme' not in self.name,  # SMART long Self-test
            'conveyance': False,  # SMART Conveyance Self-Test (ATA only)
            'selective': False,  # SMART Selective Self-Test (ATA only)
        }
        # Note have not included 'offline' test for scsi as it runs in the foregorund
        # mode. While this may be beneficial to us in someways it is against the
        # general layout and pattern that the other tests issued using pySMART are
        # followed hence not doing it currently
        """
        **(dict): ** This dictionary contains key == 'Test Name' and
        value == 'True/False' of self-tests that this device is capable of.
        """
        # Note: The above are just default values and can/will be changed
        # upon update() when the attributes and type of the disk is actually
        # determined.
        self.tests: List[TestEntry] = []
        """
        **(list of `TestEntry`):** Contains the complete SMART self-test log
        for this device, as provided by smartctl.
        """
        self._test_running = False
        """
        **(bool):** True if a self-test is currently being run.
        False otherwise.
        """
        self._test_ECD = None
        """
        **(str):** Estimated completion time of the running SMART selftest.
        Not provided by SAS/SCSI devices.
        """
        self._test_progress = None
        """
        **(int):** Estimate progress percantage of the running SMART selftest.
        """
        self.diagnostics: Diagnostics = Diagnostics()
        """
        **Diagnostics** Contains parsed and processed diagnostic information
        extracted from the SMART information. Currently only populated for
        SAS and SCSI devices, since ATA/SATA SMART attributes are manufacturer
        proprietary.
        """
        self.temperature: Optional[int] = None
        """
        **(int or None): Since SCSI disks do not report attributes like ATA ones
        we need to grep/regex the shit outta the normal "smartctl -a" output.
        In case the device have more than one temperature sensor the first value
        will be stored here too.
        Note: Temperatures are always in Celsius (if possible).
        """
        self.temperatures: Dict[int, int] = {}
        """
        **(dict of int): NVMe disks usually report multiple temperatures, which
        will be stored here if available. Keys are sensor numbers as reported in
        output data.
        Note: Temperatures are always in Celsius (if possible).
        """
        self.logical_sector_size: Optional[int] = None
        """
        **(int):** The logical sector size of the device (or LBA).
        """
        self.physical_sector_size: Optional[int] = None
        """
        **(int):** The physical sector size of the device.
        """
        self.if_attributes: Union[None, NvmeAttributes] = None
        """
        **(NvmeAttributes):** This object may vary for each device interface attributes.
        It will store all data obtained from smartctl
        """

        if self.name is None:
            warnings.warn(
                "\nDevice '{0}' does not exist! This object should be destroyed.".format(
                    name)
            )
            return
        # If no interface type was provided, scan for the device
        # Lets do this only for the non-abridged case
        # (we can work with no interface for abridged case)
        elif self._interface is None and not self.abridged:
            logger.trace(
                "Determining interface of disk: {0}".format(self.name))
            raw, returncode = self.smartctl.generic_call(
                ['-d', 'test', self.dev_reference])

            if len(raw) > 0:
                # I do not like this parsing logic but it works for now!
                # just for reference _stdout.split('\n') gets us
                # something like
                # [
                #     ...copyright string...,
                #     '',
                #     "/dev/ada2: Device of type 'atacam' [ATA] detected",
                #     "/dev/ada2: Device of type 'atacam' [ATA] opened",
                #     ''
                # ]
                # The above example should be enough for anyone to understand the line below
                try:
                    self._interface = raw[-2].split("'")[1]
                    if self._interface == "nvme":  # if nvme set SMART to true
                        self.smart_capable = True
                        self.smart_enabled = True
                except:
                    # for whatever reason we could not get the interface type
                    # we should mark this as an `abbridged` case and move on
                    self._interface = None
                    self.abbridged = True
                # TODO: Uncomment the classify call if we ever find out that we need it
                # Disambiguate the generic interface to a specific type
                # self._classify()
            else:
                warnings.warn(
                    "\nDevice '{0}' does not exist! This object should be destroyed.".format(
                        name)
                )
                return
        # If a valid device was detected, populate its information
        # OR if in unabridged mode, then do it even without interface info
        if self._interface is not None or self.abridged:
            self.update()

    @property
    def dev_interface(self) -> Optional[str]:
        """Returns the internal interface type of the device.
           It may not be the same as the interface type as used by smartctl.

        Returns:
            str: The interface type of the device. (example: ata, scsi, nvme)
                 None if the interface type could not be determined.
        """
        # Try to get the fine-tuned interface type
        fineType = self._classify()

        # If return still contains a megaraid, just asume it's type
        if 'megaraid' in fineType:
            # If any attributes is not None and has at least non None value, then it is a sat+megaraid device
            if self.attributes and any(self.attributes):
                return 'ata'
            else:
                return 'sas'

        return fineType

    @property
    def smartctl_interface(self) -> Optional[str]:
        """Returns the interface type of the device as it is used in smartctl.

        Returns:
            str: The interface type of the device. (example: ata, scsi, nvme)
                 None if the interface type could not be determined.
        """
        return self._interface

    @property
    def interface(self) -> Optional[str]:
        """Returns the interface type of the device as it is used in smartctl.

        Returns:
            str: The interface type of the device. (example: ata, scsi, nvme)
                 None if the interface type could not be determined.
        """
        return self.smartctl_interface

    @property
    def dev_reference(self) -> str:
        """The reference to the device as provided by smartctl.
           - On unix-like systems, this is the path to the device. (example /dev/<name>)
           - On MacOS, this is the name of the device. (example <name>)
           - On Windows, this is the drive letter of the device. (example <drive letter>)

        Returns:
            str: The reference to the device as provided by smartctl.
        """

        # detect if we are on MacOS
        if 'IOService' in self.name:
            return self.name

        # otherwise asume we are on unix-like systems
        return os.path.join('/dev/', self.name)

    @property
    def capacity(self) -> Optional[str]:
        """Returns the capacity in the raw smartctl format.
        This may be deprecated in the future and its only retained for compatibility.

        Returns:
            str: The capacity in the raw smartctl format
        """
        return self._capacity_human

    @property
    def diags(self) -> Dict[str, str]:
        """Gets the old/deprecated version of SCSI/SAS diags atribute.
        """
        return self.diagnostics.get_classic_format()

    @property
    def size_raw(self) -> Optional[str]:
        """Returns the capacity in the raw smartctl format.

        Returns:
            str: The capacity in the raw smartctl format
        """
        return self._capacity_human

    @property
    def size(self) -> int:
        """Returns the capacity in bytes

        Returns:
            int: The capacity in bytes
        """
        import humanfriendly

        if self._capacity is not None:
            return self._capacity
        elif self._capacity_human is not None:
            return humanfriendly.parse_size(self._capacity_human)
        else:
            return 0

    @property
    def sector_size(self) -> int:
        """Returns the sector size of the device.

        Returns:
            int: The sector size of the device in Bytes. If undefined, we'll assume 512B
        """
        if self.logical_sector_size is not None:
            return self.logical_sector_size
        elif self.physical_sector_size is not None:
            return self.physical_sector_size
        else:
            return 512

    def __repr__(self):
        """Define a basic representation of the class object."""
        return "<{0} device on /dev/{1} mod:{2} sn:{3}>".format(
            self._interface.upper() if self._interface else 'UNKNOWN INTERFACE',
            self.name,
            self.model,
            self.serial
        )

    def __getstate__(self, all_info=True):
        """
        Allows us to send a pySMART Device object over a serializable
        medium which uses json (or the likes of json) payloads
        """
        state_dict = {
            'interface': self._interface if self._interface else 'UNKNOWN INTERFACE',
            'model': self.model,
            'firmware': self.firmware,
            'smart_capable': self.smart_capable,
            'smart_enabled': self.smart_enabled,
            'smart_status': self.assessment,
            'messages': self.messages,
            'test_capabilities': self.test_capabilities.copy(),
            'tests': [t.__getstate__() for t in self.tests] if self.tests else [],
            'diagnostics': self.diagnostics.__getstate__(),
            'temperature': self.temperature,
            'attributes': [attr.__getstate__() if attr else None for attr in self.attributes]
        }
        if all_info:
            state_dict.update({
                'name': self.name,
                'path': self.dev_reference,
                'serial': self.serial,
                'is_ssd': self.is_ssd,
                'rotation_rate': self.rotation_rate,
                'capacity': self._capacity_human
            })
        return state_dict

    def __setstate__(self, state):
        state['assessment'] = state['smart_status']
        del state['smart_status']
        self.__dict__.update(state)

    def smart_toggle(self, action: str) -> Tuple[bool, List[str]]:
        """
        A basic function to enable/disable SMART on device.

        # Args:
        * **action (str):** Can be either 'on'(for enabling) or 'off'(for disabling).

        # Returns"
        * **(bool):** Return True (if action succeded) else False
        * **(List[str]):** None if option succeded else contains the error message.
        """
        # Lets make the action verb all lower case
        if self._interface == 'nvme':
            return False, ['NVME devices do not currently support toggling SMART enabled']
        action_lower = action.lower()
        if action_lower not in ['on', 'off']:
            return False, ['Unsupported action {0}'.format(action)]
        # Now lets check if the device's smart enabled status is already that of what
        # the supplied action is intending it to be. If so then just return successfully
        if self.smart_enabled:
            if action_lower == 'on':
                return True, []
        else:
            if action_lower == 'off':
                return True, []
        if self._interface is not None:
            raw, returncode = self.smartctl.generic_call(
                ['-s', action_lower, '-d', self._interface, self.dev_reference])
        else:
            raw, returncode = self.smartctl.generic_call(
                ['-s', action_lower, self.dev_reference])

        if returncode != 0:
            return False, raw
        # if everything worked out so far lets perform an update() and check the result
        self.update()
        if action_lower == 'off' and self.smart_enabled:
            return False, ['Failed to turn SMART off.']
        if action_lower == 'on' and not self.smart_enabled:
            return False, ['Failed to turn SMART on.']
        return True, []

    def all_attributes(self, print_fn=print):
        """
        Prints the entire SMART attribute table, in a format similar to
        the output of smartctl.
        allows usage of custom print function via parameter print_fn by default uses print
        """
        header_printed = False
        for attr in self.attributes:
            if attr is not None:
                if not header_printed:
                    print_fn("{0:>3} {1:24}{2:4}{3:4}{4:4}{5:9}{6:8}{7:12}{8}"
                             .format('ID#', 'ATTRIBUTE_NAME', 'CUR', 'WST', 'THR', 'TYPE', 'UPDATED', 'WHEN_FAIL',
                                     'RAW'))
                    header_printed = True
                print_fn(attr)
        if not header_printed:
            print_fn('This device does not support SMART attributes.')

    def all_selftests(self):
        """
        Prints the entire SMART self-test log, in a format similar to
        the output of smartctl.
        """
        if self.tests:
            all_tests = []
            if smartctl_type(self._interface) == 'scsi':
                header = "{0:3}{1:17}{2:23}{3:7}{4:14}{5:15}".format(
                    'ID',
                    'Test Description',
                    'Status',
                    'Hours',
                    '1st_Error@LBA',
                    '[SK  ASC  ASCQ]'
                )
            else:
                header = ("{0:3}{1:17}{2:30}{3:5}{4:7}{5:17}".format(
                    'ID',
                    'Test_Description',
                    'Status',
                    'Left',
                    'Hours',
                    '1st_Error@LBA'))
            all_tests.append(header)
            for test in self.tests:
                all_tests.append(str(test))

            return all_tests
        else:
            no_tests = 'No self-tests have been logged for this device.'
            return no_tests

    def _classify(self) -> str:
        """
        Disambiguates generic device types ATA and SCSI into more specific
        ATA, SATA, SAS, SAT and SCSI.
        """

        fine_interface = self._interface or ''
        # SCSI devices might be SCSI, SAS or SAT
        # ATA device might be ATA or SATA
        if fine_interface in ['scsi', 'ata'] or 'megaraid' in fine_interface:
            if 'megaraid' in fine_interface:
                if not 'sat+' in fine_interface:
                    test = 'sat'+fine_interface
                else:
                    test = fine_interface
            else:
                test = 'sat' if fine_interface == 'scsi' else 'sata'
            # Look for a SATA PHY to detect SAT and SATA
            raw, returncode = self.smartctl.try_generic_call([
                '-d',
                smartctl_type(test),
                '-l',
                'sataphy',
                self.dev_reference])

            if returncode == 0 and 'GP Log 0x11' in raw[3]:
                fine_interface = test
        # If device type is still SCSI (not changed to SAT above), then
        # check for a SAS PHY
        if fine_interface in ['scsi'] or 'megaraid' in fine_interface:
            raw, returncode = self.smartctl.try_generic_call([
                '-d',
                smartctl_type(fine_interface),
                '-l',
                'sasphy',
                self.dev_reference])
            if returncode == 0 and 'SAS SSP' in raw[4]:
                fine_interface = 'sas'
            # Some older SAS devices do not support the SAS PHY log command.
            # For these, see if smartmontools reports a transport protocol.
            else:
                raw = self.smartctl.all(self.dev_reference, fine_interface)

                for line in raw:
                    if 'Transport protocol' in line and 'SAS' in line:
                        fine_interface = 'sas'

        return fine_interface

    def _guess_smart_type(self, line):
        """
        This function is not used in the generic wrapper, however the header
        is defined so that it can be monkey-patched by another application.
        """
        pass

    def _make_smart_warnings(self):
        """
        Parses an ATA/SATA SMART table for attributes with the 'when_failed'
        value set. Generates an warning message for any such attributes and
        updates the self-assessment value if necessary.
        """
        if smartctl_type(self._interface) == 'scsi':
            return
        for attr in self.attributes:
            if attr is not None:
                if attr.when_failed == 'In_the_past':
                    warn_str = "{0} failed in the past with value {1}. [Threshold: {2}]".format(
                        attr.name, attr.worst, attr.thresh)
                    self.messages.append(warn_str)
                    if not self.assessment == 'FAIL':
                        self.assessment = 'WARN'
                elif attr.when_failed == 'FAILING_NOW':
                    warn_str = "{0} is failing now with value {1}. [Threshold: {2}]".format(
                        attr.name, attr.value, attr.thresh)
                    self.assessment = 'FAIL'
                    self.messages.append(warn_str)
                elif not attr.when_failed == '-':
                    warn_str = "{0} says it failed '{1}'. [V={2},W={3},T={4}]".format(
                        attr.name, attr.when_failed, attr.value, attr.worst, attr.thresh)
                    self.messages.append(warn_str)
                    if not self.assessment == 'FAIL':
                        self.assessment = 'WARN'

    def get_selftest_result(self, output=None):
        """
        Refreshes a device's `pySMART.device.Device.tests` attribute to obtain
        the latest test results. If a new test result is obtained, its content
        is returned.

        # Args:
        * **output (str, optional):** If set to 'str', the string
        representation of the most recent test result will be returned, instead
        of a `Test_Entry` object.

        # Returns:
        * **(int):** Return status code. One of the following:
            * 0 - Success. Object (or optionally, string rep) is attached.
            * 1 - Self-test in progress. Must wait for it to finish.
            * 2 - No new test results.
            * 3 - The Self-test was Aborted by host
        * **(`Test_Entry` or str):** Most recent `Test_Entry` object (or
        optionally it's string representation) if new data exists.  Status
        message string on failure.
        * **(int):** Estimate progress percantage of the running SMART selftest, if known.
        Otherwise 'None'.
        """
        # SCSI self-test logs hold 20 entries while ATA logs hold 21
        if smartctl_type(self._interface) == 'scsi':
            maxlog = 20
        else:
            maxlog = 21
        # If we looked only at the most recent test result we could be fooled
        # by two short tests run close together (within the same hour)
        # appearing identical. Comparing the length of the log adds some
        # confidence until it maxes, as above. Comparing the least-recent test
        # result greatly diminishes the chances that two sets of two tests each
        # were run within an hour of themselves, but with 16-17 other tests run
        # in between them.
        if self.tests:
            _first_entry = self.tests[0]
            _len = len(self.tests)
            _last_entry = self.tests[_len - 1]
        else:
            _len = 0
        self.update()
        # Since I have changed the update() parsing to DTRT to pickup currently
        # running selftests we can now purely rely on that for self._test_running
        # Thus check for that variable first and return if it is True with appropos message.
        if self._test_running is True:
            return 1, 'Self-test in progress. Please wait.', self._test_progress
        # Check whether the list got longer (ie: new entry)
        # If so return the newest test result
        # If not, because it's max size already, check for new entries
        if (
                (len(self.tests) != _len) or
                (
                    len == maxlog and
                    (
                        _first_entry.type != self.tests[0].type or
                        _first_entry.hours != self.tests[0].hours or
                        _last_entry.type != self.tests[len(self.tests) - 1].type or
                        _last_entry.hours != self.tests[len(
                            self.tests) - 1].hours
                    )
                )
        ):
            return (
                0 if 'Aborted' not in self.tests[0].status else 3,
                str(self.tests[0]) if output == 'str' else self.tests[0],
                None
            )
        else:
            return 2, 'No new self-test results found.', None

    def abort_selftest(self):
        """
        Aborts non-captive SMART Self Tests.   Note that this command
        will  abort the Offline Immediate Test routine only if your disk
        has the "Abort Offline collection upon new command"  capability.

        # Args: Nothing (just aborts directly)

        # Returns:
        * **(int):** The returncode of calling `smartctl -X device_path`
        """
        return self.smartctl.test_stop(smartctl_type(self._interface), self.dev_reference)

    def run_selftest(self, test_type, ETA_type='date'):
        """
        Instructs a device to begin a SMART self-test. All tests are run in
        'offline' / 'background' mode, allowing normal use of the device while
        it is being tested.

        # Args:
        * **test_type (str):** The type of test to run. Accepts the following
        (not case sensitive):
            * **short** - Brief electo-mechanical functionality check.
            Generally takes 2 minutes or less.
            * **long** - Thorough electro-mechanical functionality check,
            including complete recording media scan. Generally takes several
            hours.
            * **conveyance** - Brief test used to identify damage incurred in
            shipping. Generally takes 5 minutes or less. **This test is not
            supported by SAS or SCSI devices.**
            * **offline** - Runs SMART Immediate Offline Test. The effects of
            this test are visible only in that it updates the SMART Attribute
            values, and if errors are found they will appear in the SMART error
            log, visible with the '-l error' option to smartctl. **This test is
            not supported by SAS or SCSI devices in pySMART use cli smartctl for
            running 'offline' selftest (runs in foreground) on scsi devices.**
            * **ETA_type** - Format to return the estimated completion time/date
            in. Default is 'date'. One could otherwise specidy 'seconds'.
            Again only for ATA devices.

        # Returns:
        * **(int):** Return status code.  One of the following:
            * 0 - Self-test initiated successfully
            * 1 - Previous self-test running. Must wait for it to finish.
            * 2 - Unknown or unsupported (by the device) test type requested.
            * 3 - Unspecified smartctl error. Self-test not initiated.
        * **(str):** Return status message.
        * **(str)/(float):** Estimated self-test completion time if a test is started.
        The optional argument of 'ETA_type' (see above) controls the return type.
        if 'ETA_type' == 'date' then a date string is returned else seconds(float)
        is returned.
        Note: The self-test completion time can only be obtained for ata devices.
        Otherwise 'None'.
        """
        # Lets call get_selftest_result() here since it does an update() and
        # checks for an existing selftest is running or not, this way the user
        # can issue a test from the cli and this can still pick that up
        # Also note that we do not need to obtain the results from this as the
        # data is already stored in the Device class object's variables
        self.get_selftest_result()
        if self._test_running:
            return 1, 'Self-test in progress. Please wait.', self._test_ECD
        test_type = test_type.lower()
        interface = smartctl_type(self._interface)
        try:
            if not self.test_capabilities[test_type]:
                return (
                    2,
                    "Device {0} does not support the '{1}' test ".format(
                        self.name, test_type),
                    None
                )
        except KeyError:
            return 2, "Unknown test type '{0}' requested.".format(test_type), None

        raw, rc = self.smartctl.test_start(
            interface, test_type, self.dev_reference)
        _success = False
        _running = False
        for line in raw:
            if 'has begun' in line:
                _success = True
                self._test_running = True
            if 'aborting current test' in line:
                _running = True
                try:
                    self._test_progress = 100 - \
                        int(line.split('(')[-1].split('%')[0])
                except ValueError:
                    pass

            if _success and 'complete after' in line:
                self._test_ECD = line[25:].rstrip()
                if ETA_type == 'seconds':
                    self._test_ECD = mktime(
                        strptime(self._test_ECD, '%a %b %d %H:%M:%S %Y')) - time()
                self._test_progress = 0
        if _success:
            return 0, 'Self-test started successfully', self._test_ECD
        else:
            if _running:
                return 1, 'Self-test already in progress. Please wait.', self._test_ECD
            else:
                return 3, 'Unspecified Error. Self-test not started.', None

    def run_selftest_and_wait(self, test_type, output=None, polling=5, progress_handler=None):
        """
        This is essentially a wrapper around run_selftest() such that we
        call self.run_selftest() and wait on the running selftest till
        it finished before returning.
        The above holds true for all pySMART supported tests with the
        exception of the 'offline' test (ATA only) as it immediately
        returns, since the entire test only affects the smart error log
        (if any errors found) and updates the SMART attributes. Other
        than that it is not visibile anywhere else, so we start it and
        simply return.
        # Args:
        * **test_type (str):** The type of test to run. Accepts the following
        (not case sensitive):
            * **short** - Brief electo-mechanical functionality check.
            Generally takes 2 minutes or less.
            * **long** - Thorough electro-mechanical functionality check,
            including complete recording media scan. Generally takes several
            hours.
            * **conveyance** - Brief test used to identify damage incurred in
            shipping. Generally takes 5 minutes or less. **This test is not
            supported by SAS or SCSI devices.**
            * **offline** - Runs SMART Immediate Offline Test. The effects of
            this test are visible only in that it updates the SMART Attribute
            values, and if errors are found they will appear in the SMART error
            log, visible with the '-l error' option to smartctl. **This test is
            not supported by SAS or SCSI devices in pySMART use cli smartctl for
            running 'offline' selftest (runs in foreground) on scsi devices.**
        * **output (str, optional):** If set to 'str', the string
            representation of the most recent test result will be returned,
            instead of a `Test_Entry` object.
        * **polling (int, default=5):** The time duration to sleep for between
            checking for test_results and progress.
        * **progress_handler (function, optional):** This if provided is called
            with self._test_progress as the supplied argument everytime a poll to
            check the status of the selftest is done.
        # Returns:
        * **(int):** Return status code.  One of the following:
            * 0 - Self-test executed and finished successfully
            * 1 - Previous self-test running. Must wait for it to finish.
            * 2 - Unknown or illegal test type requested.
            * 3 - The Self-test was Aborted by host
            * 4 - Unspecified smartctl error. Self-test not initiated.
        * **(`Test_Entry` or str):** Most recent `Test_Entry` object (or
        optionally it's string representation) if new data exists.  Status
        message string on failure.
        """
        test_initiation_result = self.run_selftest(test_type)
        if test_initiation_result[0] != 0:
            return test_initiation_result[:2]
        if test_type == 'offline':
            self._test_running = False
        # if not then the test initiated correctly and we can start the polling.
        # For now default 'polling' value is 5 seconds if not specified by the user

        # Do an initial check, for good measure.
        # In the probably impossible case that self._test_running is instantly False...
        selftest_results = self.get_selftest_result(output=output)
        while self._test_running:
            if selftest_results[0] != 1:
                # the selftest is run and finished lets return with the results
                break
            # Otherwise see if we are provided with the progress_handler to update progress
            if progress_handler is not None:
                progress_handler(
                    selftest_results[2] if selftest_results[2] is not None else 50)
            # Now sleep 'polling' seconds before checking the progress again
            sleep(polling)

            # Check after the sleep to ensure we return the right result, and not an old one.
            selftest_results = self.get_selftest_result(output=output)

        # Now if (selftes_results[0] == 2) i.e No new selftest (because the same
        # selftest was run twice within the last hour) but we know for a fact that
        # we just ran a new selftest then just return the latest entry in self.tests
        if selftest_results[0] == 2:
            selftest_return_value = 0 if 'Aborted' not in self.tests[0].status else 3
            return selftest_return_value, str(self.tests[0]) if output == 'str' else self.tests[0]
        return selftest_results[:2]

    def update(self):
        """
        Queries for device information using smartctl and updates all
        class members, including the SMART attribute table and self-test log.
        Can be called at any time to refresh the `pySMART.device.Device`
        object's data content.
        """
        # set temperature back to None so that if update() is called more than once
        # any logic that relies on self.temperature to be None to rescan it works.it
        self.temperature = None
        # same for temperatures
        self.temperatures = {}
        if self.abridged:
            interface = None
            raw = self.smartctl.info(self.dev_reference)

        else:
            interface = smartctl_type(self._interface)
            raw = self.smartctl.all(
                self.dev_reference, interface)

        parse_self_tests = False
        parse_running_test = False
        parse_ascq = False
        message = ''
        self.tests = []
        self._test_running = False
        self._test_progress = None
        # Lets skip the first couple of non-useful lines
        _stdout = raw[4:]

        #######################################
        #           Encoding fixing           #
        #######################################
        # In some scenarios, smartctl returns some lines with a different/strange encoding
        # This is a workaround to fix that
        for i, line in enumerate(_stdout):
            # character ' ' (U+202F) should be removed
            _stdout[i] = line.replace('\u202f', '')

        #######################################
        #   Dedicated interface attributes    #
        #######################################

        if interface == 'nvme':
            self.if_attributes = NvmeAttributes(iter(_stdout))
        else:
            self.if_attributes = None

        #######################################
        #    Global / generic  attributes     #
        #######################################
        stdout_iter = iter(_stdout)
        for line in stdout_iter:
            if line.strip() == '':  # Blank line stops sub-captures
                if parse_self_tests is True:
                    parse_self_tests = False
                if parse_ascq:
                    parse_ascq = False
                    self.messages.append(message)
            if parse_ascq:
                message += ' ' + line.lstrip().rstrip()
            if parse_self_tests:
                num = line[0:3]
                if '#' not in num:
                    continue

                # Detect Test Format

                ## SCSI/SAS FORMAT ##
                # Example smartctl output
                # SMART Self-test log
                # Num  Test              Status                 segment  LifeTime  LBA_first_err [SK ASC ASQ]
                #      Description                              number   (hours)
                # # 1  Background short  Completed                   -   33124                 - [-   -    -]
                format_scsi = re.compile(
                    r'^[#\s]*([^\s]+)\s{2,}(.*[^\s])\s{2,}(.*[^\s])\s{2,}(.*[^\s])\s{2,}(.*[^\s])\s{2,}(.*[^\s])\s+\[([^\s]+)\s+([^\s]+)\s+([^\s]+)\]$').match(line)

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
                else:
                    ## ATA FORMAT ##
                    # Example smartctl output:
                    # SMART Self-test log structure revision number 1
                    # Num  Test_Description    Status                  Remaining  LifeTime(hours)  LBA_of_first_error
                    # # 1  Extended offline    Completed without error       00%     46660         -
                    format = 'ata'
                    parsed = re.compile(
                        r'^[#\s]*([^\s]+)\s{2,}(.*[^\s])\s{2,}(.*[^\s])\s{1,}(.*[^\s])\s{2,}(.*[^\s])\s{2,}(.*[^\s])$').match(line).groups()
                    num = parsed[0]
                    test_type = parsed[1]
                    status = parsed[2]
                    remain = parsed[3]
                    hours = parsed[4]
                    lba = parsed[5]

                    try:
                        num = int(num)
                    except:
                        num = None

                    self.tests.append(
                        TestEntry(format, num, test_type, status,
                                  hours, lba, remain=remain)
                    )
            # Basic device information parsing
            if any_in(line, 'Device Model', 'Product', 'Model Number'):
                self.model = line.split(':')[1].lstrip().rstrip()
                self._guess_smart_type(line.lower())
                continue

            if 'Model Family' in line:
                self._guess_smart_type(line.lower())
                continue

            if 'LU WWN' in line:
                self._guess_smart_type(line.lower())
                continue

            if any_in(line, 'Serial Number', 'Serial number'):
                self.serial = line.split(':')[1].split()[0].rstrip()
                continue

            vendor = re.compile(r'^Vendor:\s+(\w+)').match(line)
            if vendor is not None:
                self.vendor = vendor.groups()[0]

            if any_in(line, 'Firmware Version', 'Revision'):
                self.firmware = line.split(':')[1].strip()

            if any_in(line, 'User Capacity', 'Total NVM Capacity', 'Namespace 1 Size/Capacity'):
                # TODO: support for multiple NVMe namespaces
                m = re.match(
                    r'.*:\s+([\d,.]+)\s\D*\[?([^\]]+)?\]?', line.strip())

                if m is not None:
                    tmp = m.groups()
                    self._capacity = int(
                        tmp[0].strip().replace(',', '').replace('.', ''))

                    if len(tmp) == 2 and tmp[1] is not None:
                        self._capacity_human = tmp[1].strip().replace(',', '.')

            if 'SMART support' in line:
                # self.smart_capable = 'Available' in line
                # self.smart_enabled = 'Enabled' in line
                # Since this line repeats twice the above method is flawed
                # Lets try the following instead, it is a bit redundant but
                # more robust.
                if any_in(line, 'Unavailable', 'device lacks SMART capability'):
                    self.smart_capable = False
                    self.smart_enabled = False
                elif 'Enabled' in line:
                    self.smart_enabled = True
                elif 'Disabled' in line:
                    self.smart_enabled = False
                elif any_in(line, 'Available', 'device has SMART capability'):
                    self.smart_capable = True
                continue

            if 'does not support SMART' in line:
                self.smart_capable = False
                self.smart_enabled = False
                continue

            if 'Rotation Rate' in line:
                if 'Solid State Device' in line:
                    self.is_ssd = True
                elif 'rpm' in line:
                    self.is_ssd = False
                    try:
                        self.rotation_rate = int(
                            line.split(':')[1].lstrip().rstrip()[:-4])
                    except ValueError:
                        # Cannot parse the RPM? Assigning None instead
                        self.rotation_rate = None
                continue

            if 'SMART overall-health self-assessment' in line:  # ATA devices
                if line.split(':')[1].strip() == 'PASSED':
                    self.assessment = 'PASS'
                else:
                    self.assessment = 'FAIL'
                continue

            if 'SMART Health Status' in line:  # SCSI devices
                if line.split(':')[1].strip() == 'OK':
                    self.assessment = 'PASS'
                else:
                    self.assessment = 'FAIL'
                    parse_ascq = True  # Set flag to capture status message
                    message = line.split(':')[1].lstrip().rstrip()
                continue

            # Parse SMART test capabilities (ATA only)
            # Note: SCSI does not list this but and allows for only 'offline', 'short' and 'long'
            if 'SMART execute Offline immediate' in line:
                self.test_capabilities['offline'] = 'No' not in line
                continue

            if 'Conveyance Self-test supported' in line:
                self.test_capabilities['conveyance'] = 'No' not in line
                continue

            if 'Selective Self-test supported' in line:
                self.test_capabilities['selective'] = 'No' not in line
                continue

            if 'Self-test supported' in line:
                self.test_capabilities['short'] = 'No' not in line
                self.test_capabilities['long'] = 'No' not in line
                continue

            # SMART Attribute table parsing
            if all_in(line, '0x0', '_') and not interface == 'nvme':
                # Replace multiple space separators with a single space, then
                # tokenize the string on space delimiters
                line_ = ' '.join(line.split()).split(' ')
                if '' not in line_:
                    self.attributes[int(line_[0])] = Attribute(
                        int(line_[0]), line_[1], int(line[2], base=16), line_[3], line_[4], line_[5], line_[6], line_[7], line_[8], line_[9])
            # For some reason smartctl does not show a currently running test
            # for 'ATA' in the Test log so I just have to catch it this way i guess!
            # For 'scsi' I still do it since it is the only place I get % remaining in scsi
            if 'Self-test execution status' in line:
                if 'progress' in line:
                    self._test_running = True
                    # for ATA the "%" remaining is on the next line
                    # thus set the parse_running_test flag and move on
                    parse_running_test = True
                elif '%' in line:
                    # for scsi the progress is on the same line
                    # so we can just parse it and move on
                    self._test_running = True
                    try:
                        self._test_progress = 100 - \
                            int(line.split('%')[0][-3:].strip())
                    except ValueError:
                        pass
                continue
            if parse_running_test is True:
                try:
                    self._test_progress = 100 - \
                        int(line.split('%')[0][-3:].strip())
                except ValueError:
                    pass
                parse_running_test = False

            if all_in(line, 'Description', '(hours)'):
                parse_self_tests = True  # Set flag to capture test entries

            #######################################
            #              SCSI only              #
            #######################################
            #
            # Everything from here on is parsing SCSI information that takes
            # the place of similar ATA SMART information
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
                if self.diagnostics.Start_Stop_Spec != 0:
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
                if self.diagnostics.Load_Cycle_Spec != 0:
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

            if 'Current Drive Temperature' in line or ('Temperature:' in
                                                       line and interface == 'nvme'):
                try:
                    self.temperature = int(
                        line.split(':')[-1].strip().split()[0])

                    if 'fahrenheit' in line.lower():
                        self.temperature = int((self.temperature - 32) * 5 / 9)

                except ValueError:
                    pass

                continue

            if 'Temperature Sensor ' in line:
                try:
                    match = re.search(
                        r'Temperature\sSensor\s([0-9]+):\s+(-?[0-9]+)', line)
                    if match:
                        (tempsensor_number_s, tempsensor_value_s) = match.group(1, 2)
                        tempsensor_number = int(tempsensor_number_s)
                        tempsensor_value = int(tempsensor_value_s)

                        if 'fahrenheit' in line.lower():
                            tempsensor_value = int(
                                (tempsensor_value - 32) * 5 / 9)

                        self.temperatures[tempsensor_number] = tempsensor_value
                        if self.temperature is None or tempsensor_number == 0:
                            self.temperature = tempsensor_value
                except ValueError:
                    pass

                continue

            #######################################
            #            Common values            #
            #######################################

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
            if 'Physical block size:' in line:  # SCSI 2/2
                self.physical_sector_size = int(
                    line.split(':')[1].strip().split(' ')[0])
                continue
            if 'Namespace 1 Formatted LBA Size' in line:  # NVMe
                # Note: we will assume that there is only one namespace
                self.logical_sector_size = int(
                    line.split(':')[1].strip().split(' ')[0])
                continue

        if not self.abridged:
            if not interface == 'scsi':
                # Parse the SMART table for below-threshold attributes and create
                # corresponding warnings for non-SCSI disks
                self._make_smart_warnings()
            else:
                # If not obtained Power_On_Hours above, make a direct attempt to extract power on
                # hours from the background scan results log.
                if self.diagnostics.Power_On_Hours is None:
                    raw, returncode = self.smartctl.generic_call(
                        [
                            '-d',
                            'scsi',
                            '-l',
                            'background',
                            self.dev_reference
                        ])

                    for line in raw:
                        if 'power on time' in line:
                            self.diagnostics.Power_On_Hours = int(
                                line.split(':')[1].split(' ')[1])
        # map temperature
        if self.temperature is None:
            # in this case the disk is probably ata
            try:
                # Some disks report temperature to attribute number 190 ('Airflow_Temperature_Cel')
                # see https://bugs.freenas.org/issues/20860
                temp_attr = self.attributes[194] or self.attributes[190]
                self.temperature = int(temp_attr.raw)
            except (ValueError, AttributeError):
                pass
        # Now that we have finished the update routine, if we did not find a runnning selftest
        # nuke the self._test_ECD and self._test_progress
        if self._test_running is False:
            self._test_ECD = None
            self._test_progress = None


__all__ = ['Device', 'smart_health_assement']
