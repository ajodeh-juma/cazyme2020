#!/usr/bin/env python
"""
utility functions
"""
import argparse
import os
import re
import sys
import errno
import shutil
import tempfile
import contextlib
from pathlib import Path
from itertools import groupby

import subprocess
from textwrap import dedent
from datetime import datetime


def start_time():
    """
    determine the start time of a process
    :return:
    """
    # set start time format
    format = "%a %b %d %H:%M:%S %Y"
    stime = datetime.now()
    s = stime.strftime(format)
    print("started:\t{}".format(s))
    return stime


def end_time(stime):
    """

    :param stime:
    :return:
    """

    # set end time format
    format = "%a %b %d %H:%M:%S %Y"
    etime = datetime.now()
    e = etime.strftime(format)
    print("\ncompleted:\t {}".format(e))
    return etime


def run_time(stime, etime):
    """
    determine the total time to run a process
    :param stime:
    :param etime:
    :return:
    """

    tdelta = etime - stime

    # format the time delta object to human readable form
    d = dict(days=tdelta.days)
    d['hrs'], rem = divmod(tdelta.seconds, 3600)
    d['min'], d['sec'] = divmod(rem, 60)

    if d['min'] == 0:
        fmt = '{sec} sec'
    elif d['hrs'] == 0:
        fmt = '{min} min {sec} sec'
    elif d['days'] == 0:
        fmt = '{hrs} hr(s) {min} min {sec} sec'
    else:
        fmt = '{days} day(s) {hrs} hr(s) {min} min {sec} sec'
    print("\n[ALL done] Runtime: " + '\t' + fmt.format(**d))


def find_executable(names, default=None):
    """
    find an executable PATH from the given list of names.
    Raises an error if no executable is found.  Provide a
    value for the "default" parameter to instead return a value.

    :param names: list of given executable names
    :param default:
    :return: <str> path to the first executable found in PATH from the given list of names.
    """
    exe = next(filter(shutil.which, names), default)

    if exe is None:
        print("Unable to find any of {} in PATH={}".format(names, os.environ["PATH"]))
        print("\nHint: You can install the missing program using conda or homebrew or apt-get.\n")
        raise Exception
    return exe


def run_shell_command(cmd, logfile, raise_errors=False, extra_env=None):
    """
    run the given command string via Bash with error checking

    :param cmd: command given to the bash shell for executing
    :param logfile: file object to write the standard errors
    :param raise_errors: bool to raise error if running command fails/succeeds
    :param extra_env: mapping that provides keys and values which are overlayed onto the default subprocess environment.
    :return:
    """

    env = os.environ.copy()

    if extra_env:
        env.update(extra_env)

    try:
        p = subprocess.check_call("set -euo pipefail; " + cmd,
                                  shell=True,
                                  stderr=logfile,
                                  universal_newlines=True,
                                  executable="/bin/bash"
                                  )
    except (subprocess.CalledProcessError, OSError) as error:
        # except subprocess.CalledProcessError as error:
        rc = error.returncode
        if rc == 127:
            extra = "Are you sure this program is installed?"
        else:
            extra = " "
        print("Error occurred: shell exited with return code: {}\ncommand running: {}\n{}".format(
            error.returncode, cmd, extra), file=sys.stderr
        )
        if raise_errors:
            raise
        else:
            return False
    except FileNotFoundError as error:
        print("Unable to run shell command using {}! tool requires {} to be installed.".format(
            error.filename, error.filename), file=sys.stderr
        )
        if raise_errors:
            raise
        else:
            return False
    else:
        return True


def mkdir(directory):
    """
    recursivley create a directory if it does not exist

    :param directory: path to the directory to be created
    :return: directory
    """
    directory = os.path.abspath(directory)
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise  # raises the error again
    return directory


def available_cpu_cores(fallback: int = 1) -> int:
    """
    Returns the number (an int) of CPU cores available to this **process**, if
    determinable, otherwise the number of CPU cores available to the
    **computer**, if determinable, otherwise the *fallback* number (which
    defaults to 1).
    """
    try:
        # Note that this is the correct function to use, not os.cpu_count(), as
        # described in the latter's documentation.
        #
        # The reason, which the documentation does not detail, is that
        # processes may be pinned or restricted to certain CPUs by setting
        # their "affinity".  This is not typical except in high-performance
        # computing environments, but if it is done, then a computer with say
        # 24 total cores may only allow our process to use 12.  If we tried to
        # naively use all 24, we'd end up with two threads across the 12 cores.
        # This would degrade performance rather than improve it!
        return len(os.sched_getaffinity(0))
    except:
        # cpu_count() returns None if the value is indeterminable.
        return os.cpu_count() or fallback


def uncompress_fasta(filename, suffix=".fasta"):
    """

    :param filename:
    :param suffix:
    :return:
    """

    match = re.findall(r"(\w+.)", os.path.basename(filename))
    if match[-1] == 'gz':
        out = os.path.splitext(filename)[0]
        ext = os.path.splitext(out)[1]
        outfile = os.path.join(os.path.dirname(filename), ''.join(match[:-1]).strip(ext)) + suffix

        if Path(out).is_file():
            print(f"decompression done, check file: {out}")
        else:
            cmd = 'gunzip {}'.format(filename)
            try:
                print(f"decompressing file {filename}")
                p = subprocess.check_call(cmd, shell=True)
                # if p == 0:
                #     os.remove(os.path.abspath(filename))
            except Exception as error:
                print(f"Error: {error}")
        return outfile
