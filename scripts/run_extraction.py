#!/usr/bin/env python3
"""Run a single extraction and display results.

Example:
    python scripts/run_extraction.py --simulator sir --extractor ast
"""

import argparse
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scmextract.extractors import get_extractor
from scmextract.simulators import get_simulator
from scmextract.evaluation import evaluate_graph
from scmextract.visualization import visualize_graph, save_graph


def main():
    parser = argparse.ArgumentParser(description="Run SCM extraction on a simulator")
    parser.add_argument("--simulator", "-s", default="sir", help="Simulator name")
    parser.add_argument("--extractor", "-e", default="ast", help="Extractor name")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--visualize", "-v", action="store_true", help="Show visualization")
    args = parser.parse_args()

    # Get simulator and extractor
    print(f"Simulator: {args.simulator}")
    print(f"Extractor: {args.extractor}")

    simulator = get_simulator(args.simulator)
    extractor = get_extractor(args.extractor)

    # Get variables and source
    variables = set(simulator.get_all_variables())
    source_path = simulator.get_source_path()

    print(f"Source: {source_path}")
    print(f"Variables: {variables}")
    print()

    # Extract
    predicted = extractor.extract(source_path, variables=variables)
    ground_truth = simulator.get_ground_truth_graph()

    # Evaluate
    metrics = evaluate_graph(predicted, ground_truth)

    print("Results:")
    print(f"  Precision: {metrics['precision']:.3f}")
    print(f"  Recall:    {metrics['recall']:.3f}")
    print(f"  F1 Score:  {metrics['f1']:.3f}")
    print(f"  SHD:       {metrics['shd']}")
    print()

    print(f"Predicted edges ({predicted.num_edges()}):")
    for parent, child in predicted.get_edges():
        print(f"  {parent} -> {child}")

    print()
    print(f"Ground truth edges ({ground_truth.num_edges()}):")
    for parent, child in ground_truth.get_edges():
        print(f"  {parent} -> {child}")

    # Save output
    if args.output:
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        save_graph(predicted, output_path / "predicted.json", format="json")
        visualize_graph(predicted, output_path=str(output_path / "predicted.png"))
        print(f"\nSaved to: {output_path}")

    # Show visualization
    if args.visualize:
        visualize_graph(predicted, title=f"{args.simulator} - {args.extractor}")


if __name__ == "__main__":
    main()
