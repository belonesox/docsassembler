# -*- coding: utf-8 -*-
"""
 Модуль сканеров зависимостей файлов
"""
import sys
import os
import random
import time

# import belonesox_tools.MiscUtils as ut
import optparse 

# pylint: disable=C0111

def process_cmd_line():
    """Set up and parse command line options"""
    usage = "Usage: %prog [options] <file>"
    parser = optparse.OptionParser(usage)
  
    parser.add_option("-b", "--batchmode", action="store_true", dest="batchmode",
      help="Does not interact with user (no windows etc.)", default=False)
  
    parser.add_option('-o', '--output',
                      dest='outputfile',
                      action='store',
                      metavar="FILE",
                      help="Write stdout to FILE")
  
    parser.add_option("-s", "--skip-experiments", action="store_false", dest="doExperiments",
      help="Does computational experiments with algorithm", default=True)
  
    parser.add_option("-q", "--quiet",
      action="store_false", dest="verbose", default=True,
      help="don't print status messages to stdout")
  
    options, args = parser.parse_args()
    return options, args, parser


class Helper:
    def __init__(self):
        self.start_time = time.time()
        self.time_limit = 36*2
        self.debug_mode = True
        self.deadline = self.start_time + self.time_limit
    
        myfilename = sys._getframe(3).f_code.co_filename #pylint: disable=W0212
        mypath, mynameext = os.path.split(myfilename)
        self.basename = os.path.splitext(mynameext)[0]
        self.objdir = os.path.join(mypath, "--obj", mynameext + ".obj")
        self.prefix = os.path.join(self.objdir, "")
        self.dotprefix = os.path.join(self.objdir, "dot")
        self.svgprefix = os.path.join(self.objdir, "svg")
        self.texprefix = os.path.join(self.objdir, "tex")
        
        self.options, args, parser = process_cmd_line() #pylint: disable=W0612
        
        if self.options.outputfile:
            sys.stdout = open(self.options.outputfile, "w", encoding='utf-8')
    
        self.experiment_scale = 10
        self.experiment_trycount = 2
        self.debug_mode = True
        self.sprite_count = 1
        self.random_source = random.Random(time.time())


    def no_more_time(self):
        return time.time() > self.deadline

   
    def reset_tex(self):
        filename = self.texprefix + ".tex"
        lf = open(filename, "w", encoding='utf-8')
        lf.close()
    
    def print_tex(self, tex_str):
        filename = self.texprefix + ".tex"
        lf = open(filename, "a+", encoding='utf-8')
        lf.write(tex_str + "\n")
        lf.close()
    
    def print_statements(self, statements, frametitle,
                        prefix="",
                        graph="digraph",
                        ext="dot",
                        reset=True,
                        beforelaststatement=""):
        graph_body = ""
        graph_str = ""
        frame = 0
        if reset:
            self.reset_tex()
        for s in statements:
            if s.strip().startswith("\\"):
                self.print_tex(s.encode("windows-utf8"))
            else:
                frame += 1
                if frame == len(statements):
                    graph_body += beforelaststatement
                graph_body_print = graph_body + beforelaststatement+s
                graph_body += s
                graph_str = """
              %(graph)s G{
                %(graph_body_print)s
              }
              """ % vars()
                graphname = self.dotprefix + prefix + '-%02d.%s' % (frame, ext)
                with open(graphname, 'w', encoding='utf-8') as lf:
                    lf.write(graph_str)
                
                tex_str = ur"""
              \begin{frame}
              \frametitle{%(frametitle)s}
              \begin{center}
              \localPDF[height=0.9\paperheight, width=.95\paperwidth, keepaspectratio]{--obj/dot%(prefix)s-%(frame)02d.%(ext)s.obj/--obj/obj.svg.obj/--obj/obj}
              \end{center}
              \end{frame}
              """  % vars()
                self.print_tex(tex_str.encode("utf-8"))
      
        graphname = self.dotprefix+'-last.%s' % ext
        with open(graphname, 'w', encoding='utf-8') as lf:
            lf.write(graph_str)

