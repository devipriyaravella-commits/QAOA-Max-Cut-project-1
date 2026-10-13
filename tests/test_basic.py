"""Sanity tests: pytest -q"""
import numpy as np
from qiskit.quantum_info import Statevector

from src.problem import brute_force, build_qaoa, cut_table, ideal_probs, load_graphs
from src.processors import coupling_map, load_processor
from src.routing import compile_for

A = load_processor("processors/processor_A.json")
B = load_processor("processors/processor_B.json")
GRAPHS = load_graphs("data/raw/graphs.json")


def test_official_processor_maps():
    assert A["num_qubits"] == 5 and sorted(map(tuple, A["coupling_map"])) == [(0, 1), (1, 2), (1, 3), (3, 4)]
    assert B["num_qubits"] == 9 and len(B["coupling_map"]) == 12
    assert sorted(tuple(sorted(e)) for e in B["coupling_map"]) == sorted(
        [(0, 1), (1, 2), (1, 6), (2, 3), (2, 6), (2, 5), (3, 4), (4, 5), (5, 6), (6, 7), (6, 8), (0, 8)])


def test_identical_noise_and_basis():
    assert A["noise"] == B["noise"] and A["basis_gates"] == B["basis_gates"]


def test_graphs_valid():
    for g in GRAPHS:
        assert all(1 <= w <= 5 and w == int(w) for _, _, w in g["edges"])
        assert all(0 <= i < g["num_nodes"] and 0 <= j < g["num_nodes"] for i, j, _ in g["edges"])


def test_numpy_qaoa_matches_qiskit():
    g = GRAPHS[0]; n, e = g["num_nodes"], g["edges"]
    gam, bet = [0.7, 1.9], [0.4, 0.9]
    qk = Statevector(build_qaoa(n, e, gam, bet, measure=False)).probabilities()
    assert np.allclose(qk, ideal_probs(n, e, gam, bet), atol=1e-9)


def test_brute_force_matches_table():
    g = GRAPHS[1]; best, bits = brute_force(g["num_nodes"], g["edges"])
    assert best == cut_table(g["num_nodes"], g["edges"]).max() and len(bits) % 2 == 0


def test_compiled_respects_coupling_and_semantics():
    g = GRAPHS[0]; n, e = g["num_nodes"], g["edges"]
    gam, bet = [0.8], [0.5]
    logical = build_qaoa(n, e, gam, bet, measure=False)
    for proc in (A, B):
        comp, swaps = compile_for(build_qaoa(n, e, gam, bet), proc, seed=1)
        cm = set(coupling_map(proc).get_edges())
        for inst in comp.data:
            if inst.operation.name == "cx":
                a, b = (comp.find_bit(q).index for q in inst.qubits)
                assert (a, b) in cm
        assert swaps >= 0
