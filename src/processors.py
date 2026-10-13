"""Processor definitions, coupling maps, and noise models."""

import json
from pathlib import Path

from qiskit.transpiler import CouplingMap
from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    depolarizing_error,
)


def load_processor(path):
    """Load and validate a processor JSON configuration."""
    path = Path(path)
    proc = json.loads(path.read_text(encoding="utf-8"))

    required = {
        "name",
        "num_qubits",
        "coupling_map",
        "basis_gates",
        "noise",
    }

    missing = required - proc.keys()
    if missing:
        raise ValueError(
            f"{path}: missing processor fields: {sorted(missing)}"
        )

    n = proc["num_qubits"]
    if not isinstance(n, int) or n <= 0:
        raise ValueError("num_qubits must be a positive integer.")

    basis = proc["basis_gates"]
    if not isinstance(basis, list) or not basis:
        raise ValueError("basis_gates must be a non-empty list.")

    # Validate topology and noise configuration.
    coupling_map(proc)
    _validate_noise(proc)

    return proc


def coupling_map(proc):
    """Create a bidirectional Qiskit CouplingMap from undirected edges."""
    n = proc["num_qubits"]
    edges = proc["coupling_map"]

    if not isinstance(edges, list):
        raise ValueError("coupling_map must be a list of edges.")

    directed = []
    seen = set()

    for edge in edges:
        if len(edge) != 2:
            raise ValueError(f"Invalid coupling edge: {edge}")

        a, b = edge

        if not isinstance(a, int) or not isinstance(b, int):
            raise ValueError("Coupling endpoints must be integers.")

        if not (0 <= a < n and 0 <= b < n):
            raise ValueError(f"Coupling endpoint outside 0..{n - 1}: {edge}")

        if a == b:
            raise ValueError("Self-couplings are not allowed.")

        normalized = (min(a, b), max(a, b))
        if normalized in seen:
            raise ValueError(f"Duplicate coupling edge: {normalized}")

        seen.add(normalized)
        directed.extend([(a, b), (b, a)])

    return CouplingMap(directed)


def _validate_noise(proc):
    """Validate the noise parameters used by the Aer noise model."""
    noise = proc["noise"]

    required = {
        "one_qubit_depolarizing",
        "two_qubit_depolarizing",
        "readout_p01",
        "readout_p10",
        "noisy_gates_1q",
        "noisy_gates_2q",
    }

    missing = required - noise.keys()
    if missing:
        raise ValueError(
            f"Missing noise fields: {sorted(missing)}"
        )

    for key in (
        "one_qubit_depolarizing",
        "two_qubit_depolarizing",
        "readout_p01",
        "readout_p10",
    ):
        value = noise[key]

        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"{key} must be between 0 and 1.")

    for key in ("noisy_gates_1q", "noisy_gates_2q"):
        if not isinstance(noise[key], list):
            raise ValueError(f"{key} must be a list.")

    # Ensure the configured noise gates exist in the declared basis.
    basis = set(proc["basis_gates"])
    for key in ("noisy_gates_1q", "noisy_gates_2q"):
        unknown = set(noise[key]) - basis
        if unknown:
            raise ValueError(
                f"{key} contains gates absent from basis_gates: "
                f"{sorted(unknown)}"
            )


def build_noise_model(proc):
    """Build the configured depolarizing and asymmetric readout noise model."""
    _validate_noise(proc)

    noise = proc["noise"]
    model = NoiseModel(basis_gates=proc["basis_gates"])

    if noise["noisy_gates_1q"]:
        model.add_all_qubit_quantum_error(
            depolarizing_error(
                noise["one_qubit_depolarizing"], 1
            ),
            noise["noisy_gates_1q"],
        )

    if noise["noisy_gates_2q"]:
        model.add_all_qubit_quantum_error(
            depolarizing_error(
                noise["two_qubit_depolarizing"], 2
            ),
            noise["noisy_gates_2q"],
        )

    p01 = noise["readout_p01"]
    p10 = noise["readout_p10"]

    model.add_all_qubit_readout_error(
        ReadoutError([
            [1 - p01, p01],
            [p10, 1 - p10],
        ])
    )

    return model