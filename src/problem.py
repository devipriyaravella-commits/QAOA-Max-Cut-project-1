"""Max-Cut problem handling, exact baseline, and QAOA implementation."""

import json
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from scipy.optimize import minimize


def load_graphs(path):
    """Load and validate weighted graphs from a JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    if "graphs" not in data:
        raise ValueError("Input JSON must contain a 'graphs' list.")

    graphs = []

    for graph in data["graphs"]:
        n = int(graph["num_nodes"])
        edges = [
            (int(i), int(j), float(w))
            for i, j, w in graph["edges"]
        ]

        validate_graph(n, edges)

        graphs.append({**graph, "num_nodes": n, "edges": edges})

    return graphs


def validate_graph(n, edges):
    """Validate graph size, endpoints, and positive edge weights."""
    if n <= 0:
        raise ValueError("The number of nodes must be positive.")

    seen = set()

    for i, j, w in edges:
        if not (0 <= i < n and 0 <= j < n):
            raise ValueError(f"Invalid edge endpoint: {(i, j)}")

        if i == j:
            raise ValueError("Self-loops are not supported.")

        if not np.isfinite(w) or w <= 0:
            raise ValueError("Edge weights must be finite and positive.")

        edge = (min(i, j), max(i, j))

        if edge in seen:
            raise ValueError(f"Duplicate edge: {edge}")

        seen.add(edge)


def cut_table(n, edges):
    """Return the cut value for every computational-basis bitstring."""
    validate_graph(n, edges)

    indices = np.arange(2**n)
    values = np.zeros(2**n, dtype=float)

    for i, j, weight in edges:
        bit_i = (indices >> i) & 1
        bit_j = (indices >> j) & 1
        values += weight * (bit_i != bit_j)

    return values


def brute_force(n, edges):
    """Return the exact maximum cut and optimal MSB-first bitstrings."""
    values = cut_table(n, edges)
    optimum = float(np.max(values))

    bitstrings = [
        format(int(k), f"0{n}b")
        for k in np.flatnonzero(np.isclose(values, optimum))
    ]

    return optimum, bitstrings


def zz_diag(n, edges):
    """Return the diagonal of sum(weight * Z_i Z_j)."""
    validate_graph(n, edges)

    indices = np.arange(2**n)
    diagonal = np.zeros(2**n, dtype=float)

    for i, j, weight in edges:
        zi = 1 - 2 * ((indices >> i) & 1)
        zj = 1 - 2 * ((indices >> j) & 1)
        diagonal += weight * zi * zj

    return diagonal


def qaoa_state(n, diag, gammas, betas):
    """
    Compute the ideal QAOA statevector.

    Cost Hamiltonian:
        H_C = sum_edges weight * (I - Z_i Z_j) / 2

    Mixer Hamiltonian:
        H_M = sum_i X_i

    Each layer applies exp(-i * beta * H_M), followed by
    exp(-i * gamma * H_C). The identity contribution to H_C
    is a global phase and can be omitted.
    """
    gammas = np.asarray(gammas, dtype=float)
    betas = np.asarray(betas, dtype=float)
    diag = np.asarray(diag, dtype=float)

    if n <= 0:
        raise ValueError("n must be positive.")

    if diag.shape != (2**n,):
        raise ValueError("diag must have length 2**n.")

    if gammas.ndim != 1 or betas.ndim != 1:
        raise ValueError("gammas and betas must be one-dimensional.")

    if len(gammas) == 0 or len(gammas) != len(betas):
        raise ValueError("gammas and betas must have equal, nonzero lengths.")

    if not np.all(np.isfinite(gammas)) or not np.all(np.isfinite(betas)):
        raise ValueError("QAOA parameters must be finite.")

    # |+>^n
    psi = np.full(2**n, 2 ** (-n / 2), dtype=complex)

    for gamma, beta in zip(gammas, betas):
        # exp(-i * gamma * H_C), ignoring a global phase:
        # exp(+i * gamma * sum(weight * Z_i Z_j) / 2)
        psi *= np.exp(0.5j * gamma * diag)

        # exp(-i * beta * X) = RX(2 * beta)
        c = np.cos(beta)
        s = np.sin(beta)
        mixer = np.array(
            [[c, -1j * s], [-1j * s, c]],
            dtype=complex,
        )

        psi = psi.reshape((2,) * n)

        for qubit in range(n):
            axis = n - 1 - qubit
            psi = np.tensordot(
                mixer, psi, axes=([1], [axis])
            )
            psi = np.moveaxis(psi, 0, axis)

        psi = psi.reshape(-1)

    return psi


def ideal_probs(n, edges, gammas, betas):
    """Return ideal measurement probabilities in integer-index order."""
    state = qaoa_state(n, zz_diag(n, edges), gammas, betas)
    probs = np.abs(state) ** 2

    # Guard against floating-point drift.
    return probs / probs.sum()


def optimise_qaoa(n, edges, p=1, seed=7, restarts=20):
    """
    Maximize ideal expected cut using seeded multi-start COBYLA.

    Returns:
        gammas, betas, best_expected_cut, restart_expected_cuts
    """
    if p <= 0:
        raise ValueError("p must be positive.")

    if restarts <= 0:
        raise ValueError("restarts must be positive.")

    table = cut_table(n, edges)
    diagonal = zz_diag(n, edges)
    rng = np.random.default_rng(seed)

    def negative_expected_cut(parameters):
        gammas = parameters[:p]
        betas = parameters[p:]

        state = qaoa_state(n, diagonal, gammas, betas)
        probabilities = np.abs(state) ** 2

        return -float(probabilities @ table)

    results = []

    for _ in range(restarts):
        initial = np.concatenate([
            rng.uniform(0, 2 * np.pi, p),
            rng.uniform(0, np.pi, p),
        ])

        result = minimize(
            negative_expected_cut,
            initial,
            method="COBYLA",
            options={
                "maxiter": 500,
                "rhobeg": 0.5,
            },
        )

        if np.isfinite(result.fun):
            results.append(result)

    if not results:
        raise RuntimeError("QAOA optimization produced no valid results.")

    best = min(results, key=lambda result: result.fun)

    gammas = best.x[:p]
    betas = best.x[p:]
    expected_cut = -float(best.fun)
    restart_values = sorted(-result.fun for result in results)

    return gammas, betas, expected_cut, restart_values


def build_qaoa(n, edges, gammas, betas, measure=True):
    """
    Build a Qiskit QAOA circuit using the standard Max-Cut convention.

    Cost layer: RZZ(-gamma * weight) on each edge.
    Mixer layer: RX(2 * beta) on every qubit.
    """
    validate_graph(n, edges)

    gammas = np.asarray(gammas, dtype=float)
    betas = np.asarray(betas, dtype=float)

    if gammas.ndim != 1 or betas.ndim != 1:
        raise ValueError("gammas and betas must be one-dimensional.")

    if len(gammas) == 0 or len(gammas) != len(betas):
        raise ValueError("gammas and betas must have equal, nonzero lengths.")

    if not np.all(np.isfinite(gammas)) or not np.all(np.isfinite(betas)):
        raise ValueError("QAOA parameters must be finite.")

    circuit = QuantumCircuit(n, n if measure else 0)
    circuit.h(range(n))

    for gamma, beta in zip(gammas, betas):
        for i, j, weight in edges:
            circuit.rzz(-float(gamma) * weight, i, j)

        for qubit in range(n):
            circuit.rx(2 * float(beta), qubit)

    if measure:
        circuit.measure(range(n), range(n))

    return circuit