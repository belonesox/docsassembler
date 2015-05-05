# -*- coding: utf-8 -*-

"""
Call xelatex and parse output.
"""
import os
import os.path
import sys
import shutil
import time
import multiprocessing
import rusmakeindex as mkidx

import stastools.MiscUtils as ut
import messagefilter as mf
 
class Processor:
    """
    Main class, incapsulate all scripts
    """
    def __init__(self, filename):
        self.filename = str(os.path.abspath(filename))
        (self.path, self.nameext) = os.path.split(self.filename)
        (self.name, self.ext) = os.path.splitext(self.nameext)

    def process_py(self):
        """
        Process (that is — run) python files.
        """
        curdir = os.getcwd()
        os.chdir(self.path)
        command = ''.join([
            r'c:\app\docstruct\python27\python ',
            ' "', self.nameext, '"'])

        out = ut.get_prog_output(command)
        out = ut.unicodeanyway(out)
        print out.encode("utf8")
        os.chdir(curdir)

    def sconstruct_exists(self):
        """
        Checks if ``SConstruct`` exists in top directories.
        """
        for level in xrange(0, 10):
            sconstruct = os.path.join(self.path, r'../'*level, 'SConstruct')
            if os.path.exists(sconstruct):
                return True
        return False

    def process_tex(self):
        """
        Process TeX-files.
        """
        if self.sconstruct_exists():
            additional_ops = ""
            import socket
            hostname = socket.gethostname()
            if hostname.startswith('stas') or hostname.startswith('st-fomin'):
                additional_ops = ''.join([
                    ' --debug=explain ',
                    ' --tree=all,status  ',
                    ' --profile=profile.log  ' ])
            cpu_count =  1 #(multiprocessing.cpu_count() + 1) / 2
            command = ''.join([
                r'c:\app\docstruct\python27\scripts\scons ',
                additional_ops,
                ' --implicit-cache  ',
                ' --jobs ', str(cpu_count),
                #' --implicit-deps-unchanged ',
#                ' --profile=profile.log  ',
                ' -D ',
                ' "', self.name, '.pdf"'])
            curdir = os.getcwd()
            os.chdir(self.path)
            print self.path
            print command
            out = ut.get_prog_output_with_log(command)
            wfilename = self.filename + ".warnings"
            if os.path.exists(wfilename):
                print ut.file2string(wfilename)
                ut.removedirorfile(wfilename)

            #cutefilter = mf.CuteFilter(self.path)
            #out = cutefilter(out)
            #print out.encode("utf8")
            os.chdir(curdir)
            #out = ut.get_prog_output(command)
            #out = ut.unicodeanyway(out)
            #print out.encode("utf8")
            return
        
        respdf = os.path.join(self.path, self.name) + ".pdf"
        outpdf = os.path.join(self.path, "--obj", self.name) + ".pdf"
        outpdfsync = os.path.join(self.path, "--obj", self.name) + ".synctex.gz"
        pdfsync = os.path.join(self.path, self.name) + ".synctex.gz"
        curdir = os.getcwd()
        os.chdir(self.path)
        ut.createdir("--obj")
        command = ''.join([
            r'xelatex -synctex=1 -file-line-error-style ',
            ' -output-directory="--obj" ',
            ' -interaction nonstopmode "', self.nameext, '"'])
        
        os.environ['PATH'] = ';'.join([r'c:\app\docstruct\xetex\bin\win32',
                                       os.environ['PATH'] ])
        print os.environ["PATH"]
        print command
        filter_ = mf.CuteFilter(self.path)
        out = ut.get_prog_output(command)
        out = filter_(out)
        print out.encode("utf8")
    
        outbcffile = os.path.join(self.path, "--obj", self.name) + ".bcf"
        if os.path.exists(outbcffile):
            os.chdir('--obj')
            command = os.path.join('biber "%(outbcffile)s"' % vars())
            os.system(command)
            os.chdir('..')
        
        shutil.copyfile(outpdf, respdf )
        if os.path.exists(outpdfsync):
            shutil.copy(outpdfsync, pdfsync)
        os.chdir(curdir)
        
            
    def process(self):
        """
        Process given file according to its extension
        """
        if self.ext in ['.py']:
            self.process_py()
            
        if self.ext in ['.tex']:
            self.process_tex()

def main():
    """
      Call SumatraPDF View, try to synchronize line number
    """
    start_time = time.time()
    proc = Processor(sys.argv[1])
    proc.process()
    end_time = time.time()
    print "It takes", end_time - start_time 
    
if __name__ == '__main__':
    main()

