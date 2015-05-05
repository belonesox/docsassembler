# -*- coding: utf-8 -*-
"""
Project DB — simple hash-based persistant preject database
to store state of the project between builds
or between scan phase and builds
"""

import os
import os.path
import cPickle as pickle
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

class ProjectDB(dict):
    """
    Simple hash-based persistant preject database
    to store state of the project between builds
    or between scan phase and builds
    """
    def __init__(self, dbpath):
        self.dbpath = dbpath
        if os.path.exists(self.dbpath):
            lf = open(self.dbpath, "rb")
            db = pickle.load(lf)
            if type(db) == type({}):
                dict.__init__(self, db)
            elif type(db) == type([]):
                dict.__init__(self, dict(db)) 
            lf.close()
        self.flush()
    
    def flush(self):
        """
        Запись из памяти на диск.
        
        При записи, нужно обязательно преобразовать
        словари в сортированные списки,
        иначе файл будет постоянно меняться,
        даже если словарь будет оставаться неизменным.
        """
        keys = self.keys()
        keys.sort()
        sorteddb = [(key, self[key]) for key in keys]
        lib.silent_create_tmp_dir(os.path.split(self.dbpath)[0])
        lf = open(self.dbpath, "wb")
        p = pickle.Pickler(lf)
        p.dump(sorteddb)
        lf.close() 
    
    def __del__ (self):
        try:
            self.flush()
        except Exception, e:
            pass
