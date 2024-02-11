# -*- coding: utf-8 -*-
"""
 Translation procedures.
 Name pattern «ext1»2«ext2»
 Where
 * «ext1» — source file extension
 * «ext2» — target file extension
"""
import  os
# import belonesox_tools.MiscUtils as ut
from .transformation import Transformation
from .lib import get_target

from .actions import python_run, pdfbeamlatex
from .transformation import Transformation
import copy

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
class MetaAnalyzer:
    def __init__(self, env):
        self.META_FILE = 'obj.meta'
        self.DEPS_FILE = 'obj.deps'
        self.env = env

    def deps_scan(self, node, env, path):
        """
        «Сканируем» deps-файл, возвращаем зависимости.
        """
        # pylint: disable=R0201
        contents = node.get_text_contents().replace('\r','')
        deps = []
        if contents:
            deps = contents.split('\n')
        metapath = os.path.join(os.path.split(node.abspath)[0], self.META_FILE)
        for dep in copy.copy(deps):    
            deps += self.analyze_dep(dep, env)
            ext = os.path.splitext(dep)[1]
            if ext in ['.tex']:
                meta        = get_target(dep, self.META_FILE )
                cmd = env.Command(meta, dep, self.extract_meta)   
                deps.append(meta)
    
                fulldep     = get_target(dep, self.DEPS_FILE)
                cmd = env.Command(fulldep, meta, self.meta2deps)
                deps.append(fulldep.strip())
            
        deps.append(metapath)
        
        #deps.append(r'C:\app\docstruct\xetex\texmf-dist\tex\latex\docstruct\docstruct.sty')

        #paths = node.abspath.split(os.path.sep)
        #texname = paths[-2].split('.')[0]
        #auxname = '..\\'+texname+'.aux'
        #deps.append(auxname)
        return deps
    
    def analyze_dep(self, dep, env):
        """
          Analyze filename, and register all dependency of stack.
        """
        deps = []
        dep = dep.replace("'","").replace('"',"").strip()
        files = env.deps_analyzer.get_all_files(dep)
        cmd = None
        if len(files) > 1:
            for i in range(1, len(files)):
                master = files[i-1]
                slave  = files[i]
                ext_slave  = os.path.splitext(slave)[1]
                ext_master = os.path.splitext(master)[1]
                #if i == 1:
                #    if not os.path.exists(master) and ext_master == ".svg":
                #        master = os.path.join(os.getcwd(), "inc/stubs/stub.svg")
      
                if ext_master == ".py":
                    if master not in env.executors:
                        cmd = env.Command(slave, master, python_run)
                        env.executors[master] = cmd.data[0].executor
                    else:
                        en = env.fs.Entry(slave)
                        env.executors[master].batches[0].targets.append(en)
                        en.executor = env.executors[master]
                else:
                    pluginname = ext_master[1:] + "2" + ext_slave[1:]
                    if hasattr(Transformation, pluginname):
                        cmd = env.Command(slave, master, getattr(Transformation, pluginname))
        
                #if cmd: 
                #    deps.append(cmd)
                #else:
        #deps.append(dep)
        return files

    def meta_scan(self, node, env, path):
        """
        «Сканируем» meta-файл, возвращаем зависимости.
        """
        # pylint: disable=R0201
        contents = node.get_text_contents().replace('\r','')
        deps = []
        if contents:
            deps = contents.split('\n')
        mydepses = []
        for dep in deps:
            dep = dep.strip()
            mydepses += self.analyze_dep(dep, env)
            ext = os.path.splitext(dep)[1]
            if ext in ['.tex']:
                meta        = get_target(dep, self.META_FILE )
                cmd = env.Command(meta, dep, self.extract_meta)   
                mydepses.append(meta)
    
                fulldep     = get_target(dep, self.DEPS_FILE)
                cmd = env.Command(fulldep, meta, self.meta2deps)
                mydepses.append(fulldep.strip())
    
        return mydepses

    def extract_meta(self, target, source, env):
        if os.path.splitext(source[0].abspath)[1] == ".tex":
            return self.extract_tex(target, source, env)
        return self.dummy(target, source, env)

    def dummy(self, target, source, env):
        with open(target[0].abspath, 'w', encoding='utf-8') as lf:
            lf.write("")
        
    def extract_tex(self, target, source, env):
        """
        Сканирование TEX-файла, в поиске зависимостей и всяких полезностей.
        """
        deps = []
        node = source[0]
   
        def relativizefile(relfile):
            """
            return absolute path to file
            """
            newrelfile = relfile.replace(r"\finkdir", path)
            newrelfile = newrelfile.replace(r"\projectpath", env.project_path)
            if os.path.commonprefix([newrelfile, env.project_path]) == "":
                newrelfile = os.path.join(path, newrelfile)
            return newrelfile
    
        contents = node.get_text_contents()
        path, filename = os.path.split(node.abspath)
    
        for rule in env.project_db["include_commands"]:
            formatrule = rule["file"]
            wantedext = ""
            if "ext" in rule:
                wantedext = rule["ext"]
            re_ = rule["re"]
    
            if formatrule == "":
                formatrule = r"%(relfile)s"
    
            for include in re_.finditer(contents):
                g = {
                    'projectpath': env.project_path,
                    'currentfilename': filename,
                    'currentpath': path,
                    'currentfile': filename,
                }
                idx = re_.groupindex.keys()
                for symname in idx:
                    g[symname] = include.group(symname)
                relfile = formatrule % g
        
                if os.path.splitext(relfile)[1] != wantedext:
                    relfile += wantedext
        
                relfile = relativizefile(relfile)
                relfile = os.path.realpath(relfile)
                deps.append(relfile)
    
        strdeps = []
        for dep in deps:
            if type(dep) == type(""):
                strdeps.append(dep)
            else:
                for node in dep:
                    strdeps.append(node.abspath)
        mystr = '\n'.join(strdeps)
        with open(target[0].abspath, 'w', encoding='utf-8') as lf:
            lf.write(mystr)

    def meta2deps(self, target, source, env):
        strs = []
        for src in source:
            srcstr = src.get_text_contents().replace('\r','')
            strs.append(srcstr.strip())
            srcstrs = srcstr.split('\n')
            for str in srcstrs:
                depsfile = get_target(str, self.DEPS_FILE)
                if os.path.exists(depsfile):
                    depsfilestr = open(depsfile, 'r', encoding='utf-8').read().strip()
                    if depsfilestr: 
                        strs.append(depsfilestr)
        mystr = '\n'.join(strs)
        with open(target[0].abspath, 'w', encoding='utf-8') as lf:
            lf.write(mystr)


    def register_pdf(self, filename):
        if os.path.sep not in filename:
            filename = os.path.join(self.env.GetLaunchDir(), filename)
        pathname = os.path.splitext(os.path.abspath(filename))[0]
        path, name = os.path.split(pathname)
        target = os.path.realpath(pathname + ".pdf")
        source = os.path.realpath(pathname + ".tex")
        metafile   = get_target(source, self.META_FILE)
        depsfile   = get_target(source, self.DEPS_FILE)
        cmd = self.env.Command(depsfile, metafile, self.meta2deps)
        cmd = self.env.Command(metafile, source, self.extract_meta)   
        cmd = self.env.Command(target, [source, depsfile], pdfbeamlatex)
        auxfile    = os.path.join(path, '--obj', name + '.aux')
        if not os.path.exists(auxfile):
            os.makedirs(os.path.split(auxfile)[0], exist_ok=True)
            # ut.createdir(os.path.split(auxfile)[0])
            with open(auxfile, 'w', encoding='utf-8') as lf:
                lf.write("")
        self.env.Depends(cmd, auxfile)
        self.env.Precious(target)    
            
    def register_html(self, filename):
        if os.path.sep not in filename:
            filename = os.path.join(self.env.GetLaunchDir(), filename)
        pathname = os.path.splitext(os.path.abspath(filename))[0]
        path, name = os.path.split(pathname)
        target = os.path.realpath(pathname + ".html")
        source = pathname
        if pathname.lower().endswith('readme.md') or 'slides.md' in pathname:
            cmd = self.env.Command(target, [source], Transformation.md2html)
            self.env.Precious(target)    
