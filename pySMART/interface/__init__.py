# SPDX-FileCopyrightText: 2022 Rafael Leira, Naudit HPCN S.L.
# SPDX-License-Identifier: LGPL-2.1-or-later

"""
Copyright (C) 2022 Rafael Leira, Naudit HPCN S.L.

This package contains the special objects to handle and store data related to disk interfaces.
This is required as ATA disks and NVMe disks have different attributes and different ways to get them.
"""

from .ata import AtaAttributes
from .common import CommonIface
from .nvme import NvmeAttributes, NvmeError
from .scsi import SCSIAttributes


__all__ = [
    'AtaAttributes',
    'CommonIface',
    'NvmeAttributes',
    'SCSIAttributes',
]
