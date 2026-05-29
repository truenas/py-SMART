# SPDX-FileCopyrightText: 2021 Rafael Leira, Naudit HPCN S.L.
# SPDX-License-Identifier: LGPL-2.1-or-later

class SmartctlfileSampleNotFound(Exception):
    def __init__(self, path, args=[]):
        args_str = ' '.join(args)
        super().__init__(
            f'Smartctlmockup didn\'t found requested file on {path}. This might be the simulating the call of "smartctl {args_str}"')
