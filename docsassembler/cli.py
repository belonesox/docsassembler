"""Console script for terrarium_assembler."""
# import argparse
import sys
import os
import re
import SCons
# import SCons.compat
# import SCons.CacheDir
# import SCons.Debug
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

    # Here's where everything really happens.

    # First order of business:  set up default warnings and then
    # handle the user's warning options, so that we can issue (or
    # suppress) appropriate warnings about anything that might happen,
    # as configured by the user.

    # default_warnings = [ SCons.Warnings.WarningOnByDefault,
    #                      SCons.Warnings.DeprecatedWarning,
    #                    ]

    # for warning in default_warnings:
    #     SCons.Warnings.enableWarningClass(warning)
    # SCons.Warnings._warningOut = _scons_internal_warning
    # SCons.Warnings.process_warn_strings(options.warn)

    # Now that we have the warnings configuration set up, we can actually
    # issue (or suppress) any warnings about warning-worthy things that
    # occurred while the command-line options were getting parsed.
    # try:
    #     dw = options.delayed_warnings
    # except AttributeError:
    #     pass
    # else:
    #     delayed_warnings.extend(dw)
    # for warning_type, message in delayed_warnings:
    #     SCons.Warnings.warn(warning_type, message)

    # if not SCons.Platform.virtualenv.virtualenv_enabled_by_default:
    #     if options.enable_virtualenv:
    #         SCons.Platform.virtualenv.enable_virtualenv = True

    # if options.ignore_virtualenv:
    #     SCons.Platform.virtualenv.ignore_virtualenv = True

    # if options.diskcheck:
    #     SCons.Node.FS.set_diskcheck(options.diskcheck)

    # Next, we want to create the FS object that represents the outside
    # world's file system, as that's central to a lot of initialization.
    # To do this, however, we need to be in the directory from which we
    # want to start everything, which means first handling any relevant
    # options that might cause us to chdir somewhere (-C, -D, -U, -u).
    # if options.directory:
    #     script_dir = os.path.abspath(_create_path(options.directory))
    # else:
    #     script_dir = os.getcwd()
    
    script_dir = os.getcwd()
    target_top = None
    if options.climb_up:
        target_top = '.'  # directory to prepend to targets
        while script_dir and not _SConstruct_exists(script_dir,
                                                    options.repository,
                                                    options.file):
            script_dir, last_part = os.path.split(script_dir)
            if last_part:
                target_top = os.path.join(last_part, target_top)
            else:
                script_dir = ''

    if script_dir and script_dir != os.getcwd():
        # if not options.silent:
        #     display("scons: Entering directory `%s'" % script_dir)
        try:
            os.chdir(script_dir)
        except OSError:
            sys.stderr.write("Could not change directory to %s\n" % script_dir)

    # Now that we're in the top-level SConstruct directory, go ahead
    # and initialize the FS object that represents the file system,
    # and make it the build engine default.
    fs = SCons.Node.FS.get_default_fs()

    # for rep in options.repository:
    #     fs.Repository(rep)

    # Now that we have the FS object, the next order of business is to
    # check for an SConstruct file (or other specified config file).
    # If there isn't one, we can bail before doing any more work.
    scripts = ['SConstruct']
    # if options.file:
    #     scripts.extend(options.file)
    # if not scripts:
    #     sfile = _SConstruct_exists(repositories=options.repository,
    #                                filelist=options.file)
    #     if sfile:
    #         scripts.append(sfile)

    # if not scripts:
    #     if options.help:
    #         # There's no SConstruct, but they specified -h.
    #         # Give them the options usage now, before we fail
    #         # trying to read a non-existent SConstruct file.
    #         raise SConsPrintHelpException
    #     raise SCons.Errors.UserError("No SConstruct file found.")

    # if scripts[0] == "-":
    #     d = fs.getcwd()
    # else:
    #     d = fs.File(scripts[0]).dir
    d = fs.File(scripts[0]).dir
    fs.set_SConstruct_dir(d)

    _set_debug_values(options)
    # SCons.Node.implicit_cache = options.implicit_cache
    # SCons.Node.implicit_deps_changed = options.implicit_deps_changed
    # SCons.Node.implicit_deps_unchanged = options.implicit_deps_unchanged

    # if options.no_exec:
    #     SCons.SConf.dryrun = 1
    #     SCons.Action.execute_actions = None
    # if options.question:
    #     SCons.SConf.dryrun = 1
    # if options.clean:
    #     SCons.SConf.SetBuildType('clean')
    # if options.help:
    #     SCons.SConf.SetBuildType('help')
    SCons.SConf.SetCacheMode('auto') #options.config)
    SCons.SConf.SetProgressDisplay(progress_display)

    # if options.no_progress or options.silent:
    #     progress_display.set_mode(0)

    # if site_dir unchanged from default None, neither --site-dir
    # nor --no-site-dir was seen, use SCons default
    if options.site_dir is None:
        _load_all_site_scons_dirs(d.get_internal_path())
    # elif options.site_dir:  # if a dir was set, use it
    #     _load_site_scons_dir(d.get_internal_path(), options.site_dir)

    if options.include_dir:
        sys.path = options.include_dir + sys.path

    # If we're about to start SCons in the interactive mode,
    # inform the FS about this right here. Else, the release_target_info
    # method could get called on some nodes, like the used "gcc" compiler,
    # when using the Configure methods within the SConscripts.
    # This would then cause subtle bugs, as already happened in #2971.
    if options.interactive:
        SCons.Node.interactive = True
    # That should cover (most of) the options.
    # Next, set up the variables that hold command-line arguments,
    # so the SConscript files that we read and execute have access to them.
    # TODO: for options defined via AddOption which take space-separated
    # option-args, the option-args will collect into targets here,
    # because we don't yet know to do any different.
    targets = []
    xmit_args = []
    for a in parser.largs:
        # Skip so-far unrecognized options, and empty string args
        if a.startswith('-') or a in ('', '""', "''"):
            continue
        if '=' in a:
            xmit_args.append(a)
        else:
            targets.append(a)
    SCons.Script._Add_Targets(targets + parser.rargs)
    SCons.Script._Add_Arguments(xmit_args)

    # If stdout is not a tty, replace it with a wrapper object to call flush
    # after every write.
    #
    # Tty devices automatically flush after every newline, so the replacement
    # isn't necessary.  Furthermore, if we replace sys.stdout, the readline
    # module will no longer work.  This affects the behavior during
    # --interactive mode.  --interactive should only be used when stdin and
    # stdout refer to a tty.
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        sys.stdout = SCons.Util.Unbuffered(sys.stdout)
    if not hasattr(sys.stderr, 'isatty') or not sys.stderr.isatty():
        sys.stderr = SCons.Util.Unbuffered(sys.stderr)

    # memory_stats.append('before reading SConscript files:')
    # count_stats.append(('pre-', 'read'))

    # And here's where we (finally) read the SConscript files.

    progress_display("scons: Reading SConscript files ...")

    # if print_time:
    #     start_time = time.time()
    try:
        for script in scripts:
            SCons.Script._SConscript._SConscript(fs, script)
    except SCons.Errors.StopError as e:
        # We had problems reading an SConscript file, such as it
        # couldn't be copied in to the VariantDir.  Since we're just
        # reading SConscript files and haven't started building
        # things yet, stop regardless of whether they used -i or -k
        # or anything else.
        revert_io()
        sys.stderr.write("scons: *** %s  Stop.\n" % e)
        sys.exit(2)
    # if print_time:
    #     global sconscript_time
    #     sconscript_time = time.time() - start_time

    progress_display("scons: done reading SConscript files.")

    # memory_stats.append('after reading SConscript files:')
    # count_stats.append(('post-', 'read'))

    # Re-{enable,disable} warnings in case they disabled some in
    # the SConscript file.
    #
    # We delay enabling the PythonVersionWarning class until here so that,
    # if they explicitly disabled it in either in the command line or in
    # $SCONSFLAGS, or in the SConscript file, then the search through
    # the list of deprecated warning classes will find that disabling
    # first and not issue the warning.
    #SCons.Warnings.enableWarningClass(SCons.Warnings.PythonVersionWarning)
    SCons.Warnings.process_warn_strings(options.warn)

    # Now that we've read the SConscript files, we can check for the
    # warning about deprecated Python versions--delayed until here
    # in case they disabled the warning in the SConscript files.
    # if python_version_deprecated():
    #     msg = "Support for pre-%s Python version (%s) is deprecated.\n" + \
    #           "    If this will cause hardship, contact scons-dev@scons.org"
    #     deprecated_version_string = ".".join(map(str, deprecated_python_version))
    #     SCons.Warnings.warn(SCons.Warnings.PythonVersionWarning,
    #                         msg % (deprecated_version_string, python_version_string()))

    if not options.help:
        # [ ] Clarify why we need to create Builder here at all, and
        #     why it is created in DefaultEnvironment
        # https://bitbucket.org/scons/scons/commits/d27a548aeee8ad5e67ea75c2d19a7d305f784e30
        if SCons.SConf.NeedConfigHBuilder():
            SCons.SConf.CreateConfigHBuilder(SCons.Defaults.DefaultEnvironment())

    # Now re-parse the command-line options (any to the left of a '--'
    # argument, that is) with any user-defined command-line options that
    # the SConscript files may have added to the parser object.  This will
    # emit the appropriate error message and exit if any unknown option
    # was specified on the command line.

    parser.preserve_unknown_options = False
    parser.parse_args(parser.largs, options)

    if options.help:
        help_text = SCons.Script.help_text
        if help_text is None:
            # They specified -h, but there was no Help() inside the
            # SConscript files.  Give them the options usage.
            raise SConsPrintHelpException
        else:
            print(help_text)
            print("Use scons -H for help about command-line options.")
        exit_status = 0
        return

    # Change directory to the top-level SConstruct directory, then tell
    # the Node.FS subsystem that we're all done reading the SConscript
    # files and calling Repository() and VariantDir() and changing
    # directories and the like, so it can go ahead and start memoizing
    # the string values of file system nodes.

    fs.chdir(fs.Top)

    SCons.Node.FS.save_strings(1)

    # Now that we've read the SConscripts we can set the options
    # that are SConscript settable:
    SCons.Node.implicit_cache = options.implicit_cache
    SCons.Node.FS.set_duplicate(options.duplicate)
    fs.set_max_drift(options.max_drift)

    SCons.Job.explicit_stack_size = options.stack_size

    # Hash format and chunksize are set late to support SetOption being called
    # in a SConscript or SConstruct file.
    SCons.Util.set_hash_format(options.hash_format)
    if options.md5_chunksize:
        SCons.Node.FS.File.hash_chunksize = options.md5_chunksize * 1024

    platform = SCons.Platform.platform_module()

    if options.interactive:
        SCons.Script.Interactive.interact(fs, OptionsParser, options,
                                          targets, target_top)

    else:

        # Build the targets
        nodes = _build_targets(fs, options, targets, target_top)
        if not nodes:
            revert_io()
            print('Found nothing to build')
            exit_status = 2



def main():
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.argv = [sys.argv[0],  '-D'] + sys.argv[1:]
    print(sys.argv)

    # sys.exit(smain())

    parser = SConsOptions.Parser("""SCons by Steven Knight et al.:\n\tSCons: v4.4.0, Sat, 21 Jan 2023 00:00:00 +0000, by _reproducible on _reproducible\n\tSCons path: ['/usr/lib/python3.11/site-packages/SCons']\nCopyright (c) 2001 - 2023 The SCons Foundation""")
    values = SConsOptions.SConsValues(parser.get_default_values())
    SCons.Script.Main.OptionsParser = parser

    options, args = parser.parse_args(sys.argv[1:], values)
    _main(parser)
    sys.exit(0)


if __name__ == '__main__':
    sys.exit(main())

