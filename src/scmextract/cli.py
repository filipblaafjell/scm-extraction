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


if __name__ == "__main__":
    cli()
