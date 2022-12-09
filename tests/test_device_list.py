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

from pySMART import Device, DeviceList
from pySMART.utils import get_object_properties

from .smartctlfile import SmartctlFile

# discover tests

single_device_tests_main_path = './tests/dataset/listingtests/'

folders = [single_device_tests_main_path +
           p for p in os.listdir(single_device_tests_main_path)]


class TestListDevice():

    def get_device_data(self, folder: str) -> dict:
        try:
            with open(os.path.join(folder, 'device.json')) as json_file:
                data = json.load(json_file)
        except:
            data = {}

        return data

    def create_list_device(self, folder: str, data: dict) -> DeviceList:
        sf = SmartctlFile(folder)

        if 'init' not in data:
            return DeviceList(smartctl=sf)

        else:
            return DeviceList(init=data['init'], smartctl=sf)

    @pytest.mark.parametrize("folder", folders)
    def test_list_devices(self, folder):

        data = self.get_device_data(folder)

        device_data: DeviceList = self.create_list_device(folder, data)

        # Check that the number of devices is correct
        assert len(device_data.devices) == data['count']
