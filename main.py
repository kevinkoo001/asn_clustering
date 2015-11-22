import os
import logging
from datetime import *
import draw_graph
import optparse
import do_cluster

LOGFILE = 'georouting.log'

def generate_d3_json():
    in_dir = './CC-edges-labels/data/'    # directory that all edges and links reside in
    out_dir = './asn'                     # output_dir: directory that stores all json files into

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
    if cc not in g.get_all_countries():
        logging.error('No country has been found: %s' % cc)
        sys.exit(1)
    g.plot_per_country(cc)

def check_corelationship(partial=True, DEBUG=False):
    g = generate_graphs()
    g.metric_checker(partial, DEBUG)

if __name__ == '__main__':
    usage  = "Usage: %prog [-d <input_dir> <output_dir>| -t <country code> | -c | -h]"
    usage += "\n   eg: %prog -d ./CC-edges-labels/data/ ./asn/"
    usage += "\n   eg: %prog -t AF"
    usage += "\n   eg: %prog -c (you may need to define [XXX] in draw_graph.py manually) "
    p = optparse.OptionParser(usage=usage, version=0.3)

    p.add_option("-d", "--d3_json", dest="json", action="store_true",
                  help="Generate JSON files for D3js")

    p.add_option("-t", "--topology", dest="topo", action="store_true",
                  help="Draw an ASN topology for a given country")

    p.add_option("-c", "--correlations", dest="correlations", action="store_true",
                  help="Find the cor")

    p.add_option("-g", "--debug", dest="debug", action="store_true",
                  help="Debugging option (console message in details)")

    # Check provided arguments from command line
    (options, args) = p.parse_args()

    logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)

    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    logging.info('[<---------- BEGIN LOGGING --------->]')

    if options.json and len(args) == 2:
        if os.path.exists(args[0]) and os.path.exists(args[1]):
            generate_d3_json()
        else:
            logging.warning('Either provided path does not exist or check the arguments...!')
    elif options.topo:
        if len(args) == 1:
            draw_topology(args[0])
        else:
            logging.warning('Check the arguments for topology...!')
    elif options.correlations:
        if len(args) == 0:
            # [XXX] Change 'partial' value if necessary
            check_corelationship(partial=True, DEBUG=options.debug)
        else:
            logging.warning('Check the arguments for corelationship...!')
    else:
        print 'Something went wrong!'

    logging.info('[<----------- END LOGGING ---------->]')