# -*- coding: utf-8 -*-
"""
SCons-фреймворк по большей части 
процедурный, а не ООП,
и единственное, доступное почти всем функциям
при сборке и анализе
 — это Environment.
 
Так что мы переопределяем этот объект, снабжая его 
персистент-хешом. 
"""
import platform
import os
import re

from .projectdb import ProjectDB
from .mydepends import MetaAnalyzer
from .dependency_analyzer import DependencyAnalyzer
from .scanners import DocScanner 

from SCons.Script import Environment, Scanner

class DocstructEnvironment(Environment):
    """
    Умный Environment, хранящий настройки проекта.
    """
    def __init__(self, tools_path, **params):
        self.project_path = os.getcwd().replace('\\', '/')
        self.Decider('MD5-timestamp')
        self.deps_analyzer = DependencyAnalyzer()
        project_db = ProjectDB("--obj/project.pickle")
        
        project_db['paths'] = {
            'graphviz' : '',
            'python' : '',
            'inkscape' : '',
            'tex' : '',
            'gs' : ''
        }
        if platform.system() != 'Linux':
            project_db['paths']['graphviz']   = os.path.join(tools_path, "graphviz", "bin") 
            project_db['paths']['python']   = os.path.join(tools_path, "python27") 
            project_db['paths']['inkscape'] = os.path.join(tools_path, "inkscape") 
            project_db['paths']['tex'] = os.path.join(tools_path, r"xetex\bin\win32")
            project_db['paths']['gs'] = os.path.join(tools_path, r"xetex\tlpkg\tlgs\bin")
            os.environ['PATH'] = ';'.join([project_db['paths']['python'],
                                            project_db['paths']['tex'],
                                            project_db['paths']['gs'],
                                            os.environ['PATH'] ])

        self.project_db = project_db
        Environment.__init__(self, **params)
        self['ENV']['PATH'] = os.environ['PATH']

        self.project_db["include_commands"] = [
            {
                'regexp': r'\n[^%]*?\\(include|input|localInclude){(?P<relfile>[^#}]+)}',
                'file':   '%(relfile)s',
                'allowed_exts':   ['.pgf'],
                'ext':   '.tex'
            },
            {
                'regexp': r'\n[^%]*?\\(verbatiminput){(?P<relfile>[^#}]+)}',
                'file':   '%(relfile)s',
                'ext':   ''
            },
            {
                'regexp': r'\n[^%]*?\\(includeOnce){(?P<relfile>[^#}]+)}',
                'file':   r'\projectpath/%(relfile)s',
                'ext':    '.tex'
            },
            {
                'regexp': r'(?s)\n[^%]*?\\(localPDF)(\[[^\[]*\])?{(?P<relfile>[^#}]+)}',
                'file':   r'',
                'ext':    '.pdf'
            },
            {
                'regexp': r'\n[^%]*?\\(localSVG)(\[.*\])?{(?P<dir>[^#}]+)}{(?P<relfile>[^#}]+)}',
                'file':   r'%(dir)s/--obj/%(relfile)s.svg.obj/obj.pdf',
                'ext':    ''
            },  
            {
                'regexp': r'\n[^%]*?\\(projectSVG)(\[.*\])?{(?P<dir>[^#}]+)}{(?P<relfile>[^#}]+)}',
                'file':   r'\projectpath/%(dir)s/--obj/%(relfile)s.svg.obj/obj.pdf',
                'ext':    ''
            }  
        ]    

        for item in self.project_db["include_commands"]:
            if "re" not in item:
                item["re"] = re.compile(item['regexp'])

        self.executors = {}

        self.meta_analyzer = MetaAnalyzer(self)
        metascan = Scanner(function = self.meta_analyzer.meta_scan,
                                skeys = ['.meta'],
                                recursive = 0)

        self.Append(SCANNERS = metascan)

        depsscan = Scanner(function = self.meta_analyzer.deps_scan,
                                skeys = ['.deps'],
                                recursive = 0)

        self.Append(SCANNERS = depsscan)

        ds = DocScanner(self)
        mdscan = Scanner(function = ds.md_scan, skeys=['.md'], recursive=True)
        self.Append(SCANNERS = mdscan )

        #texscan = Scanner(function = ds.tex_scan, skeys = ['.tex'], recursive = 0)
        #self.Append(SCANNERS = texscan )
        
        #svgscan = Scanner(function = ds.svg_scan, skeys = ['.svg'], recursive = 1)
        #self.Append(SCANNERS = svgscan )
        
        self.warnings = []
        
    def __repr__(self):
        return "ENV"
        
