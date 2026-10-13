"""Metrics for QAOA circuits and Max-Cut experiments."""

import math
import numpy as np


TWO_Q = {
    "cx", "cz", "ecr", "swap",
    "rxx", "ryy", "rzz",
}


def circuit_metrics(qc):
    """Return circuit depth, operation counts, and used-qubit count."""
    ops = {str(gate).lower(): int(count)
           for gate, count in qc.count_ops().items()}

    used = {
        qc.find_bit(qubit).index
        for instruction in qc.data
        if instruction.operation.name != "barrier"
        for qubit in instruction.qubits
    }

    return {
        "depth": int(qc.depth()),
        "total_ops": sum(ops.values()),
        "two_qubit_gates": sum(
            count for gate, count in ops.items()
            if gate in TWO_Q
        ),
        "physical_qubits_used": len(used),
        "operations": ops,
    }


def proportion_se(p, n):
    """Standard error of an estimated Bernoulli proportion."""
    if n <= 0:
        raise ValueError("n must be positive.")

    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be between 0 and 1.")

    return math.sqrt(p * (1.0 - p) / n)


def counts_to_probs(counts, n):
    """Convert Qiskit measurement counts into a length-2**n probability array."""
    if n <= 0:
        raise ValueError("n must be positive.")

    if not counts:
        raise ValueError("Measurement counts cannot be empty.")

    total = sum(counts.values())
    if total <= 0:
        raise ValueError("Total measurement count must be positive.")

    probs = np.zeros(2 ** n, dtype=float)

    for bitstring, count in counts.items():
        bits = str(bitstring).replace(" ", "")

        if len(bits) != n or any(bit not in "01" for bit in bits):
            raise ValueError(
                f"Invalid {n}-bit measurement outcome: {bitstring!r}"
            )

        if count < 0:
            raise ValueError("Measurement counts cannot be negative.")

        probs[int(bits, 2)] += count / total

    return probs


def cut_stats(probs, tab, shots):
    """Return expected cut, standard error, and best observed cut."""
    probs = np.asarray(probs, dtype=float)
    tab = np.asarray(tab, dtype=float)

    if probs.ndim != 1 or tab.ndim != 1 or probs.shape != tab.shape:
        raise ValueError("probs and tab must be equal-length 1D arrays.")

    if shots <= 0:
        raise ValueError("shots must be positive.")

    if not np.all(np.isfinite(probs)) or np.any(probs < 0):
        raise ValueError("Probabilities must be finite and nonnegative.")

    if not np.isclose(probs.sum(), 1.0, atol=1e-8):
        raise ValueError("Probabilities must sum to 1.")

    if not np.all(np.isfinite(tab)):
        raise ValueError("Cut values must be finite.")

    expected_cut = float(np.dot(probs, tab))
    variance = float(np.dot(probs, (tab - expected_cut) ** 2))

    # Standard error of the sample mean of cut values.
    standard_error = math.sqrt(max(variance, 0.0) / shots)

    # Positive probabilities identify outcomes observed in the distribution.
    best_cut = float(np.max(tab[probs > 0]))

    return expected_cut, standard_error, best_cut


def hellinger_fidelity(p, q):
    """Squared classical fidelity between two probability distributions."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)

    if p.ndim != 1 or q.ndim != 1 or p.shape != q.shape:
        raise ValueError("p and q must be equal-length 1D arrays.")

    if (
        not np.all(np.isfinite(p))
        or not np.all(np.isfinite(q))
        or np.any(p < 0)
        or np.any(q < 0)
    ):
        raise ValueError("Distributions must be finite and nonnegative.")

    if not np.isclose(p.sum(), 1.0, atol=1e-8):
        raise ValueError("Distribution p must sum to 1.")

    if not np.isclose(q.sum(), 1.0, atol=1e-8):
        raise ValueError("Distribution q must sum to 1.")

    fidelity = float(np.sum(np.sqrt(p * q)) ** 2)

    # Guard against tiny floating-point excursions outside [0, 1].
    return min(1.0, max(0.0, fidelity))