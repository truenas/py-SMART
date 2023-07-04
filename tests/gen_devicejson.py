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

import argparse
import json
import sys
import os
from typing import Dict, Any

from pySMART import Device
from pySMART.utils import get_object_properties

from .smartctlfile import SmartctlFile


def update_device(folder, device_name, interface_name=None):
    sf = SmartctlFile(folder)

    json_dict = {"name": device_name}

    if interface_name is None:
        dev = Device(device_name, smartctl=sf)

    else:
        dev = Device(device_name, interface=interface_name, smartctl=sf)
        json_dict['interface'] = interface_name

    json_dict['values'] = get_object_properties(dev, deep_copy=True)

    # Remove non serializable objects
    to_delete = [
        'smartctl',
    ]

    # add to list private objects
    for entry in json_dict['values']:
        if entry[0] == '_':
            to_delete.append(entry)

    for todel in to_delete:
        if todel in json_dict['values']:
            del json_dict['values'][todel]

    # Transform tests
    if 'tests' in json_dict['values']:
        test_list = []
        for tst in json_dict['values']['tests']:
            if tst is None:
                test_list.append(None)
            else:
                test_list.append(get_object_properties(tst))

        json_dict['values']['tests'] = test_list

    # Direct transform for other properties
    to_transform = ['diagnostics']
    for prop in json_dict['values']:
        if prop in to_transform:
            json_dict['values'][prop] = get_object_properties(
                json_dict['values'][prop])

    with open(os.path.join(folder, 'device.json'), "w") as f:
        f.write(json.dumps(json_dict, indent=4, sort_keys=True))


def main():

    parser = argparse.ArgumentParser(
        description='Generate device.json from data stored in file for future tests.')
    parser.add_argument('--folder', required=True,
                        help='The folder where the device info is stored')
    parser.add_argument('--device',
                        help='The device name')
    parser.add_argument('--interface', default=None,
                        help='The device interface')
    parser.add_argument('--updateSubfolders', default=False, action='store_true',
                        help='If set, the tool will scan the folder, read previusly stored tests, and regenerate them')

    args = parser.parse_args()

    folder = args.folder
    device_name = args.device
    interface_name = args.interface

    if args.updateSubfolders == False and device_name is None:
        print("Error, --device argument is required!")
        sys.exit(-1)

    elif args.updateSubfolders == False:
        update_device(folder, device_name, interface_name)

    elif args.updateSubfolders == True:
        subdirs = os.listdir(folder)
        for subdir in subdirs:
            subdir = os.path.join(folder, subdir)

            if os.path.isdir(subdir):
                json_path = os.path.join(subdir, 'device.json')
                if os.path.exists(json_path):
                    with open(json_path) as json_file:
                        data = json.load(json_file)

                    # Check if we should skip this device
                    if 'skip' in data and data['skip'] == True:
                        continue

                    # Check if interface is present
                    if 'interface' not in data:
                        update_device(subdir, data['name'])

                    else:
                        update_device(subdir, data['name'], data['interface'])

                else:
                    print(f"Warning: {json_path} does not exists!. Skipped...")

    else:
        print("Unknown error!")
        sys.exit(-1)


if __name__ == "__main__":
    main()
