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

smartctl_type = {
    'ata': 'ata',
    'csmi': 'ata',
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

__all__ = ['smartctl_type']
