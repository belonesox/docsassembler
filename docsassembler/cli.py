"""Console script for terrarium_assembler."""
# import argparse
import sys
import os
import re
from pathlib import Path

import SCons
import SCons.Defaults
import SCons.Environment
import SCons.Errors
import SCons.Job
import SCons.Node
import SCons.Node.FS
import SCons.Platform
import SCons.Platform.virtualenv
import SCons.SConf
import SCons.Script
import SCons.Taskmaster
import SCons.Util
import SCons.Warnings
import SCons.Script.Main
import SCons.Script.Interactive
from SCons.Script import SConsOptions

from SCons.Script.Main import main as smain
from SCons.Script.Main import _SConstruct_exists, _create_path, _build_targets, revert_io, _load_all_site_scons_dirs, SetOption, _set_debug_values


display = SCons.Util.display
progress_display = SCons.Util.DisplayEngine()


def _main(parser):
    global exit_status
    global this_build_status

    options = parser.values
    
    targets_top_dir = os.getcwd()
    sconscript_dir = Path(targets_top_dir)
    scons_filename = None
    while sconscript_dir:
        scons_filename = 'SConstruct'
        if (sconscript_dir / scons_filename).exists():
            break
        scons_filename = '.sconstruct'
        if (sconscript_dir / scons_filename).exists():
            break
        if (sconscript_dir / '.git').exists():
            break

        parent_ = sconscript_dir.parent    
        if not parent_:
            break

        sconscript_dir = parent_

    if not (sconscript_dir / scons_filename).exists():
        with open((sconscript_dir / scons_filename).as_posix(), 'w') as lf:
            lf.write("""
# -*- coding: utf-8 -*-
import os
import os.path

targets = BUILD_TARGETS

import docsassembler as docs
env = docs.DocstructEnvironment(r"", ENV = os.environ )
env['ENV']['PATH'] = os.environ['PATH']

env.Decider('timestamp-match')
docs.write_project_path()

taskCleanObj = os.path.join(os.getcwd(), '--obj/cleanObj') 
cmd = env.Command(taskCleanObj, [], [docs.clean_obj])
env.Alias('clean-obj', cmd)

for filename in targets:
    if filename.endswith(".pdf"):
        env.meta_analyzer.register_pdf(filename)
            """)

    os.chdir(sconscript_dir)
    fs = SCons.Node.FS.get_default_fs()
    scripts = [scons_filename]

    _set_debug_values(options)
    SCons.SConf.SetCacheMode('auto') 
    SCons.SConf.SetProgressDisplay(progress_display)

    d = fs.File(scripts[0]).dir
    fs.set_SConstruct_dir(d)
    _load_all_site_scons_dirs(d.get_internal_path())

    targets = []
    for a in parser.largs:
        targets.append(a)
    SCons.Script._Add_Targets(targets) 

    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        sys.stdout = SCons.Util.Unbuffered(sys.stdout)
    if not hasattr(sys.stderr, 'isatty') or not sys.stderr.isatty():
        sys.stderr = SCons.Util.Unbuffered(sys.stderr)

    progress_display("scons: Reading SConscript files ...")

    try:
        for script in scripts:
            SCons.Script._SConscript._SConscript(fs, script)
    except SCons.Errors.StopError as e:
        revert_io()
        sys.stderr.write("scons: *** %s  Stop.\n" % e)
        sys.exit(2)

    progress_display("scons: done reading SConscript files.")

    SCons.Warnings.process_warn_strings(options.warn)
    parser.preserve_unknown_options = False
    parser.parse_args(parser.largs, options)

    fs.chdir(fs.Top)

    SCons.Node.FS.save_strings(1)
    SCons.Node.implicit_cache = options.implicit_cache
    SCons.Node.FS.set_duplicate(options.duplicate)
    fs.set_max_drift(1) #options.max_drift)
    SCons.Job.explicit_stack_size = options.stack_size
    SCons.Util.set_hash_format(options.hash_format)
    nodes = _build_targets(fs, options, targets, targets_top_dir)
    ...


def main():
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.argv = [sys.argv[0],  '-D'] + sys.argv[1:]
    print(sys.argv)

    # sys.exit(smain())
    # parser = SConsOptions.Parser("""SCons by Steven Knight et al.:\n\tSCons: v4.4.0, Sat, 21 Jan 2023 00:00:00 +0000, by _reproducible on _reproducible\n\tSCons path: ['/usr/lib/python3.11/site-packages/SCons']\nCopyright (c) 2001 - 2023 The SCons Foundation""")
    parser = SConsOptions.Parser("""DocsAssembler""")
    values = SConsOptions.SConsValues(parser.get_default_values())
    SCons.Script.Main.OptionsParser = parser

    options, args = parser.parse_args(sys.argv[1:], values)
    _main(parser)
    sys.exit(0)


if __name__ == '__main__':
    sys.exit(main())

