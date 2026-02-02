"""Abstract base classes for simulators and extractors."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Set

import pandas as pd

from scmextract.core.types import CausalGraph


class BaseSimulator(ABC):
    """Abstract base class for simulators with known causal structure.

    Simulators wrap simulation code and provide:
    - Access to source code for extraction
    - Ground truth causal graph for evaluation
    - Ability to run the simulation
    """

    name: str = "base"

    @abstractmethod
    def get_source_path(self) -> Path:
        """Return the path to the simulator source file.

        Returns:
            Path to the Python file containing the simulation code.
        """
        pass

    @abstractmethod
    def get_state_variables(self) -> List[str]:
        """Return the list of state variables in the simulation.

        Returns:
            List of variable names that represent the simulation state.
        """
        pass

    @abstractmethod
    def get_ground_truth_graph(self) -> CausalGraph:
        """Return the known ground truth causal graph.

        Returns:
            CausalGraph representing the true causal structure.
        """
        pass

    @abstractmethod
    def run(self, steps: int = 1000, **kwargs) -> pd.DataFrame:
        """Run the simulation and return results.

        Args:
            steps: Number of simulation steps.
            **kwargs: Additional simulation parameters.

        Returns:
            DataFrame with simulation results.
        """
        pass

    def get_all_variables(self) -> List[str]:
        """Return all variables relevant for causal extraction.

        By default, returns state variables. Override to include parameters
        or intermediate variables.

        Returns:
            List of all variable names.
        """
        return self.get_state_variables()


class BaseExtractor(ABC):
    """Abstract base class for causal graph extraction methods.

    Extractors analyze source code to identify causal relationships
    between variables.
    """

    name: str = "base"

    @abstractmethod
    def extract(self, source_path: Path, variables: Optional[Set[str]] = None) -> CausalGraph:
        """Extract causal graph from source code.

        Args:
            source_path: Path to the Python source file.
            variables: Optional set of variables to focus on.
                      If None, extract all detected relationships.

        Returns:
            CausalGraph representing the extracted causal structure.
        """
        pass

    def extract_from_string(self, source_code: str,
                           variables: Optional[Set[str]] = None) -> CausalGraph:
        """Extract causal graph from source code string.

        Args:
            source_code: Python source code as string.
            variables: Optional set of variables to focus on.

        Returns:
            CausalGraph representing the extracted causal structure.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support extraction from string"
        )
