# -*- coding: utf-8 -*-
"""
 Общие процедуры-утилиты для модуля docstruct
"""
import os

# pylint: disable=W0612
# :W0612: *Unused variable %r*
#   Used when a variable is defined but not used.
# pylint: disable=W0613
# :W0613: *Unused argument %r*
#   Used when a function or method argument is not used.
# pylint: disable=W0703
# :W0703: *Catch "Exception"*
#   Used when an except catches Exception instances.


def silent_create_tmp_dir(dirpath):
    """
    Тихо создает каталог, при необходимости создает родительские каталоги.
    На все создаваемые каталоги пытается выставить атрибут скрытых файлов.
    """
    if not os.path.exists(dirpath):
        try:
            os.mkdir(dirpath)
        except Exception, e:
            (path, d) = os.path.split(dirpath)
            if d != "":
                silent_create_tmp_dir(path)
                os.mkdir(dirpath)
            hide_path(dirpath)      

def hide_path(path):
    """
    Делает путь скрытым.
    """
    try:
        from win32api import SetFileAttributes
        from win32con import FILE_ATTRIBUTE_HIDDEN
        SetFileAttributes(path, FILE_ATTRIBUTE_HIDDEN)
    except Exception, e:
        pass


def get_target(source, newname):
    """
    Вычисление пути для некоторого производного файла
    от текущего.
    Для файла ``ZZZZZ.YYY``, порождаемого от файла ``AAAAA.BBB``,
    будет 
    AAAAA.BBB  -> ./--obj/AAAAA.BBB.obj/ZZZZZ.YYY
    >>> get_target("aaa.yyy", "bbb.xxx")
    '--obj\\\\aaa.yyy.obj\\\\bbb.xxx'
    """
    (path, nameext) = os.path.split(source)
    (name, ext) = os.path.splitext(nameext)
    (dummy, newext) = os.path.splitext(newname)
    #here = (dummy == "") or (path.find("--obj") > 0)
    #if here:
    #    target = os.path.join(path, name+newext)
    #else:
    target = os.path.join(path, "--obj", nameext + ".obj", newname)
    return target

def utf8anyway(astr):
    """
     Try to guess input encoding and decode input "bytes"-string to utf8 string.
    """
    str_ = astr
    if type(str_) == type(""):
        for encoding in "utf-8", "windows-1251":
            try:
                str_ = unicode(astr.decode(encoding))
                break
            except UnicodeDecodeError:
                pass
    return str_.encode("utf-8")

def unicode_anyway(astr):
    """
     Try to guess input encoding and decode input "bytes"-string to unicode string.
    """
    str_ = astr
    if type(str_) == type(""):
        for encoding in "utf-8", "windows-1251":
            try:
                str_ = unicode(astr.decode(encoding))
                break
            except UnicodeDecodeError:
                pass
    return str_


def log_in_out(fn):
    from itertools import chain
    def wrapped(*v, **k):
        def myrepr(aval):
            import SCons.Node.FS
            if type(aval) == SCons.Node.FS.File:
                return aval.abspath
            if type(aval) == type([]):
                return "".join(["[", ", ".join([myrepr(vv) for vv in aval]) ,"]"])
            return str(aval)
        name = fn.__name__
        if name == "wrapped":
            pass
        print "--> %s(%s)" % (name, ", ".join(map(myrepr, chain(v, k.values()))))
        res = fn(*v, **k)
        print "<-- %s ..." % (name)
        return res
    if 1: #__debug__:
        return wrapped
    return fn   

def file2string(filepath):
    """
    Считать файл и вернуть его содержимое одной строкой
    """
    lfile = open(filepath, "r")
    lstr = lfile.read()
    lfile.close()
    return lstr


if __name__ == "__main__":
    import doctest
    #doctest.testmod()
    doctest.testmod(verbose=True)

