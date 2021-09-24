#!/usr/bin/env python3
import ddrescuelib
__version__ = '0.0'

if __name__ == '__main__':
    ddrescue = ddrescuelib.ddrescue_class()
    print(ddrescue.get_version())