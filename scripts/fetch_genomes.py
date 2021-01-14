#!/usr/bin/env python3

"""
fetch refseq sequences using ncbi-download
"""
import os
import sys
import subprocess
import pandas as pd
from utils import find_executable
from utils import uncompress_fasta


def get_genomes(metadata_file, out_dir):
    """
    get taxids from the metadata file for use in downloading the genomes
    :param metadata_file:
    :param out_dir:
    :return:
    """

    # locate the executable
    tool = find_executable(["ncbi-genome-download"])

    # read the sheet having genomes metadata
    meta_df = pd.read_excel(metadata_file, sheet_name="Taxa_metadata")

    # create a dict with tax ids as key and genome names and bioproject accessions as values
    subset_df = meta_df[['Tax_ID', 'Species', 'BioProject Accession', 'Scientific_Name']]
    meta_dic = subset_df.set_index('Tax_ID').T.to_dict('list')

    for tax_id, records in meta_dic.items():
        bioproj_acc = records[1]
        # fetch the genbank ftp path for genome
        call = ['esearch -db assembly -query "txid{}[Organism] AND {}[BioProject]" '
                '| efetch -format docsum '
                '| xtract -pattern DocumentSummary  -element FtpPath_GenBank'.format(tax_id, bioproj_acc)]
        cmd = " ".join(call)
        # call = ['esearch -db assembly -query "{}[All Fields] AND {}[BioProject]" '
        #         '| efetch -format docsum '
        #         '| xtract -pattern DocumentSummary  -element FtpPath_GenBank'.format(genome, bioproj_acc)]
        # cmd = " ".join(call)
        try:
            sys.stdout.write("\nfetching Genebank ftp path for taxonomy id {}".format(tax_id))
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            ftp_path = p.communicate()[0].strip().decode('utf-8')
            ftp_path = os.path.join(ftp_path, os.path.basename(ftp_path) + '_genomic.fna.gz')
            meta_dic[tax_id].append(ftp_path)
        except (subprocess.CalledProcessError, OSError) as error:
            rc = error.returncode
            sys.stderr.write("\nerror {} occurred when fetching genome accession\ncommand running: {}".format(rc, cmd))

    for tax_id, records in meta_dic.items():
        species, bioproj_acc, sciname, ftp_path = records[0], records[1], records[2], records[3]
        fna = os.path.basename(ftp_path)

        output_dir = os.path.join(out_dir, str(tax_id))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if fna != "_genomic.fna.gz":
            unzipped = os.path.join(output_dir, os.path.splitext(fna)[0])

            if os.path.exists(unzipped):
                print(f"unzipped file {unzipped} exists")
            else:
                call = ['wget --continue -q \
                            --directory-prefix={} {} && gunzip {}'.format(output_dir, ftp_path, unzipped)]
                cmd = ' '.join(call)
                try:
                    sys.stdout.write("\nfetching sequence file {}".format(ftp_path))
                    subprocess.check_call(cmd, shell=True)
                except (subprocess.CalledProcessError, OSError) as error:
                    rc = error.returncode
                    sys.stderr.write("\nerror {} occurred when fetching genome accession\ncommand running: {}".format(rc, cmd))
        else:
            species, genus = records[0], records[0].split()[0]
            strain = records[2].replace('[', '').replace(']', '').rsplit(" ", 2)[1:]
            strain = " ".join(strain)

            output_dir = os.path.join(out_dir, str(tax_id))
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            call = ['ncbi-genome-download --section genbank --formats "fasta" '
                    '--assembly-levels "all" --genera "{}" --strains "{}" --taxids {} '
                    '--output-folder {} --flat-output -v bacteria'.format(genus, strain, tax_id, output_dir)]
            cmd = " ".join(call)

            try:
                sys.stdout.write("\nfetching genbank genome assembly for taxid {}\n".format(tax_id))
                p = subprocess.check_call(cmd, shell=True)
                if p == 0:
                    for fn in os.listdir(output_dir):
                        uncompress_fasta(filename=os.path.join(output_dir, fn), suffix=".fna")
            except (subprocess.CalledProcessError, OSError) as error:
                rc = error.returncode
                sys.stderr.write("\nerror {} occurred when fetching genome accession\ncommand running: {}".format(rc, cmd))


if __name__ == "__main__":
    #metadata_file = "/home/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/metadata/Taxa_metadata.xlsx"
    #out_dir = "/var/scratch/jjuma/Stanley_Onyango/cazyme_project_05102020/genomes"

    metadata_file = "/Users/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/metadata/taxa_metadata_test.xlsx"
    out_dir = "/Users/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/genomes"

    get_genomes(metadata_file=metadata_file, out_dir=out_dir)
