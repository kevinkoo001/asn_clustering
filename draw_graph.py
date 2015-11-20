import os
import sys
import random
import logging
import json
import util

try:
    # http://networkx.github.io/documentation/networkx-1.9.1/examples/index.html
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
except ImportError:
    logging.error('Required library: networkx, matplotlib')

import numpy as np

CC_FILE = 'country_code.csv'
CAIDA_FILE = '20150801.as-rel-caida.txt'
ASN_TO_CC = 'asn_reg-cymru.txt'
DIR_TO_STORE = './sub-graphs/topologies/'

CSRSP_CC = ['BH', 'BY', 'CU', 'IR', 'PK', 'SA', 'SD',
            'SY', 'TM', 'AE', 'UZ', 'VN', 'EG', 'MM', 'TN',
            'KZ', 'MY', 'LK', 'TH', 'TR', 'JO', 'LY', 'TJ', 'VE', 'YE',
            'AU', 'KR', 'US', 'CN', 'FR', 'RU', 'IN', 'GB'] # Large Size

# ['ER', 'KP', 'ET'] // Has censorship but no ASN found

class Graph:
    def __init__(self):
        self.FHI = dict()
        self.asn_to_cc = dict()
        self.edges_per_country = dict()
        self.asns_per_country = dict()
        self.country_code = dict()
        self.G_per_country = dict()

    # Country name, Country Code, FHI
    def read_known_countries(self):
        cc_code = util.csvImport(CC_FILE, ',')
        for cc in cc_code:
            self.country_code[cc[0].strip().upper()] = cc[1].strip()
            self.FHI[cc[0].strip().upper()] = cc[2].strip()
        
    def get_all_countries(self):
        return list(set(self.asns_per_country.keys()))

    def get_country_by_cc(self):
        return self.country_code

    def get_FHI_by_cc(self):
        return self.FHI

    def get_country_graph(self, cc):
        return self.G_per_country[cc]

    def get_graph_per_country(self, cc):
        return self.G_per_country[cc]

    def get_domestic_asns(self, cc):
        return set([asn for asn, c in self.asns_per_country[cc] if c == cc])

    def get_foreign_asns(self, cc):
        return set([asn for asn, c in self.asns_per_country[cc] if c != cc])

    def get_asns_connected_to_foreign(self, cc):
        return set([s for (s, d) in self.edges_per_country[cc] if d in self.get_foreign_asns(cc)])

    def check_cc(self, cc):
        if cc not in self.asns_per_country.keys():
            print 'Invalid Country Code!'
            sys.exit(1)
            
    """
    Get all vertices and edges per country from reading CAIDA_FILE and ASN_TO_CC
    CAIDA_FILE format
        src|dst|type (peer, )
    ASN_TO_CC format
        AS      | CC | Registry | Allocated  | AS Name
    """
    def get_vertex_edge_per_country(self, country=None, details=False):
        self.read_known_countries()
        asn_mappings_data = util.csvImport(ASN_TO_CC, '|', header=True)
        caida_data = util.csvImport(CAIDA_FILE, '|', header=False)
        
        ignore_asns = set()
        ignore_ccs = set()

        # Gather ASN-CC mappings
        for a in asn_mappings_data:
            asn, cc, full_name = int(a[0].strip()), a[1].strip().upper(), a[4].strip()
            # Do not bother if empty CC or ZZ (not allocated)
            if len(cc) == 0 or 'ZZ' in full_name:
                ignore_asns.add(asn)
            else:
                self.asn_to_cc[asn] = full_name[-2:] if cc == 'EU' and cc != full_name[-2:] else cc

        collected_ccs = set(self.asn_to_cc.values())
        print '[1] Registered Country Codes: %d' % len(self.country_code)
        print '[2] Identified ASNs: %d' % len(self.asn_to_cc)
        print '[3] Countries which possess one or more ASNs: %d' % len(collected_ccs)
        
        for cc in list(collected_ccs):
            if cc.strip() not in self.country_code.keys():
                ignore_ccs.add(cc)

        print '[4] Ignored (unidentified) country code: %d' % len(ignore_ccs)
        print '[5] Ignored (unidentified) ASNs: %d' % len(ignore_asns)

        # Process to prepare for the graph with ASNs(nodes) and their connectivity(edges) from CAIDA
        total, cnt = 0, 0

        for cd in caida_data:
            if cd[0][0] != '#':
                total += 1
                src_asn, dst_asn, type = int(cd[0]), int(cd[1]), int(cd[2])
                if src_asn in list(ignore_asns) or dst_asn in list(ignore_asns):
                    #print 'Either %s or %s does not belong to any country..' % (src_asn, dst_asn)
                    cnt += 1
                    pass
                else:
                    try:
                        cc = self.asn_to_cc[src_asn]

                        # ASNs per country
                        if cc in self.asns_per_country.keys():
                            self.asns_per_country[cc] += [(src_asn, self.asn_to_cc[src_asn])]
                            self.asns_per_country[cc] += [(dst_asn, self.asn_to_cc[dst_asn])]
                        else:
                            self.asns_per_country[cc] = [(src_asn, self.asn_to_cc[src_asn])]
                            self.asns_per_country[cc] = [(dst_asn, self.asn_to_cc[dst_asn])]

                        # Edges per country
                        if cc in self.edges_per_country.keys():
                            self.edges_per_country[cc] += [(src_asn, dst_asn)]
                        else:
                            self.edges_per_country[cc] = [(src_asn, dst_asn)]
                        
                    except:
                        cnt += 1
                        pass
        
        print '[6] Ignored connectivity due to either [4] or [5]: %d/%d (%2.3f%%)' \
                % (cnt, total, round(cnt/float(total), 2))
        
        if country is not None:
            self.check_cc(country)
            print '\t[%s] Nodes: %d' % (country, len(sorted(set(self.asns_per_country[country]))))
            print '\t[%s] Links: %d' % (country, len(sorted(set(self.edges_per_country[country]))))
        
        if details:
            print '[7] Nodes(ASNs) and links for each country'
            for c in sorted(self.asns_per_country.keys()):
                print '\t[%s] Edges: %d, Nodes: %d' % (c, len(self.edges_per_country[c]), len(self.asns_per_country[c]))

    def create_all_graphs(self):
        # Generate a graph G(V,E) per each country
        for cc in self.asns_per_country.keys():
            G = nx.Graph()
            all_asns = set()

            # Adding vertexes to the graph for each country
            for asn, country in self.asns_per_country[cc]:
                all_asns.add(asn)
            G.add_nodes_from(list(all_asns))
            self.G_per_country[cc] = G
        
        for cc in self.edges_per_country.keys():
            all_edges = set()

            # Adding edges to the graph for each country
            for src, dst in self.edges_per_country[cc]:
                all_edges.add((src, dst))
            self.G_per_country[cc].add_edges_from(list(all_edges))

    def plot_per_country(self, cc=None):
        def graph_check(cc, stats=True):
            node_cnt = self.G_per_country[cc].number_of_nodes()
            edge_cnt = self.G_per_country[cc].number_of_edges()
            if stats:
                print '\t[%s] Nodes: %d, Edges: %d' \
                    % (cc, node_cnt, edge_cnt)

        def save_plots(G, cc, label=True, show=False):
            #plt.figure(num=None, figsize=(500, 500), dpi=80)
            plt.figure(num=None, dpi=80)
            plt.title(self.country_code[cc] + ' (' + cc + ')')
            plt.axis('off')
            graph_check(cc, stats=False)

            asns_in_target = self.get_domestic_asns(cc)
            asns_foreign = self.get_foreign_asns(cc)

            '''
            pos = nx.spring_layout(G, iterations=node_cnt + edge_cnt) # position for all nodes
            nx.draw(G, pos, nodelist=asns_in_target, node_size=10, alpha=0.8, node_color='lightblue')
            nx.draw(G, pos, nodelist=asns_foreign, node_size=10, alpha=0.8, node_color='yellow')
            #nx.draw_shell(G, nodelist=asns_in_target, node_size=10, alpha=1, node_color='lightblue')
            #nx.draw_circular(G, nodelist=asns_foreign, node_size=10, alpha=1, node_color='yellow')
            '''

            pos = nx.spring_layout(G)
            nx.draw_networkx_nodes(G, pos, nodelist=asns_in_target, node_size=50, alpha=0.9, node_color='lightblue')
            nx.draw_networkx_nodes(G, pos, nodelist=asns_foreign, node_size=50, alpha=0.9, node_color='red')
            nx.draw_networkx_edges(G, pos)

            cut = 1.07
            plt.xlim(0, cut * max(xx for xx, yy in pos.values()))
            plt.ylim(0, cut * max(yy for xx, yy in pos.values()))

            # node_size=120, font_size=7 is reasonable to see for a mid-sized graph
            if label:
                labels = {}
                for asn, c in self.asns_per_country[cc]:
                    labels[asn] = c
                nx.draw_networkx_labels(G, pos, labels, font_size=7)  # For Labels (country name)

            if show:
                plt.show()
            else:
                f_path = DIR_TO_STORE + cc + '.png'
                if not os.path.exists(DIR_TO_STORE):
                    os.mkdir(DIR_TO_STORE)
                plt.savefig(f_path, bbox_inches='tight')
                plt.close()

        if cc is None:
            for c in sorted(self.asns_per_country.keys()):
                graph_check(c)
                save_plots(self.G_per_country[c], c, label=False, show=False)
        else:
            graph_check(cc)
            save_plots(self.G_per_country[cc], cc, label=False, show=True)

    def compute_properties(self, cc):
        G = self.get_country_graph(cc)

        # TODO - Draw another Graph for domestic countries only
        domestic = self.get_domestic_asns(cc)
        foreign = self.get_foreign_asns(cc)
        asns_connected_to_foreign = self.get_asns_connected_to_foreign(cc)
        cc_indexes = {}
        #print '%s, %d, %d, %d, %d, %d' % (cc, len(domestic), len(foreign), len(asns_connected_to_foreign),
        #                                  self.G_per_country[cc].number_of_nodes(), self.G_per_country[cc].number_of_edges())

        print '[%s] %s' % (cc, self.country_code[cc])
        print '\tDomestic: %d, International: %d' % (len(domestic), len(foreign))
        print '\tNodes: %d, Edges: %d' \
              % (self.G_per_country[cc].number_of_nodes(), self.G_per_country[cc].number_of_edges())

        if len(foreign) == 0:
            #print '\tNo foreign connection found in %s' % cc
            return -1, -1
        elif len(foreign) == 1:
            #print '\tOnly 1 connection to the outside..'
            return -2, -2
        elif self.G_per_country[cc].number_of_edges() + self.G_per_country[cc].number_of_nodes() < 10:
            #print '\tToo small nodes or edges to decide..'
            return -3, -3
        elif self.G_per_country[cc].number_of_edges() + self.G_per_country[cc].number_of_nodes() > 500:
            #print '\tTOO BIG.. just skipped!!'
            return -99, -99
        else:

            #print '\tEstimates the average clustering coefficient: %2.4f' % nx.algorithms.average_clustering(G)
            #print nx.algorithms.average_degree_connectivity(G)
            #print nx.algorithms.average_neighbor_degree(G)
            #print '\tAverage Degree Connectivity: %2.4f' % nx.algorithms.average_degree_connectivity(G)
            #print '\tAverage Neighbor Degree: %2.4f' % nx.algorithms.average_neighbor_degree(G)
            #print '\tAverage Node Connectivity: %2.4f' % nx.algorithms.average_node_connectivity(G)
            #print '\tAverage Shortest Path Length: %2.4f' % nx.algorithms.average_shortest_path_length(G)

            # of domestic ASNs which connects to foreign countries / # of total ASNs in a country
            X = len(foreign) / float(len(domestic) + len(foreign))
            Y = float(len(asns_connected_to_foreign)) / len(foreign)

            #print '\tX: %2.4f' % X
            # of domestic ASNs which connects to foreign countries / # of foreign ASNs connected to a country

            #print '\tY: %2.4f' % Y
            # surveillance index (si) = 1/x + 1/y
            Z = (1/X+1/Y)
            #print '\tIndex(= 1/X + 1/Y): %2.4f' % Z
            cc_indexes[cc] = 1/X + 1/Y
            # nx.algorithms.average_node_connectivity(G)
            return nx.algorithms.average_node_connectivity(G), nx.algorithms.average_neighbor_degree(G)

    def decision_censorship(self):
        x, y = [], []
        #colors = cm.rainbow(np.linspace(0, 1, len(y)))
        for cc in self.get_all_countries():
            X,Y = self.compute_properties(cc)
            x.append(X)
            y.append(Y)

        plt.scatter(np.array([k for k in x if k > 0]), np.array([k for k in y if k > 0]), color='blue')

        nx, ny = [], []
        for cc in CSRSP_CC:
            X,Y = self.compute_properties(cc)
            nx.append(X)
            ny.append(Y)

        plt.scatter(np.array([k for k in nx if k > 0]), np.array([k for k in ny if k > 0]), color='red')
        print 'No foreign connection found: %d' % (x.count(-1) + nx.count(-1))
        print 'Only 1 connection to the outside: %d' % (x.count(-2) + nx.count(-2))
        print 'Too small nodes or edges to decide: %d' % (x.count(-3) + nx.count(-3))
        print 'TOO BIG.. just skipped: %d' % (x.count(-99) + nx.count(-99))

        plt.show()


class D3_json:
    def __init__(self, data_dir, out_dir):
        self.target_dir = data_dir
        self.out_dir = out_dir
        self.asn_nid = dict()
        self.countries = []
        self.edges_per_country = dict()
        self.asns_per_country = dict()

    def _get_nodes_for_json(self, cc):
        prev_country = ''
        nid = 0     # ASN node ID
        cid = -1    # country id
        nodes = []

        for asn, node in self.asns_per_country[cc]:
            asn_entry = {}
            if prev_country != node:
                cid += 1
            self.asn_nid[asn] = nid
            asn_entry["ASN"] = str(asn)
            asn_entry["country"] = cid
            asn_entry["c_name"] = node
            nodes.append(asn_entry)
            prev_country = node
            nid += 1

        return nodes

    def _get_links_for_json(self, cc):
        links = []

        for src, dst in self.edges_per_country[cc]:
            link_entry = {}
            link_entry["source"] = self.asn_nid[int(src)]
            link_entry["target"] = self.asn_nid[int(dst)]
            link_entry["value"] = random.randint(1,10)
            links.append(link_entry)

        return links

    # [STEP 1] Get all vertices and edges per country
    # Double-check the G(V,E) btn Java and Python code
    def get_vertex_edge_per_country(self):
        for target in os.listdir(self.target_dir):
            tg_path = self.target_dir + target
            cc = target[:2]
            self.countries.append(cc)

            # A node represents a country, an edge represents the link between ASN
            if 'label' in target:
                nodes = util.csvImport(tg_path, ',', header=False)
                for asn, node in nodes:
                    if cc in self.asns_per_country.keys():
                        self.asns_per_country[cc] += [(int(asn), node)]
                    else:
                        self.asns_per_country[cc] = [(int(asn), node)]
            elif 'edge' in target:
                edges = util.csvImport(tg_path, ',', header=False)
                for src, dst in edges:
                    if cc in self.edges_per_country.keys():
                        self.edges_per_country[cc] += [(src, dst)]
                    else:
                        self.edges_per_country[cc] = [(src, dst)]
            else:
                continue
                
    # [STEP 2] Generate a JSON file per each country for d3js
    def generate_json_graph(self):
        # Prepare JSON data type
        def prepare_data(cc, nodes, links):
            json_data = dict()
            json_data["nodes"] = nodes
            json_data["links"] = links
            return json.dumps(json_data, indent=2)

        cnt = 1
        for cc in sorted(set(self.countries)):
            json_file = self.out_dir + os.sep + cc.lower() + '.json'
            try:
                nodes = self._get_nodes_for_json(cc)
                links = self._get_links_for_json(cc)
                print "[%2d] %s: %d ASNs, %d Links" % (cnt, cc, len(nodes), len(links))
                with open(json_file, 'w') as f:
                    f.write(prepare_data(cc, nodes, links))
                cnt += 1
            except:
                pass