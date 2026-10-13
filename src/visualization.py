
"""Figures for Max-Cut graphs, processor topologies, and QAOA benchmarks."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


COL = {
    "Processor A": "#4c78a8",
    "Processor B": "#f58518",
    "All-to-all (reference)": "#9aa5b1",
}


def _save(fig, path):
    """Save a figure, creating the destination directory if necessary."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _validate_probability_array(probs, expected_length, label):
    """Validate a probability distribution."""
    probs = np.asarray(probs, dtype=float)

    if probs.ndim != 1 or len(probs) != expected_length:
        raise ValueError(
            f"{label} must be a one-dimensional array of "
            f"length {expected_length}."
        )

    if not np.all(np.isfinite(probs)) or np.any(probs < 0):
        raise ValueError(f"{label} contains invalid probabilities.")

    if not np.isclose(probs.sum(), 1.0, atol=1e-6):
        raise ValueError(f"{label} must sum to 1.")

    return probs


def plot_problem_graphs(graphs, optima, path):
    """Plot weighted graphs and highlight edges crossing an optimal cut."""
    if not graphs:
        raise ValueError("graphs cannot be empty.")

    fig, axes = plt.subplots(
        1, len(graphs), figsize=(4.2 * len(graphs), 4), squeeze=False
    )

    try:
        for ax, graph in zip(axes.ravel(), graphs):
            graph_id = graph["id"]
            n = int(graph["num_nodes"])

            if n <= 0:
                raise ValueError(f"{graph_id}: num_nodes must be positive.")

            if graph_id not in optima:
                raise KeyError(f"No optimum data found for {graph_id}.")

            optimum, bitstrings = optima[graph_id]
            if not bitstrings:
                raise ValueError(f"{graph_id}: no optimal bitstrings provided.")

            bits = str(bitstrings[0])
            if len(bits) != n or any(bit not in "01" for bit in bits):
                raise ValueError(f"{graph_id}: invalid optimal bitstring {bits!r}.")

            graph_nx = nx.Graph()
            graph_nx.add_nodes_from(range(n))
            graph_nx.add_weighted_edges_from(graph["edges"])

            # Bitstring is MSB-first; node q uses the q-th bit from the right.
            side = {q: int(bits[::-1][q]) for q in range(n)}
            pos = nx.spring_layout(graph_nx, seed=4, weight=None)

            nx.draw(
                graph_nx,
                pos,
                ax=ax,
                with_labels=True,
                node_size=650,
                font_color="white",
                node_color=[
                    "#c0392b" if side[q] else "#2c6fbb"
                    for q in graph_nx.nodes
                ],
            )

            cut_edges = [
                (i, j)
                for i, j, _ in graph["edges"]
                if side[i] != side[j]
            ]

            nx.draw_networkx_edges(
                graph_nx,
                pos,
                edgelist=cut_edges,
                edge_color="#27ae60",
                width=3,
                ax=ax,
            )

            edge_labels = {
                (i, j): int(weight)
                for i, j, weight in graph["edges"]
            }
            nx.draw_networkx_edge_labels(
                graph_nx, pos, edge_labels=edge_labels, ax=ax, font_size=9
            )

            ax.set_title(
                f"{graph_id} {graph['name']}\n"
                f"optimal cut = {float(optimum):g} "
                "(green = cut edges)",
                fontsize=9,
            )

        _save(fig, path)

    except Exception:
        plt.close(fig)
        raise


def plot_topology(proc, path):
    """Plot a processor's qubit connectivity."""
    n = int(proc["num_qubits"])
    if n <= 0:
        raise ValueError("num_qubits must be positive.")

    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from(map(tuple, proc["coupling_map"]))

    fig, ax = plt.subplots(figsize=(4.8, 4))

    try:
        nx.draw(
            graph,
            nx.kamada_kawai_layout(graph),
            with_labels=True,
            node_size=750,
            ax=ax,
            node_color="#ffe0b3" if n > 5 else "#cfe3ff",
            font_weight="bold",
        )

        ax.set_title(
            f"{proc['name']}: {n} qubits, "
            f"{len(proc['coupling_map'])} couplings"
        )
        _save(fig, path)

    except Exception:
        plt.close(fig)
        raise


def plot_ab_summary(summ, path):
    """Compare mean and standard deviation for benchmark metrics."""
    import pandas as pd

    required = {
        "graph", "p", "processor",
        "swaps_mean", "swaps_std",
        "twoq_mean", "twoq_std",
        "depth_mean", "depth_std",
        "ratio_mean", "ratio_std",
    }

    missing = required - set(summ.columns)
    if missing:
        raise ValueError(f"Benchmark summary is missing columns: {sorted(missing)}")

    if summ.empty:
        raise ValueError("Benchmark summary is empty.")

    metrics = [
        ("swaps_mean", "swaps_std", "SWAPs inserted"),
        ("twoq_mean", "twoq_std", "Two-qubit gates"),
        ("depth_mean", "depth_std", "Circuit depth"),
        ("ratio_mean", "ratio_std", "Approximation ratio"),
    ]

    keys = summ[["graph", "p"]].drop_duplicates().values.tolist()
    procs = [name for name in COL if name in set(summ["processor"])]

    if not procs:
        raise ValueError("No recognized processor names found in summary.")

    fig, axes = plt.subplots(1, 4, figsize=(18, 4))
    bar_width = 0.8 / len(procs)

    try:
        for ax, (mean_col, std_col, title) in zip(axes, metrics):
            for k, processor in enumerate(procs):
                values, errors = [], []

                for graph_id, p_value in keys:
                    rows = summ[
                        (summ["graph"] == graph_id)
                        & (summ["p"] == p_value)
                        & (summ["processor"] == processor)
                    ]

                    values.append(
                        float(rows[mean_col].iloc[0]) if not rows.empty else np.nan
                    )
                    errors.append(
                        float(rows[std_col].iloc[0])
                        if not rows.empty and pd.notna(rows[std_col].iloc[0])
                        else 0.0
                    )

                ax.bar(
                    np.arange(len(keys)) + k * bar_width,
                    values,
                    bar_width,
                    yerr=errors,
                    color=COL[processor],
                    label=processor,
                    capsize=2,
                )

            ax.set_xticks(
                np.arange(len(keys)) + bar_width * (len(procs) - 1) / 2
            )
            ax.set_xticklabels(
                [f"{graph_id}\np={p_value}" for graph_id, p_value in keys],
                fontsize=8,
            )
            ax.set_title(title, fontsize=10)

        axes[0].legend(fontsize=7)
        _save(fig, path)

    except Exception:
        plt.close(fig)
        raise


def plot_tradeoff(summ, path):
    """Plot two-qubit gate count against approximation ratio."""
    required = {
        "processor", "p", "twoq_mean", "twoq_std",
        "ratio_mean", "ratio_std", "graph",
    }

    missing = required - set(summ.columns)
    if missing:
        raise ValueError(f"Benchmark summary is missing columns: {sorted(missing)}")

    if summ.empty:
        raise ValueError("Benchmark summary is empty.")

    fig, ax = plt.subplots(figsize=(6.2, 4.6))

    try:
        for processor, color in COL.items():
            data = summ[summ["processor"] == processor]

            for p_value, marker in [(1, "o"), (2, "s")]:
                subset = data[data["p"] == p_value]
                if subset.empty:
                    continue

                ax.errorbar(
                    subset["twoq_mean"],
                    subset["ratio_mean"],
                    xerr=subset["twoq_std"],
                    yerr=subset["ratio_std"],
                    fmt=marker,
                    color=color,
                    label=f"{processor}, p={p_value}",
                    capsize=2,
                    alpha=0.9,
                )

                for _, row in subset.iterrows():
                    ax.annotate(
                        str(row["graph"]),
                        (row["twoq_mean"], row["ratio_mean"]),
                        fontsize=7,
                        xytext=(4, 3),
                        textcoords="offset points",
                    )

        ax.set_xlabel("Two-qubit gates after compilation")
        ax.set_ylabel("Approximation ratio (expected cut / optimum)")
        ax.set_title("Routing overhead vs solution quality")
        ax.legend(fontsize=7)
        _save(fig, path)

    except Exception:
        plt.close(fig)
        raise


def plot_landscape(grid_g, grid_b, F, opt, path, title):
    """Plot an ideal QAOA approximation-ratio landscape."""
    grid_g = np.asarray(grid_g, dtype=float)
    grid_b = np.asarray(grid_b, dtype=float)
    F = np.asarray(F, dtype=float)

    if grid_g.ndim != 1 or grid_b.ndim != 1:
        raise ValueError("grid_g and grid_b must be one-dimensional.")

    if F.shape != (len(grid_b), len(grid_g)):
        raise ValueError(
            "F must have shape (len(grid_b), len(grid_g))."
        )

    if not np.isfinite(opt) or opt <= 0:
        raise ValueError("opt must be a positive finite optimum value.")

    if not np.all(np.isfinite(F)):
        raise ValueError("F contains non-finite values.")

    fig, ax = plt.subplots(figsize=(5.2, 4.2))

    try:
        image = ax.imshow(
            F / opt,
            origin="lower",
            aspect="auto",
            cmap="viridis",
            extent=[grid_g[0], grid_g[-1], grid_b[0], grid_b[-1]],
        )

        ax.set_xlabel(r"$\gamma$")
        ax.set_ylabel(r"$\beta$")
        ax.set_title(title, fontsize=10)
        fig.colorbar(image, ax=ax, label="Ideal approximation ratio")
        _save(fig, path)

    except Exception:
        plt.close(fig)
        raise


def plot_distributions(entries, ideal_probs, n, opt_bits, path, top=12, title=""):
    """Compare ideal and experimental probabilities for the most likely states."""
    n = int(n)
    if n <= 0:
        raise ValueError("n must be positive.")

    if top <= 0:
        raise ValueError("top must be positive.")

    state_count = 2 ** n
    ideal_probs = _validate_probability_array(
        ideal_probs, state_count, "ideal_probs"
    )

    if not entries:
        entries = {}

    series = {"Ideal (noiseless)": ideal_probs}

    for label, probabilities in entries.items():
        series[label] = _validate_probability_array(
            probabilities, state_count, f"probabilities for {label}"
        )

    top = min(int(top), state_count)
    order = np.argsort(-ideal_probs)[:top]

    fig, ax = plt.subplots(figsize=(10, 3.8))
    bar_width = 0.8 / len(series)

    try:
        for k, (label, probabilities) in enumerate(series.items()):
            ax.bar(
                np.arange(top) + k * bar_width,
                probabilities[order],
                bar_width,
                label=label,
                color=COL.get(label, "#2d2d2d"),
            )

        ax.set_xticks(
            np.arange(top) + bar_width * (len(series) - 1) / 2
        )
        ax.set_xticklabels(
            [format(int(i), f"0{n}b") for i in order],
            rotation=60,
            fontsize=8,
        )

        ax.set_ylabel("Probability")
        ax.set_title(
            title + "   (optimal cuts: " + ", ".join(opt_bits) + ")",
            fontsize=10,
        )
        ax.legend(fontsize=8)
        _save(fig, path)

    except Exception:
        plt.close(fig)
        raise


def save_circuit(qc, path):
    """Save a Qiskit circuit diagram."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig = qc.draw("mpl", idle_wires=False, fold=40)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
