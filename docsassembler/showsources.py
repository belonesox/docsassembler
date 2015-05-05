# -*- coding: utf-8 -*-

"""
Call SumatraPDF and perform PDFSync
"""
import os
import os.path
import sys
import subprocess
# pylint: disable=F0401

import dependency_analyzer

def main():
    """
      Call SumatraPDF View, try to synchronize line number
    """
    def notepad(afile, linenum):
        realpath = os.path.abspath(afile)
        scmd = ''.join([
                r'C:\app\docstruct\npp\notepad++.exe',
                ' -n', str(linenum), ' ',
                ' "', realpath, '" '])
#        os.system(scmd)
        subprocess.Popen(scmd)
        

    def inkscape(afile):
        realpath = os.path.abspath(afile)
        scmd = ''.join([
                r'C:\app\docstruct\inkscape\inkscape.exe',
                ' "', realpath, '" '])
        os.system(scmd)
        
    realpath = os.path.abspath(sys.argv[1])
    linenum = sys.argv[2]

    deps_analyzer = dependency_analyzer.DependencyAnalyzer()
    files = deps_analyzer.get_all_files(realpath)
    if len(files) > 1:
        for afile in files[:-1]:
            pathname, ext = os.path.splitext(afile)
            if ext in ['.py', '.tex']:
                notepad(afile, 0)
            if ext in ['.svg']:
                inkscape(afile)
    notepad(realpath, linenum)
            
    
if __name__ == '__main__':
    main()

