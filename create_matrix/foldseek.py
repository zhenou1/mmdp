

import os, subprocess, pandas, sys
from datetime import datetime


def foldseek_search(query_path, result_tsv):

    """
    This function uses foldseek to rapidly compare protein structures by TMalign and produces a tabular output with tmscore and average plddt
    """

    #Create custom database from query folder
    subprocess.run(['foldseek', 'createdb', query_path, f'foldseek_db/work_{date}/queryDB'])

    #Create index for the created database for easy search
    subprocess.run(['foldseek', 'createindex', f'foldseek_db/work_{date}/queryDB', 'foldseek_db/tmp'])

    #Tabular output with tmscores
    subprocess.run(['foldseek', 'easy-search', f'foldseek_db/work_{date}/queryDB', f'foldseek_db/work_{date}/queryDB', result_tsv, 'foldseek_db/tmp', '--format-output', 'query,target,alntmscore,lddt,evalue,bits'])

    #Add header to the tabular output
    subprocess.run(['sed', '-i', '1i query\ttarget\ttmscore\taverage_lddt\teval\tbits', result_tsv])


def tm_score(result_tsv, score_out):

    """
    This function reads in the tabular output from foldseek and produces txt file outputs for creating similarity matrix
    """

    #Read in tabular output
    df = pandas.read_table(result_tsv)

    tmscore = []

    #Create a list of tmscores
    for i in range(len(df)):
        id1 = df['query'][i].split('.')[0]
        id2 = df['target'][i].split('.')[0]
        tmscore.append((id1, id2, df['tmscore'][i],))

    #Write out tmscores in new text file
    with open(score_out, 'w') as output:
        for id1, id2, tm in tmscore:
            output.write(f"{id1} {id2} {tm}\n")


if __name__ == "__main__":

    #Create new work directories to store databases to avoid crashes
    now = datetime.now()
    date = now.strftime("%y_%m_%d_%H_%M_%S")

    if os.path.exists('foldseek_db'):
        pass
    else:
        os.mkdir('foldseek_db')
    
    os.mkdir(f'foldseek_db/work_{date}')

    result_tsv = f'fs_results_{sys.argv[1]}.tsv'
    score_out = f'tmscores_{sys.argv[1]}.txt'

    foldseek_search(sys.argv[1], result_tsv)
    tm_score(result_tsv, score_out)