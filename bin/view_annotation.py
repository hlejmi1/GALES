#!/usr/bin/env python3

"""

Starts a local HTTP server in order to visualize an annotation.

Performs the following computes on first execution, saving files
within the --input_directory so that these don't have to be re-run
on future executions:

1. Parse the FASTA file for molecule statistics
2. Parse the GFF file for basic annotation statistics
3. Perform a GO slim mapping

"""

import argparse
from biocode import utils, gff
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.server import CGIHTTPRequestHandler
import json
import os
import pickle
import re
import sys
import urllib.parse
import webbrowser

def main():
    parser = argparse.ArgumentParser( description='Visualize a GALES annotation')

    ## output file to be written
    parser.add_argument('-i', '--input_directory', type=str, required=True, help='Path to a directory containing the GALES results' )
    parser.add_argument('-f', '--fasta_file', type=str, required=True, help='Path to the FASTA file that was input to GALES' )
    parser.add_argument('-p', '--port', type=int, required=False, default=8081, help='Port on which you want to run the web server' )
    args = parser.parse_args()

    server_host = '127.0.0.1'
    server_port = args.port

    # we need to be dealing with full paths
    args.input_directory = os.path.abspath(args.input_directory)
    args.fasta_file = os.path.abspath(args.fasta_file)
    gff_file = "{0}/attributor.annotation.gff3".format(args.input_directory)
    fasta_stats_file = "{0}/fasta_stats.json".format(args.input_directory)
    gff_stats_file = "{0}/gff_stats.json".format(args.input_directory)
    slim_counts_file = "{0}/obo_slim_counts.json".format(args.input_directory)

    # base names of the pickle files
    gff_stored_base = "{0}/gff.stored".format(args.input_directory)
    gff_stored_assemblies = "{0}.assemblies.pickle".format(gff_stored_base)
    gff_stored_features = "{0}.features.pickle".format(gff_stored_base)

    exec_path = os.path.dirname(os.path.abspath(__file__))
    obo_slim_map_pickle_file = "{0}/../data/tadpole_transcriptome_slim.map.pickle".format(exec_path)
    ui_path = "{0}/../ui".format(exec_path)
    os.chdir(ui_path)

    print("\n--------------------------------------------------------------------------------")
    print("Checking for stored statistics and analyses within input directory, or creating them.")
    print("This can cause the first execution on any input directory to take a few minutes.")
    print("--------------------------------------------------------------------------------\n")

    if os.path.exists(fasta_stats_file):
        print("Checking for FASTA stats file ... found.", flush=True)
    else:
        print("Checking for FASTA stats file ... not found. Parsing ... ", end='', flush=True)
        generate_fasta_stats(fasta_file=args.fasta_file, json_out=fasta_stats_file)
        print("done.", flush=True)

    if os.path.exists(gff_stored_features):
        print("Checking for stored GFF features file ... found.", flush=True)
        with open(gff_stored_assemblies, 'rb') as ga_f:
            gff_assemblies = pickle.load(ga_f)

        with open(gff_stored_features, 'rb') as gf_f:
            gff_features = pickle.load(gf_f)
    else:
        print("Checking for stored GFF features file ... not found. Parsing ... ", flush=True)
        (gff_assemblies, gff_features) = gff.get_gff3_features(gff_file)
        with open(gff_stored_assemblies, 'wb') as ga_f:
            pickle.dump(gff_assemblies, ga_f)

        with open(gff_stored_features, 'wb') as gf_f:
            pickle.dump(gff_features, gf_f)
        print("done.", flush=True)
        
    if os.path.exists(gff_stats_file):
        print("Checking for GFF stats file ... found.", flush=True)
    else:
        print("Checking for GFF stats file ... not found.  Parsing ... ", end='', flush=True)
        generate_gff_stats(gff_assemblies=gff_assemblies, gff_features=gff_features, json_out=gff_stats_file)
        print("done.", flush=True)

    print("Gathering terms annotated within the GFF ... ", flush=True, end='')
    source_go_terms = parse_go_terms_from_gff(gff_file)
    print("done.", flush=True)

    print("Mapping annotated terms to GO slim ... ", flush=True, end='')
    slim_counts = map_to_slim(source_terms=source_go_terms, slim_map_file=obo_slim_map_pickle_file)
    print("done.", flush=True)

    with open(slim_counts_file, 'w') as outfile:
        json.dump(slim_counts, outfile)

    run(host=server_host, port=server_port, script_args=args)

    
def generate_fasta_stats(fasta_file=None, json_out=None):
    result = { 'success': 0 }
    fasta_dict = utils.fasta_dict_from_file(fasta_file)
    result['stats_assembly_count'] = len(fasta_dict)

    shortest = None
    longest = None
    assembly_sum_length = 0
    gc_count = 0

    for id in fasta_dict:
        contig_len = len(fasta_dict[id]['s'])
        assembly_sum_length += contig_len
        gc_count += fasta_dict[id]['s'].upper().count('C') + fasta_dict[id]['s'].upper().count('G')

        if shortest is None or contig_len < shortest:
            shortest = contig_len

        if longest is None or contig_len > longest:
            longest = contig_len

    result['stats_assembly_sum_length'] = assembly_sum_length
    result['stats_assembly_longest_length'] = longest
    result['stats_assembly_shortest_length'] = shortest
    result['stats_assembly_gc'] = "{0:.1f}%".format((gc_count / assembly_sum_length) * 100)
    result['success'] = 1

    with open(json_out, 'w') as outfile:
        json.dump(result, outfile)


def generate_gff_stats(gff_assemblies=None, gff_features=None, json_out=None):
    result = { 'success': 1, 'stats_gene_count': 0, 'stats_hypo_gene_count': 0,
               'stats_gene_mean_length': None, 'stats_specific_annot_count': 0,
               'stats_rRNA_count': 0, 'stats_tRNA_count': 0, 'stats_go_terms_assigned': 0,
               'stats_ec_numbers_assigned': 0, 'stats_gene_symbols_assigned': 0,
               'stats_dbxrefs_assigned': 0
             }
    (assemblies, features) = (gff_assemblies, gff_features)
    gene_length_sum = 0

    for assembly_id in assemblies:
        for gene in assemblies[assembly_id].genes():
            result['stats_gene_count'] += 1
            gene_length_sum += gene.locations[0].fmax - gene.locations[0].fmin

            result['stats_rRNA_count'] = len(gene.rRNAs())
            result['stats_tRNA_count'] = len(gene.tRNAs())

            ## annotation is on mRNAs
            for mRNA in gene.mRNAs():
                for polypeptide in mRNA.polypeptides():
                    annot = polypeptide.annotation

                    if annot is not None:
                        if 'hypothetical' in annot.product_name:
                            result['stats_hypo_gene_count'] += 1
                        else:
                            result['stats_specific_annot_count'] += 1

                        result['stats_go_terms_assigned'] += len(annot.go_annotations)
                        result['stats_ec_numbers_assigned'] += len(annot.ec_numbers)
                        result['stats_dbxrefs_assigned'] += len(annot.dbxrefs)

                        if annot.gene_symbol is not None:
                            result['stats_gene_symbols_assigned'] += 1

    result['stats_gene_mean_length'] = "{0:.1f}".format(gene_length_sum / result['stats_gene_count'])
    result['stats_mean_go_terms_per_gene'] = "{0:.1f}".format(result['stats_go_terms_assigned'] / result['stats_gene_count'])
    
    with open(json_out, 'w') as outfile:
        json.dump(result, outfile)

# Goal is to create summary slim counts on main page like this:
#   http://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0130720
# Great viewer
#   http://visualdataweb.de/webvowl
def map_to_slim(source_terms=None, slim_map_file=None):
    # Slim terms to skip.  Usually the root Big Three terms
    skip_slim_terms = ['GO:0008150', 'GO:0003674', 'GO:0005575']
    slim_map = pickle.load( open(slim_map_file, 'rb') )
    
    counts = dict()

    for ns in slim_map:
        counts[ns] = {'unknown': 0}
    
    for gff_term in source_terms:
        gff_id = "GO:{0}".format(gff_term)
        slim_term = None
        
        for ns in slim_map:
            if gff_id in slim_map[ns]:
                slim_term = slim_map[ns][gff_id]
                if slim_term is None:
                    counts[ns]['unknown'] += source_terms[gff_term]
                else:
                    if slim_term not in counts[ns]:
                        counts[ns][slim_term] = 0

                    counts[ns][slim_term] += source_terms[gff_term]

                break

    return counts


def parse_go_terms_from_gff(file):
    terms = dict()
    assemblies, features = gff.get_gff3_features(file)
    for assembly_id in assemblies:
        for gene in assemblies[assembly_id].genes():
            for mRNA in gene.mRNAs():
                for polypeptide in mRNA.polypeptides():
                    annot = polypeptide.annotation
                    for go_annot in annot.go_annotations:
                        if go_annot.go_id in terms:
                            terms[go_annot.go_id] += 1
                        else:
                            terms[go_annot.go_id] = 1

    return terms
        

       
def run(host=None, port=None, script_args=None):
    args = {'annotation_dir': script_args.input_directory, 'fasta_file': script_args.fasta_file}
    args_string = urllib.parse.urlencode(args)

    initial_url = "http://{0}:{1}/index.html?{2}".format(host, port, args_string)
    print("Starting GALESui server.  Open your browser to the following URL:\n\n{0}".format(initial_url), flush=True)
 
    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = (host, port)
    handler = CGIHTTPRequestHandler
    handler.cgi_directories = ["/cgi"]
    httpd = HTTPServer(server_address, CGIHTTPRequestHandler)

    # I couldn't get this to work.  It just opens a browser to a blank window
    #webbrowser.open_new_tab(initial_url)
    httpd.serve_forever()
    

 
    
if __name__ == '__main__':
    main()







