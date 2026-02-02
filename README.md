# SCM Extract

Extract Structural Causal Models (SCMs) from simulator code.

A research toolkit for automatically extracting causal graphs from Python simulation code using static analysis.

## Installation

```bash
# Clone the repository
git clone https://github.com/filipblaafjell/scm-extraction.git
cd scm-extraction

# Install in development mode
pip install -e ".[dev]"
```

## Quick Start

### Extract causal graph from a file

```bash
scmextract extract path/to/model.py --method ast -v Susceptible -v Infected -v Resistant
```

### Run an experiment with evaluation

```bash
scmextract run configs/experiments/sir_basic.yaml
```

### Benchmark across simulators

```bash
scmextract benchmark --output results/benchmark
```

### List available resources

```bash
scmextract list-simulators
scmextract list-extractors
```

## Usage

### As a CLI tool

```bash
# Extract and save to JSON
scmextract extract src/scmextract/simulators/sir.py -m ast -o graph.json

# Extract and save visualization
scmextract extract src/scmextract/simulators/sir.py -m ast -o graph.png

# Run configured experiment
scmextract run configs/experiments/sir_basic.yaml -o results/my_experiment
```

### As a Python library

```python
from scmextract import ASTExtractor, SIRSimulator
from scmextract.evaluation import evaluate_graph

# Get simulator and its ground truth
simulator = SIRSimulator()
ground_truth = simulator.get_ground_truth_graph()

# Extract causal graph
extractor = ASTExtractor()
variables = set(simulator.get_all_variables())
predicted = extractor.extract(simulator.get_source_path(), variables=variables)

# Evaluate
metrics = evaluate_graph(predicted, ground_truth)
print(f"F1 Score: {metrics['f1']:.3f}")
print(f"SHD: {metrics['shd']}")
```

## Project Structure

```
scm-extraction/
├── src/scmextract/
│   ├── core/           # Base classes and types
│   ├── extractors/     # Extraction methods (AST, etc.)
│   ├── simulators/     # Simulator wrappers with ground truth
│   ├── evaluation/     # Metrics (precision, recall, F1, SHD)
│   ├── visualization/  # Graph visualization
│   └── cli.py          # Command-line interface
├── configs/            # Experiment configurations
├── scripts/            # Standalone scripts
├── tests/              # Test suite
└── results/            # Experiment outputs (gitignored)
```

## Extending

### Adding a new simulator

See [docs/adding_extractors.md](docs/adding_extractors.md) for guidance on adding new extractors.

To add a simulator:

```python
from scmextract.core.base import BaseSimulator
from scmextract.simulators.registry import SimulatorRegistry

@SimulatorRegistry.register("my_simulator")
class MySimulator(BaseSimulator):
    def get_source_path(self):
        return Path(__file__)

    def get_state_variables(self):
        return ["X", "Y", "Z"]

    def get_ground_truth_graph(self):
        return CausalGraph.from_dependencies({"Y": ["X"], "Z": ["Y"]})

    def run(self, steps=1000):
        # Run simulation...
        pass
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=scmextract
```

## License

MIT
