import pandas as pd
import processEgoNet
import processSocialDDT
import processDiagnostics
import os
import datetime

save = 1
ego_net_foo = processEgoNet.process_ego_net()
alter_foo = processEgoNet.merge_alters()
ddt_foo = processSocialDDT.process_ddt()
diag_foo = processDiagnostics.process_diagnostics()
diag_foo = diag_foo[['Group', 'DM1_Female', 'Age', 'DM8A_Race', 'DM15_HighestGradeCompleted',
                     'DM17B_HouseholdIncome', 'DM18B_ParentsIncome', 'Performance_IQ',
                     'Full4IQ', 'Verbal_IQ', 'AL_PC', 'AL6', 'AS_PC', 'CD_PC', 'MJ_PC',
                     'Drug_PC', 'AD_PC', 'HD_PC', 'ADHD_PC', 'CD_Dx', 'AUD_Dx', 'MUD_Dx',
                     'CocUD_Dx', 'StimUD_Dx', 'SedUD_Dx', 'OpUD_Dx', 'OtherUD_Dx']]


def complete_cases(x1=ego_net_foo, x2=ddt_foo):
    x1 = pd.DataFrame({'SubID': x1.index.unique(),
                       'have_net_data': 1})
    x1.set_index('SubID', inplace=True)

    x2 = pd.DataFrame({'SubID': x2.index.unique(),
                       'have_ddt_data': 1})
    x2.set_index('SubID', inplace=True)

    x1['have_net_data'] = 1
    x2['have_ddt_data'] = 1
    result = pd.concat([x1, x2], axis=1)
    result[(result['have_net_data'] + result['have_ddt_data']) > 1].info()
    return result


def _merge_(x1, x2, x3):
    foo = pd.merge(left=x1, right=x2, how='left', left_index=True, right_index=True)
    result = pd.merge(left=foo, right=x3, how='left', left_index=True, right_index=True)
    return result


df_complete = complete_cases()
df_merged = _merge_(df_complete, diag_foo, ego_net_foo)
df_merged.info()
print(df_merged.groupby(['Group'])[['Size', 'Density', 'Contact_AVG', 'Importance_AVG', 'Support_AVG']].mean())
print(df_merged.groupby(['Group'])[['AlcFrequency_AVG', 'AlcQuantity_AVG',
                                    'AlcDrinkWithPerson_AVG', 'AlcParty_AVG']].mean())
print(df_merged.groupby(['Group'])[['MJFrequency_AVG', 'MJSmokeWithPerson_AVG', 'DrgFrequency_AVG',
                                    'DrgUseWith_Person_AVG', 'MJDrgParty_AVG']].mean())
print(df_merged.groupby(['Group'])[['NumOfDrinkers', 'NumOfMJUsers', 'NumOfDrgUsers', 'NumOfPoly']].mean())

df_alter_merge = pd.merge(left=df_complete, right=diag_foo, how='left', left_index=True, right_index=True)
df_alter_merge = pd.merge(left=alter_foo, right=df_alter_merge, how='left', left_on='SubID', right_index=True)

if save == 1:
    out_path = r'..\\data\\processed'
    file_name = r'data - net-ss3 merged - ' + datetime.date.today().strftime('%Y-%m-%d') + '.csv'
    df_merged.to_csv(os.path.join(out_path, file_name))

    file_name = r'data - net-ss3 alter merged - ' + datetime.date.today().strftime('%Y-%m-%d') + '.csv'
    df_alter_merge.to_csv(os.path.join(out_path, file_name))


