import os
import sys
import random
import logging
import json
import util

try:
    # http://networkx.github.io/documentation/networkx-1.9.1/examples/index.html
    import networkx as nx
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
except ImportError:
    logging.error('Required library: networkx, numpy, matplotlib')

CC_FILE = 'country_code.csv'
CAIDA_FILE = 'caida_traceroute_data.txt'
ASN_TO_CC = 'asn_reg-cymru.txt'
DIR_TO_STORE = './sub-graphs/topologies/'

CSRSP_CC = ['BH', 'BY', 'CU', 'IR', 'PK', 'SA', 'SD',
            'SY', 'TM', 'AE', 'UZ', 'VN', 'EG', 'MM', 'TN',
            'KZ', 'MY', 'LK', 'TH', 'TR', 'JO', 'LY', 'TJ', 'VE', 'YE',
            'AU', 'KR', 'US', 'CN', 'FR', 'RU', 'IN', 'GB'] # Large Size

METRIC_RESULT = 'metric_results.csv'

# ['ER', 'KP', 'ET'] // Has censorship but no ASN found

class Graph:
    def __init__(self):
        self.FHI = dict()   # Free House Index (2012): the lower, the better
        self.DI = dict()    # Democratic Index (2014): the higher, the better
        self.RWBI = dict()  # Reporters Without Borders Index (2015): the lower, the better
        self.asn_to_cc = dict()
        self.edges_per_country = dict()
        self.asns_per_country = dict()
        self.country_code = dict()
        self.G_per_country = dict()

    # Country name, Country Code, FHI
    def read_known_countries(self):
        cc_code = util.csvImport(CC_FILE, ',', header=True)
        for cc in cc_code:
            self.country_code[cc[0].strip().upper()] = cc[1].strip()
            self.FHI[cc[0].strip().upper()] = float(cc[2].strip())
            self.DI[cc[0].strip().upper()] = float(cc[3].strip())
            self.RWBI[cc[0].strip().upper()] = float(cc[4].strip())
        
    def get_all_countries(self):
        return list(set(self.asns_per_country.keys()))

    def get_country_by_cc(self):
        return self.country_code

    def get_fhi_per_country(self, cc):
        try:
            fhi = self.FHI[cc]
        except KeyError:
            logging.error('Can\'t find the country code: %s', cc)
            sys.exit(1)
        return fhi

    def get_di_per_country(self, cc):
        try:
            di = self.DI[cc]
        except KeyError:
            logging.error('Can\'t find the country code: %s', cc)
            sys.exit(1)
        return di

    def get_rwbi_per_country(self, cc):
        try:
            rwbi = self.RWBI[cc]
        except KeyError:
            logging.error('Can\'t find the country code: %s', cc)
            sys.exit(1)
        return rwbi

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
        logging.info('Loading all vertices and edges per country...!')
        logging.info('\t[1] Registered Country Codes: %d' % len(self.country_code))
        logging.info('\t[2] Identified ASNs: %d' % len(self.asn_to_cc))
        logging.info('\t[3] Countries which possess one or more ASNs: %d' % len(collected_ccs))
        
        for cc in list(collected_ccs):
            if cc.strip() not in self.country_code.keys():
                ignore_ccs.add(cc)

        logging.info('\t[4] Ignored (unidentified) country code: %d' % len(ignore_ccs))
        logging.info('\t[5] Ignored (unidentified) ASNs: %d' % len(ignore_asns))

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
        
        logging.info('\t[6] Ignored connectivity due to either [4] or [5]: %d/%d (%2.3f%%)' \
                % (cnt, total, round(cnt/float(total), 2)))
        
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

    # Returns (FHI, metric) per each country
    def inspect_metrics(self, cc, metrics, partial=True, DEBUG=False):
        def remove_foriegn_cc(G, foreign):
            # Remove foreign nodes and edges for the accurate metrics, if necessary
            G.remove_edges_from([e for e in G.edges() if e[0] in foreign or e[1] in foreign])
            for n in list(foreign):
                try:
                    G.remove_node(n)
                except:
                    pass
            return G

        def special_handler(m, v):
            for x in m:
                v[x] = -1
            return v

        G = self.get_country_graph(cc)

        metrics = metrics[4:]

        metric_values = {}
        scale = self.G_per_country[cc].number_of_edges() + self.G_per_country[cc].number_of_nodes()
        if scale <= 1000:
            logging.info('\t[%s] Too small nodes or edges to decide..' % cc)
            return special_handler(metrics, metric_values)

        elif scale > 5000:
            logging.info('\t[%s] TOO BIG.. just skipped!!' % cc)
            return special_handler(metrics, metric_values)

        else:
            domestic = self.get_domestic_asns(cc)
            foreign = self.get_foreign_asns(cc)
            asns_connected_to_foreign = self.get_asns_connected_to_foreign(cc)

            n_foreign_asns = len(foreign)
            n_asns_out_conn = len(asns_connected_to_foreign)

            '''
            [Notes]
            Default metrics
                n_nodes
                n_edges
                n_foreign_asns
                n_asns_out_conn
            If the metric requires the foreign nodes, then use self.get_country_graph(cc) instead of G
            Several features (=metrics) to consider from networkx libraries
                m1. average_clustering: return the average clustering coefficient (float)
                m2. average_degree_connectivity: return the average nearest neighbor degree of nodes with degree k (dict)
                m3. average_neighbor_degree: return the average degree of the neighborhood of each node (dict)
                m4. average_node_connectivity: return the average connectivity (float)
                m5. average_shortest_path_length: return the average shortest path length (float)
                m6. surveillance_index (si) = 1/x + 1/y
                    x: # of domestic ASNs which connects to foreign countries / # of total ASNs in a country
                    y: # of domestic ASNs which connects to foreign countries / # of foreign ASNs connected to a country

                [Distance Measures]
                m7.  Center: return the center of G, the set of nodes with eccentricity equal to radius (list)
                m8.  Diameter: return the diameter of G (int)
                m9.  Eccentricity: return the eccentricity that a node v is the maximum distance from v to all other nodes (dict)
                m10. Periphery: return the periphery of the graph G (list)
                m11. Radius: return the radius (the minimum eccentricity) of the graph G (float)
                m12. Density: return the density of a graph (float; d = 2m/n(n-1), where n: # of nodes, m: # of edges)
                m13. Components: return the number of connected components in G (int)
            '''

            G = remove_foriegn_cc(G, foreign)

            if len(G) <= 1 or len(foreign) == 0:
                logging.info('\t[%s] No foreign node or graph is too small after removing foreign countries' % cc)
                return special_handler(metrics, metric_values)

            metric_values[metrics[0]] = G.number_of_nodes()
            metric_values[metrics[1]] = G.number_of_edges()
            metric_values[metrics[2]] = n_foreign_asns
            metric_values[metrics[3]] = n_asns_out_conn

            metric_values[metrics[4]] = nx.algorithms.average_clustering(G) # m1
            metric_values[metrics[5]] = np.mean(nx.algorithms.average_degree_connectivity(G).values()) # m2
            metric_values[metrics[6]] = np.mean(nx.algorithms.average_neighbor_degree(G).values()) # m3
            metric_values[metrics[7]] = nx.algorithms.average_node_connectivity(G) # m4

            x = len(foreign) / float(len(domestic) + len(foreign))
            y = float(len(asns_connected_to_foreign)) / len(foreign)
            metric_values[metrics[9]] = 1/x + 1/y      # m6
            metric_values[metrics[16]] = nx.number_connected_components(G) # m13

            # The metrics below only works when G is all connected
            # If multiple components are discovered, then use the largest connected component for the metric
            if not nx.is_connected(G):
                G = max(nx.connected_component_subgraphs(G), key=len)

            metric_values[metrics[8]] = nx.algorithms.average_shortest_path_length(G) # m5
            metric_values[metrics[10]] = np.mean(nx.algorithms.distance_measures.center(G)) # m7
            metric_values[metrics[11]] = nx.algorithms.distance_measures.diameter(G) # m8
            metric_values[metrics[12]] = np.mean(nx.algorithms.distance_measures.eccentricity(G).values()) # m9
            metric_values[metrics[13]] = np.mean(nx.algorithms.distance_measures.periphery(G)) # m10
            metric_values[metrics[14]] = nx.algorithms.distance_measures.radius(G) # m11
            metric_values[metrics[15]] = nx.classes.function.density(G) # m12

            return metric_values

    # Compute a pre-defined metric to choose meaningful features for clustering!
    def metric_checker(self, partial=True, DEBUG=False):
        metrics_cc = {}
        fhi_cc, di_cc, rwbi_cc = {}, {}, {}

        targets = []
        metrics = ['cc', 'fhi', 'di', 'rwbi', 'a. n_nodes', 'b. n_edges', 'c. n_foreign_asns', 'd. n_asns_out_conn',
                   'e. average_clustering', 'f. average_degree_connectivity', 'g. average_neighbor_degree',
                   'h. average_node_connectivity', 'i. surveillance_index',
                   'j. average_shortest_path_length', 'k. center', 'l. diameter', 'm. eccentricity',
                   'n. periphery', 'o. radius', 'p. density', 'q. components']

        logging.info('Extracting indexes for metric computation...')

        fhi = filter(lambda x: x>0, self.FHI.values())
        max_fhi, min_fhi = max(fhi), min(fhi)
        di = filter(lambda x: x>0, self.DI.values())
        max_di, min_di = max(di), min(di)
        rwbi = filter(lambda x: x>0, self.RWBI.values())
        max_rwbi, min_rwbi = max(rwbi), min(rwbi)

        logging.info('\tFound %d countries for FHI (Free House Index)', len(fhi))
        logging.info('\tFound %d countries for DI (Democracy Index)', len(di))
        logging.info('\tFound %d countries for RWBI (Reporters Without Borders Index)', len(rwbi))

        logging.info('Inspecting the metrics per each country...')

        # Set up the target countries to be considered
        # For simplicity, take only countries that all index values are available
        for cc in sorted(self.get_all_countries()):
            if self.get_fhi_per_country(cc) > 0 and self.get_di_per_country(cc) > 0 and self.get_rwbi_per_country(cc) > 0:
                # Indexes are normalized as [0 - 1],
                fhi_cc[cc] = 1 - ((self.get_fhi_per_country(cc) - min_fhi) / (max_fhi - min_fhi))
                di_cc[cc] = (self.get_di_per_country(cc) - min_di) / (max_di - min_di)
                rwbi_cc[cc] = 1 - ((self.get_rwbi_per_country(cc) - min_rwbi) / (max_rwbi - min_rwbi))

                targets.append(cc)
                logging.info('\t[%s] Comptuting metrics...', cc)
                metric_values = self.inspect_metrics(cc, metrics, partial, DEBUG)
                metrics_cc[cc] = [metric_values[m] for m in sorted(metric_values.keys())]

        if os.path.isfile(METRIC_RESULT):
            f = open(METRIC_RESULT, 'a')
        else:
            f = open(METRIC_RESULT, 'w')
            headers = ''
            for m in metrics:
                headers += m + ','
            f.write(headers + '\n')

        for cc in sorted(targets):
            if metrics_cc[cc][4] > 0:
                f.write(cc + ', ' + str(fhi_cc[cc]) + ', ' + str(di_cc[cc]) + ', ' + str(rwbi_cc[cc]) + ', ')
                for metric in metrics_cc[cc]:
                    f.write(str(metric) + ', ')
                f.write('\n')

        X1 = [fhi_cc[x] for x in sorted(targets)]
        X2 = [di_cc[x] for x in sorted(targets)]
        X3 = [rwbi_cc[x] for x in sorted(targets)]

        print "Processed %d countries...!" % len(targets)

        for i in range(len(metrics_cc[cc])):
            Y = []
            for cc in sorted(targets):
                Y.append(metrics_cc[cc][i])
            print '\tFHI : %.3f' % np.corrcoef(X1, Y, bias=0)[1, 0]
            print '\tDI  : %.3f' % np.corrcoef(X2, Y, bias=0)[1, 0]
            print '\tRWBI: %.3f' % np.corrcoef(X3, Y, bias=0)[1, 0]

        f.close()

        '''
        X, Y = [], []
        for cc in sorted(self.get_all_countries()):
            x, y = self.inspect_metrics(cc, partial, DEBUG)
            X.append(x)
            Y.append(y)

        plt.suptitle('Free House Index VS Metric')
        plt.xlabel('FHI')
        # [XXX] Label here accordingly
        plt.ylabel('Avg clustering')

        axes = plt.gca()
        axes.set_xlim([0, int(max(X) * 1.05)])
        axes.set_ylim([0, int(max(Y) * 1.05)])
        plt.grid(True)

        targets = [(x, y) for x, y in zip(X, Y) if x > 0 and y > 0]
        plt.scatter(np.array([x for x, y in targets]), np.array([y for x, y in targets]), color='blue')

        CX, CY = [], []
        for cc in sorted(CSRSP_CC):
            x, y = self.inspect_metrics(cc, partial, DEBUG)
            CX.append(x)
            CY.append(y)

        c_targets = [(x, y) for x, y in zip(CX, CY) if x > 0 and y > 0]
        plt.scatter(np.array([x for x, y in c_targets]), np.array([y for x, y in c_targets]), color='red')

        if partial:
            logging.info('The countries below have been skipped...!')
            logging.info('\t[1] No foreign connection found: %d' % (X.count(-1) + CX.count(-1)))
            logging.info('\t[2] Only 1 connection to the outside: %d' % (X.count(-2) + CX.count(-2)))
            logging.info('\t[3] Too small nodes or edges to decide: %d' % (X.count(-3) + CX.count(-3)))
            logging.info('\t[4] TOO BIG.. just skipped: %d' % (X.count(-99) + CX.count(-99)))
            logging.info('\t[5] Target countries to investigate: %d' % \
                         (len(self.get_all_countries()) - len([skipped for skipped in X + CX if skipped < 0])))

        logging.info('\tCorrelation Coefficient Statistics: %.5f' % np.corrcoef(X + CX, Y + CY, bias=0)[1, 0])
        plt.show()
        '''

# This class is to draw topologies using d3js only
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