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
import os
from typing import Dict, Any

from pySMART import Device

from .smartctlfile import SmartctlFile


def get_all_properties(obj) -> Dict[str, Any]:
    type_name = type(obj).__name__
    prop_names = dir(obj)

    ret = vars(obj)

    available_types = ['dict', 'str', 'int', 'float', 'list', 'NoneType']

    for prop_name in prop_names:
        prop_val = getattr(obj, prop_name)
        prop_val_type_name = type(prop_val).__name__

        if prop_name[0] != '_' and prop_val_type_name in available_types and prop_name not in ret:
            ret[prop_name] = prop_val

    return ret


def main():

    parser = argparse.ArgumentParser(
        description='Generate device.json from data stored in file for future tests.')
    parser.add_argument('--folder', required=True,
                        help='The folder where the device info is stored')
    parser.add_argument('--device', required=True,
                        help='The device name')
    parser.add_argument('--interface', default=None,
                        help='The device interface')

    args = parser.parse_args()

    folder = args.folder
    device_name = args.device
    interface_name = args.interface

    sf = SmartctlFile(folder)

    json_dict = {"name": device_name}

    if interface_name is None:
        dev = Device(device_name, smartctl=sf)

    else:
        dev = Device(device_name, interface=interface_name, smartctl=sf)
        json_dict['interface'] = interface_name

    json_dict['values'] = get_all_properties(dev)

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

    # Transform attributes
    if 'attributes' in json_dict['values']:
        att_list = []
        for att in json_dict['values']['attributes']:
            if att is None:
                att_list.append(None)
            else:
                att_list.append(vars(att))

        json_dict['values']['attributes'] = att_list

    # Transform tests
    if 'tests' in json_dict['values']:
        test_list = []
        for tst in json_dict['values']['tests']:
            if tst is None:
                test_list.append(None)
            else:
                test_list.append(vars(tst))

        json_dict['values']['tests'] = test_list

    with open(os.path.join(folder, 'device.json'), "w") as f:
        f.write(json.dumps(json_dict, indent=4))


if __name__ == "__main__":
    main()
