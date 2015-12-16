import os
import sys
import subprocess
import logging
import csv
from sys import platform

try:
    from progress.bar import Bar
    import numpy as np
    import matplotlib.pyplot as plt
except:
    logging.error('Required package: progress, matplotlib and numpy')

def csvImport(csvFile, delim, header=True):
    # Reading a csv file and return data
    try:
        with open(csvFile, 'r') as f:
            reader = csv.reader(f, delimiter=delim, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            if header:
                header = reader.next()
            data = [row for row in reader]

    except csv.Error as e:
        logging.warning("Error reading CSV file at line %s: %s" % (reader.linenum, e))
        sys.exit(-1)
        
    return data
    
'''
Extract all ASN from CAIDA data
(src_asn | dst_asn | type)
'''
def extract_asn(f):
    asns = set()
    data = csvImport(f, '|')
    for d in data:
        if d[0][0] == '#':
            continue
        else:
            asns.add(d[0])
            asns.add(d[1])
    return asns
    
'''
Get the country from cymru.com, which returns following format
(AS | CC | Registry | Allocated | AS Name)
    Ex) whois -h whois.cymru.com -v AS10022
        10022   | NZ | apnic    | 2000-04-28 | DSLAK-AS-AP Internet access for Datacom Systems Auckland,NZ
'''
def get_reg_info(caida, saveTo=False):
    def check_platform():
        if platform == 'win32' or not 'linux' in platform:
            logging.error('AS information can be retrieved using whois in linux platform') 
            if 'whois' not in os.system('which whois'):
                logging.error('Check if the linux system has installed "whois"!')
            sys.exit(-1)

    check_platform()
    logging.info('Trying to get the ASN registration info from cymru.com')
    
    if saveTo:
        f = open(saveTo, 'a')
        f.write('AS      | CC | Registry | Allocated  | AS Name\n')
    
    all_asns_caida = sorted(list(extract_asn(caida)))
    print 'Found %d ASNs from CAIDA DB in total' % len(all_asns_caida)
    bar = Bar('\tProcessing: ', max=len(all_asns_caida), fill='=', suffix='%(percent)d%%')
    
    for asn in all_asns_caida:
        bar.next()
        if int(asn):
            p = subprocess.Popen(['whois', '-h', 'whois.cymru.com', '-v', 'AS' + str(asn)], \
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if saveTo:
                try:
                    f.write(out.split('\n')[2]+'\n')
                except:
                    logging.error('Failed to get ASN: %d' % int(asn))
                    pass
            else: 
                out.split('\n')[2]
    f.close()
    bar.finish()
    
    if saveTo:
        print 'All whois data has been saved into %s' % saveTo

def cdf_plot(dataset, colors):
    for data, label, color in zip(dataset, sorted(colors.keys()), [colors[x] for x in sorted(colors.keys())]):
        sorted_data = np.sort(data)
        y = np.arange(len(sorted_data)) / float(len(sorted_data))
        plt.plot(sorted_data, y, c=color, label=label)

    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.grid()
    plt.legend(loc='lower right')
    plt.xlabel('Normalized Index (The higher, the better)')
    plt.ylabel('CDF')

    plt.show()


if __name__ == '__main__':
    pass
    #get_reg_info('20150801.as-rel.txt', saveTo='asn_reg2.txt')
    '''
    data = csvImport('metric_results.csv', ',', header=True)
    metrics = dict()
    metrics['fhi'], metrics['di'], metrics['rwbi'] = [], [], []

    for row in data:
        metrics['fhi'] += [float(row[1])]
        metrics['di'] += [float(row[2])]
        metrics['rwbi'] += [float(row[3])]

    colors = {'DI': 'red', 'FHI': 'green', 'RWBI': 'blue'}
    dataset = [metrics['fhi'], metrics['rwbi'], metrics['di']]
    cdf_plot(dataset, colors)
    '''