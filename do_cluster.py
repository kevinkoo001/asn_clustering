import os
import logging
import draw_graph
import itertools

try:
    import networkx as nx
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.feature_extraction import image
    from sklearn.cluster import spectral_clustering
    
except importError:
    logging.error('Required library: networkx, numpy, matplot, sklearn')

class Cluster:
    def __init__(self):
        #self.Graph = Graph
        pass
    
    '''
    Algorithms for Graph Similarity and Subgraph Matching
    https://www.cs.cmu.edu/~jingx/docs/DBreport.pdf
    Metric for affinix matrix: simlarity
    '''
    def select_k(self, spectrum, minimum_energy = 0.9):
        running_total = 0.0
        total = sum(spectrum)
        if total == 0.0:
            return len(spectrum)
        for i in range(len(spectrum)):
            running_total += spectrum[i]
            if running_total / total >= minimum_energy:
                return i + 1
        return len(spectrum)

    def calc_similarity(self, G1, G2):
        # Get laplacian
        L1 = nx.spectrum.laplacian_spectrum(G1) 
        L2 = nx.spectrum.laplacian_spectrum(G2)

        k1 = self.select_k(L1)
        k2 = self.select_k(L2)
        k = min(k1, k2)

        similarity = sum((L1[:k] - L2[:k])**2)
        r = 999999999 if similarity == 0 else round(1/similarity, 8)
        return r
        #return similarity
        
    def spec_cluster(self, aff_matrix):
        labels = spectral_clustering(aff_matrix, n_clusters=5, eigen_solver='arpack')
        plt.scatter(aff_matrix[:,:], aff_matrix[:,:], alpha=0.5)
        plt.show()
        return labels
   
if __name__ == '__main__':
    C = Cluster()
    #G = draw_graph.Graph('../Previous_BGP/edge_lablel_data/')
    G = draw_graph.Graph()
    G.get_vertex_edge_per_country2()
    G.create_all_graphs()

    all_countries = sorted(G.get_countries())[:50]
    similarity_comb = [x for x in sorted(itertools.combinations(all_countries, 2))]
    m_size = len(all_countries)
    
    index_matrix = dict()
    for i, cc in enumerate(all_countries):
        index_matrix[cc] = i
        
    affinity = np.zeros(shape=(m_size, m_size))
    
    '''
        a,    b,    c,    d,    e
    a (0,0) (0,1) (0,2) (0,3) (0,4)
    b (1,0) (1,1) (1,2) (1,3) (1,4)
    c (2,0) (2,1) (2,2) (2,3) (2,4)
    d (3,0) (3,1) (3,2) (3,3) (3,4)
    e (4,0) (4,1) (4,2) (4,3) (4,4)
    '''
    print "Size of affinity matrix: %dx%d" % (m_size, m_size)
    for c1, c2 in similarity_comb:
        s = C.calc_similarity(G.get_graph_per_country(c1), G.get_graph_per_country(c2))
        affinity[index_matrix[c1], index_matrix[c2]] = s
        affinity[index_matrix[c2], index_matrix[c1]] = s
        
    result = C.spec_cluster(affinity).tolist()
    for k, v in sorted(zip(index_matrix.keys(), index_matrix.values())):
        print '%s: Class [%d]' % (k, result[v])
        
    #print g1.create_graph('AF').nodes(), g1.create_graph('AF').edges()
    #print g2.create_graph('QA').nodes(), g2.create_graph('QA').edges()
    #print c.calc_similarity(g.create_graph('AF'), g.create_graph('QA'))