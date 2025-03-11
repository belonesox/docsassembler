"""Console script for terrarium_assembler."""
# import argparse
import sys
import os
import re
import shutil
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
    while len(sconscript_dir.as_posix())>2:
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

    if scons_filename is None:
        scons_filename = '.sconstruct'
        sconscript_dir = Path(targets_top_dir)

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
    if filename.endswith(".html"):
        env.meta_analyzer.register_html(filename)
    if filename.endswith(".md.tex"):
        env.meta_analyzer.register_tex(filename)
    if filename.endswith(".docx"):
        env.meta_analyzer.register_docx(filename)
    if filename.endswith(".pandoc"):
        env.meta_analyzer.register_pandoc(filename)
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


def dasws():
    for args in sys.argv:
        if args == '--version':
            sys.stdout.write('3.1.12.3') 
            return

    md_text = sys.stdin.read() 
    preview_filename = 'preview.md'
    Path(preview_filename).write_text(md_text)
    os.system(f'das {preview_filename}.html >/dev/null 2>&1')
    html_text = Path(f'{preview_filename}.html').read_text()
    html_text = html_text.replace('lang xml:lang>', '>')
    sys.stdout.write(html_text) 
    ...


def main():
    if 'systeminstall' in sys.argv:
        systeminstall()
        return

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

def systeminstall():
    packages = f'''
texlive
texlive-latex
texlive-type1cm
pandoc
graphviz
    '''

    for package in packages.strip().split('\n'):
        for prefix in 'dnf install', 'apt-get install':
            scmd = f'sudo {prefix} -y {package} || true'
            print(scmd)
            os.system(scmd)

    os.system("sudo dnf install texlive-scheme-full --exclude='texlive-*-doc*' -y ")

    docstruct_target_dir = Path('~/texmf/tex/latex/docstruct').expanduser()
    print("*"*30)
    print(docstruct_target_dir)
    print("*"*30)
    docstruct_target_dir.mkdir(parents=True, exist_ok=True)
    docstruct_sty = Path(__file__).parent / 'latex/docstruct.sty' 
    shutil.copy(docstruct_sty, docstruct_target_dir)
    ...

if __name__ == '__main__':
    sys.exit(main())

