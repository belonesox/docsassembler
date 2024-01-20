# -*- coding: utf-8 -*-
"""
 Translation procedures.
 Name pattern «ext1»2«ext2»
 Where
 * «ext1» — source file extension
 * «ext2» — target file extension
"""
import  os
import sys
import tempfile
import shutil
import subprocess
# import belonesox_tools.MiscUtils as ut

from  lxml import etree
from  .messagefilter import CuteFilter
from .lib import hide_path
from pathlib import Path

# pylint: disable-msg=W0612
# :W0612: *Unused variable %r*
#   Used when a variable is defined but not used.
# pylint: disable-msg=W0613
# :W0613: *Unused argument %r*
#   Used when a function or method argument is not used.
# pylint: disable-msg=W0703
# :W0703: *Catch "Exception"*
#   Used when an except catches Exception instances.
# pylint: disable-msg=W0233
# :W0233: *__init__ method from a non direct base class %r is called*
#   Used when an __init__ method is called on a class which is not in the direct

def set_texinput():
    path_to_style_dir = Path(__file__).parent / 'latex'
    old_texpinputs = ''
    if 'TEXINPUTS' in os.environ:
        old_texpinputs = os.environ['TEXINPUTS']
    os.environ['TEXINPUTS'] = ':'.join([old_texpinputs, path_to_style_dir.as_posix()])


class Transformation:

    @staticmethod
    def dot2pdf_generic(env, target, source):
        """
            .DOT —> .PDF
        """  
        dot = "dot"
        if os.path.splitext(source[0].abspath)[1] == ".neato":
            dot = "neato"
        if os.path.splitext(source[0].abspath)[1] == ".fdp":
            dot = "fdp"
        if os.path.splitext(source[0].abspath)[1] == ".circo":
            dot = "circo"
        src = source[0].abspath
        tmp = target[0].abspath + ".svg"
        (pathname, ext) = os.path.splitext(target[0].abspath)

        dot = os.path.join(env.project_db['paths']['graphviz'], dot)
        os.system('%(dot)s -Tsvg %(src)s -Gbgcolor=transparent -Gmargin=0 -o %(tmp)s' % vars())
        tgt = target[0].abspath
        inkscapepath = os.path.join(env.project_db['paths']['inkscape'], 'inkscape')
        command = ''.join([inkscapepath, ' --without-gui --export-area-drawing ',
                        ' --export-background-opacity=0 --export-pdf="%s.pdf" ',
                        ' --export-text-to-path "%s"']) % (pathname, tmp)
        os.system(command)


    @staticmethod
    def dot2pdf(env, target, source):
        """
        Translate DOT files to PDF
        """
        Transformation.dot2pdf_generic(env, target, source)

    @staticmethod
    def neato2pdf(env, target, source):
        """
        Translate NEATO files to PDF
        """
        Transformation.dot2pdf_generic(env, target, source)

    @staticmethod
    def fdp2pdf(env, target, source):
        """
        Translate FDP files to PDF
        """
        Transformation.dot2pdf_generic(env, target, source)

    @staticmethod
    def circo2pdf(env, target, source):
        """
        Translate CIRCO files to PDF
        """
        Transformation.dot2pdf_generic(env, target, source)

    @staticmethod
    def dot2svg_generic(env, target, source):
        """
        Translate DOT files to SVG (generic procedure)
        """
        dot = "dot"
        ext = os.path.splitext(source[0].abspath)[1]
        if ext in [".neato", ".fdp", ".circo"]:
            dot = ext[1:] 
        src = source[0].abspath
        tgt = target[0].abspath

        dot = os.path.join(env.project_db['paths']['graphviz'], dot)
        os.system('%(dot)s -Tsvg %(src)s -Gbgcolor=transparent -Gmargin=0 -o %(tgt)s' % vars())

    @staticmethod
    def dot2svg(env, target, source):
        """
        Translate DOT files to SVG
        """
        Transformation.dot2svg_generic(env, target, source)

    @staticmethod
    def neato2svg(env, target, source):
        """
        Translate NEATO files to SVG
        """
        Transformation.dot2svg_generic(env, target, source)

    @staticmethod
    def fdp2svg(env, target, source):
        """
        Translate FDP files to SVG
        """
        Transformation.dot2svg_generic(env, target, source)

    @staticmethod
    def circo2svg(env, target, source):
        """
        Translate CIRCO files to SVG
        """
        Transformation.dot2svg_generic(env, target, source)

    @staticmethod
    def twopi2svg(env, target, source):
        """
        Translate TWOPI files to SVG
        """
        Transformation.dot2svg_generic(env, target, source)

    @staticmethod
    def svg2eps(target, source, env):
        """
        Translate SVG files to EPS
        """
        (pathname, ext) = os.path.splitext(target[0].abspath)
        assert(ext in [".eps"])
        inkscapepath = os.path.join(env.project_db['paths']['inkscape'], 'inkscape')
        command = ''.join([inkscapepath, ' --without-gui --export-area-drawing ',
                    ' --export-background-opacity=0 --export-eps="%s.eps" ',
                    ' --export-text-to-path "%s"']) % (pathname, source[0].abspath)
        os.system(command)

    @staticmethod
    def md2tex(env, target, source):
        """
        Translate Markdown files to Tex
        """
        (pathname, ext) = os.path.splitext(target[0].abspath)
        template_path = Path(__file__).parent / 'latex/docstruct.latex' 
        assert(ext in [".tex"])
        command = ' '.join(['pandoc', '-s',  source[0].abspath, 
                            '--template', template_path.as_posix(), '-o', target[0].abspath])
        os.system(command)

    @staticmethod
    def tex2pdf(target, source, env):
        """
        Translate SVG files to EPS
        """
        (pathname, ext) = os.path.splitext(target[0].abspath)
        assert(ext in [".pdf"])
        tmpname = os.path.join(tempfile.gettempdir(), tempfile.gettempprefix())
        tmptexname = tmpname + ".tex"
        tmppdfname = tmpname + ".pdf"
        tmppcropname = tmpname + ".crop.pdf"
        shutil.copy(source[0].abspath, tmptexname)
        set_texinput()
        scmd = os.path.join(env.project_db['paths']['tex'],
            'xelatex -interaction nonstopmode "%(tmptexname)s"'
            % vars())
        curdir = os.getcwd()
        os.chdir(tempfile.gettempdir())
        
        cutefilter = CuteFilter(tempfile.gettempdir())
        out= "Mock:" + scmd
        try:
            out = subprocess.check_output(scmd, shell=True).decode("utf8")    
        except Exception as ex_:    
            print(ex_)

        out = cutefilter(out)
        try:
            os.system(scmd)
        except Exception as ex_:    
            print(ex_)

        print(os.environ['PATH'])
        print("!!", scmd)
        scmd = os.path.join(env.project_db['paths']['tex'],
            "".join(['pdfcrop "', tmppdfname, '" "', target[0].abspath, '"']))
        os.system(scmd)
        os.chdir(curdir)
        print("!tex2pdf OK!")

    @staticmethod
    def preprocess_svg(sourcefile):
        """
        Preprocess possible composite SVG file,
        for all nodes with label like "xxx.svg"
        include "xxx.svg" instead of the node.
        """
        lf = open(sourcefile, 'r', encoding='utf-8')   
        doc = etree.parse(lf)
        lf.close()
        root = doc.getroot() 
        for element in root.iterfind(".//{http://www.w3.org/2000/svg}g"):
            if "{http://www.inkscape.org/namespaces/inkscape}label" in element.attrib:
                label = element.get("{http://www.inkscape.org/namespaces/inkscape}label").strip()
                if label.endswith(".svg"):
                    includedsvg = os.path.realpath(os.path.join(os.path.split(sourcefile)[0], label))
                    if os.path.exists(includedsvg):
                        ls = Transformation.preprocess_svg(includedsvg)
                        svgroot = etree.fromstring(ls)
                        for child in element:
                            element.remove(child)
                        #if 'width' in svgroot.attrib:
                        #   del svgroot.attrib['width']
                        #if 'height' in svgroot.attrib:
                        #   del svgroot.attrib['height']
                        svgroot.attrib['width'] = r"100%"  
                        svgroot.attrib['height'] = r"100%"  
    #                 if 'viewBox' in svgroot.attrib:
    #                    del svgroot.attrib['viewBox']
                        element.append(svgroot)
        res_ =  etree.tostring(root, pretty_print=True, encoding = "unicode")    
        # res_ = res_.decode('utf-8')
        return res_


    @staticmethod
    def svg2pdf(target, source, env):
        """
        Translate SVG files to PDF
        """
        (pathname, ext) = os.path.splitext(target[0].abspath)
        assert(ext in [".pdf"])
        preprocessedname = source[0].abspath
        ls = Transformation.preprocess_svg(source[0].abspath)
        preprocessedname = os.path.join(os.path.split(source[0].abspath)[0],
                                        os.path.split(source[0].abspath)[1] + ".obj")
        if os.path.exists(preprocessedname):
            os.unlink(preprocessedname)
        lf = open(preprocessedname, "w", encoding='utf-8')   
        lf.write(ls)
        lf.close()
        hide_path(preprocessedname)
        inkpath=env.project_db['paths']['inkscape']
        command = os.path.join(inkpath,
                    ''.join(['inkscape --without-gui --export-area-drawing ',
                        ' --export-background-opacity=0 --export-pdf="%s.pdf" ',
                        ' --export-text-to-path "%s"']) % (pathname, preprocessedname) )
        os.system(command)

