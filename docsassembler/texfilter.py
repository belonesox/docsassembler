# -*- coding: utf-8 -*-
"""
 Модуль функций-преобразователей для SCONS.
 Свойства проекта и прочие globals передаются через Environment
"""
import os
import re

import belonesox_tools.MiscUtils as ut

class TeXFilter:
    """
       Фильтрация и облагораживание TeX-сообщений.     
    """
    # pylint: disable=R0903
    def __init__(self, basepath):
        restr = ''.join([
                r'(?ms)', 
                r'(?P<file>[^\n]+?):(?P<line>\d+?):(?P<message>[^\n]+)',
                r'|(?P<dummy>[^\n]+)'
            ])
        self.output_re = re.compile(restr)
        self.path = basepath
        
    def __call__(self, tex_output):
        outputlines = []
        for match in self.output_re.finditer(tex_output):
            groups = match.groupdict()
            if groups['dummy']:
                dummy = ut.unicodeanyway(groups['dummy'])
                outputlines.append(u"~~ " + dummy )
            else:
                realpath = os.path.abspath(os.path.join(self.path, groups['file']))
                outputlines += [u"--->!!---> " + ':'.join([realpath,
                                                  groups['line'],
                                                  groups['message']
                                                  ])]
        return '\n'.join(outputlines)


