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
from setuptools import setup
from subprocess import Popen, PIPE
import os
import re


def read_file(path):
    with open(os.path.join(os.path.dirname(__file__), path)) as fp:
        return fp.read()


def _get_version_match(content):
    # Search for lines of the form: # __version__ = 'ver'
    regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    version_match = re.search(regex, content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string in '__init__.py'.")


def get_version(path):
    try:
        p = Popen(['git', 'describe', '--always', '--tags'],
                  stdout=PIPE, stderr=PIPE)
        p.stderr.close()
        line = p.stdout.readlines()[0]
        describe = line.strip()[1:].decode('utf-8').split('-')
        if len(describe) == 1:
            return describe[0]
        else:
            return describe[0]+'.'+describe[1]

    except Exception as e:
        print(e)
        return _get_version_match(read_file(path))


def get_long_description():
    this_directory = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

    return long_description


REQUIREMENTS = [
    'humanfriendly',
]

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    name=os.environ.get('PACKAGE_NAME', 'pySMART'),
    version=get_version(os.path.join('pySMART', '__init__.py')),
    author='Marc Herndon',
    author_email='Herndon.MarcT@gmail.com',
    packages=['pySMART', 'pySMART.interface'],
    url='https://github.com/truenas/py-SMART',
    license='GNU LGPLv2.1',
    description='Wrapper for smartctl (smartmontools)',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': [
            # Requirements only needed for development
            'pytest',
            'pytest-cov',
        ]
    },
)
