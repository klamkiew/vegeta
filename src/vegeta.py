#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VeGETA -- Viral GEnome sTructure Alignments

VeGETA is a python program that takes several genome sequences
from different viruses as an input. In the very first step,
VeGETA will cluster these sequences into groups (clades) based 
on their sequence similarity. For each clade, the centroid sequence is
determined as representative genome, i.e. the sequence with the lowest
distance to all other sequences of this clade. 

In a second step, VeGETA calculates a multiple sequence alignment of 
the representative genomes. This alignment is progressively refined
using 'MAFFT' and 'LocARNA'. In the end, we provide a local-structure guided
MSA of the representative viruses.

Python Dependencies:
  docopt

Other Dependencies:
  ViennaRNA package
  MAFFT
  LocARNA
  mcl

Contact:
  kevin.lamkiewicz@uni-jena.de

Citation:
  Lamkiewicz, K., et al. (20xx), "Structure-guided multiple sequence alignments of complete viral genomes.", Journal, Issue, Volume.

Usage:
  vegeta.py [options] <inputSequences> [<genomeOfInterest>]

Options:
  -h, --help              Show this help message and exits.
  -v, --verbose           Get some extra information from VeGETA during calculation. [Default: False]
  --version               Prints the version of VeGETA and exits.
  -o DIR, --output DIR    Specifies the output directory of VeGETA. [Default: pwd]

  -k KMER, --kmer KMER    Length of the considered kmer. [Default: 8]

  -a, --alignment-only    Only performs the alignment calculation, without prior clustering. 
                          NOTE: This is not recommended for large datasets. [Default: False]
  -c, --cluster-only      Only performs the clustering step of sequences, without the alignment. [Default: False]
  

Version:
  VeGETA v0.1 (alpha)
"""

import sys
import os
import logging

from colorlog import ColoredFormatter
from docopt import docopt

from ClusterViruses import Clusterer


def create_logger():
    """
    doc string.
    """

    logger = logging.getLogger()
    #logger.setLevel(logging.WARNING)

    handle = logging.StreamHandler()
    #handle.setLevel(logging.WARNING)

    formatter = ColoredFormatter("%(log_color)sVeGETA %(levelname)s -- %(asctime)s -- %(message)s", "%Y-%m-%d %H:%M:%S", 
                                    log_colors={
                                            'DEBUG':    'bold_cyan',
                                            'INFO':     'bold_green',
                                            'WARNING':  'bold_yellow',
                                            'ERROR':    'bold_red',
                                            'CRITICAL': 'bold_red'}
                                )

    #handle.setFormatter(logging.Formatter("ViMiFi %(levelname)s -- %(asctime)s -- %(message)s", "%Y-%m-%d %H:%M:%S"))
    handle.setFormatter(formatter)
    logger.addHandler(handle)
    return logger

def create_outdir(outdir):
    try:
      os.mkdir(outdir)
      logger.info(f"Creating output directory: {outdir}")
    except FileExistsError:
      logger.warning(f"The output directory exists. Files will be overwritten.")

def parse_arguments(d_args):
  """
  Parse all given arguments and check for error (e.g. file names).

  Arguments:
  d_args -- dict with input parameters and their values

  Returns:
  parsed and checked parameter list
  """

  if d_args['--version']:
    print("VeGETA version 0.1")
    exit(0)

  
  verbose = d_args['--verbose']
  if verbose:
    logger.setLevel(logging.INFO)

  inputSequences = d_args['<inputSequences>']
  if not os.path.isfile(inputSequences):
    logger.error("Couldn't find input sequences. Check your file")
    exit(1)

  goi = d_args['<genomeOfInterest>']
  if goi and not os.path.isfile(goi):
    logger.error("Couldn't find genome of interest. Check your file")
    exit(1)

  output = d_args['--output']
  if output == 'pwd':
    output = os.getcwd()
  create_outdir(f"{output}/vegeta")

  try:
    k = int(d_args['--kmer'])
  except ValueError:
    logger.error("Invalid parameter for k-mer size. Please input a number.")
    exit(2)
  
  alnOnly = d_args['--alignment-only']
  clusterOnly = d_args['--cluster-only']


  return (inputSequences, goi, f"{output}/vegeta", alnOnly, clusterOnly, k)

if __name__ == "__main__":
  logger = create_logger()
  (inputSequences, goi, outdir, alnOnly, clusterOnly, k) = parse_arguments(docopt(__doc__))

  if alnOnly:
    logger.info("Skipping clustering and directly calculate the alignment.")

  if clusterOnly:
    logger.info("Only clustering is performed. The alignment calculation will be skipped.")  
  
  if not alnOnly:
    virusClusterer = Clusterer(inputSequences, k) 
    virusClusterer.determine_profile()
    logger.info("Calculating all pairwise kmer distances. This may take a while.")
    virusClusterer.pairwise_distances()
    virusClusterer.create_matrix()
    logger.info("Now performing mcl to cluster the sequences.")
    virusClusterer.perform_mcl(outdir)
    virusClusterer.extract_cluster(outdir)
    #virusClusterer.get_centroids()
