#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import glob
from design_space_enumerator.main import *

__author__ = "malcolm@davidsonnanosolutions.com"
__copyright__ = "malcolm@davidsonnanosolutions.com"
__license__ = "mit"

data = ['BaO', 'BaTiO']
save_path = os.path.join('test_output.csv')


def test_enumerate_formula():
    assert 'BaO' in enumerate_formula(['Ba', 'O'], 2)


def test_handle_output_to_csv():
    handle_output_method(data, use_csv=True, filepath=save_path)
    files = glob.glob('*.csv')
    assert 'test_output.csv' in files


def test_extract_from_file():
    assert 'BaO' in extract_from_file('test_import.csv')
