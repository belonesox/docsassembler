# -*- coding: utf-8 -*-

"""
Call SumatraPDF and perform PDFSync
"""
import os
import os.path
import glob
import sys
import time
import subprocess

# pylint: disable=F0401
import win32ui
import dde

def main():
    """
      Call SumatraPDF View, try to synchronize line number
    """
    realpath = os.path.abspath(sys.argv[1])
    srcpath = os.path.abspath(sys.argv[2])
    (pdfpath, pdfnameext) = os.path.split(realpath)
    (pdfname, pdfext) = os.path.splitext(pdfnameext)
    (path, nameext) = os.path.split(srcpath)
    (name, ext) = os.path.splitext(nameext)
    srcpath = srcpath.replace('\\', '/')
    lineno = sys.argv[3]
    
    scmd = ''.join([r'C:\app\docstruct\pdfview\SumatraPDF.exe ',
                    ' -reuse-instance ',
                    ' -inverse-search ',
#                    r'"\"C:\app\docstruct\npp\notepad++.exe\" -n%l \"%f\"" ',
                    r'"\"C:\app\docstruct\python27\pythonw.exe\" \"C:\app\docstruct\python27\Lib\site-packages\docsassembler\showsources.py\"   \"%f\" %l "',
                    '"', realpath, '"'  ])
    
    p = subprocess.Popen(scmd, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT)
    
    print(scmd)
    time.sleep(1)    

    server = dde.CreateServer()
    server.Create("pdfviewproxy")
    
    conversation = dde.CreateConversation(server)

    srcfile = srcpath
    if pdfpath == path and pdfname == name:
        srcfile = nameext    
    
    print("Try to connect")
    conversation.ConnectTo("SUMATRA", "control")
    ddecmd = ''.join(['[ForwardSearch("', realpath, '", "',
                                          srcfile, '", ', lineno, ',0,0,1)]'])
    print("Try to exec", ddecmd)
    conversation.Exec(ddecmd)

    print("PDFViewer connected...")
    server.Destroy()
    
if __name__ == '__main__':
    main()

