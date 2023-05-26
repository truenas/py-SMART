pySMART
===========

![](https://img.shields.io/pypi/v/pySMART?label=release)
![](https://img.shields.io/pypi/pyversions/pySMART)
[![Python Tests](https://github.com/truenas/py-SMART/actions/workflows/check.yml/badge.svg)](https://github.com/truenas/py-SMART/actions/workflows/check.yml)
![](https://img.shields.io/github/actions/workflow/status/truenas/py-smart/publish-to-test-pypi.yml)
![](https://img.shields.io/github/issues/truenas/py-smart)
![](https://img.shields.io/github/issues-pr/truenas/py-smart)
![](https://img.shields.io/pypi/dm/pysmart)

Copyright (C) 2021-2023 [Rafael Leira](https://github.com/ralequi)\
Copyright (C) 2021 [Truenas team](https://www.truenas.com/)\
Copyright (C) 2015 Marc Herndon

pySMART is a simple Python wrapper for the ``smartctl`` component of
``smartmontools``. It is officially compatible with Linux, Windows and FreeBSD,
as long as smartctl is on the system path. Running with administrative rights
is strongly recommended, as smartctl cannot accurately detect all device types
or parse all SMART information without these permissions.

With only a device's name (ie: /dev/sda, pd0), the package will create a
``Device`` object, populated with all relevant information about that
device. The documented API can then be used to query this object for
information, initiate self-tests, and perform other functions.

Usage
=====
The most common way to use pySMART is to create a logical representation of the
physical storage device that you would like to work with, as shown::


```python
>>> from pySMART import Device
>>> sda = Device('/dev/sda')
>>> sda
<SATA device on /dev/sda mod:WDC WD5000AAKS-60Z1A0 sn:WD-WCAWFxxxxxxx>
```

``Device`` class members can be accessed directly, and a number of helper methods
are provided to retrieve information in bulk.  Some examples are shown below::

```python
>>> sda.assessment  # Query the SMART self-assessment
'PASS'
>>> sda.attributes[9]  # Query a single SMART attribute
<SMART Attribute 'Power_On_Hours' 068/000 raw:23644>
>>> sda.all_attributes()  # Print the entire SMART attribute table
ID# ATTRIBUTE_NAME          CUR WST THR TYPE     UPDATED WHEN_FAIL    RAW
  1 Raw_Read_Error_Rate     200 200 051 Pre-fail Always  -           0
  3 Spin_Up_Time            141 140 021 Pre-fail Always  -           3908
  4 Start_Stop_Count        098 098 000 Old_age  Always  -           2690
  5 Reallocated_Sector_Ct   200 200 140 Pre-fail Always  -           0
    ... # Edited for brevity
199 UDMA_CRC_Error_Count    200 200 000 Old_age  Always  -           0
200 Multi_Zone_Error_Rate   200 200 000 Old_age  Offline -           0
>>> sda.tests[0]  # Query the most recent self-test result
<SMART Self-test [Short offline|Completed without error] hrs:23734 LBA:->
>>> sda.all_selftests()  # Print the entire self-test log
ID Test_Description Status                        Left Hours  1st_Error@LBA
 1 Short offline    Completed without error       00%  23734  -
 2 Short offline    Completed without error       00%  23734  -
   ... # Edited for brevity
 7 Short offline    Completed without error       00%  23726  -
 8 Short offline    Completed without error       00%  1      -
```

Alternatively, the package provides a ``DeviceList`` class. When instantiated,
this will auto-detect all local storage devices and create a list containing
one ``Device`` object for each detected storage device::

```python
>>> from pySMART import DeviceList
>>> devlist = DeviceList()
>>> devlist
<DeviceList contents:
<SAT device on /dev/sdb mod:WDC WD20EADS-00R6B0 sn:WD-WCAVYxxxxxxx>
<SAT device on /dev/sdc mod:WDC WD20EADS-00S2B0 sn:WD-WCAVYxxxxxxx>
<CSMI device on /dev/csmi0,0 mod:WDC WD5000AAKS-60Z1A0 sn:WD-WCAWFxxxxxxx>
>
>>> devlist.devices[0].attributes[5]  # Access Device data as above
<SMART Attribute 'Reallocated_Sector_Ct' 173/140 raw:214>
```

In the above cases if a new DeviceList is empty or a specific Device reports an
"UNKNOWN INTERFACE", you are likely running without administrative privileges.
On POSIX systems, you can request smartctl is run as a superuser by setting the
sudo attribute of the global SMARTCTL object to True. Note this may cause you
to be prompted for a password.


```python
>>> from pySMART import DeviceList
>>> from pySMART import Device
>>> sda = Device('/dev/sda')
>>> sda
<UNKNOWN INTERFACE device on /dev/sda mod:None sn:None>
>>> devlist = DeviceList()
>>> devlist
<DeviceList contents:
>
>>> from pySMART import SMARTCTL
>>> SMARTCTL.sudo = True
>>> sda = Device('/dev/sda')
>>> sda
[sudo] password for user:
<SAT device on /dev/sda mod:ST10000DM0004-1ZC101 sn:ZA20VNPT>
>>> devlist = DeviceList()
>>> devlist
<DeviceList contents:
<NVME device on /dev/nvme0 mod:Sabrent Rocket 4.0 1TB sn:03850709185D88300410>
<NVME device on /dev/nvme1 mod:Samsung SSD 970 EVO Plus 2TB sn:S59CNM0RB05028D>
<NVME device on /dev/nvme2 mod:Samsung SSD 970 EVO Plus 2TB sn:S59CNM0RB05113H>
<SAT device on /dev/sda mod:ST10000DM0004-1ZC101 sn:ZA20VNPT>
<SAT device on /dev/sdb mod:ST10000DM0004-1ZC101 sn:ZA22W366>
<SAT device on /dev/sdc mod:ST10000DM0004-1ZC101 sn:ZA22SPLG>
<SAT device on /dev/sdd mod:ST10000DM0004-1ZC101 sn:ZA2215HL>
>
```

In general, it is recommended to run the base script with enough privileges to
execute smartctl, but this is not possible in all cases, so this workaround is
provided as a convenience. However, note that using sudo inside other
non-terminal projects may cause dev-bugs/issues.

Using the pySMART wrapper, Python applications be be rapidly developed to take
advantage of the powerful features of smartmontools.

Installation
============
``pySMART`` is available on PyPI and installable via ``pip``::

```bash
python -m pip install pySMART
```

The only external (non-python) dependency is the ``smartctl`` component of the smartmontools
package.  This should be pre-installed in most Linux distributions, or it
can be obtained through your package manager.  Likely one of the following::

```bash
apt-get install smartmontools
#    or
yum install smartmontools
```

On Windows PC's, smartmontools must be downloaded and installed.  The latest
version can be obtained from the project's homepage, http://www.smartmontools.org/.

Note that after installing smartmontools on Windows, the directory containing
``smartctl.exe`` must be added to the system path, if it is not already.

Documentation
=============
API documentation for ``pySMART`` was generated using ``pdoc`` and can be
found in the /docs folder within the package archive.

Development
===========
Tests are run using ``pytest``.  Under [folder tests](tests), there is a
readme with instructions on how to run the tests.

Acknowledgements
================
I would like to thank the entire team behind smartmontools for creating and
maintaining such a fantastic product.

In particular I want to thank Christian Franke, who maintains the Windows port
of the software.  For several years I have written Windows batch files that
rely on smartctl.exe to automate evaluation and testing of large pools of
storage devices.  Without his work, my job would have been significantly
more miserable. :)

Additionally I would like to thank iXsystems, Inc., the team behind the amazing
FreeNAS and TrueNAS products.  Several years ago that team approached me with an
interest in pySMART, though I have no other affiliation with the company.  At
their request I made a simple change to allow pySMART to run on FreeBSD and
changed the license from GPL to LGPL to allow them to build upon my work and
incorporate it into their products.  They began hosting the code on their github,
and in the intervening years they've taken the project to all new heights.
Because of their work the code is now Python 3 compatible, supports NVME hardware
devices, and has several other improvements and bug fixes.

Final Note on Licensing
=======================
At the request of several companies seeking to use this code in their products,
the license has been changed from GPL to the slightly more permissive LGPL.
This should allow you to call into pySMART as a library as use it as-is in your
own project without fear of "GPL contamination".  If you are reading this and
thinking that the license is still too restrictive, please contact me. I am very
willing to make the code available privately under a more permissive license,
including for some corporate or commercial uses. I'd just like for you to say hello
first, and tell me a bit about your project and how pySMART could fit into it. 
