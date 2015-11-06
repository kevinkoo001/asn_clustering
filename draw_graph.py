import os
import random
import logging
import json
import util

try:
    # http://networkx.github.io/documentation/networkx-1.9.1/examples/index.html
    import networkx as nx
    import matplotlib.pyplot as plt
except importError:
    logging.error('Required library: networkx, matplotlib')

CC_FILE = 'country_code.csv'
CAIDA_FILE = '20150801.as-rel-caida.txt'
ASN_TO_CC = 'asn_reg-cymru.txt'

class Graph:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.countries = set()
        self.edges_per_country = dict()
        self.asns_per_country = dict()
        self.asn_nid = dict()
        self.country_code = dict()

    # Country name, Country Code
    def get_country_by_code(self):
        cc_code = util.csvImport(CC_FILE, ',')
        for cc in cc_code:
             self.country_code[cc[1].strip().upper()] = cc[0].strip()
        return self.country_code

    def get_nodes(self, cc):
        self.asn_nid = {}
        prev_country = ''
        nid = 0     # ASN node ID
        cid = -1    # country id
        asns_data = []
        
        for asn, node in self.asns_per_country[cc]:
            asn_entry = {}
            if prev_country != node:
                cid += 1
            self.asn_nid[asn] = nid
            asn_entry["ASN"] = str(asn)
            asn_entry["country"] = cid
            asn_entry["c_name"] = node
            asns_data.append(asn_entry)
            prev_country = node
            nid += 1
            
        return asns_data
            
    def get_links(self, cc):
        links_data = []
        
        for src, dst in self.edges_per_country[cc]:
            link_entry = {}
            link_entry["source"] = self.asn_nid[int(src)]
            link_entry["target"] = self.asn_nid[int(dst)]
            link_entry["value"] = random.randint(1,10)
            links_data.append(link_entry)
        
        return links_data

    # This is just for drawing json grpah
    def generate_json_graph(self, target_dir):
        # Prepare JSON data type
        def prepare_data(country):
            nodes = self.get_nodes(country)
            links = self.get_links(country)
            json_data = dict()
            json_data["nodes"] = nodes
            json_data["links"] = links
            return json.dumps(json_data, indent=2)
            
        cnt = 1
        for c in self.countries:
            json_file = target_dir + os.sep + c.lower() + '.json'
            try:
                self.get_nodes(c)
                self.get_links(c)
                json_data = prepare_data(c)
                print "[%2d] %s" % (cnt, json_file)
                with open(json_file, 'w') as f:
                    f.write(json_data)
                cnt += 1
            except:
                pass

    # Compute vertex and edge per country from reading previous project format
    def get_vertex_edge_per_country(self):
        for target in os.listdir(self.data_dir):
            tg_path = self.data_dir + target
            cc = target[:2]
            self.countries.add(cc)
            
            # A node represents a country, an edge represents the link between ASN
            if 'label' in target:
                nodes = util.csvImport(tg_path, ',', header=True)
                for asn, node in nodes:
                    if cc in self.asns_per_country.keys():
                        self.asns_per_country[cc] += [(int(asn), node)]
                    else:
                        self.asns_per_country[cc] = [(int(asn), node)]
            elif 'edges' in target:
                edges = util.csvImport(tg_path, ',', header=True)
                for src, dst, type in edges:
                    if cc in self.edges_per_country.keys():
                        self.edges_per_country[cc] += [(src, dst)]
                    else:
                        self.edges_per_country[cc] = [(src, dst)]
            else:
                continue

    '''
    Compute vertex and edge per country from reading CAIDA_FILE and ASN_TO_CC
    CAIDA_FILE format
        src|dst|type (peer, )
    ASN_TO_CC format
        AS      | CC | Registry | Allocated  | AS Name
    '''
    def get_vertex_edge_per_country2(self):
        c_code = self.get_country_by_code()
        asn_mappings_data = util.csvImport(ASN_TO_CC, '|', header=True)
        asn_to_cc = {}
        ignore_asns = set()

        for a in asn_mappings_data:
            asn, cc, full_name = a[0].strip(), a[1].strip().upper(), a[4].strip()
            # Do not bother if empty CC or ZZ (not allocated)
            if len(cc) == 0 or 'ZZ' in full_name:
                ignore_asns.add(int(asn))
            else:
                asn_to_cc[int(asn)] = full_name[-2:] if cc == 'EU' and cc != full_name[-2:] else cc

        print len(asn_to_cc), len(set(asn_to_cc.values())), len(c_code)

        collected_ccs = list(set(asn_to_cc.values()))
        ignore_ccs = set()
        for cc in collected_ccs:
            if cc.strip() not in c_code.keys():
                ignore_ccs.add(cc)

        print 'Ignored country code: %d' % len(ignore_ccs)
        print 'Ignored ASNs: %d' % len(ignore_asns)

        caida_data = util.csvImport(CAIDA_FILE, '|', header=False)

        for cd in caida_data:
            if cd[0][0] != '#':
                src_asn, dst_asn, type = int(cd[0]), int(cd[1]), int(cd[2])
                if src_asn in list(ignore_asns) or dst_asn in list(ignore_asns):
                    #print 'Either %s or %s does not belong to any country..' % (src_asn, dst_asn)
                    pass
                else:
                    try:
                        # ASNs per country
                        cc = asn_to_cc[src_asn]
                        if cc in self.asns_per_country.keys():
                            self.asns_per_country[cc] += [(dst_asn, asn_to_cc[dst_asn])]
                            self.asns_per_country[cc] += [(src_asn, asn_to_cc[src_asn])]
                        else:
                            self.asns_per_country[cc] = [(dst_asn, asn_to_cc[dst_asn])]
                            self.asns_per_country[cc] = [(src_asn, asn_to_cc[src_asn])]

                        # Edges per country
                        if cc in self.edges_per_country.keys():
                            self.edges_per_country[cc] += [(src_asn, dst_asn)]
                        else:
                            self.edges_per_country[cc] = [(src_asn, dst_asn)]
                    except:
                        pass
        '''
        for c in list(sorted(set(asn_to_cc.values()) - ignore_ccs)):
            # print self.edges_per_country['AE']
            # print self.asns_per_country['AE']
            try:
                print '[%s] Edges %d:, Nodes: %d' % (c, len(self.edges_per_country[c]), len(self.asns_per_country[c]))
            except:
                pass
        '''

    def create_graph(self, target, saveTo=False):
        G_per_country = {}
        
        for c in self.asns_per_country.keys():
            G = nx.Graph()
            all_asns = set()
            
            # Adding nodes to the graph for each country
            for asn, country in self.asns_per_country[c]:
                all_asns.add(asn)
            G.add_nodes_from(list(all_asns))
            G_per_country[c] = G
        
        for c in self.edges_per_country.keys():
            all_edges = set()
            
            # Adding edges to the graph for each country
            for src, dst in self.edges_per_country[c]:
                all_edges.add((int(src), int(dst)))
            G_per_country[c].add_edges_from(list(all_edges))
            
        #for c in sorted(self.asns_per_country.keys()):
        #    print c, G_per_country[c].number_of_nodes(), G_per_country[c].number_of_edges()

        nx.draw(G)
        target_c = target #G_per_country.keys()[-1]
        pos = nx.spring_layout(G, iterations=100) # position for all nodes
        asns_in_target = [asn for asn,c in self.asns_per_country[target_c] if c==target_c]
        asns_connected = [asn for asn,c in self.asns_per_country[target_c] if c!=target_c]
        labels = {}
        for asn,c in self.asns_per_country[target_c]:
            labels[asn] = c
        #print target_c, len(self.asns_per_country[target_c]), len(asns_in_target), len(asns_connected)
        #print asns_in_target, asns_connected

        # nodes
        try:
            plt.title(target_c)
            nx.draw_networkx_nodes(G, pos, nodelist=asns_in_target, node_size=800, alpha=0.8, node_color='r')
            nx.draw_networkx_nodes(G, pos, nodelist=asns_connected, node_size=500, alpha=0.5, node_color='b')
            nx.draw_networkx_labels(G, pos, labels, font_size=10)
        except:
            print 'Something went wrong!!'
            pass
            
        plt.axis('off')
        plt.show()

        return G_per_country[target]
        '''
        if saveTo:
            for c in self.edges_per_country.keys():
                nx.draw(G_per_country[c])
                plt.show()
        '''

if __name__ == '__main__':
    logging.basicConfig(filename='detection.log', level=logging.DEBUG)
    g = Graph('../Previous_BGP/edge_lablel_data/')
    g.get_vertex_edge_per_country2()
    #g.generate_json_graph('asn')
    g.create_graph('KR')

