# -*- coding: utf-8 -*-
"""
 Модуль функций-преобразователей для SCONS.
 Свойства проекта и прочие globals передаются через Environment
"""
import os
import re

# import belonesox_tools.MiscUtils as ut

class CuteFilter:
    """
       Фильтрация и облагораживание Cute-сообщений.     
    """
    # pylint: disable=R0903
    def __init__(self, basepath):
        restr = ''.join([
            r'(?ms)', 
            r'(?P<file>[^\n]+?):(?P<line>\d+?):(?P<message>[^\n]+)',
            r'|(Traceback \(most recent call last\):\n\s+',
                r'File "(?P<pyfile>.+)", ',
                r'line (?P<pyline>\d+),[^\n]+\n[^\n]+\n(?P<pymessage>[^\n]+))',
            r'|(?P<commonerror>(\*\* ERROR \*\*',
                r'|! Emergency stop',
                r'|\*\* WARNING \*\*',
                r')[^\n]+)',
            r'|(?P<dummy>[^\n]+)'
        ])
        self.output_re = re.compile(restr)
        self.path = basepath
        suppress_warnings_str = ''.join([
            r'(?ms)((.*memory objects still allocated.*)',
            r'|(.*Failed to convert input string to UTF16.*)',
            r')'
        ])
        self.suppress_warnings_re  = re.compile(suppress_warnings_str)
        self.warnings = []
        
    def __call__(self, text_output):
        reg = r''.join([
                r'(?P<block>(?P<prefix>[:/\\A-Z\w\d\.-]*?)[/\\]--obj[/\\]',
                    r'(?P<mastername>[A-Z\d\w\.-]+)\.obj)'
                    ])
        chainre = re.compile(reg)
        
        def formatwarning(filename, line, message):
            marker = "--->!!---> "
            warning =  marker + ':'.join([filename, line, message])

            prefix = ""
            for m in chainre.finditer(filename):
                f = os.path.join(prefix, m.group("prefix"), m.group("mastername"))
                warning += '\n' + marker + f + ':0: source file'
                prefix += os.path.join(prefix, m.group("block"))
            return warning     

        def formatcommonwarning(message):
            marker = "--->##---> "
            warning =  marker + message
            return warning     

        outputlines = []
        for match in self.output_re.finditer(text_output):
            groups = match.groupdict()
            if groups['dummy']:
                # dummy = ut.unicodeanyway(groups['dummy'])
                dummy = groups['dummy']
                outputlines.append("" + dummy )
            else:
                if groups['file']:
                    file_ = groups['file']
                    line_ = groups['line']
                    message_ = groups['message']
                    realpath = os.path.abspath(os.path.join(self.path, file_))
                    warning = formatwarning(realpath, line_, message_)
                if groups['pyfile']:
                    realpath  = groups['pyfile']
                    line_ = groups['pyline']
                    message_ = groups['pymessage']
                    warning = formatwarning(realpath, line_, message_)
                if groups['commonerror']:
                    commonerror = groups['commonerror']
                    warning = None
                    if self.suppress_warnings_re.match(commonerror):
                        outputlines.append("" + commonerror)
                    else:
                        warning = formatcommonwarning(commonerror)
                if warning:        
                    outputlines.append(warning)
                    self.warnings.append(warning)
        return '\n'.join(outputlines) 


