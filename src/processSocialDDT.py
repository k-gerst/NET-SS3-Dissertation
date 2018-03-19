import pandas as pd
import numpy as np
import os
import re
import datetime


def process_ddt(save=0, path='..\\data\\raw\\transfer_2018-03-08\\DDT\\'):
    data_path = path
    files = [f for f in os.listdir(data_path) if re.search(r'NCREN_DTDdata_\d{4}', f)]
    df = pd.concat(([pd.read_table(data_path + file) for file in files]), ignore_index=True)

    # Define `flatten()`: flattens a list of lists
    # Found: https://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    # Loop breakdown:
    #  for sublist in l:
    #      for item in sublist:
    #          flat_list.append(item)

    # flatten = lambda l: [item for sublist in l for item in sublist]

    def flatten(l):
        return [item for sublist in l for item in sublist]

    # Define dictionaries for replace
    P_map = {'PL': 1, 'PM': 2, 'PH': 3}
    A_map = {'AL': 1, 'AH': 2}
    S_map = {'SL': 1, 'SH': 2}

    df['dis'] = flatten([re.findall('P.', x) for x in df['Trial']])
    df['alc'] = flatten([re.findall('A.', x) for x in df['Trial']])
    df['soc'] = flatten([re.findall('S.', x) for x in df['Trial']])

    df['Trial_Alt'] = df['alc'] + df['soc'] + df['dis']

    df['dis'].replace(P_map, inplace=True)
    df['alc'].replace(A_map, inplace=True)
    df['soc'].replace(S_map, inplace=True)

    df.rename(columns={'Subject': 'SubID'}, inplace=True)
    mapper = {'y': 1, 'n': 0, -999: np.nan}
    df.replace(mapper, inplace=True)
    df.set_index(['SubID'], inplace=True)

    if save == 1:
        out_path = r'..\\data\\processed\\'
        file_name = r'data - socDDT long - ' + datetime.date.today().strftime('%Y-%m-%d') + '.csv'
        df.to_csv(os.path.join(out_path, file_name))

    assert isinstance(df, object)
    return df
