# -*- coding: utf-8 -*-
"""
 Модуль сканеров зависимостей файлов
"""
import os
import re

class DependencyAnalyzer:
    """
    Хранитель логики определения зависимостей между файлами
    """
    def __init__(self):
        reg = ''.join([r"(?P<block>",
                        r"(?P<prefix>[:/\\A-Z\w\d\.-]*?)",
                        r"[/\\]--obj[/\\]",
                        "(?P<mastername>[A-Z\d\w\.-]+)\.obj)"
                     ])
        
        self.chainre = re.compile(reg)

    def get_all_files(self, afile):
        """
        Для заданного файла возвращает и все его исходники
        """
        if afile.endswith(r'greedy.tex.obj\obj.pdf'):
            pass
        files = []
        prefix = ""
        dep = afile.replace("'","").replace('"',"").replace('\\','/')
        for m in self.chainre.finditer(dep):
            f = os.path.join(prefix, m.group("prefix"), m.group("mastername"))
            files.append(f)
            prefix += os.path.join(prefix, m.group("block"))
        files.append(dep)
        return files


