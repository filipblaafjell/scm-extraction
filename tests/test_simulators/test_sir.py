"""Tests for SIR simulator."""

import pytest

from scmextract.simulators.sir import SIRSimulator


class TestSIRSimulator:
    def test_initialization(self):
        """Test default initialization."""
        sim = SIRSimulator()
        assert sim.initial_susceptible == 950
        assert sim.initial_infected == 50
        assert sim.initial_resistant == 0
        assert sim.population == 1000

    def test_custom_initialization(self):
        """Test custom parameters."""
        sim = SIRSimulator(
            susceptible=800,
            infected=100,
            resistant=100,
            rate_si=0.1,
            rate_ir=0.05,
        )
        assert sim.initial_susceptible == 800
        assert sim.initial_infected == 100
        assert sim.initial_resistant == 100
        assert sim.population == 1000
        assert sim.rate_si == 0.1
        assert sim.rate_ir == 0.05

    def test_run_returns_dataframe(self):
        """Test that run returns a DataFrame with correct columns."""
        sim = SIRSimulator()
        results = sim.run(steps=100)

        assert len(results) == 100
        assert "Time" in results.columns
        assert "Susceptible" in results.columns
        assert "Infected" in results.columns
        assert "Resistant" in results.columns

    def test_population_conserved(self):
        """Test that total population is conserved."""
        sim = SIRSimulator()
        results = sim.run(steps=100)

        total = results["Susceptible"] + results["Infected"] + results["Resistant"]
        assert all(abs(total - 1000) < 1e-10)

    def test_get_state_variables(self):
        """Test get_state_variables returns S, I, R."""
        sim = SIRSimulator()
        vars = sim.get_state_variables()

        assert "Susceptible" in vars
        assert "Infected" in vars
        assert "Resistant" in vars

    def test_get_all_variables(self):
        """Test get_all_variables includes parameters and intermediates."""
        sim = SIRSimulator()
        vars = sim.get_all_variables()

        # State variables
        assert "Susceptible" in vars
        assert "Infected" in vars
        assert "Resistant" in vars

        # Intermediate
        assert "S_to_I" in vars
        assert "I_to_R" in vars

        # Parameters
        assert "rateSI" in vars
        assert "rateIR" in vars

    def test_get_ground_truth_graph(self):
        """Test ground truth graph structure."""
        sim = SIRSimulator()
        graph = sim.get_ground_truth_graph()

        # Check variables
        assert "Susceptible" in graph.variables
        assert "Infected" in graph.variables
        assert "Resistant" in graph.variables

        # Check some expected edges
        deps = graph.to_dependencies()

        # S_to_I depends on rateSI, Susceptible, Infected
        assert "S_to_I" in deps
        assert "rateSI" in deps["S_to_I"]
        assert "Susceptible" in deps["S_to_I"]
        assert "Infected" in deps["S_to_I"]

        # I_to_R depends on Infected, rateIR
        assert "I_to_R" in deps
        assert "Infected" in deps["I_to_R"]
        assert "rateIR" in deps["I_to_R"]

    def test_get_source_path(self):
        """Test that source path points to a valid file."""
        sim = SIRSimulator()
        path = sim.get_source_path()

        assert path.exists()
        assert path.suffix == ".py"
        assert "sir" in path.name.lower()
