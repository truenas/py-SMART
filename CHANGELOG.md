Version 1.3.1
=============
- Added support for test polling_minutes. Requested in [#77](https://github.com/truenas/py-SMART/issues/77) and [#78](https://github.com/truenas/py-SMART/pull/78). Thanks @Gigahawk
- Minnor typo fixed in NvmeAttributes (issue [#81](https://github.com/truenas/py-SMART/issues/81)).  Thanks @petersulyok
- **Breaking changes**
    - **smartctl.all**:
        - Officially removed support for python 3.7.

Version 1.3.0
=============

- Fixed some special NVMe capacity parsing issues (issue [#73](https://github.com/truenas/py-SMART/issues/73)). Thanks @wolfdate25
- Fixed nvme test parsing on smartmontools >= 7.4 (issue [#75](https://github.com/truenas/py-SMART/issues/75)). Thanks @NicholasCJL
- Other minnor fixes with @ulmitov's help
- **Breaking changes**
    - **smartctl.all**:
        - Officially removed support for python 3.7. However, pyproject.toml still allows the 3.7 version. This will be removed in the next release.
    - **smartctl.interface.ata**:
        - Now ata interfaces are handled in the same way as NVMe interfaces.
        - device.attribute references if_attributes.legacyAttributes for backwards compatibility.

Version 1.2.5
=============
- Minnor fix on serial NVME readings (MR [#69](https://github.com/truenas/py-SMART/pull/69)). Thanks @Heidistein
- Minnor fix on reads/writes NVME readings (MR [#71](https://github.com/truenas/py-SMART/pull/71). Thanks @Heidistein
- Fixed capacity detection in some devices & envirorments (issue [#72](https://github.com/truenas/py-SMART/issues/72)). Thanks @Shablykinm
- Now file/process encodings are automatically detected. This whould fix issue [#72](https://github.com/truenas/py-SMART/issues/72)).
- Minnor refactor on interface.nvme and ata attributes. This should not affect any user.

Version 1.2.4
=============
- [dev tools] Test reorganization
- [dev tools] Added new tests (issues [#46](https://github.com/truenas/py-SMART/issues/46))
- Fixed parsing of NVMe devices on some systems / languages (issue [#63](https://github.com/truenas/py-SMART/issues/63))
- Fixed parsing of NVMe tests on smartmontools >=7.4 (issue [#64](https://github.com/truenas/py-SMART/issues/64))
- Fixed parsing of ATA attributes on some systems (issue [#65](https://github.com/truenas/py-SMART/issues/65))
- Fixed parsing of Drive type detection (calling -d test) (issue [#65](https://github.com/truenas/py-SMART/issues/65))
- Removed setup.py and moved to pyproject.toml 

Version 1.2.3
=============
- Improved parsing of device vendor (requested in [#58](https://github.com/truenas/py-SMART/issues/58))
- As reported in [#57](https://github.com/truenas/py-SMART/issues/57), sometimes there is a None vale in some device diagnostics. This is now handled.
- DeviceList: Added init param `catch_errors` (defaults to `False`) to catch errors when parsing devices. This is useful when you want to parse a list of devices and you don't want to stop the parsing if one of the devices fails. The error will be printed to logger.exception and the device will be skipped. Requested in [#59](https://github.com/truenas/py-SMART/issues/59).

Version 1.2.2
=============
- Fixing more python typing issues
- Fixed issue with device interfaces on some methods [#56](https://github.com/truenas/py-SMART/issues/56)
- Smartctl now has exec method for better overloadings. Requested in [#54](https://github.com/truenas/py-SMART/issues/54)
- Fix disk capacity parsing: Now we retrieve the human and the "real" values. Size() will return the real/machine value instead the expanded human value which introduces some inaccuracies.
- Fix disk capacity parsing on NVMe devices ([#53](https://github.com/truenas/py-SMART/issues/53))
- Fixed some strange issues with char \u202f ([#52](https://github.com/truenas/py-SMART/issues/52))
- **Breaking changes**
    - **smartctl.all**:
        - Parameters where reordered to make it more consistent with the rest of the library.
    - **device.interface**, **device.smartctl_interface** and **device.dev_interface**:
        - Attribute `interface` moved into `_interface`
        - Added new property `smartctl_interface` which returns the interface value used by smartctl
        - Added new property `dev_interface` which returns a fine tuned interface value that reflects more accurately the device interface
        - Added new property `interface` that wraps around `smartctl_interface` for compatibility.

Version 1.2.1
=============
- Fixed some issues with scsi devices parsing ([#51](https://github.com/truenas/py-SMART/issues/51))
- Fixed some issues with ATA attributes parsing on ssd+usb+arm devices ([#50](https://github.com/truenas/py-SMART/issues/50))
- Removed support for python 3.6 (just for testing convenience, probably it will still works for months)

Version 1.2.0
=============
- Added property *vendor* to *Device* object
- Added property *sector_size* to *Device* object
- Added property *logical_sector_size* to *Device* object
- Added property *physical_sector_size* to *Device* object
- Added "sudo" property to the Smartctl class for POSIX systems.
- Added global SMARTCTL object used for defaults.
- Added sector sizes to diagnostics class and other minor improvements to its structure.
- Added class NvmeAttributes to handle specific attributes on NVMe devices.
- Added device property: `if_attributes` to return the device's interface attributes. This is
    currently only implemented for NVMe devices but ATA/SCSI devices will be implemented in the
    future.
- Minor changes on parsing regexes
- Checks for temperature units (farenheit) and converts to celsius
- Fixed MacOS compatibility issues up to version 11.x
- Fixed some localization (lang) issues
- Fixed issue ([#49](https://github.com/truenas/py-SMART/issues/49)) detecting selective test 
    capabilities as short/long tests on device parsing

Version 1.1.0
=============
- Minor fixes
- Added tests
- **Breaking changes**
    - **Typing**:
        - Tests and attributes have been typed. This may cause some exceptions if you have been attached to the "everything is a string" previously philosophy.
        - Some attributes have been kept back for compatibility but others (like num) have been directly converted into an integer. Test everything after the upgrade
        - Other typing changes might take place in the future when it is confirmed that smartctl always uses a fixed time instead of "anything" (str for us).
    - **device.tests**: Now returns an empty list instead of None when there are no tests present
    - **device.diags**: Device.diags have been deprecated and moved into a class called Diagnostics. For compatibility reasons, a property called "diags" has been created. This property simulates the old diags behavior.

Version 1.0.6
=============
- This release contains minnor changes and upgrades to support python 3.8/9/10 as other other mithor improvements
- It contains all the commits on TRUENAS/pySMART from 9/8/2019 to this version tag.

Version 1.0.0
=============
- This release contains all the commits on TRUENAS/pySMART from 11/6/2015 to 9/8/2019.
- This mostly adds multiplatform support for freebsd and many other interesting improvements

