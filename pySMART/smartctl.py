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
from subprocess import Popen, PIPE
from .utils import SMARTCTL_PATH
from typing import List, Tuple, Union

import logging
import os

logger = logging.getLogger('pySMART')

os.environ["LANG"] = "C"


class Smartctl:
    def __init__(self, smartctl_path=SMARTCTL_PATH, options: List[str] = [], sudo: Union[bool, List[str]] = False):
        """
        Instantiates and initializes the Smartctl wrapper.

        Args:
            smartctl_path (str | PathLike): path to the smartctl executable
            options (List[str]): extra options to use when invoking smartctl
            sudo (bool | List[str]):
                if True use sudo -E when calling smartctl on POSIX systems.
                If given as a list, then these arguments are passed to sudo.
                (e.g. `sudo=['-u', 'foo']` will run `sudo -u foo ...`).
        """
        self.smartctl_path = smartctl_path
        self.options: List[str] = options
        self._sudo: Union[None, List[str]] = None
        self.sudo = sudo

    @property
    def sudo(self):
        """
        Example:
            >>> # xdoctest: +REQUIRES(POSIX)
            >>> self = Smartctl()
            >>> print(f'self.sudo={self.sudo}')
            >>> self.sudo = True
            >>> print(f'self.sudo={self.sudo}')
            >>> self.sudo = []
            >>> print(f'self.sudo={self.sudo}')
            >>> self.sudo = False
            >>> print(f'self.sudo={self.sudo}')
            self.sudo=None
            self.sudo=['-E']
            self.sudo=[]
            self.sudo=None
        """
        return self._sudo

    @sudo.setter
    def sudo(self, value):
        if not isinstance(value, list):
            if value:
                # Setting sudo=True corresponds to ['-E'] by default
                value = ['-E']
            else:
                # Falsy non-list values become None
                value = None

        if value is not None and os.name != 'posix':
            logger.warn('Setting sudo is ignored on non-posix systems')
        self._sudo = value

    def add_options(self, new_options: List[str]):
        """Adds options to be passed on some smartctl queries

        Args:
            new_options (List[str]): A list of options in raw smartctl format
        """
        self.options = self.options + new_options

    def generic_call(self, params: List[str], pass_options=False) -> Tuple[List[str], int]:
        """Generic smartctl query

        Args:
            params (List[str]): The list of arguments to be passed
            pass_options (bool, optional): If true options list would be passed. Defaults to False.

        Returns:
            Tuple[List[str], int]: A raw line-by-line output from smartctl and the process return code
        """
        if not self.smartctl_path:
            raise FileNotFoundError("Command smartctl doesn't exist!")

        popen_list = []
        if os.name == 'posix':
            if self.sudo is not None:
                popen_list.extend(['sudo'] + self.sudo)

        popen_list.append(self.smartctl_path)

        if pass_options:
            popen_list.extend(self.options)

        popen_list.extend(params)

        logger.trace("Executing the following cmd: {0}".format(popen_list))

        cmd = Popen(popen_list, stdout=PIPE, stderr=PIPE)

        _stdout, _stderr = [i.decode('utf8') for i in cmd.communicate()]

        return _stdout.split('\n'), cmd.returncode

    def scan(self) -> List[str]:
        """Queries smartctl with option --scan-open

        Returns:
            List[str]: A raw line-by-line output from smartctl
        """
        return self.generic_call(['--scan-open'])[0]

    def health(self, disk: str) -> List[str]:
        """Queries smartctl with option --health

        Args:
            disk (str): the disk os-full-path

        Returns:
            List[str]: A raw line-by-line output from smartctl
        """

        return self.generic_call(['--health', disk])[0]

    def info(self, disk: str) -> List[str]:
        """Queries smartctl with option --info

        Args:
            disk (str): the disk os-full-path

        Returns:
            List[str]: A raw line-by-line output from smartctl
        """

        return self.generic_call(['--info', disk], pass_options=True)[0]

    def all(self, disk_type: str, disk: str) -> List[str]:
        """Queries smartctl with option --all

        Args:
            disk_type (str): the disk type
            disk (str): the disk os-full-path

        Returns:
            List[str]: A raw line-by-line output from smartctl
        """

        return self.generic_call(['-d', disk_type, '--all', disk], pass_options=True)[0]

    def test_stop(self, disk_type: str, disk: str) -> int:
        """Queries smartctl with option -X

        Args:
            disk_type (str): the disk type
            disk (str): the disk os-full-path

        Returns:
            int: the smartctl process return code
        """
        return self.generic_call(['-d', disk_type, '-X', disk])[1]

    def test_start(self, disk_type: str, test_type: str, disk: str) -> int:
        """Queries smartctl with option -t <test_type>

        Args:
            disk_type (str): the disk type
            test_type (str): the test type
            disk (str): the disk os-full-path

        Returns:
            int: the smartctl process return code
        """
        return self.generic_call(['-d', disk_type, '-t', test_type, disk])[0]


# A global smartctl object used as the defaults in Device and DeviceList.
SMARTCTL = Smartctl()
