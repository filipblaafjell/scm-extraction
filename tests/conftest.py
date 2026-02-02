"""Shared test fixtures."""

import numpy as np
import pytest

from scmextract.core.types import CausalGraph


@pytest.fixture
def simple_graph():
    """A simple 3-node graph: A -> B -> C"""
    variables = ["A", "B", "C"]
    adj = np.array([
        [0, 1, 0],  # A -> B
        [0, 0, 1],  # B -> C
        [0, 0, 0],
    ], dtype=np.int8)
    return CausalGraph(variables=variables, adjacency_matrix=adj)


@pytest.fixture
def diamond_graph():
    """Diamond graph: A -> B, A -> C, B -> D, C -> D"""
    variables = ["A", "B", "C", "D"]
    adj = np.array([
        [0, 1, 1, 0],  # A -> B, A -> C
        [0, 0, 0, 1],  # B -> D
        [0, 0, 0, 1],  # C -> D
        [0, 0, 0, 0],
    ], dtype=np.int8)
    return CausalGraph(variables=variables, adjacency_matrix=adj)


@pytest.fixture
def empty_graph():
    """Graph with no edges."""
    variables = ["X", "Y", "Z"]
    adj = np.zeros((3, 3), dtype=np.int8)
    return CausalGraph(variables=variables, adjacency_matrix=adj)
