"""SIR (Susceptible-Infected-Resistant) epidemic model simulator."""

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from scmextract.core.base import BaseSimulator
from scmextract.core.types import CausalGraph
from scmextract.simulators.registry import SimulatorRegistry


@SimulatorRegistry.register("sir")
class SIRSimulator(BaseSimulator):
    """SIR epidemic model simulator.

    The SIR model divides a population into three compartments:
    - S (Susceptible): Individuals who can become infected
    - I (Infected): Individuals who are currently infected
    - R (Resistant/Recovered): Individuals who have recovered and are immune

    Dynamics:
        dS/dt = -beta * S * I / N
        dI/dt = beta * S * I / N - gamma * I
        dR/dt = gamma * I

    Where:
        - beta (rateSI): Infection rate
        - gamma (rateIR): Recovery rate
        - N: Total population
    """

    def __init__(
        self,
        susceptible: int = 950,
        infected: int = 50,
        resistant: int = 0,
        rate_si: float = 0.05,
        rate_ir: float = 0.01,
    ):
        """Initialize SIR model.

        Args:
            susceptible: Initial susceptible population.
            infected: Initial infected population.
            resistant: Initial resistant/recovered population.
            rate_si: Infection rate (beta).
            rate_ir: Recovery rate (gamma).
        """
        self.initial_susceptible = susceptible
        self.initial_infected = infected
        self.initial_resistant = resistant
        self.rate_si = rate_si
        self.rate_ir = rate_ir
        self.population = susceptible + infected + resistant

    def get_source_path(self) -> Path:
        """Return path to this source file."""
        return Path(__file__)

    def get_state_variables(self) -> List[str]:
        """Return the main state variables."""
        return ["Susceptible", "Infected", "Resistant"]

    def get_all_variables(self) -> List[str]:
        """Return all variables including parameters and intermediates."""
        return [
            "Susceptible", "Infected", "Resistant",
            "S_to_I", "I_to_R",
            "rateSI", "rateIR", "numIndividuals"
        ]

    def get_ground_truth_graph(self) -> CausalGraph:
        """Return the true causal structure of the SIR model.

        The ground truth reflects the mathematical relationships:
        - S_to_I = f(rateSI, Susceptible, Infected, numIndividuals)
        - I_to_R = f(Infected, rateIR)
        - Susceptible_t = f(Susceptible_{t-1}, S_to_I)
        - Infected_t = f(Infected_{t-1}, S_to_I, I_to_R)
        - Resistant_t = f(Resistant_{t-1}, I_to_R)
        """
        variables = self.get_all_variables()

        dependencies = {
            "S_to_I": ["rateSI", "Susceptible", "Infected", "numIndividuals"],
            "I_to_R": ["Infected", "rateIR"],
            "Susceptible": ["Susceptible", "S_to_I"],
            "Infected": ["Infected", "S_to_I", "I_to_R"],
            "Resistant": ["Resistant", "I_to_R"],
        }

        return CausalGraph.from_dependencies(dependencies, variables=variables)

    def run(self, steps: int = 1000, **kwargs) -> pd.DataFrame:
        """Run the SIR simulation.

        Args:
            steps: Number of time steps to simulate.

        Returns:
            DataFrame with columns: Time, Susceptible, Infected, Resistant
        """
        Susceptible = [self.initial_susceptible]
        Infected = [self.initial_infected]
        Resistant = [self.initial_resistant]

        rateSI = self.rate_si
        rateIR = self.rate_ir
        numIndividuals = self.population

        for step in range(1, steps):
            S_to_I = (rateSI * Susceptible[-1] * Infected[-1]) / numIndividuals
            I_to_R = Infected[-1] * rateIR

            Susceptible.append(Susceptible[-1] - S_to_I)
            Infected.append(Infected[-1] + S_to_I - I_to_R)
            Resistant.append(Resistant[-1] + I_to_R)

        return pd.DataFrame({
            "Time": list(range(len(Susceptible))),
            "Susceptible": Susceptible,
            "Infected": Infected,
            "Resistant": Resistant,
        })

    def plot(self, results: pd.DataFrame = None, output_path: str = "sir_plot.png"):
        """Plot the SIR simulation results.

        Args:
            results: DataFrame from run(). If None, runs simulation first.
            output_path: Path for the output image.
        """
        import matplotlib.pyplot as plt

        if results is None:
            results = self.run()

        plt.figure(figsize=(10, 6))
        plt.plot(results["Time"], results["Susceptible"], color="blue", label="Susceptible")
        plt.plot(results["Time"], results["Infected"], color="red", label="Infected")
        plt.plot(results["Time"], results["Resistant"], color="green", label="Resistant")
        plt.xlabel("Time")
        plt.ylabel("Population")
        plt.title(f"SIR Model (beta={self.rate_si}, gamma={self.rate_ir})")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
