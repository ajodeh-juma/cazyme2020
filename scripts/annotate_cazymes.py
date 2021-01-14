#!/usr/bin/env python3
"""
automated Carbohydrate-active enzyme ANnotation

python3 annotate_cazymes.py \
-i input_fasta \
-s sequence_type ['protein', 'prok', 'meta'] \
-t tools ['hmmer', 'diamond', 'hotpep', 'all'] \
-db path_to_db \
-o path_to_out_dir """

# --- standard imports ---#
import os
import sys
import logging
import argparse
from textwrap import dedent

# --- third party imports ---#


# --- project specific imports ---#
from utils import mkdir
from utils import find_executable
from utils import run_shell_command

logfile = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0] + '.log'
logging.getLogger().setLevel(logging.DEBUG)
logFormatter = logging.Formatter('[%(asctime)s] - %(''levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')

# fileHandler = logging.FileHandler(filename=logfile)
# fileHandler.setFormatter(logFormatter)
# logging.getLogger().addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logging.getLogger().addHandler(consoleHandler)

f_out = open(logfile, 'w')


def parse_args():
    """command line options"""

    # class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    #     pass

    parser = argparse.ArgumentParser(
        # formatter_class=CustomFormatter,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prefix_chars='-',
        description=__doc__
    )

    required_group = parser.add_argument_group(dedent('''required arguments'''))
    # required_group.add_argument('-i', '--input-file', metavar='<file>',
    #                             dest='input_file',
    #                             help="input file in FASTA format"
    #                             )
    required_group.add_argument('-d', '--dataDir', type=str, metavar='<dir>',
                                dest='data_dir',
                                help="path to the directory having variant calling output, vcf file format"
                                )
    required_group.add_argument('-s', '--seq-type', metavar='<str>', type=str,
                                dest='seq_type', choices=['protein', 'prok', 'meta'],
                                help="Type of sequence input. protein=proteome; prok=prokaryote; meta=metagenome "
                                )
    required_group.add_argument('-db', '--database-dir', metavar='<dir>',
                                dest='db_dir',
                                help="path to the database directory"
                                )
    parser.add_argument('-t', '--tools', metavar="<tool1,tool2,tool3>", nargs="?",
                        dest="tools", default='all',
                        help="Choose a combination of tools to run ['hmmer', 'diamond', 'hotpep', 'all']"
                        )
    parser.add_argument('-o', '--outDir', metavar='<dir>',
                        dest='out_dir',
                        help="path to the directory to write the output files, if not existing, it will "
                             "will be created. If not provided, the default is the current working directory"
                        )
    parser.add_argument('--dbcan-args', type=str, metavar='<str>',
                        dest='dbcan_args', default='',
                        help="extra arguments to be passed directly to the run_dbcan.py executable "
                             "(e.g., --dbcan-args='--db_dir dbcan_output_dir')"
                        )
    return parser


def dbcan_cazymes(input_file, seq_type, tools, db_dir, out_dir, dbcan_args=""):
    """

    :param input_file: <str> input file in FASTA format
    :param seq_type: <str> sequence type of the input
    :param tools: <str> tools for cazyme annotation
    :param db_dir: <str> path to the database directory
    :param out_dir <str> path to output directory
    :param dbcan_args: <str> extra arguments passed on to the executable
    :return:
    """

    # locate the executable
    dbcan = find_executable(['run_dbcan.py'])

    tools = list(map(str, tools.split(',')))

    diamond_out = os.path.join(out_dir, 'diamond.out')
    hmmer_out = os.path.join(out_dir, 'hmmer.out')
    hotpep_out = os.path.join(out_dir, 'Hotpep.out')
    if os.path.exists(diamond_out) and os.path.exists(hmmer_out) and os.path.exists(hotpep_out):
        pass
        # logging.critical("CAZyme predicted outputs \n{}\n{}\n{} exists!".format(diamond_out, hmmer_out, hotpep_out))
    else:
        call = ["{} {} {} --tools {} --db_dir {} --out_dir {} {}".format(dbcan, input_file, seq_type, ",".join(tools),
                                                                         db_dir, out_dir, dbcan_args)]
        cmd = " ".join(call)

        logging.info("CAZyme prediction on {}".format(os.path.basename(input_file)))
        run_shell_command(cmd=cmd, logfile=f_out, raise_errors=False, extra_env=None)
    return out_dir


def main():
    """

    :return:
    """
    parser = parse_args()
    args = parser.parse_args()

    # check for input data directory
    if args.data_dir is None:
        logging.info("please specify the directory having FASTA format files\n")
        sys.exit(2)
    if args.data_dir is not None and os.path.exists(args.data_dir) and os.path.isdir(args.data_dir) and \
            len(os.listdir(args.data_dir)) != 0:
        logging.info("[data directory]: {}".format(os.path.abspath(args.data_dir)))
    if os.path.isdir(args.data_dir) and os.path.exists(args.data_dir) and len(
            os.listdir(args.data_dir)) == 0:
        logging.error("[data directory]: {0} is empty!".format(os.path.abspath(args.data_dir)))
        sys.exit(1)
    if args.data_dir is not None and os.path.exists(args.data_dir) and not os.path.isdir(args.data_dir):
        raise NotADirectoryError(args.data_dir, "Is not a directory")

    # check output directory
    if args.out_dir is None:
        logging.info("[output dir] not specified, output will be written to {}".format(args.data_dir))
        args.out_dir = args.data_dir
    else:
        args.out_dir = mkdir(args.out_dir)
        logging.info("[output dir] - {}".format(os.path.abspath(args.out_dir)))

    for root, dirs, fnames in os.walk(args.data_dir):
        fnames.sort()
        for fn in fnames:
            if fn.endswith('.fna') or fn.endswith('.fasta'):
                fn = os.path.abspath(os.path.join(root, fn))
                outdir = os.path.dirname(fn)
                mkdir(outdir)
                dbcan_cazymes(input_file=fn,
                              seq_type=args.seq_type,
                              tools=args.tools,
                              db_dir=os.path.abspath(args.db_dir),
                              out_dir=outdir,
                              dbcan_args=args.dbcan_args)


if __name__ == '__main__':
    main()