"""Command-line interface for SCM extraction."""

import json
from pathlib import Path
from typing import Optional

import click

from scmextract.core.config import load_config
from scmextract.extractors.registry import ExtractorRegistry, get_extractor
from scmextract.simulators.registry import SimulatorRegistry, get_simulator
from scmextract.evaluation.metrics import evaluate_graph
from scmextract.visualization.graph_viz import save_graph, visualize_graph


@click.group()
@click.version_option(version="0.1.0", prog_name="scmextract")
def cli():
    """SCM Extract - Extract Structural Causal Models from simulator code."""
    pass


@cli.command()
@click.argument("source_file", type=click.Path(exists=True))
@click.option("--method", "-m", default="ast", help="Extraction method (default: ast)")
@click.option("--variables", "-v", multiple=True, help="Variables to extract (can specify multiple)")
@click.option("--output", "-o", type=click.Path(), help="Output file (JSON, DOT, or PNG based on extension)")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output except errors")
def extract(source_file: str, method: str, variables: tuple, output: Optional[str], quiet: bool):
    """Extract causal graph from a Python source file.

    Example:
        scmextract extract model.py --method ast -v S -v I -v R -o graph.json
    """
    source_path = Path(source_file)
    var_set = set(variables) if variables else None

    extractor = get_extractor(method)
    graph = extractor.extract(source_path, variables=var_set)

    if output:
        output_path = Path(output)
        ext = output_path.suffix.lower()
        if ext == ".json":
            save_graph(graph, output_path, format="json")
        elif ext == ".dot":
            save_graph(graph, output_path, format="dot")
        elif ext in (".png", ".jpg", ".jpeg"):
            save_graph(graph, output_path, format="png")
        else:
            save_graph(graph, output_path, format="json")

        if not quiet:
            click.echo(f"Saved to: {output_path}")
    else:
        if not quiet:
            click.echo("\nExtracted Causal Graph:")
            click.echo(f"  Variables: {graph.variables}")
            click.echo(f"  Edges ({graph.num_edges()}):")
            for parent, child in graph.get_edges():
                click.echo(f"    {parent} -> {child}")


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--output-dir", "-o", type=click.Path(), help="Override output directory")
def run(config_file: str, output_dir: Optional[str]):
    """Run an extraction experiment from a YAML config file.

    Example:
        scmextract run configs/experiments/sir_basic.yaml
    """
    config = load_config(config_file)

    if output_dir:
        config.output_dir = output_dir

    click.echo(f"Running experiment: {config.name}")

    # Get simulator and extractor
    simulator = get_simulator(config.simulator)
    extractor = get_extractor(config.extractor)

    # Determine variables
    variables = set(config.variables) if config.variables else set(simulator.get_all_variables())

    click.echo(f"  Simulator: {config.simulator}")
    click.echo(f"  Extractor: {config.extractor}")
    click.echo(f"  Variables: {len(variables)}")

    # Extract
    source_path = simulator.get_source_path()
    predicted = extractor.extract(source_path, variables=variables)

    # Get ground truth and evaluate
    ground_truth = simulator.get_ground_truth_graph()
    metrics = evaluate_graph(predicted, ground_truth)

    click.echo("\nResults:")
    click.echo(f"  Precision: {metrics['precision']:.3f}")
    click.echo(f"  Recall:    {metrics['recall']:.3f}")
    click.echo(f"  F1 Score:  {metrics['f1']:.3f}")
    click.echo(f"  SHD:       {metrics['shd']}")

    # Save results
    output_path = Path(config.output_dir) / config.name
    output_path.mkdir(parents=True, exist_ok=True)

    # Save metrics
    metrics_file = output_path / "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)

    # Save predicted graph
    save_graph(predicted, output_path / "predicted.json", format="json")

    # Save visualization
    visualize_graph(predicted, output_path=str(output_path / "predicted.png"), title=f"{config.name} - Predicted")

    click.echo(f"\nResults saved to: {output_path}")


@cli.command("list-simulators")
def list_simulators():
    """List available simulators."""
    simulators = SimulatorRegistry.list_simulators()

    if not simulators:
        click.echo("No simulators registered.")
        return

    click.echo("Available simulators:")
    for name, cls in simulators.items():
        doc = cls.__doc__.split("\n")[0] if cls.__doc__ else "No description"
        click.echo(f"  {name}: {doc}")


@cli.command("list-extractors")
def list_extractors():
    """List available extraction methods."""
    extractors = ExtractorRegistry.list_extractors()

    if not extractors:
        click.echo("No extractors registered.")
        return

    click.echo("Available extractors:")
    for name, cls in extractors.items():
        doc = cls.__doc__.split("\n")[0] if cls.__doc__ else "No description"
        click.echo(f"  {name}: {doc}")


@cli.command()
@click.option("--methods", "-m", multiple=True, help="Extraction methods to benchmark (default: all)")
@click.option("--simulators", "-s", multiple=True, help="Simulators to benchmark (default: all)")
@click.option("--output", "-o", default="results/benchmark", help="Output directory")
def benchmark(methods: tuple, simulators: tuple, output: str):
    """Run benchmark across simulators and extraction methods.

    Example:
        scmextract benchmark --methods ast --output results/benchmark
    """
    import csv
    from datetime import datetime

    # Get all extractors and simulators if not specified
    extractor_names = list(methods) if methods else list(ExtractorRegistry.list_extractors().keys())
    simulator_names = list(simulators) if simulators else list(SimulatorRegistry.list_simulators().keys())

    if not extractor_names:
        click.echo("No extractors available.")
        return

    if not simulator_names:
        click.echo("No simulators available.")
        return

    click.echo(f"Benchmarking {len(extractor_names)} extractor(s) on {len(simulator_names)} simulator(s)")
    click.echo(f"  Extractors: {', '.join(extractor_names)}")
    click.echo(f"  Simulators: {', '.join(simulator_names)}")
    click.echo()

    # Prepare output directory
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    # Collect results
    results = []

    for sim_name in simulator_names:
        simulator = get_simulator(sim_name)
        ground_truth = simulator.get_ground_truth_graph()
        variables = set(simulator.get_all_variables())
        source_path = simulator.get_source_path()

        for ext_name in extractor_names:
            click.echo(f"  {sim_name} + {ext_name}...", nl=False)

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

            click.echo(f" F1={metrics['f1']:.3f}, SHD={metrics['shd']}")

            # Save individual results
            result_dir = output_path / sim_name / ext_name
            result_dir.mkdir(parents=True, exist_ok=True)
            save_graph(predicted, result_dir / "predicted.json", format="json")
            visualize_graph(predicted, output_path=str(result_dir / "predicted.png"),
                          title=f"{sim_name} - {ext_name}")

    # Save summary CSV
    csv_path = output_path / "summary.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    # Save summary JSON
    summary = {
        "timestamp": datetime.now().isoformat(),
        "extractors": extractor_names,
        "simulators": simulator_names,
        "results": results,
    }
    with open(output_path / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    click.echo(f"\nBenchmark complete. Results saved to: {output_path}")


if __name__ == "__main__":
    cli()
