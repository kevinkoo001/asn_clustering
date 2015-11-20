import sys
import os
import draw_graph
import optparse
import do_cluster

def generate_d3_json():
    in_dir = './CC-edges-labels/data/'    # directory that all edges and links reside in
    out_dir = './asn_json'                # output_dir: directory that stores all json files into

    d3 = draw_graph.D3_json(in_dir, out_dir) # Create a d3js object
    d3.get_vertex_edge_per_country()         # Generate graphs per country
    d3.generate_json_graph()                 # Generate json files per country

def generate_graphs():
    G = draw_graph.Graph()
    G.get_vertex_edge_per_country()
    G.create_all_graphs()
    return G

def draw_topology(cc):
    g = generate_graphs()
    g.plot_per_country(cc)

def check_corelationship():
    g = generate_graphs()
    g.decision_censorship()

if __name__ == '__main__':
    p = optparse.OptionParser(version=0.3)

    p.add_option("-d", "--gen_d3_json", dest="json", action="store_true",
                  help="Generate JSON files upon G(V,E) for D3js")

    p.add_option("-t", "--topology", dest="topo", action="store_true",
                  help="Plot an ASN topology for a given country")

    p.add_option("-c", "--corelationship", dest="corelationship", action="store_true",
                      help="BPF filter that specifies a subset of the traffic to be monitored")

    # Check provided arguments from command line
    try:
        (options, args) = p.parse_args()
    except:
        print 'What have you done??!'
        sys.exit(1)

    if options.json and len(args) == 0:
        generate_d3_json()
    elif options.topo and len(args) == 1:
        draw_topology(args[2])
    elif options.corelationship and len(args) == 0:
        check_corelationship()
    else:
        print 'Something went wrong!'
        sys.exit(1)