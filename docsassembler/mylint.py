#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Friendly version of Pylint Utility
"""

import sys
import os
import getpass

import belonesox_tools.MiscUtils as ut

if len(sys.argv)<2:
    raise Exception("Задайте имя файла для проверки")

ut.install_if_asked()

class MyPyLint:
    """
      Инкапсуляция работы с Pylintом
    """
    def __init__(self, filepath):
        """
        """
        self.filepath  = filepath
        self.pylintfilename = None
        self.path, self.nameext = os.path.split(filepath)
        curpath = self.path
        while True:
            filename = os.path.join(curpath, "pylint.rc") 
            if os.path.exists(filename):
                self.pylintfilename = filename
                break
            
    def check(self):
        from pylint import lint as linter 
        argv = [
            "--rcfile", self.pylintfilename,
            "-iy",
            #"--comment=y",
            #"--disable-msg=I0011",
            "-fparseable",
            self.filepath
        ]
        linter.Run(argv) 
      

def _main():
    """
    Main procedure
    """
    mpl = MyPyLint(sys.argv[1])
    mpl.check()

if __name__ == "__main__":
    _main()
    sys.exit(0)