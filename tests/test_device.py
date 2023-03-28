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
from pySMART.utils import get_object_properties

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
            skip_values = ['attributes', 'tests',
                           'diagnostics', 'if_attributes']
            for value in values:
                # Special comparators
                if value == 'temperatures':
                    for temp in values[value]:
                        assert dev.temperatures[int(
                            temp)] == values[value][temp]

                elif value not in skip_values:
                    # Generic case
                    assert getattr(dev, value) == values[value]

    @pytest.mark.parametrize("folder", folders)
    def test_device_diagnostics(self, folder):

        device_data = self.get_device_data(folder)

        dev: Device = self.create_device(folder, device_data)

        if 'values' in device_data and 'diagnostics' in device_data['values']:
            diagnostics = device_data['values']['diagnostics']
            assert get_object_properties(dev.diagnostics) == diagnostics

    @pytest.mark.parametrize("folder", folders)
    def test_device_iface_attributes(self, folder):
        """
        Test if dedicated-interface attributes have been correctly loaded
        """

        device_data = self.get_device_data(folder)

        dev: Device = self.create_device(folder, device_data)

        if 'values' in device_data and 'if_attributes' in device_data['values']:
            if_attributes = device_data['values']['if_attributes']
            if dev.if_attributes is None:
                assert if_attributes is None
            else:
                dev_if_attributes = get_object_properties(
                    dev.if_attributes)
                assert dev_if_attributes is not None

                # Handle NvmeAtrributes/errors
                if 'errors' in dev_if_attributes:
                    dev_if_attributes['errors'] = [get_object_properties(
                        err) for err in dev_if_attributes['errors']]

                assert dev_if_attributes == if_attributes

    @pytest.mark.parametrize("folder", folders)
    def test_device_attributes(self, folder):

        device_data = self.get_device_data(folder)

        dev: Device = self.create_device(folder, device_data)

        if 'values' in device_data and 'attributes' in device_data['values']:
            attributes = device_data['values']['attributes']
            i = 0
            for attribute in attributes:
                # Generic case
                if dev.attributes[i] is None:
                    assert dev.attributes[i] == attribute
                else:
                    assert get_object_properties(
                        dev.attributes[i]) == attribute

                i = i + 1

    @pytest.mark.parametrize("folder", folders)
    def test_device_tests(self, folder):

        device_data = self.get_device_data(folder)

        dev: Device = self.create_device(folder, device_data)

        if 'values' in device_data and 'tests' in device_data['values']:
            tests = device_data['values']['tests']
            i = 0
            for test in tests:
                # Generic case
                if dev.tests[i] is None:
                    assert dev.tests[i] == test
                else:
                    assert get_object_properties(dev.tests[i]) == test

                print(dev.tests[i])

                i = i + 1
