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
import json
import os
import pytest

from pySMART import Device

from .smartctlfile import SmartctlFile

# discover tests

single_device_tests_main_path = './tests/dataset/singletests/'

folders = [single_device_tests_main_path +
           p for p in os.listdir(single_device_tests_main_path)]


class TestSingleDevice():

    def get_device_data(self, folder: str):
        with open(os.path.join(folder, 'device.json')) as json_file:
            data = json.load(json_file)

        return data

    def create_device(self, folder: str, data) -> Device:
        sf = SmartctlFile(folder)

        if 'interface' not in data:
            return Device(data['name'], smartctl=sf)

        else:
            return Device(data['name'], interface=data['interface'], smartctl=sf)

    @pytest.mark.parametrize("folder", folders)
    def test_device_creation(self, folder):

        device_data = self.get_device_data(folder)

        dev: Device = self.create_device(folder, device_data)

    @pytest.mark.parametrize("folder", folders)
    def test_generic_checks(self, folder):

        device_data = self.get_device_data(folder)

        dev: Device = self.create_device(folder, device_data)

        if 'values' in device_data:
            values = device_data['values']
            for value in values:
                # Special comparators
                if value == 'temperatures':
                    for temp in values[value]:
                        assert dev.temperatures[int(
                            temp)] == values[value][temp]

                else:
                    # Generic case
                    assert getattr(dev, value) == values[value]
