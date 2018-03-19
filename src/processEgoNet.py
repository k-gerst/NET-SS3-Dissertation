import pandas as pd
import networkx as nx
import os
import re
import egoNetClass
import datetime


def process_ego_net(save=0, path='..\\data\\raw\\transfer_2018-03-08\\egoNET\\'):
    data_path = path
    file_list = [f for f in os.listdir(data_path) if
                 re.search(r'[\s-]*\d{1,4}[\s-]*\d{1,2}[\s-]*\d{1,4}_weighted_matrix', f)]
    subID_list = [re.search(r'NET-SS3\s?-\s?(.{4})[\s-]*', s).group(1) for s in file_list]
    net_list = []

    for subID in subID_list:
        G_foo = egoNetClass.egoNet(subID, data_path, weight=3, drop_parents=True)
        net_list.append(G_foo)

    attributes = [dict(SubID=pd.to_numeric(subid.subid),
                       Size=nx.number_of_nodes(subid.G),
                       Density=nx.density(subid.G),
                       Female_Prop=subid.nodeList['Gender'].mean(),
                       Contact_AVG=subid.nodeList['Contact'].mean(),
                       Importance_AVG=subid.nodeList['Importance'].mean(),
                       Support_AVG=subid.nodeList['Support'].mean(),
                       NumOfDrinkers=subid.nodeList[
                           (subid.nodeList['AlcFrequency'] >= 5) & (subid.nodeList['AlcQuantity'] >= 1)].shape[0],
                       AlcFrequency_AVG=subid.nodeList['AlcFrequency'].mean(),
                       AlcFrequency_MED=subid.nodeList['AlcFrequency'].median(),
                       AlcQuantity_AVG=subid.nodeList['AlcQuantity'].mean(),
                       AlcQuantity_MED=subid.nodeList['AlcQuantity'].median(),
                       AlcDrinkWithPerson_AVG=subid.nodeList['AlcDrinkWithPerson'].mean(),
                       AlcDrinkWithPerson_MED=subid.nodeList['AlcDrinkWithPerson'].median(),
                       AlcParty_AVG=subid.nodeList['AlcParty'].mean(),
                       AlcParty_MED=subid.nodeList['AlcParty'].median(),
                       NumOfMJUsers=subid.nodeList[(subid.nodeList['MJFrequency'] >= 5)].shape[0],
                       MJFrequency_AVG=subid.nodeList['MJFrequency'].mean(),
                       MJFrequency_MED=subid.nodeList['MJFrequency'].median(),
                       MJSmokeWithPerson_AVG=subid.nodeList['MJSmokeWithPerson'].mean(),
                       MJSmokeWithPerson_MED=subid.nodeList['MJSmokeWithPerson'].median(),
                       NumOfDrgUsers=subid.nodeList[(subid.nodeList['DrgFrequency'] >= 5)].shape[0],
                       DrgFrequency_AVG=subid.nodeList['DrgFrequency'].mean(),
                       DrgFrequency_MED=subid.nodeList['DrgFrequency'].median(),
                       DrgUseWith_Person_AVG=subid.nodeList['DrgUseWith_Person'].mean(),
                       DrgUseWith_Person_MED=subid.nodeList['DrgUseWith_Person'].median(),
                       MJDrgParty_AVG=subid.nodeList['MJDrgParty'].mean(),
                       MJDrgParty_MED=subid.nodeList['MJDrgParty'].median(),
                       NumOfPoly=subid.nodeList[(subid.nodeList['AlcFrequency'] >= 5) & (
                                   (subid.nodeList['MJFrequency'] >= 3) | (
                                       subid.nodeList['DrgFrequency'] >= 3))].shape[0]) for subid in net_list]

    attributes_df = pd.DataFrame.from_records(attributes,
                                              columns=('SubID', 'Size', 'Density', 'Female_Prop', 'Contact_AVG', 'Importance_AVG',
                                                       'Support_AVG', 'NumOfDrinkers', 'AlcFrequency_AVG',
                                                       'AlcFrequency_MED', 'AlcQuantity_AVG', 'AlcQuantity_MED',
                                                       'AlcDrinkWithPerson_AVG', 'AlcDrinkWithPerson_MED',
                                                       'AlcParty_AVG', 'NumOfMJUsers', 'AlcParty_MED', 'MJFrequency_AVG',
                                                       'MJFrequency_MED', 'MJSmokeWithPerson_AVG',
                                                       'MJSmokeWithPerson_MED', 'NumOfDrgUsers', 'DrgFrequency_AVG',
                                                       'DrgFrequency_MED', 'DrgUseWith_Person_AVG',
                                                       'DrgUseWith_Person_MED', 'MJDrgParty_AVG', 'MJDrgParty_MED',
                                                       'NumOfPoly'),
                                              index='SubID')

    attributes_df = attributes_df.sort_index(ascending=True)

    if save == 1:
        out_path = r'..\\data\\processed\\'
        file_name = r'data - network attributes - ' + datetime.date.today().strftime('%Y-%m-%d') + '.csv'
        attributes_df.to_csv(os.path.join(out_path, file_name))

    assert isinstance(attributes_df, object)
    return attributes_df


def merge_alters(save=0, path='..\\data\\raw\\transfer_2018-03-08\\egoNET\\'):
    data_path = path
    file_list = [f for f in os.listdir(data_path) if
                 re.search(r'[\s-]*\d{1,4}[\s-]*\d{1,2}[\s-]*\d{1,4}_weighted_matrix', f)]
    subID_list = [re.search(r'NET-SS3\s?-\s?(.{4})[\s-]*', s).group(1) for s in file_list]
    net_list = []

    for subID in subID_list:
        G_foo = egoNetClass.egoNet(subID, data_path, weight=3, drop_parents=True)
        net_list.append(G_foo)

    # foo_node = net_list[10].nodeList

    alter_merge = pd.DataFrame()
    for subid in net_list:
        foo_merge = subid.nodeList
        foo_merge['SubID'] = pd.to_numeric(subid.subid)
        alter_merge = alter_merge.append(foo_merge)

    important = ['SubID']
    reordered = important + [c for c in net_list[10].nodeList.columns if c not in important]
    return alter_merge[reordered]
