#!/usr/bin/env python
"""Tests for `near_dedup` package."""
# pylint: disable=redefined-outer-name

import pytest
import bloom_filter

@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    del response

'''
def test_very_basic_bf():
    docs = ["Hello", "Yes", "Hello"]
    bf = bloom_filter.BloomFilter(n=10, f=0.02)
    bf.add(docs[0])
    bf.add(docs[1])
    bf.add(docs[2])
    
    assert bf.query(docs[0])
    assert bf.query(docs[1])
    assert bf.query(docs[2])
    assert not bf.query("no")
'''

def test_basic_bf():
    
    bf = bloom_filter.BloomFilter(n=1000, f=0.02)
    
    with open('tests/basic_test_example_files.txt') as topo_file:
        for line in topo_file:
            bf.add(line)
    
    assert bf.query("TWO CHERRY PUMPKIN TARTS")
    assert bf.query("CHEESEBURGER EN PARADISE")
    #assert bf.query("THIS FILE SHOULDNT BE QUERIED")
    #assert bf.query("CHEESEBURGERZ IN PARADISE")

