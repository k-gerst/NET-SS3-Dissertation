import pandas as pd
import numpy as np
import os
import datetime


def process_diagnostics(save=0):
    df_ms1 = pd.read_csv('..\\data\\raw\\transfer_2018-03-08\\diagnostic\\2018-03-02 - MS1 - Database Merge.csv')
    df_ms2 = pd.read_csv('..\\data\\raw\\transfer_2018-03-08\\diagnostic\\2018-03-05 - MS2 - Database Merge.csv')

    col_list = list(df_ms2.columns[np.array(df_ms2.columns.isin(df_ms1.columns))])
    df_ms1 = df_ms1[col_list]
    df_ms2 = df_ms2[col_list]
    df_merged = pd.concat([df_ms1, df_ms2], ignore_index=True)
    df_merged.set_index('SubID', inplace=True)

    if save == 1:
        out_path = r'..\\data\\processed\\'
        file_name = r'data - diagnostics - ' + datetime.date.today().strftime('%Y-%m-%d') + '.csv'
        df_merged.to_csv(os.path.join(out_path, file_name))

    return df_merged
