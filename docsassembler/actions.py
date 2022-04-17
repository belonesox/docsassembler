# -*- coding: utf-8 -*-
"""
 Модуль функций-преобразователей для SCONS.
 Свойства проекта и прочие globals передаются через Environment
"""
import os
import glob
import time
import subprocess
from   copy import copy
import re
import shutil
import sys
import stat
from .rusmakeindex import makeindex
import tempfile
from .messagefilter import CuteFilter
from .lib import *


# import belonesox_tools.MiscUtils as ut

#import texfilter as tx

# pylint: disable=W0612
# :W0612: *Unused variable %r*
#   Used when a variable is defined but not used.
# pylint: disable=W0613
# :W0613: *Unused argument %r*
#   Used when a function or method argument is not used.
# pylint: disable=W0703
# :W0703: *Catch "Exception"*
#   Used when an except catches Exception instances.

   
def clean_obj(target, source, env):
    """
    Жесткая очистка всех сгенерированных промежуточных («объектных») файлов.
    """
    from shutil import rmtree
    for root, dirs, files in os.walk(os.getcwd()):
        for d in dirs:
            if d == "--obj":
                filename = os.path.join(root, d)
                rmtree(filename)

def dummy(env, target, source):
    """
    Пустое действие
    """
    pass

def inkscape(target, source, env):
    """
    Перегоняем SVG в PDF
    """
    (pathname, ext) = os.path.splitext(target[0].abspath)
    assert(ext in [".pdf"])
    inkscapepath = os.path.join(env.project_db['paths']['inkscape'], 'inkscape')
    scmd = ''.join(['"', inkscapepath,
                       '" --without-gui --export-area-drawing ',
                       ' --export-background-opacity=0 --export-pdf="%s.pdf" ',
                       ' --export-text-to-path "%s"' ]) % (
                        pathname, source[0].abspath )
    print("************", scmd, '---------------')
    os.system(scmd)


def pdfbeamlatex(target, source, env):
    """
    PDFLatex-обработка для слайдов.
    """
    filename = str(source[0].abspath)
    (path, nameext) = os.path.split(filename)
    (name, ext) = os.path.splitext(nameext)
    outpdf = os.path.join(path, "--obj", name) + ".pdf"
    outpdfsync = os.path.join(path, "--obj", name) + ".synctex"
    outlog = os.path.join(path, "--obj", name) + ".log"
    pdfsync = os.path.join(path, name) + ".synctex"
    texlog = os.path.join(path, name) + ".log"
    curdir = os.getcwd()
    beamdir = path
    os.chdir(path)
    os.makedirs("--obj", exist_ok=True)
    scmd = ''.join([
        r'xelatex -synctex=-1 -file-line-error-style  -output-directory="--obj" ',
        ' -interaction nonstopmode "', nameext, '"'])
    print(os.environ["PATH"])
    print(scmd)
    #texfilter = tx.TeXFilter(path)    
    cutefilter = CuteFilter(path)
    out= "Mock:" + scmd
    try:
        out = subprocess.check_output(scmd, shell=True, stderr=subprocess.STDOUT)
    except Exception as ex_:
        out = ex_.output
        pass    
    out = cutefilter(out.decode("utf8"))
    print(out)
    env.warnings += cutefilter.warnings
    
    with open(filename + ".warnings", 'w', encoding='utf-8') as lf:
        lf.write("\n".join(env.warnings))

    outbcffile = os.path.join(path, "--obj", name) + ".bcf"
    if os.path.exists(outbcffile):
        os.chdir('--obj')
        scmd = os.path.join(env.project_db['paths']['tex'],
            'biber "%(outbcffile)s"'
            % vars())
        os.system(scmd)
        os.chdir('..')
    
    makeindex(env, filename)
    shutil.copyfile(outpdf, target[0].abspath)
    if os.path.exists(outpdfsync):
        shutil.copy(outpdfsync, pdfsync)
    if os.path.exists(outlog):
        shutil.copy(outlog, texlog)
    os.chdir(curdir)

@log_in_out
def extract_algorithms(ps_infile, env):
    """
    Вытаскиваем части кода-алгоритмы
    """
    import pygments
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import LatexFormatter
    
    algorithm_regexp = re.compile(
        r"(?ms)\#ALGORITHM\s+(?P<name>[a-zA-z-0-9]+)\s*(?P<code>.+?)\s*\#ENDALGORITHM")
    hideline_regexps = [re.compile(r"(?m)^.*\#hide *\n"), re.compile(r"(?m)\n.*\#hide *") ]
    ls = open(ps_infile, 'r', encoding='utf-8').read()
    for algorithm in algorithm_regexp.finditer(ls):
        algfilename = get_target(ps_infile, algorithm.group('name')+".py")
        texfilename = get_target(ps_infile, algorithm.group('name')+".tex")
        #lf = open(algfilename, 'w')
        code = algorithm.group('code')
        for r in hideline_regexps:
            code = re.sub(r, "", code)
        #code = lib.utf8anyway(code)    
        #lf.write(code)
        #lf.close()
        
        #tempblock = os.path.join(tempfile.gettempdir(), tempfile.gettempprefix())
        #ls = ''.join([env.project_db['paths']['python'],
        #             r'\scripts\pygmentize -f latex -l python ',
        #             ' -o "%(tempblock)s" "%(algfilename)s" ' % vars() ])
        #os.system(ls)
        
        lexer = get_lexer_by_name('python')
        latex_tokens = pygments.lex(code, lexer)
        
        latex_formatter = LatexFormatter(texcomments = True)
        latex = pygments.format(latex_tokens, latex_formatter)
        stexblock = r"""
\documentclass{minimal}
\usepackage{xecyr}
\XeTeXdefaultencoding "utf-8"
\XeTeXinputencoding "utf-8"
\defaultfontfeatures{Mapping=tex-text}
\setmonofont{Consolas}
\usepackage{color}
\usepackage{fancyvrb}
\usepackage[russian,english]{babel} 
        """ + latex_formatter.get_style_defs() + r"""
\begin{document}
        """ + latex + r"""
\end{document}
        """
        with open(texfilename, 'w', encoding='utf-8') as lf:
            lf.write(stexblock)



@log_in_out
def python_run(target, source, env):
    """
    Запуск Python-файла
    """
    filename = str(source[0].abspath)
    (path, nameext) = os.path.split(filename)
    (name, ext) = os.path.splitext(nameext)
    extract_algorithms(filename, env)
    curdir = os.getcwd()
    os.chdir(path)
    
    scmd = ''.join([env.project_db['paths']['python'],
                 '\\python "', filename, '" ',
                 '--output="', path, '/--obj/',
                 nameext, '.obj/log.out"',
                 ])
    
    cutefilter = CuteFilter(path)
    out = subprocess.check_output(scmd, shell=True).decode("utf8")    
    out = cutefilter(out)
    print(out)
    env.warnings += cutefilter.warnings
    #pattern = "%s/*" % (os.path.split(target[0].abspath)[0])
    #for f in glob.glob(pattern):
    #    if os.path.splitext(f)[1] == ".svg":
    #        svgtarget = lib.get_target(f,"svg.eps")
    #        env.Command(svgtarget, f, [inkscape])
    #    if os.path.splitext(f)[1] in [".dot", ".neato", ".fdp"]:
    #        svgfilename = lib.get_target(f,"obj.svg")
    #        env.Command(svgfilename, f, [transformation.dot2svg])
    #        epsfilename = lib.get_target(f,"obj.eps")
    #        env.Command(epsfilename, svgfilename, [inkscape])
    #        pdffilename = lib.get_target(f,"obj.pdf")
    #        env.Command(pdffilename, svgfilename, [inkscape])
    os.chdir(curdir)

def log_current_time(target, source, env):
    """
    Log current time and source files list to target
    """
    filename = str(target[0].abspath)
    lf = open(filename, "w", encoding='utf-8')
    ls = "The task completed at %s" % time.ctime()
    lf.write(ls)
    lf.write("\n List of prepared components:\n")
    for t in source:
        lf.write(t.abspath+"\t\t\t"+t.get_csig()+"\n")
    lf.close()

@log_in_out
def write_project_path():
    """
     Wrote files with info about paths
    """
    silent_create_tmp_dir("--obj")
    filename = os.path.join(os.getcwd(),"--obj/project-path")
    projectpath = os.getcwd()
    projectpath = projectpath.replace("\\","/")
    lf = open(filename, "w", encoding='utf-8')
    lf.write(projectpath)
    lf.close()

if __name__ == "__main__":
    import doctest
    #doctest.testmod()
    doctest.testmod(verbose=True)
