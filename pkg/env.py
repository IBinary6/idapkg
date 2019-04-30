"""
:os: operating system. 'win' | 'mac' | 'linux'
:ea: current ea. 32 | 64
:version: Decimal object for IDA Pro's version (ex. :code:`Decimal(6.95)`)
:version_info:
    namedtuple with version details
    (ex. :code:`VersionPair(major=7, minor=0, micro=171130)`)

"""

import collections
import os as _os
import re
import sys
from decimal import Decimal

OS_MAP = {'win32': 'win', 'darwin': 'mac', 'linux2': 'linux'}

# Will be set from IDA Pro
ea = -1
os = 'unknown'
version = Decimal('0.0')


def __load_version_from_ida():
    global ea, os, version
    if idc.__EA64__:
        ea = 64
    else:
        ea = 32

    os = OS_MAP[sys.platform]
    version = idaapi.get_kernel_version()

    version = re.sub(r'^(\d.)0(\d.*)', r'\1\2', version)
    version = Decimal(version)


version_info_cls = collections.namedtuple('VersionPair', 'major minor micro')
version_info = version_info_cls(0, 0, 0)


def __load_ida_native_version():
    global version_info

    if version_info:
        return version_info
    sysdir = _os.path.dirname(_os.path.dirname(idaapi.__file__))
    exe_name = 'ida' if ea == 32 else 'ida64'
    if os == 'win':
        path = _os.path.join(sysdir, exe_name + '.exe')
        with open(path, 'rb') as f:
            data = f.read()
            needle = 'F\0i\0l\0e\0V\0e\0r\0s\0i\0o\0n\0\0\0\0\0'
            offset = data.rfind(needle) + len(needle)
            offset2 = data.find('\0\0', offset) + 1
            version_str = data[offset:offset2].decode('utf16').encode('utf8')

            version_str = version_str[:version_str.rfind('.')] + version_str[version_str.rfind('.') + 1:]
    elif os == 'mac':
        path = _os.path.join(sysdir, exe_name)
        with open(path, 'rb') as f:
            data = f.read()
            needle = '<key>CFBundleShortVersionString</key>'
            offset = data.rfind(needle)
            offset = data.find('<string>', offset) + 8
            offset2 = data.find('</string', offset)
            version_str = data[offset:offset2]

    version_info = version_info_cls._make(map(int, version_str.split('.')))
    return version_info


try:
    import idc
    import idaapi

    __load_version_from_ida()
    __load_ida_native_version()

except ImportError:
    idc, idaapi = None, None
    pass

__all__ = ['os', 'ea', 'version', 'version_info']
