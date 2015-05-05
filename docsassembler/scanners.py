# -*- coding: utf-8 -*-
"""
 Модуль сканеров зависимостей файлов
"""
import os
import actions as act
import transformation
import dependency_analyzer
from lxml import etree
import lib 

# pylint: disable=W0612
# :W0612: *Unused variable %r*
#   Used when a variable is defined but not used.
# pylint: disable=W0613
# :W0613: *Unused argument %r*
#   Used when a function or method argument is not used.
# pylint: disable=W0703
# :W0703: *Catch "Exception"*
#   Used when an except catches Exception instances.
# pylint: disable=W0233
# :W0233: *__init__ method from a non direct base class %r is called*
#   Used when an __init__ method is called on a class which is not in the direct

class DocScanner:
    """
    Сканер документов на зависимости.
    Алгоритмы (регэкспы) настраиваются для каждого проекта
    (передаются с базой проекта).
    """
    def __init__(self, env):
        self.deps_analyzer = dependency_analyzer.DependencyAnalyzer()
        self.executors = {}
        self.env = env
        env.compile()

    def __repr__(self):
        return "SCANNER"

    @lib.log_in_out
    def svg_scan(self, node, env, path):
        """
           Сканируем SVG-файл, ищем включаемые SVG-файлы
        """
        # pylint: disable=R0201
        if os.path.splitext(node.abspath)[1] != ".svg" or not os.path.exists(node.abspath):
            return []
        contents = node.get_contents()
        path, filename = os.path.split(node.abspath)
        deps = []
        root = etree.fromstring(contents)
        labelattrname = "{http://www.inkscape.org/namespaces/inkscape}label"
        for element in root.iterfind(".//{http://www.w3.org/2000/svg}g"):
            if labelattrname  in element.attrib:
                label = element.get(labelattrname).strip()
                if label.endswith(".svg"):
                    deps.append(label)
        return deps
  
    @lib.log_in_out
    def tex_scan(self, node, env, path):
        """
        Сканирование LaTeX-файла.
        """
        if os.path.splitext(node.abspath)[1] != ".tex":
            return []
        
        #print "-->!!--> tex-scan ", node.abspath

        def relativizefile(relfile):
            """
            returb absolute path to file
            """
            newrelfile = relfile.replace(r"\finkdir", path)
            newrelfile = newrelfile.replace(r"\projectpath", env.project_path)
            if os.path.commonprefix([newrelfile, env.project_path]) == "":
                newrelfile = os.path.join(path, newrelfile)
            return newrelfile
    
        @lib.log_in_out
        def process(dep):
            """
              Analyze filename, and register all dependency of stack.
            """
            dep = dep.replace("'","").replace('"',"")
            files = self.deps_analyzer.get_all_files(dep)
            if len(files) > 1:
                for i in xrange(1, len(files)):
                    master = files[i-1]
                    slave  = files[i]
                    ext_slave  = os.path.splitext(slave)[1]
                    ext_master = os.path.splitext(master)[1]
                    #if i == 1:
                    #    if not os.path.exists(master) and ext_master == ".svg":
                    #        master = os.path.join(os.getcwd(), "inc/stubs/stub.svg")
          
                    if ext_master == ".py":
                        if self.executors.get(master, None) is None:
                            cmd = env.Command(slave, master, act.python_run)
                            self.executors[master] = cmd.data[0].executor
                        else:
                            en = env.fs.Entry(slave)
                            self.executors[master].batches[0].targets.append(en)
                            en.executor = self.executors[master]
                    else:
                        pluginname = ext_master[1:] + "2" + ext_slave[1:]
                        if hasattr(transformation, pluginname):
                            env.Command(slave, master, getattr(transformation, pluginname))
      
            deps.append(dep)
    
        include_commands = env.project_db["include_commands"]
        contents = node.get_contents()
        path, filename = os.path.split(node.abspath)
    
        deps = []
        for rule in include_commands:
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
        
                if "writetofile" in rule:
                    wfilename = rule["writetofile"] % g
                    wfilename = relativizefile(wfilename)
                    lib.silent_create_tmp_dir(os.path.split(wfilename)[0])
                    content = include.group("content")
                    lf = open(wfilename,"w")
                    content = content.replace("\n%","\n")
                    if "encoding" in rule:
                        content = lib.unicode_anyway(content)
                        content = content.encode(rule["encoding"])
                    lf.write(content)
                    lf.close()
        
                if os.path.splitext(relfile)[1] != wantedext:
                    relfile += wantedext
        
                relfile = relativizefile(relfile)
                relfile = os.path.realpath(relfile)
                process(relfile)
    
        return deps
