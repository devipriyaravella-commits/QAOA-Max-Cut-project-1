
"""Connectivity-aware transpilation with explicit routing SWAP accounting."""

from qiskit import transpile

from .processors import coupling_map


def compile_for(qc, proc, seed=0, opt=1):
    """
    Compile a circuit for a processor's coupling map.

    Returns:
        compiled_circuit: Circuit translated into the processor's basis gates.
        routing_swaps: Number of SWAP gates inserted in the routed circuit.

    SWAPs are counted before decomposition. Each SWAP is then decomposed
    into native gates without running another unrestricted transpilation.
    """
    if "basis_gates" not in proc:
        raise ValueError("Processor configuration must contain basis_gates.")

    basis = list(proc["basis_gates"])
    if not basis:
        raise ValueError("Processor basis_gates cannot be empty.")

    if "swap" in basis:
        routing_basis = basis
    else:
        routing_basis = basis + ["swap"]

    # Stage 1: Route using the processor's actual connectivity.
    routed = transpile(
        qc,
        coupling_map=coupling_map(proc),
        basis_gates=routing_basis,
        optimization_level=opt,
        seed_transpiler=seed,
    )

    routing_swaps = int(routed.count_ops().get("swap", 0))

    # Stage 2: Decompose only SWAP gates into native basis operations.
    # Do not transpile again without the coupling map.
    compiled = routed.decompose(gates_to_decompose=["swap"])

    # Check that SWAP gates were removed.
    if compiled.count_ops().get("swap", 0):
        raise RuntimeError("SWAP decomposition left unsupported SWAP gates.")

    # Check that all operations belong to the processor's declared basis,
    # allowing circuit bookkeeping operations.
    bookkeeping = {"measure", "barrier", "reset", "delay"}
    unsupported = set(compiled.count_ops()) - set(basis) - bookkeeping

    if unsupported:
        raise RuntimeError(
            f"Compiled circuit contains operations outside the processor "
            f"basis: {sorted(unsupported)}"
        )

    return compiled, routing_swaps


def compile_all_to_all(qc, proc, seed=0, opt=1):
    """Compile an unrestricted-connectivity simulation reference."""
    if "basis_gates" not in proc:
        raise ValueError("Processor configuration must contain basis_gates.")

    compiled = transpile(
        qc,
        basis_gates=list(proc["basis_gates"]),
        optimization_level=opt,
        seed_transpiler=seed,
    )

    return compiled, 0
