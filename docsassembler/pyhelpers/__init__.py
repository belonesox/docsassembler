# -*- coding: utf-8 -*-
"""
 Модуль сканеров зависимостей файлов
"""
import sys
import os
import random
import time

# pylint: disable=C0111


def process_cmd_line():
    import optparse
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

        self.tex_template = r"""
\documentclass{minimal}
\usepackage{amssymb}
\setlength\arraycolsep{10pt}
\setlength\tabcolsep{16pt}
\setlength\arrayrulewidth{.3pt}
\usepackage{xecyr}
\XeTeXdefaultencoding "utf-8"
\XeTeXinputencoding "utf-8"
\defaultfontfeatures{Mapping=tex-text}
\setmonofont{Consolas}
\usepackage{color}
\usepackage{fancyvrb}
\usepackage[russian,english]{babel} 
\begin{document}
%(tex)s
\end{document}
"""
        self.lines = []
        frame = sys._getframe(0)
        # print(frame.f_code.co_filename)
        while frame.f_back:
            # print(frame.f_code.co_filename)
            frame = frame.f_back
            if not frame.f_back or 'debugpy' in frame.f_back.f_code.co_filename:
                break
        myfilename = frame.f_code.co_filename  # pylint: disable=W0212
        mypath, mynameext = os.path.split(myfilename)
        self.basename = os.path.splitext(mynameext)[0]
        self.objdir = os.path.join(mypath, "--obj", mynameext + ".obj")
        if not os.path.exists(self.objdir):
            # ut.createdir(self.objdir)
            os.makedirs(self.objdir, exist_ok=True)
        self.prefix = os.path.join(self.objdir, "")
        self.dotprefix = os.path.join(self.objdir, "dot")
        self.svgprefix = os.path.join(self.objdir, "svg")
        self.texprefix = os.path.join(self.objdir, "tex")

        self.options, args, parser = process_cmd_line()  # pylint: disable=W0612

        if self.options.outputfile:
            sys.stdout = open(self.options.outputfile, "w")

        self.experiment_scale = 10
        self.experiment_trycount = 2
        self.debug_mode = True
        self.sprite_count = 1
        self.random_source = random.Random(time.time())

    def add_line(self, line):
        self.lines.append(line)

    def print_lines_to_tex(self):
        tex = "\n".join(self.lines)
        texdoc = self.tex_template % {'tex': tex}
        filename = self.texprefix + ".tex"
        # ut.string2file(texdoc, filename)
        with open(filename, 'w', encoding='utf-8') as lf:
            lf.write(texdoc)

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
                # ut.string2file(graph_str, graphname)
                with open(graphname, 'w', encoding='utf-8') as lf:
                    lf.write(graph_str)

                tex_str = r"""
              \begin{frame}
              \frametitle{%(frametitle)s}
              \begin{center}
              \localPDF[height=0.9\paperheight, width=.95\paperwidth, keepaspectratio]{--obj/dot%(prefix)s-%(frame)02d.%(ext)s.obj/--obj/obj.svg.obj/--obj/obj}
              \end{center}
              \end{frame}
              """ % vars()
                self.print_tex(tex_str)

        graphname = self.dotprefix+'-last.%s' % ext
        with open(graphname, 'w', encoding='utf-8') as lf:
            lf.write(graph_str)
        # ut.string2file(graph_str, graphname)
