# SPDX-FileCopyrightText: 2021 Rafael Leira, Naudit HPCN S.L.
# SPDX-License-Identifier: LGPL-2.1-or-later

import re
import os
from pySMART.smartctl import Smartctl
from .exceptions import SmartctlfileSampleNotFound
from typing import Union, Tuple, List

import logging
logger = logging.getLogger('pySMART')


class SmartctlFile(Smartctl):
    """This class is just a mockup of the Smartctl class
    """

    def __init__(self, smartctl_path, options: List[str] = []):
        """Instantiates and initializes the Smartctl wrapper."""

        self.smartctl_path = smartctl_path
        self.options: List[str] = options

    def generic_call(self, params: List[str], pass_options=False) -> Tuple[List[str], int]:
        """Generic smartctl query

        Args:
            params (List[str]): The list of arguments to be passed
            pass_options (bool, optional): If true options list would be passed. Defaults to False.

        Returns:
            Tuple[List[str], int]: A raw line-by-line output from smartctl and the process return code
        """
        if pass_options:
            final_params = self.options + params
        else:
            final_params = params

        filename = '_' + '_'.join(final_params)

        filename = os.path.join(
            self.smartctl_path, re.sub('[/\\\\:]', '_', filename))

        logger.debug("Opening file: {0}".format(filename))

        try:
            with open(filename, mode='rb') as f:
                raw_data = f.read()
        except:
            raise SmartctlfileSampleNotFound(filename, final_params)

        return self._decode_output(raw_data), 0
