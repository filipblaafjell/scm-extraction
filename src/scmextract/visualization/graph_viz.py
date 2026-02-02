"""Visualization utilities for causal graphs."""

from pathlib import Path
from typing import Dict, Optional, Set

import matplotlib.pyplot as plt
import networkx as nx

from scmextract.core.types import CausalGraph


def to_networkx(graph: CausalGraph) -> nx.DiGraph:
    """Convert CausalGraph to NetworkX DiGraph.

    Args:
        graph: CausalGraph instance.

    Returns:
        NetworkX directed graph.
    """
    G = nx.DiGraph()
    G.add_nodes_from(graph.variables)

    for parent, child in graph.get_edges():
        G.add_edge(parent, child)

    return G


def to_dot(graph: CausalGraph, title: str = "Causal Graph") -> str:
    """Convert CausalGraph to DOT format for Graphviz.

    Args:
        graph: CausalGraph instance.
        title: Graph title.

    Returns:
        DOT format string.
    """
    lines = [f'digraph "{title}" {{', "    rankdir=BT;", "    node [shape=box];"]

    for parent, child in graph.get_edges():
        lines.append(f'    "{parent}" -> "{child}";')

    lines.append("}")
    return "\n".join(lines)


def visualize_graph(
    graph: CausalGraph,
    output_path: Optional[str] = None,
    title: str = "Causal Graph",
    node_categories: Optional[Dict[str, Set[str]]] = None,
    figsize: tuple = (12, 8),
) -> None:
    """Visualize a causal graph using matplotlib and networkx.

    Args:
        graph: CausalGraph to visualize.
        output_path: Path to save the image. If None, displays interactively.
        title: Plot title.
        node_categories: Optional dict mapping category names to sets of node names.
                        Used for coloring nodes by category.
        figsize: Figure size as (width, height).
    """
    G = to_networkx(graph)

    plt.figure(figsize=figsize)
    plt.title(title, fontsize=14, fontweight="bold")

    # Default color scheme
    default_colors = {
        "parameters": "#90EE90",     # Light green
        "intermediate": "#FFB366",   # Orange
        "state": "#87CEEB",          # Light blue
    }

    # Determine node colors
    color_map = []
    for node in G.nodes():
        color = "#D3D3D3"  # Default gray
        if node_categories:
            for category, nodes in node_categories.items():
                if node in nodes:
                    color = default_colors.get(category, "#D3D3D3")
                    break
        color_map.append(color)

    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Draw
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=2500, alpha=0.9)
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight="bold")
    nx.draw_networkx_edges(
        G, pos, edge_color="#666666", arrows=True,
        arrowsize=20, arrowstyle="->", connectionstyle="arc3,rad=0.1"
    )

    # Legend if categories provided
    if node_categories:
        legend_elements = []
        for category in node_categories:
            color = default_colors.get(category, "#D3D3D3")
            legend_elements.append(
                plt.scatter([], [], c=color, s=100, label=category.capitalize())
            )
        plt.legend(handles=legend_elements, loc="upper left", fontsize=9)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()
    else:
        plt.show()


def save_graph(graph: CausalGraph, output_path: str, format: str = "json") -> None:
    """Save causal graph to file.

    Args:
        graph: CausalGraph to save.
        output_path: Output file path.
        format: Output format ('json', 'dot', or 'png').
    """
    import json

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "json":
        data = {
            "variables": graph.variables,
            "edges": graph.get_edges(),
            "dependencies": graph.to_dependencies(),
        }
        if graph.metadata:
            data["metadata"] = graph.metadata
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    elif format == "dot":
        dot_content = to_dot(graph)
        with open(output_path, "w") as f:
            f.write(dot_content)

    elif format == "png":
        visualize_graph(graph, output_path=str(output_path))

    else:
        raise ValueError(f"Unknown format: {format}. Use 'json', 'dot', or 'png'.")
