#!/usr/bin/env python3

"""
summarize dbcan diamond output file
"""
import os
import re
import pandas as pd
import functools


def get_genomes(overview_file):
    """
    summarize the dbcan diamond output file: counting every cazyme id
    :param diamond_out
    :param overview_file
    :param out_file:
    :return:
    """

    # # read the sheet having genomes metadata
    # print("reading file: {}".format(diamond_file))
    # diamond_df = pd.read_csv(diamond_file, sep="\t")
    # cols = list(diamond_df.columns)

    # cazy_dict = dict()
    # for index, row in diamond_df.iterrows():
    #     if row['CAZy ID'].split('|')[-1] == "":
    #         cazy_ids = row['CAZy ID'].split('|')[1:-1]
    #         for id in cazy_ids:
    #             id = id.rsplit('_')[0]
    #             cazy_dict[row['Gene ID']+' '+id] = [row['Gene ID'], id, row['% Identical'], row['Length'],
    #                                                 row['Mismatches'], row['Gap Open'], row['Gene Start'],
    #                                                 row['Gene End'], row['CAZy Start'], row['CAZy End'],
    #                                                 row['E Value'], row['Bit Score']]
    #     else:
    #         cazy_ids = row['CAZy ID'].split('|')[1:]

    #         for id in cazy_ids:
    #             id = id.rsplit('_')[0]
    #             cazy_dict[row['Gene ID']+' '+id] = [row['Gene ID'], id, row['% Identical'], row['Length'],
    #                                                 row['Mismatches'], row['Gap Open'], row['Gene Start'],
    #                                                 row['Gene End'], row['CAZy Start'], row['CAZy End'],
    #                                                 row['E Value'], row['Bit Score']]

    # df_out = pd.DataFrame(list(cazy_dict.values()), columns=cols)
    # sample_id = os.path.basename(os.path.dirname(diamond_file))
    # diamond_cazy_df = pd.DataFrame(df_out.groupby('CAZy ID', as_index=True)['CAZy ID'].count()).rename(columns={'CAZy ID': sample_id}).reset_index()


    # read the overview output
    print("reading file {}".format(overview_file))
    overview_df = pd.read_csv(overview_file, sep="\t")
    cols = list(overview_df.columns)
    overview_dict = dict()

    for index, row in overview_df.iterrows():
        if row['Hotpep'] != '-' and row['DIAMOND'] != '-' and row['#ofTools'] >= 2:
            cazy_id = re.sub(r'\([^)]*\)', "", row['Hotpep'])

            if not cazy_id in overview_dict:
                overview_dict[row['Gene ID']+' '+cazy_id] = [row['Gene ID'], row['HMMER'], row['Hotpep'], row['DIAMOND'], row['#ofTools'], cazy_id]

    df_out = pd.DataFrame(list(overview_dict.values()), columns=['Gene ID',  'HMMER', 'Hotpep', 'DIAMOND', '#ofTools', 'CAZy ID'])
    sample_id = os.path.basename(os.path.dirname(overview_file))
    overview_cazy_df = pd.DataFrame(df_out.groupby('CAZy ID', as_index=True)['CAZy ID'].count()).rename(columns={'CAZy ID': sample_id}).reset_index()
    overview_cazy_df = overview_cazy_df.sort_values('CAZy ID')
    overview_geneid_cazy_df = pd.DataFrame(df_out.groupby(['Gene ID', 'CAZy ID'], as_index=True)['CAZy ID'].count()).rename(columns={'CAZy ID': sample_id}).reset_index()
    overview_geneid_cazy_df = overview_geneid_cazy_df.sort_values('CAZy ID')

    out = "/var/scratch/jjuma/Stanley_Onyango/cazyme_project_05102020/summary/{}_overview_geneids_cazyids_summary.csv".format(sample_id)
    out = os.path.abspath(out)
    if not os.path.exists(os.path.dirname(out)):
        os.makedirs(os.path.dirname(out))
    overview_geneid_cazy_df.to_csv(out, index=False, sep=",")
    return overview_cazy_df, overview_geneid_cazy_df


if __name__ == "__main__":
    #genomes_dir="/Users/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/genomes/"
    #out1 = "/Users/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/summary/dbcan_overview_aggregated_cazyids_summary.csv"

    genomes_dir = "/var/scratch/jjuma/Stanley_Onyango/cazyme_project_05102020/genomes"
    out1 = "/var/scratch/jjuma/Stanley_Onyango/cazyme_project_05102020/summary/dbcan_overview_aggregated_cazyids_summary.csv"
    diamond_dfs = []
    overview_dfs = []

    for root, dirs, fnames in os.walk(genomes_dir):
        fnames.sort()
        for fn in fnames:
            # if fn == 'diamond.out':
            #     diamond_file = os.path.abspath(os.path.join(root, fn))
            if fn == 'overview.txt':
                overview_file = os.path.abspath(os.path.join(root, fn))
                if os.path.getsize(overview_file) == 0:
                    continue
                else:
                    overview_cazy, overview_geneid_cazy = get_genomes(overview_file=overview_file)
                    overview_dfs.append(overview_cazy)

    overview_results = functools.reduce(lambda left, right: pd.merge(left, right, on=['CAZy ID'], how='outer'), overview_dfs).fillna(0)


    out1 = os.path.abspath(out1)
    if not os.path.exists(os.path.dirname(out1)):
        os.makedirs(os.path.dirname(out1))
    overview_results.to_csv(out1, index=False, sep=",")
