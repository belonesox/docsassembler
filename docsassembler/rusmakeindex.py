# -*- coding: utf-8 -*-
# $Id: rusmakeindex.py,v 1.3 2007/12/23 20:43:51 StasFomin Exp $
"""
Special hacked makeindex for russian latex
"""

import sys
import os

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

def get_replacement_dict():
    """
    returns translieration dictionary
    """
    replacements = """
CYRA|À
cyra|à
CYRB|Á
cyrb|á
CYRV|Â
cyrv|â
CYRG|Ã
cyrg|ã
CYRD|Ä
cyrd|ä
CYRE|Å
cyre|å
CYRYO|¨
cyryo|¸
CYRZH|Æ
cyrzh|æ
CYRZ|Ç
cyrz|ç
CYRI|È
cyri|è
CYRISHRT|É
cyrishrt|é
CYRK|Ê
cyrk|ê
CYRL|Ë
cyrl|ë
CYRM|Ì
cyrm|ì
CYRN|Í
cyrn|í
CYRO|Î
cyro|î
CYRP|Ï
cyrp|ï
CYRR|Ð
cyrr|ð
CYRS|Ñ
cyrs|ñ
CYRT|Ò
cyrt|ò
CYRU|Ó
cyru|ó
CYRF|Ô
cyrf|ô
CYRH|Õ
cyrh|õ
CYRC|Ö
cyrc|ö
CYRCH|×
cyrch|÷
CYRSH|Ø
cyrsh|ø
CYRSHCH|Ù
cyrshch|ù
CYRERY|Û
cyrery|û
CYREREV|Ý
cyrerev|ý
CYRYU|Þ
cyryu|þ
CYRYA|ß
cyrya|ÿ
"""
    repl_list = replacements.split("\n")[1:-1]
    repl_dict = {}
    for f in repl_list:
        (key, repl) = f.split("|")
        expression = r"\IeC {\%s }" % key
        repl_dict[expression] = repl
    return repl_dict    

def makeindex(env, fname):
    """
    Hack
    """
    print "**************", fname
    (path, nameext) = os.path.split(fname)
    (name, ext) = os.path.splitext(nameext)
    pathname = os.path.join(path, name)
    curdir = os.getcwd()
    os.chdir(os.path.join(path, '--obj'))
    
    idxname = os.path.join(path, '--obj', name + ".idx")
    if not os.path.exists(idxname):
        return
    lf = open(idxname, 'r')  	
    idxtext = lf.read( )
    lf.close()
    
    repl_dict = get_replacement_dict()
    for what in repl_dict:
        to = repl_dict[what]
        idxtext = idxtext.replace(what, to)    

    ilgname = name + ".ilg"
    cmd = "".join( [ os.path.join(env.project_db['paths']['tex'], 'makeindex'),
                    '  -t "',  ilgname, '" < "', idxname, '"'])
    progin, progout = os.popen2(cmd)
    #progin.write(idxtext)
    #progin.close()
    indtext = progout.read()
    indname  = os.path.join(path, '--obj', name + ".ind")
    tr = r"\begin{theindex}\addcontentsline{toc}{chapter}{\TheIndexName}"
    indtext = indtext.replace(r"\begin{theindex}", tr)     

    lf = open(indname, 'w')  	
    lf.write(indtext)
    lf.close()
    os.chdir(curdir)
    
if __name__ == '__main__':
    FILENAME = sys.argv[1]
    sys.exit(not makeindex(FILENAME))





