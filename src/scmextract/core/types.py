"""Core data types for SCM extraction."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import numpy as np


@dataclass
class CausalGraph:
    """Represents a causal graph as an adjacency matrix.

    Attributes:
        variables: Ordered list of variable names.
        adjacency_matrix: Binary matrix where adj[i,j]=1 means variable i causes variable j.
        metadata: Optional dictionary for additional information.
    """
    variables: List[str]
    adjacency_matrix: np.ndarray
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate the graph structure."""
        n = len(self.variables)
        if self.adjacency_matrix.shape != (n, n):
            raise ValueError(
                f"Adjacency matrix shape {self.adjacency_matrix.shape} "
                f"doesn't match {n} variables"
            )
        if self.metadata is None:
            self.metadata = {}

    @classmethod
    def from_dependencies(cls, dependencies: Dict[str, List[str]],
                         variables: Optional[List[str]] = None) -> "CausalGraph":
        """Create a CausalGraph from a dependency dictionary.

        Args:
            dependencies: Dict mapping each variable to its parents (causes).
            variables: Optional ordered list of variables. If None, inferred from dependencies.

        Returns:
            CausalGraph instance.
        """
        if variables is None:
            all_vars = set(dependencies.keys())
            for parents in dependencies.values():
                all_vars.update(parents)
            variables = sorted(all_vars)

        n = len(variables)
        var_to_idx = {v: i for i, v in enumerate(variables)}
        adj = np.zeros((n, n), dtype=np.int8)

        for target, parents in dependencies.items():
            if target not in var_to_idx:
                continue
            j = var_to_idx[target]
            for parent in parents:
                if parent in var_to_idx:
                    i = var_to_idx[parent]
                    adj[i, j] = 1

        return cls(variables=variables, adjacency_matrix=adj)

    def to_dependencies(self) -> Dict[str, List[str]]:
        """Convert adjacency matrix back to dependency dictionary.

        Returns:
            Dict mapping each variable to its list of parents.
        """
        dependencies = {}
        n = len(self.variables)
        for j in range(n):
            parents = []
            for i in range(n):
                if self.adjacency_matrix[i, j] == 1:
                    parents.append(self.variables[i])
            if parents:
                dependencies[self.variables[j]] = parents
        return dependencies

    def get_edges(self) -> List[tuple]:
        """Get list of directed edges as (parent, child) tuples."""
        edges = []
        n = len(self.variables)
        for i in range(n):
            for j in range(n):
                if self.adjacency_matrix[i, j] == 1:
                    edges.append((self.variables[i], self.variables[j]))
        return edges

    def num_edges(self) -> int:
        """Return the number of edges in the graph."""
        return int(np.sum(self.adjacency_matrix))

    def __eq__(self, other: object) -> bool:
        """Check equality with another CausalGraph."""
        if not isinstance(other, CausalGraph):
            return False
        return (
            self.variables == other.variables and
            np.array_equal(self.adjacency_matrix, other.adjacency_matrix)
        )

    def __repr__(self) -> str:
        return f"CausalGraph(variables={self.variables}, edges={self.num_edges()})"


@dataclass
class ExperimentConfig:
    """Configuration for an extraction experiment.

    Attributes:
        name: Experiment identifier.
        simulator: Name of the simulator to use.
        extractor: Name of the extraction method.
        variables: List of variables to extract (optional, uses simulator defaults).
        output_dir: Directory for results.
        options: Additional method-specific options.
    """
    name: str
    simulator: str
    extractor: str
    variables: Optional[List[str]] = None
    output_dir: str = "results"
    options: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"ExperimentConfig(name='{self.name}', simulator='{self.simulator}', extractor='{self.extractor}')"
