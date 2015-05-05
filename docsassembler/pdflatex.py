# -*- coding: utf-8 -*-

"""
Call xelatex and parse output.
"""
import os
import os.path
import sys
import shutil


import belonesox_tools.MiscUtils as ut
import texfilter as tx

def main():
    """
      Call SumatraPDF View, try to synchronize line number
    """
    filename = str(os.path.abspath(sys.argv[1]))
    (path, nameext) = os.path.split(filename)
    (name, ext) = os.path.splitext(nameext)
    respdf = os.path.join(path, name) + ".pdf"
    outpdf = os.path.join(path, "--obj", name) + ".pdf"
    outpdfsync = os.path.join(path, "--obj", name) + ".pdfsync"

    pdfsync = os.path.join(path, name) + ".pdfsync"
    curdir = os.getcwd()
    os.chdir(path)
    ut.createdir("--obj")
    command = ''.join([
        r'xelatex -synctex=1 -file-line-error-style  -output-directory="--obj" ',
        ' -interaction nonstopmode "', nameext, '"'])
    
    os.environ['PATH'] = ';'.join([r'c:\app\docstruct\xetex\bin\win32',
                                   os.environ['PATH'] ])
    print os.environ["PATH"]
    print command
    texfilter = tx.TeXFilter(path)
    out = ut.get_prog_output(command)
    out = texfilter(out)
    print out.encode("utf8")

    shutil.copyfile(outpdf, respdf )
    if os.path.exists(outpdfsync):
        foutpdfsync = open(outpdfsync, "r")
        fpdfsync = open(pdfsync, "w")
        for line in foutpdfsync.readlines():
            if line.startswith("("):
                realpath = os.path.realpath(line[1:-1])
                if not realpath[-4:-3] == ".":
                    realpath = realpath + ".tex"
                newline = "(" + realpath.replace('\\','/') + "\n" 
            else:
                newline = line
            fpdfsync.write(newline)
        fpdfsync.close()    
        foutpdfsync.close()
    os.chdir(curdir)

    
if __name__ == '__main__':
    main()

