import os
import random
import logging
import json
import util

try:
    import networkx as nx
    import matplotlib.pyplot as plt
except importError:
    logging.error('Required library: networkx, matplotlib')

ABBR = ["AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AP", "AR", "AS", "AT", "AU", "AW", "AX", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BM", "BN", "BO", "BQ", "BR", "BS", "BT", "BW", "BY", "BZ", "CA", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN", "CO", "CR", "CU", "CV", "CW", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE", "EG", "ER", "ES", "ET", "EU", "FI", "FJ", "FM", "FO", "FR", "GA", "GB", "GM", "GN", "GP", "GQ", "GR", "GT", "GU", "GW", "GY", "HK", "HN", "HR", "HT", "HU", "IE", "IL", "IM", "IQ", "IR", "IS", "JE", "JM", "JO", "JP", "KE", "KG", "KH", "KN", "KR", "KW", "KY", "KZ", "LA", "LB", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "MF", "MG", "MK", "ML", "MM", "MN", "MO", "MR", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PM", "PR", "PS", "PT", "PW", "PY", "QA", "RE", "RS", "RW", "SA", "SB", "SC", "SD", "SE", "SG", "SI", "SK", "SL", "SM", "SN", "SO", "SR", "SS", "SV", "SX", "SY", "SZ", "TD", "TG", "TJ", "TL", "TM", "TN", "TO", "TR", "TT", "TZ", "UG", "US", "UY", "UZ", "VC", "VE", "VG", "VI", "VN", "VU", "WS", "YE", "YE", "YT", "ZA", "ZM", "ZW"]
CNTR = ["Andorra", "United Arab Emirates", "Afghanistan", "Antigua and Barbuda", "Anguilla", "Albania", "Armenia", "Angola", "X2", "Argentina", "American Samoa", "Austria", "Australia", "Aruba", "X3", "Azerbaijan", "Bosnia and Herzegovina", "Barbados", "Bangladesh", "Belgium", "Burkina Faso", "Bulgaria", "Bahrain", "Burundi", "Benin", "Bermuda", "Brunei", "Bolivia", "X4", "Brazil", "Bahamas", "Bhutan", "Botswana", "Belarus", "Belize", "Canada", "Democratic Republic of the Congo", "Central African Republic", "Republic of the Congo ", "Switzerland", "Ivory Coast", "Cook Islands", "Chile", "Cameroon", "China", "Colombia", "Costa Rica", "Cuba", "Cape Verde", "Curacao", "Cyprus", "Czech Republic", "Germany", "Djibouti", "Denmark", "Dominica", "Dominican Republic", "Algeria", "Ecuador", "Estonia", "Egypt", "Eritrea", "Spain", "Ethiopia ", "European Union", "Finland ", "Fiji", "Micronesia", "Faroe Islands", "France", "Gabon", "United Kingdom", "Gambia", "Guinea", "X5", "Equatorial Guinea", "Greece", "Guatemala", "Guam", "Guinea-Bissau", "Guyana", "Hong Kong", "Honduras", "Croatia", "Haiti", "Hungary", "Ireland", "Israel", "Isle of Man", "Iraq", "Iran", "Iceland", "Jersey", "Jamaica", "Jordan", "Japan", "Kenya", "Kyrgyzstan", "Cambodia", "Saint Kitts and Nevis", "South Korea", "Kuwait", "Cayman Islands", "Kazakhstan", "Laos", "Lebanon", "Liechtenstein", "Sri Lanka", "Liberia", "Lesotho", "Lithuania", "Luxembourg", "Latvia", "Libya", "Morocco", "Monaco", "Moldova", "Saint Martin", "Madagascar", "Macedonia", "Mali", "Myanmar", "Mongolia", "Macao", "Mauritania", "Malta", "Mauritius", "Maldives", "Malawi", "Mexico", "Malaysia", "Mozambique", "Namibia", "New Caledonia", "Niger", "X1", "Nigeria", "Nicaragua", "Netherlands", "Norway", "Nepal", "Nauru", "Niue", "New Zealand", "Oman", "Panama", "Peru", "French Polynesia", "Papua New Guinea", "Philippines", "Pakistan", "Saint Pierre and Miquelon", "Puerto Rico", "Palestine", "Portugal", "Palau", "Paraguay", "Qatar", "Reunion", "Serbia", "Rwanda", "Saudi Arabia", "Solomon Islands", "Seychelles", "Sudan", "Sweden", "Singapore", "Slovenia", "Slovakia", "Sierra Leone", "San Marino", "Senegal", "Somalia", "Suriname", "South Sudan", "El Salvador", "Sint Maarten", "Syria", "Swaziland", "Chad", "Togo", "Tajikistan", "East Timor", "Turkmenistan", "Tunisia", "Tonga", "Turkey", "Trinidad and Tobago", "Tanzania", "Uganda", "United State", "Uruguay", "Uzbekistan", "Saint Vincent and the Grenadines", "Venezuela", "British Virgin Islands", "U.S. Virgin Islands", "Vietnam", "Vanuatu", "Samoa", "Yemen", "Yemen", "Mayotte", "South Africa", "Zambia", "Zimbabwe"]
    
class Graph:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.countries = set()
        self.edges_per_country = dict()
        self.asns_per_country = dict()
        self.asn_nid = dict()
        self.country_code = dict()
        
    def __country_by_code(self):
        for i in range(len(ABBR)):
            self.country_code[ABBR[i]] = CNTR[i]
            #print ABBR[i] + ', ' + CNTR[i]
        
    def get_nodes(self, country_id):
        self.asn_nid = {}
        prev_country = ''
        nid = 0     # ASN node ID
        cid = -1    # country id
        asns_data = []
        
        for asn, node in self.asns_per_country[country_id]:
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
            
    def get_links(self, country_id):
        links_data = []
        
        for src, dst in self.edges_per_country[country_id]:
            link_entry = {}
            link_entry["source"] = self.asn_nid[int(src)]
            link_entry["target"] = self.asn_nid[int(dst)]
            link_entry["value"] = random.randint(1,10)
            links_data.append(link_entry)
        
        return links_data

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
                
    def get_vertex_edge_per_country(self):
        self.__country_by_code()
        for target in os.listdir(self.data_dir):
            tg_path = self.data_dir + target
            country_id = target[:2]
            self.countries.add(country_id)
            
            # A node represents a country, an edge represents the link between ASN
            if 'label' in target:
                nodes = util.csvImport(tg_path, ',', header=True)
                for asn, node in nodes:
                    if country_id in self.asns_per_country.keys():
                        self.asns_per_country[country_id] += [(int(asn), node)]
                    else:
                        self.asns_per_country[country_id] = [(int(asn), node)]
            elif 'edges' in target:
                edges = util.csvImport(tg_path, ',', header=True)
                for src, dst, type in edges:
                    if country_id in self.edges_per_country.keys():
                        self.edges_per_country[country_id] += [(src, dst)]
                    else:
                        self.edges_per_country[country_id] = [(src, dst)]
            else:
                continue
        
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
        '''
        nx.draw(G)
        target_c = target #G_per_country.keys()[-1]
        pos = nx.spring_layout(G, iterations=100) # position for all nodes
        asns_in_target = [asn for asn,c in self.asns_per_country[target_c] if c==target_c]
        asns_connected = [asn for asn,c in self.asns_per_country[target_c] if c!=target_c]
        labels = {}
        for asn,c in self.asns_per_country[target_c]:
            labels[asn] = c
        print target_c, len(self.asns_per_country[target_c]), len(asns_in_target), len(asns_connected)
        print asns_in_target, asns_connected

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
        '''
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
    g.get_vertex_edge_per_country()
    #g.generate_json_graph('asn')
    g.create_graph('AF')
