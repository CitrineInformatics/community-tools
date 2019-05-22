#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script can be used to enumerate a design space by way of the cartesian
product filtered using Pymatgen.
"""

import argparse
import sys
import logging
import typing
import pandas as pd
import os
import pypif
from citrination_client import CitrinationClient
from typing import Iterable, Optional
from pymatgen import Composition
from itertools import combinations

from design_space_enumerator import __version__

__author__ = "malcolm@davidsonnanosolutions.com"
__copyright__ = "malcolm@davidsonnanosolutions.com"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def enumerate_formula(elements: Iterable[str], num_members: int) -> list:
    """[Generates a list of chemical fromulas]

    Arguments:
        elements {list} -- [Elements to build formulas from]
        num_members {int} -- [The number of elements in the formula]

    Returns:
        list -- [Permutations of the given formula]
    """
    try:
        enum = ["".join(x)
                for x in combinations(elements, num_members)]
    except Exception as exc:
        print('-- Could not compute combinations --')
        raise(exc)
    return screen_formulas(enum)


def screen_formulas(candidates: Iterable[str]) -> Iterable[str]:
    """[Filters unique chemical compositions]

    Arguments:
        candidates {Iterable[str]} -- [List of chemical formula candidates]

    Returns:
        Iterable[str] -- [Filtered list of candidates]
    """
    try:
        formulas = []
        for formula in candidates:
            comp = Composition(formula)
            if comp.reduced_formula not in formulas:
                formulas.append(comp.reduced_formula)
        return formulas
    except Exception as exc:
        print('-- Could not filter candidates --')
        raise(exc)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Enumerate a design space from a list of elements.")
    parser.add_argument(
        '--version',
        action='version',
        version='design-space-enumerator {ver}'.format(ver=__version__))
    parser.add_argument(
        '-e',
        '--elements',
        dest="elements",
        help="list of elemebts as Al,Br,...",
        action='append',
        type=str)
    parser.add_argument(
        '-n',
        dest="num_elements",
        help="Number of elements in the chemical formula",
        type=int)
    parser.add_argument(
        '-dfp',
        '--designfilepath',
        dest="design_filepath",
        help="file path to a CSV of elements to enumerate",
        default=None,
        type=str)
    parser.add_argument(
        '-sfp',
        '--savefilepath',
        dest="save_filepath",
        help="file path to save design space as CSV",
        default="design_space.csv",
        type=str)
    parser.add_argument(
        '-k',
        '--apikey',
        dest="api_string",
        help="Citrination API key environment variable name",
        default="CITRINATION_API_KEY",
        type=str)
    parser.add_argument(
        '-s',
        '--site',
        dest="site",
        help="Citrination site url",
        default="https://citrination.com",
        type=str)
    parser.add_argument(
        '-sv',
        '--save',
        dest="use_csv",
        help="Do not use a csv file to store data",
        default=True,
        action='store_false')
    parser.add_argument(
        '-cn',
        '--citrination',
        dest="use_citrination",
        help="Use citrination to store data",
        default=False,
        action='store_true')
    parser.add_argument(
        '-ds',
        '--dataset',
        dest="dataset_id",
        help="Citrination dataset ID to store data at",
        default=None,
        type=str)
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    return parser.parse_args(args)


def extract_from_file(filepath: str) -> Iterable[str]:
    """[Handles extracting lists of elements from a csv]
    
    Arguments:
        filepath {str} -- [The path to the design space csv]
    
    Returns:
        Iterable[str] -- [The list of elements to be enumerated]
    """
    return pd.read_csv(filepath, header=None, dtype=str).values.tolist()[0]


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def to_pif(data: Iterable[str]):
    try:
        systems = [pypif.obj.ChemicalSystem(
            chemical_formula=formula) for formula in data]
        with open('pifs.json', 'w') as f:
            pypif.pif.dump(systems, f, indent=2)
    except Exception as exc:
        print('-- Could not generate PIF --')
        raise(exc)


def store_on_citrination(data: Iterable[str], dataset_id: str, site: str, api_string: str) -> str:
    """[Handles storing data in a Citrination dataset]
    
    Arguments:
        data {Iterable[str]} -- [The enumerated design space]
        dataset_id {str} -- [Citrination datset id to store data at]
        site {str} -- [Citrination site to store datset on]
        api_string {str} -- [The api key string in environment variables]
    
    Returns:
        str -- [The Citrination dataset id]
    """
    try:
        api_key = os.environ.get(api_string)
    except Exception as exc:
        print('-- API key not found in environment variables --')
        raise(exc)
    client = CitrinationClient(api_key, site)
    to_pif(data)
    # create a new dataset version, if the dataset does not exist; create it.
    try:
        client.data.create_dataset_version(dataset_id)
    except Exception as exc:
        dataset_id = client.data.create_dataset().id
    client.data.upload(dataset_id, 'pifs.json')
    ready = False
    while not ready:
        status = client.data.get_ingest_status(dataset_id)
        if status:
            ready = True
        else:
            _logger.info('Citrination Ingestion Status: {}'.format(status))
    return dataset_id
    # Build data upload here


def handle_output_method(data: Iterable[str], store_citrination: bool, use_csv: bool, dataset_id: str,  site: str, api_string: str, filepath: str):
    """[Handles saving or uploading the enumerated design space]
    
    Arguments:
        data {Iterable[str]} -- [The enumerated design space]
        store_citrination {bool} -- [Upload to the Citrination platform]
        use_csv {bool} -- [Store using a csv file]
        dataset_id {str} -- [Citrination datset id to store data at]
        site {str} -- [Citrination site to store datset on]
        api_string {str} -- [The api key string in environment variables]
        filepath {str} -- [The file path to save the enumerated csv at]
    """
    if use_csv:
        #filepath = str(os.path.join(filepath))
        _logger.debug("Save File Path: {}".format(filepath))
        tabulated_data = pd.DataFrame(data=data, columns=['Chemical Formula'])
        tabulated_data.to_csv(filepath, index=False)
        _logger.info('Design Space Saved: {}'.format(filepath))
    elif store_citrination:
        dataset_id = store_on_citrination(data, dataset_id, site=site, api_string=api_string)
        _logger.info(
            'Data Uploaded to Citrination Dataset ID: {}'.format(dataset_id))


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting design space enumeration...")
    # Pull out the list of elements
    if args.design_filepath:
        elements = extract_from_file(os.path.join(args.design_filepath))
    else:
        elements = args.elements
    formulas = enumerate_formula(elements, args.num_elements)
    handle_output_method(formulas, args.use_citrination, args.use_csv, args.dataset_id, args.site, args.api_string, args.save_filepath)

    _logger.info("Enumeration Ended")
    _logger.info("Example of {} formulas generated: {}".format(
        len(formulas), formulas[0]))


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
