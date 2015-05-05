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
from    lxml import etree
import  lib
import tempfile
import shutil
import belonesox_tools.MiscUtils as ut
import messagefilter as mf

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


def dot2pdf(env, target, source):
    """
    Translate DOT files to PDF
    """
    dot2pdf_generic(env, target, source)

def neato2pdf(env, target, source):
    """
    Translate NEATO files to PDF
    """
    dot2pdf_generic(env, target, source)

def fdp2pdf(env, target, source):
    """
    Translate FDP files to PDF
    """
    dot2pdf_generic(env, target, source)

def circo2pdf(env, target, source):
    """
    Translate CIRCO files to PDF
    """
    dot2pdf_generic(env, target, source)

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

def dot2svg(env, target, source):
    """
    Translate DOT files to SVG
    """
    dot2svg_generic(env, target, source)

def neato2svg(env, target, source):
    """
    Translate NEATO files to SVG
    """
    dot2svg_generic(env, target, source)

def fdp2svg(env, target, source):
    """
    Translate FDP files to SVG
    """
    dot2svg_generic(env, target, source)

def circo2svg(env, target, source):
    """
    Translate CIRCO files to SVG
    """
    dot2svg_generic(env, target, source)

def twopi2svg(env, target, source):
    """
    Translate TWOPI files to SVG
    """
    dot2svg_generic(env, target, source)

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
    command = os.path.join(env.project_db['paths']['tex'],
        'xelatex -interaction nonstopmode "%(tmptexname)s"'
        % vars())
    curdir = os.getcwd()
    os.chdir(tempfile.gettempdir())
    
    cutefilter = mf.CuteFilter(tempfile.gettempdir())
    out= "Mock:" + command
    out = ut.get_prog_output(command)
    out = cutefilter(out)
    #print out.encode("utf8")
    os.system(command)

    print os.environ['PATH']
    print "!!", command
    command = os.path.join(env.project_db['paths']['tex'],
        "".join(['pdfcrop "', tmppdfname, '" "', target[0].abspath, '"']))
    os.system(command)
    os.chdir(curdir)



def preprocess_svg(sourcefile):
    """
    Preprocess possible composite SVG file,
    for all nodes with label like "xxx.svg"
    include "xxx.svg" instead of the node.
    """
    lf = open(sourcefile)   
    doc = etree.parse(lf)
    lf.close()
    root = doc.getroot() 
    for element in root.iterfind(".//{http://www.w3.org/2000/svg}g"):
        if "{http://www.inkscape.org/namespaces/inkscape}label" in element.attrib:
            label = element.get("{http://www.inkscape.org/namespaces/inkscape}label").strip()
            if label.endswith(".svg"):
                includedsvg = os.path.realpath(os.path.join(os.path.split(sourcefile)[0], label))
                if os.path.exists(includedsvg):
                    ls = preprocess_svg(includedsvg)
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
    return etree.tostring(root, pretty_print = True)    

def svg2pdf(target, source, env):
    """
    Translate SVG files to PDF
    """
    (pathname, ext) = os.path.splitext(target[0].abspath)
    assert(ext in [".pdf"])
    preprocessedname = source[0].abspath
    ls = preprocess_svg(source[0].abspath)
    preprocessedname = os.path.join(os.path.split(source[0].abspath)[0],
                                    os.path.split(source[0].abspath)[1] + ".obj")
    if os.path.exists(preprocessedname):
        os.unlink(preprocessedname)
    lf = open(preprocessedname,"w")   
    lf.write(ls)
    lf.close()
    lib.hide_path(preprocessedname)
    inkpath=env.project_db['paths']['inkscape']
    command = os.path.join(inkpath,
                ''.join(['inkscape --without-gui --export-area-drawing ',
                       ' --export-background-opacity=0 --export-pdf="%s.pdf" ',
                       ' --export-text-to-path "%s"']) % (pathname, preprocessedname) )
    os.system(command)

