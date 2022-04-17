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
CYRA|�
cyra|�
CYRB|�
cyrb|�
CYRV|�
cyrv|�
CYRG|�
cyrg|�
CYRD|�
cyrd|�
CYRE|�
cyre|�
CYRYO|�
cyryo|�
CYRZH|�
cyrzh|�
CYRZ|�
cyrz|�
CYRI|�
cyri|�
CYRISHRT|�
cyrishrt|�
CYRK|�
cyrk|�
CYRL|�
cyrl|�
CYRM|�
cyrm|�
CYRN|�
cyrn|�
CYRO|�
cyro|�
CYRP|�
cyrp|�
CYRR|�
cyrr|�
CYRS|�
cyrs|�
CYRT|�
cyrt|�
CYRU|�
cyru|�
CYRF|�
cyrf|�
CYRH|�
cyrh|�
CYRC|�
cyrc|�
CYRCH|�
cyrch|�
CYRSH|�
cyrsh|�
CYRSHCH|�
cyrshch|�
CYRERY|�
cyrery|�
CYREREV|�
cyrerev|�
CYRYU|�
cyryu|�
CYRYA|�
cyrya|�
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
    print("**************", fname)
    (path, nameext) = os.path.split(fname)
    (name, ext) = os.path.splitext(nameext)
    pathname = os.path.join(path, name)
    curdir = os.getcwd()
    os.chdir(os.path.join(path, '--obj'))
    
    idxname = os.path.join(path, '--obj', name + ".idx")
    if not os.path.exists(idxname):
        return
    lf = open(idxname, 'r', encoding="utf-8")  	
    idxtext = lf.read( )
    lf.close()
    
    repl_dict = get_replacement_dict()
    for what in repl_dict:
        to = repl_dict[what]
        idxtext = idxtext.replace(what, to)    

    ilgname = name + ".ilg"
    scmd = "".join( [ os.path.join(env.project_db['paths']['tex'], 'makeindex'),
                    '  -t "',  ilgname, '" < "', idxname, '"'])

    indtext = ''
    try:
        import subprocess
        indtext = subprocess.check_output(scmd, shell=True).decode("utf8")
    except:
        pass    

    # progin, progout = os.popen2(cmd)
    #progin.write(idxtext)
    #progin.close()
    # indtext = progout.read()
    indname  = os.path.join(path, '--obj', name + ".ind")
    tr = r"\begin{theindex}\addcontentsline{toc}{chapter}{\TheIndexName}"
    indtext = indtext.replace(r"\begin{theindex}", tr)     

    lf = open(indname, 'w', encoding="utf-8")  	
    lf.write(indtext)
    lf.close()
    os.chdir(curdir)
    
if __name__ == '__main__':
    FILENAME = sys.argv[1]
    sys.exit(not makeindex(FILENAME))





