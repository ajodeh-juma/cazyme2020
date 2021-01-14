#!/usr/bin/env python

import os
import shutil


def add_genomes(data_dir, genomes_dir):
    """
    add missing genomes FASTA files
    :param data_dir:
    :param genomes_dir:
    :return:
    """
    for filename in os.listdir(data_dir):
        taxid = os.path.splitext(filename)[0].rsplit('_')[1]
        if not os.path.exists(os.path.join(genomes_dir, taxid)):
            os.makedirs(os.path.join(genomes_dir, taxid))
            shutil.copy2(src=os.path.join(data_dir, filename), dst=os.path.join(genomes_dir, taxid))
        else:
            shutil.copy2(src=os.path.join(data_dir, filename), dst=os.path.join(genomes_dir, taxid))


if __name__ == '__main__':
    add_genomes(data_dir="/home/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/missing22_genomes",
                genomes_dir="/var/scratch/jjuma/Stanley_Onyango/cazyme_project_05102020/genomes")
