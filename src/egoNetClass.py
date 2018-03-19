import pandas as pd
import re  # provides regular expression matching operations (https://docs.python.org/2/library/re.html#module-re)
import os
import networkx as nx
import matplotlib.pyplot as plt


def anon_alters(subid, node_list):
    """
    Takes list of node names as input and returns an anonymized list of node IDs.
    Node IDs use the following convention: 'SubID-NodeID'
    """
    anon_list = [str(subid) + '-' + str(n).zfill(2) for n in list(range(1, len(node_list) + 1))]
    mapper = dict(zip(node_list, anon_list))
    return mapper


class egoNet(object):
    """
    Custom class object that handles the pre-processing steps of the ego network data. Results in a networkx object.
    
    Attributes:
    
    Methods:
    
    """

    def __init__(self, subid, path, weight=2, drop_parents=False):
        """ 
        Returns a networkx object. 
        """
        self.subid = subid
        self.path = path

        # Retrieve weighted alter-alter adjacency matrix
        file_wt_mat = [f for f in os.listdir(path) if
                       re.search(re.escape(str(self.subid)) + r'[\s-]*\d{2,4}[\s-]*\d{1,2}[\s-]*\d{1,4}_weighted_matrix',
                                 f)]
        wt_mat = pd.read_csv(path + file_wt_mat[0], index_col=0)
        wt_mat['source'] = wt_mat.index.values
        del wt_mat.index.name

        # Generate source-target (long) matrix from weighted alter-alter adjacency matrix.
        edges = pd.melt(wt_mat, id_vars='source', var_name='target', value_name='weight')

        # Retrieve alter attribute matrix
        file_attrib_mat = [f for f in os.listdir(path) if re.search(
            re.escape(str(self.subid)) + r'[\s-]*\d{2,4}[\s-]*\d{1,2}[\s-]*\d{1,4}_alter_summary', f)]
        nodes = pd.read_csv(path + file_attrib_mat[0])

        # Generate anonymous alter ID key-value dictionary
        mapper = anon_alters(subid=subid, node_list=wt_mat['source'])
        # self.mapper = mapper

        # Replace alter names with anonymous IDs
        edges.replace(mapper, inplace=True)
        nodes.replace(mapper, inplace=True)
        nodes.set_index('Alter_Name', inplace=True)
        nodes.rename(
            columns=dict(zip(nodes.columns, [re.sub(r'[\s]?(Alter_)?', '', x) for x in nodes.columns])),
            inplace=True)

        relationship_map = {1: 'parent',
                            2: 'spouse',
                            3: 'significant other',
                            4: 'child',
                            5: 'sibling',
                            6: 'other relative',
                            7: 'friend',
                            8: 'co-worker',
                            9: 'other'}
        nodes['Relationship'].replace(relationship_map, inplace=True)

        if drop_parents:
            parent_rows = nodes[nodes['Relationship'] == 'parent'].index
            nodes = nodes.drop(parent_rows)
            edges = edges.loc[~((edges['source'].isin(parent_rows)) | (edges['target'].isin(parent_rows)))]

        # Create edge matrix conditional on weight of edge (default = 2)
        self.edgeList = edges[edges['weight'] > weight]
        # Create node
        self.nodeList = nodes

        G_foo = nx.Graph()
        G_foo.add_nodes_from(nodes.index)
        G_foo.add_edges_from([tuple(x) for x in self.edgeList[['target', 'source']].values])

        self.G = G_foo
        # self.G = nx.from_pandas_dataframe(edges, 'source', 'target', 'weight')
        nx.set_node_attributes(self.G, nodes.to_dict(orient='index'))

    def circular_draw(self):
        nx.draw(self.G, pos=nx.circular_layout(self.G), labels=self.nodeList['Relationship'],
                node_color=self.nodeList['AlcDrinkWithPerson'],
                cmap=plt.cm.plasma, alpha=0.8)
        plt.show()

    def info(self):
        print(self.subid)
        print(nx.info(self.G))

    def variable_recode(node_list):
        """ 
        Returns relabeled features following item conventions.
        """

        relationship_map = {1: 'parent',
                            2: 'spouse',
                            3: 'significant other',
                            4: 'child',
                            5: 'sibling',
                            6: 'other relative',
                            7: 'friend',
                            8: 'co-worker',
                            9: 'other'}
        node_list['Relationship'].replace(relationship_map)
