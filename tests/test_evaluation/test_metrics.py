"""Tests for evaluation metrics."""

import numpy as np
import pytest

from scmextract.core.types import CausalGraph
from scmextract.evaluation.metrics import (
    precision,
    recall,
    f1_score,
    structural_hamming_distance,
    evaluate_graph,
)


class TestPrecision:
    def test_perfect_prediction(self, simple_graph):
        """Precision should be 1.0 when prediction matches ground truth."""
        assert precision(simple_graph, simple_graph) == 1.0

    def test_no_correct_edges(self):
        """Precision should be 0.0 when no predicted edges are correct."""
        # Predicted: A -> B
        pred = CausalGraph.from_dependencies({"B": ["A"]}, ["A", "B", "C"])
        # Truth: B -> C
        truth = CausalGraph.from_dependencies({"C": ["B"]}, ["A", "B", "C"])
        assert precision(pred, truth) == 0.0

    def test_partial_correct(self):
        """Precision with some correct edges."""
        # Predicted: A -> B, A -> C (2 edges)
        pred = CausalGraph.from_dependencies({"B": ["A"], "C": ["A"]}, ["A", "B", "C"])
        # Truth: A -> B only (1 edge)
        truth = CausalGraph.from_dependencies({"B": ["A"]}, ["A", "B", "C"])
        assert precision(pred, truth) == 0.5

    def test_empty_prediction_empty_truth(self, empty_graph):
        """Precision should be 1.0 when both are empty."""
        assert precision(empty_graph, empty_graph) == 1.0

    def test_empty_prediction_nonempty_truth(self, empty_graph, simple_graph):
        """Precision should be 0.0 when predicting nothing but truth has edges."""
        assert precision(empty_graph, simple_graph) == 0.0


class TestRecall:
    def test_perfect_prediction(self, simple_graph):
        """Recall should be 1.0 when prediction matches ground truth."""
        assert recall(simple_graph, simple_graph) == 1.0

    def test_missing_edges(self):
        """Recall with missing edges."""
        # Predicted: A -> B only
        pred = CausalGraph.from_dependencies({"B": ["A"]}, ["A", "B", "C"])
        # Truth: A -> B, B -> C (2 edges)
        truth = CausalGraph.from_dependencies({"B": ["A"], "C": ["B"]}, ["A", "B", "C"])
        assert recall(pred, truth) == 0.5

    def test_empty_truth(self, simple_graph, empty_graph):
        """Recall should be 0.0 when truth is empty but prediction is not."""
        assert recall(simple_graph, empty_graph) == 0.0


class TestF1Score:
    def test_perfect_prediction(self, simple_graph):
        """F1 should be 1.0 when prediction matches ground truth."""
        assert f1_score(simple_graph, simple_graph) == 1.0

    def test_zero_precision_and_recall(self, empty_graph, simple_graph):
        """F1 should be 0.0 when both precision and recall are 0."""
        assert f1_score(empty_graph, simple_graph) == 0.0

    def test_f1_calculation(self):
        """Test F1 = 2 * P * R / (P + R)."""
        # Predicted: A -> B, A -> C (2 edges, 1 correct)
        pred = CausalGraph.from_dependencies({"B": ["A"], "C": ["A"]}, ["A", "B", "C"])
        # Truth: A -> B, B -> C (2 edges)
        truth = CausalGraph.from_dependencies({"B": ["A"], "C": ["B"]}, ["A", "B", "C"])

        p = precision(pred, truth)  # 1/2 = 0.5
        r = recall(pred, truth)     # 1/2 = 0.5
        expected_f1 = 2 * p * r / (p + r)  # 0.5

        assert f1_score(pred, truth) == pytest.approx(expected_f1)


class TestStructuralHammingDistance:
    def test_identical_graphs(self, simple_graph):
        """SHD should be 0 for identical graphs."""
        assert structural_hamming_distance(simple_graph, simple_graph) == 0

    def test_one_extra_edge(self, simple_graph):
        """SHD should be 1 for one extra edge."""
        # Add one edge to simple_graph
        pred = CausalGraph.from_dependencies(
            {"B": ["A"], "C": ["B", "A"]},  # Extra A -> C
            ["A", "B", "C"]
        )
        assert structural_hamming_distance(pred, simple_graph) == 1

    def test_one_missing_edge(self, simple_graph):
        """SHD should be 1 for one missing edge."""
        # Remove one edge
        pred = CausalGraph.from_dependencies({"B": ["A"]}, ["A", "B", "C"])
        assert structural_hamming_distance(pred, simple_graph) == 1

    def test_completely_different(self):
        """SHD for completely different graphs."""
        # Pred: A -> B
        pred = CausalGraph.from_dependencies({"B": ["A"]}, ["A", "B", "C"])
        # Truth: B -> C
        truth = CausalGraph.from_dependencies({"C": ["B"]}, ["A", "B", "C"])
        # 1 FP (A->B) + 1 FN (B->C) = 2
        assert structural_hamming_distance(pred, truth) == 2


class TestEvaluateGraph:
    def test_returns_all_metrics(self, simple_graph):
        """evaluate_graph should return all metrics."""
        result = evaluate_graph(simple_graph, simple_graph)

        assert "precision" in result
        assert "recall" in result
        assert "f1" in result
        assert "shd" in result

        assert result["precision"] == 1.0
        assert result["recall"] == 1.0
        assert result["f1"] == 1.0
        assert result["shd"] == 0
