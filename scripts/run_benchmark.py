#!/usr/bin/env python3
"""Run benchmark across all simulators and extractors.

Example:
    python scripts/run_benchmark.py --output results/benchmark
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scmextract.extractors import ExtractorRegistry, get_extractor
from scmextract.simulators import SimulatorRegistry, get_simulator
from scmextract.evaluation import evaluate_graph
from scmextract.visualization import visualize_graph, save_graph


def main():
    parser = argparse.ArgumentParser(description="Run benchmark across simulators and extractors")
    parser.add_argument("--output", "-o", default="results/benchmark", help="Output directory")
    parser.add_argument("--extractors", "-e", nargs="+", help="Specific extractors to run")
    parser.add_argument("--simulators", "-s", nargs="+", help="Specific simulators to run")
    args = parser.parse_args()

    # Get extractors and simulators
    extractor_names = args.extractors or list(ExtractorRegistry.list_extractors().keys())
    simulator_names = args.simulators or list(SimulatorRegistry.list_simulators().keys())

    print(f"Benchmarking {len(extractor_names)} extractor(s) on {len(simulator_names)} simulator(s)")
    print(f"  Extractors: {', '.join(extractor_names)}")
    print(f"  Simulators: {', '.join(simulator_names)}")
    print()

    # Prepare output
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    # Run benchmark
    results = []

    for sim_name in simulator_names:
        simulator = get_simulator(sim_name)
        ground_truth = simulator.get_ground_truth_graph()
        variables = set(simulator.get_all_variables())
        source_path = simulator.get_source_path()

        for ext_name in extractor_names:
            print(f"  {sim_name} + {ext_name}...", end="", flush=True)

            extractor = get_extractor(ext_name)
            predicted = extractor.extract(source_path, variables=variables)
            metrics = evaluate_graph(predicted, ground_truth)

            results.append({
                "simulator": sim_name,
                "extractor": ext_name,
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "shd": metrics["shd"],
                "num_predicted_edges": predicted.num_edges(),
                "num_true_edges": ground_truth.num_edges(),
            })

            print(f" F1={metrics['f1']:.3f}, SHD={metrics['shd']}")

            # Save individual results
            result_dir = output_path / sim_name / ext_name
            result_dir.mkdir(parents=True, exist_ok=True)
            save_graph(predicted, result_dir / "predicted.json", format="json")
            visualize_graph(
                predicted,
                output_path=str(result_dir / "predicted.png"),
                title=f"{sim_name} - {ext_name}"
            )

    # Save summary
    csv_path = output_path / "summary.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "extractors": extractor_names,
        "simulators": simulator_names,
        "results": results,
    }
    with open(output_path / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nBenchmark complete. Results saved to: {output_path}")

    # Print summary table
    print("\n" + "=" * 60)
    print(f"{'Simulator':<15} {'Extractor':<12} {'Precision':>10} {'Recall':>10} {'F1':>10} {'SHD':>6}")
    print("-" * 60)
    for r in results:
        print(f"{r['simulator']:<15} {r['extractor']:<12} {r['precision']:>10.3f} {r['recall']:>10.3f} {r['f1']:>10.3f} {r['shd']:>6}")
    print("=" * 60)


if __name__ == "__main__":
    main()
