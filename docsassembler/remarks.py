# -*- coding: utf-8 -*-
"""
Функциональность сбора заметок из LateX-файлов.
"""
import os
import os.path
import re
from copy import copy

class RemarksInLatex:
    """
    Класс присоединяется к проектной БД,
    и при запуске обработки загружает туда заметки из заданного файла.
    """
    def __init__(self, project_db):
        self.project_db = project_db
        self.remark_re = re.compile(
            ''.join([r"(?ms)^\\begin{(?P<type>remark)}",
                     r"(\\label{(?P<label>.*?)})(?P<remark>.+?)",
                     r"\\end{(?P=type)}"]))
        self.owner_re = re.compile(r"\\owner{(?P<owner>.*?)}")
      
    def collect_remarks(self, abspath, contents):
        """
            Сбор и сохранение в проектной БД заметок из заданного файла.
            Подается имя файла и содержание.
        """
        if os.path.splitext(abspath)[1] == ".tex" and abspath.find("--obj") < 0:  
            if not "remarks" in self.project_db:
                self.project_db["remarks"] = {}
                remarks = self.project_db["remarks"]
                remarks[abspath] = []
            for remark in self.remark_re.finditer(contents):
                rem = {"owner": "No"}  
                rem["text"] = self.owner_re.sub("",
                                remark.group('remark')).replace("\r","")
                rem["label"] = remark.group('label')
                for own in self.owner_re.finditer(remark.group('remark')):
                    rem["owner"] = own.group("owner").upper()
                remarks[abspath].append(copy(rem))  


