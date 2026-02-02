"""Evaluation metrics for comparing causal graphs."""

from typing import Dict, Set, Tuple

import numpy as np

from scmextract.core.types import CausalGraph


def _get_edge_sets(
    predicted: CausalGraph, ground_truth: CausalGraph
) -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    """Extract edge sets from two graphs for comparison.

    Args:
        predicted: Predicted causal graph.
        ground_truth: Ground truth causal graph.

    Returns:
        Tuple of (predicted_edges, true_edges) as sets of (parent, child) tuples.
    """
    pred_edges = set(predicted.get_edges())
    true_edges = set(ground_truth.get_edges())
    return pred_edges, true_edges


def precision(predicted: CausalGraph, ground_truth: CausalGraph) -> float:
    """Calculate precision of predicted edges.

    Precision = TP / (TP + FP) = correct edges / predicted edges

    Args:
        predicted: Predicted causal graph.
        ground_truth: Ground truth causal graph.

    Returns:
        Precision score between 0 and 1.
    """
    pred_edges, true_edges = _get_edge_sets(predicted, ground_truth)

    if len(pred_edges) == 0:
        return 1.0 if len(true_edges) == 0 else 0.0

    true_positives = len(pred_edges & true_edges)
    return true_positives / len(pred_edges)


def recall(predicted: CausalGraph, ground_truth: CausalGraph) -> float:
    """Calculate recall of predicted edges.

    Recall = TP / (TP + FN) = correct edges / true edges

    Args:
        predicted: Predicted causal graph.
        ground_truth: Ground truth causal graph.

    Returns:
        Recall score between 0 and 1.
    """
    pred_edges, true_edges = _get_edge_sets(predicted, ground_truth)

    if len(true_edges) == 0:
        return 1.0 if len(pred_edges) == 0 else 0.0

    true_positives = len(pred_edges & true_edges)
    return true_positives / len(true_edges)


def f1_score(predicted: CausalGraph, ground_truth: CausalGraph) -> float:
    """Calculate F1 score of predicted edges.

    F1 = 2 * (precision * recall) / (precision + recall)

    Args:
        predicted: Predicted causal graph.
        ground_truth: Ground truth causal graph.

    Returns:
        F1 score between 0 and 1.
    """
    p = precision(predicted, ground_truth)
    r = recall(predicted, ground_truth)

    if p + r == 0:
        return 0.0

    return 2 * (p * r) / (p + r)


def structural_hamming_distance(predicted: CausalGraph, ground_truth: CausalGraph) -> int:
    """Calculate Structural Hamming Distance (SHD).

    SHD counts the number of edge insertions, deletions, and flips
    needed to transform the predicted graph into the ground truth.

    For DAGs without considering edge reversals:
    SHD = |predicted - truth| + |truth - predicted|
        = FP + FN

    Args:
        predicted: Predicted causal graph.
        ground_truth: Ground truth causal graph.

    Returns:
        SHD as non-negative integer.
    """
    pred_edges, true_edges = _get_edge_sets(predicted, ground_truth)

    false_positives = len(pred_edges - true_edges)
    false_negatives = len(true_edges - pred_edges)

    return false_positives + false_negatives


def evaluate_graph(predicted: CausalGraph, ground_truth: CausalGraph) -> Dict[str, float]:
    """Compute all evaluation metrics for a predicted graph.

    Args:
        predicted: Predicted causal graph.
        ground_truth: Ground truth causal graph.

    Returns:
        Dictionary with keys: precision, recall, f1, shd
    """
    return {
        "precision": precision(predicted, ground_truth),
        "recall": recall(predicted, ground_truth),
        "f1": f1_score(predicted, ground_truth),
        "shd": structural_hamming_distance(predicted, ground_truth),
    }
