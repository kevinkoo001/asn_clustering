#!/usr/bin/python
import pp
import sys
from datetime import datetime
from radix import Radix
import json
import ripe.atlas.sagan
import pycountry
from ripe.atlas.cousteau import ProbeRequest
import subprocess
import pdb
from Atlas import Measure
from Atlas import MeasurementFetch
from Atlas import MeasurementInfo
from Atlas import MeasurementPrint
from Atlas import MeasurementEnhance
import time

ATLAS_API_KEY = "5f35d4a7-b7d3-4ab8-b519-4fb18ebd2ead"
now = str( datetime.now() ).split( '.' )[ 0 ]

nonRoutableIPs = Radix()
nonRoutableIPs.add( '192.168.0.0/16' )
nonRoutableIPs.add(  '10.0.0.0/8' )
nonRoutableIPs.add( '172.16.0.0/16' )

country_name = sys.argv[ 1 ]
if len( sys.argv ) < 3:
    dry_run = False
else:
    dry_run = True

country_list = list(pycountry.countries)
country_dict = dict( ( x.name, x.alpha2 ) for x in country_list )

rtree = Radix()
prefixToAsnMapFile = 'data-add-RIPE.txt'
with open( prefixToAsnMapFile ) as ptoasnmap:
    contents = ptoasnmap.read()
    lines = contents.split( '\n' )
    for l in lines:
        if not l:
            continue
        asn, prefix = l.split()
        rnode = rtree.add( prefix )
        rnode.data[ 'asn' ] = asn

def getASInfo( ip ):
    asn = None
    if ip == 'None':
        return asn
    try:
        node = rtree.search_best( ip )
    except: pdb.set_trace()
    if node:
        asn = node.data[ 'asn' ]
    return asn

def get_asn_links( iproute ):
    for hop, ip in iproute.iteritems():
        print getASInfo( ip )
        
def get_ip_route( data ):
    route = {}
    hopcount = 0
    incomplete = 0
    dst = data[ 'dst_addr' ]
    src = data[ 'src_addr' ]
    if not nonRoutableIPs.search_best( src ):
        route[ hopcount ] = src
    hopcount += 1
    hops = data.get( 'result', [] )
    for hop in hops:
        if 'result' in hop:
            res = hop[ 'result' ]
            ipsAtHop = [ x[ 'from' ] for x in res if 'from' in x ]
            if not ipsAtHop:
                incomplete += 1
            else:
                ip = ipsAtHop[ 0 ]
                if not nonRoutableIPs.search_best( ip ):
                    route[ hopcount ] = ip
        else:
            route[ hopcount ] = None
            incomplete += 1
        hopcount += 1
    if not nonRoutableIPs.search_best( dst ):
        route[ hopcount ] = dst
    return route

def filter_cruft( data ):
    if 'result' in data:
        res = data['result']
        for hop_idx, hop in enumerate( res ):
            if 'result' in hop:
                hop['result'] = [hr for hr in hop['result'] if 'edst' not in hr]
    return data

def get_country_code( country_name ):
    if country_name in country_dict:
        return country_dict[ country_name ]
    country_code = [ country_dict[ key ] for key in country_dict.keys()
                     if country_name.lower() in key.lower() ][ 0 ]
    return country_code
                                    
def get_asn_list( country_name ):
    country_code = get_country_code( country_name )
    output = subprocess.check_output(
        "curl www.cc2asn.com/data/%s_asn" % country_code.lower(), shell=True )
    return [ asn for asn in output.split( '\n' ) if asn ]
    
def get_probes( country_name, source=False ):
    country_code = get_country_code( country_name )
    filters = { "country_code": country_code }
    probes = ProbeRequest( **filters )
    probe_list = []
    if source:
        for p in probes:
            if 'address_v4' in p and p['address_v4'] and \
               'system-ipv4-works' in p['tags']:
                probe_list.append( p[ 'id' ] )
    else:
        for p in probes:
            if 'address_v4' in p and p['address_v4'] and \
               'system-ipv4-works' in p['tags']:
                probe_list.append( p[ 'address_v4' ] )
    return probe_list

def get_geo_distributed_probes( source=False ):
    probes = []
    probes.extend( get_probes( 'United States', source=source )[ :5 ] )
    probes.extend( get_probes( 'Egypt', source=source )[ : 2] )
    probes.extend( get_probes( 'Brazil', source=source )[ : 4 ] )
    probes.extend( get_probes( 'Russia', source=source )[ : 4 ] )
    probes.extend( get_probes( 'China', source=source )[ : 4 ] )
    probes.extend( get_probes( 'Australia', source=source )[ : 4 ] )
    probes.extend( get_probes( 'United Kingdom', source=source )[ : 4 ] )
    probes.extend( get_probes( 'India', source=source )[ : 3 ] )
    probes.extend( get_probes( 'South Africa', source=source )[ : 3 ] )
    probes.extend( get_probes( 'Jordan', source=source )[ : 3 ] )
    probes.extend( get_probes( 'Mexico', source=source )[ : 3 ] )
    probes.extend( get_probes( 'France', source=source )[ : 3 ] )
    probes.extend( get_probes( 'Japan', source=source )[ : 3 ] )
    probes.extend( get_probes( 'Norway', source=source )[ : 3 ] )
    return probes

def run_measurement( country_name, out=True ):
    msms = []
    
    if out:
        # If measurement is running from inside the country to outside it:
        source_probes = get_probes( country_name, source=True )[ : 50 ]
        dest_probes = get_geo_distributed_probes()
    else:
        # If measurement is running from outside the country to inside it:
        source_probes = get_geo_distributed_probes( source=True )
        dest_probes = get_probes( country_name )[: 50]
    print len( source_probes ), len( dest_probes )
    
    for dest in dest_probes:
        try:
            msm_id = Measure.oneofftrace(
                source_probes, dest, af=4, paris=1,
                description="ASN graph for %s: testing traceroute to %s" % ( country_name, dest ) )
            if msm_id:
                msms.append( { 'source': source_probes, 'destination': dest, 'msm': msm_id } )
        except:
            time.sleep( 100 )
            pdb.set_trace()
            pass
    return msms

asns = get_asn_list( country_name )
if country_name.lower() == 'china':
    asns.extend( get_asn_list( 'Hong Kong' ) )
    
with open( 'asgraph-sep01-%s.json' % country_name ) as f:
    mesh_graph = json.load( f )

edges = mesh_graph[ "edges" ]
nodes = mesh_graph[ "nodes" ]
nodes_dict = {}
final_graph = []

for node in nodes:
    key = node[ 'id' ]
    nodes_dict[ key ] = node[ 'name' ]

for edge in edges:
    src = nodes_dict[ edge['source'] ]
    dst = nodes_dict[ edge['target'] ]
    final_graph.append( frozenset( ( src, dst ) ) )

print "From the mesh traceroute, found %d links" % len( final_graph )
print "Any duplicates? Length with dups removed: %d" % len( frozenset( final_graph ) )

if dry_run:
    with open( 'msms_out_%s.json' % country_name ) as fi:
        msms_out = json.load( fi )
    with open( 'msms_in_%s.json' % country_name ) as fi:
        msms_in = json.load( fi )
else:
    print "Doing our own measurement on %s.." % country_name
    msms_out = run_measurement( country_name )
    with open( 'msms_out_%s_%s.json' % ( country_name, now ), "w" ) as fi:
        json.dump( msms_out, fi )
    print "Giving the measurements time to finish before starting the new ones.."
    time.sleep( 200 )
    msms_in = run_measurement( country_name, out=False )
    with open( 'msms_in_%s_%s.json' % ( country_name, now ), "w" ) as fi:
        json.dump( msms_in, fi )

def wrapper( data ):
    from Atlas import MeasurementEnhance
    from radix import Radix
    return MeasurementEnhance.aslinksplus( data, Radix() )
    
def append_to_graph( msms ):
    as_links = []
    job_server = pp.Server()
    for mmt in msms:
        msm_id = mmt[ 'msm' ]
        jobs = []
        for data in MeasurementFetch.fetch( msm_id ):
            data = filter_cruft( data )
            as_links_func = job_server.submit( wrapper, args=(data,) )
            jobs.append( as_links_func )

        for job in jobs:
            as_links.extend( job()[ 'links' ] )
            
    for link in as_links:
        if link[ 'src' ] in asns or link[ 'dst' ] in asns:
            print (link['src'], link['dst'] )
            final_graph.append( frozenset( (link['src'], link['dst'] ) ) )
                
append_to_graph( msms_out )
append_to_graph( msms_in )

# Getting rid of the duplicates
final_graph = list( frozenset( final_graph ) )
domestic_edges = []
domestic_nodes = []
nodes_list = []
edges_list = []

for e in final_graph:
    e_tuple = list( e )
    edges_list.append( { 'source': e_tuple[ 0 ], 'target': e_tuple[ 1 ] } )
    nodes_list.extend( e_tuple )
    if e_tuple[ 0 ] in asns and e_tuple[ 1 ] in asns:
        domestic_edges.append( { 'source': e_tuple[ 0 ], 'target': e_tuple[ 1 ] } )
        domestic_nodes.extend( e_tuple )

nodes_list = list( frozenset( nodes_list ) )
domestic_nodes = list( frozenset( domestic_nodes ) )

with open( "asgraph-%s-%s.json" % ( country_name, now ), "w" ) as out:
    json.dump( { 'nodes': nodes_list, 'edges': edges_list}, out )

with open( "asgraph-%s-domestic-%s.json" % ( country_name, now ), "w" ) as out:
    json.dump( { 'nodes': domestic_nodes, 'edges': domestic_edges }, out )
