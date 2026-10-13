"""A/B benchmark runner: same QAOA parameters, shots, seeds and noise on Processor A, B and an all-to-all reference."""
import time

import numpy as np
import pandas as pd
from qiskit_aer import AerSimulator

from .metrics import circuit_metrics, counts_to_probs, cut_stats, hellinger_fidelity, proportion_se
from .problem import brute_force, build_qaoa, cut_table, ideal_probs, optimise_qaoa
from .processors import build_noise_model
from .routing import compile_all_to_all, compile_for

ALL2ALL = "All-to-all (reference)"


def prepare_instances(graphs, p_values, seed=7, restarts=20):
    """Exact optimum + optimised (ideal) QAOA parameters for every (graph, p). Parameters are reused on A and B."""
    inst = {}
    for g in graphs:
        n, edges = g["num_nodes"], g["edges"]
        opt, opt_bits = brute_force(n, edges)
        tab = cut_table(n, edges)
        for p in p_values:
            gam, bet, ideal_exp, _ = optimise_qaoa(n, edges, p, seed=seed, restarts=restarts)
            probs = ideal_probs(n, edges, gam, bet)
            inst[(g["id"], p)] = dict(graph=g, n=n, edges=edges, p=p, opt=opt, opt_bits=opt_bits, tab=tab,
                                      gammas=gam, betas=bet, ideal_exp=ideal_exp, ideal_probs=probs,
                                      random_exp=float(tab.mean()))
    return inst


def run_benchmark(inst, procs, shots=4096, n_seeds=10, opt_level=1, sim_seed=2026, log=print):
    """Returns (runs_df, circuits) where circuits[(gid,p,label)] = best-seed compiled circuit (fewest 2Q gates)."""
    ideal_sim = AerSimulator()
    sims = {label: AerSimulator(noise_model=build_noise_model(pr)) for label, pr in procs.items()}
    ref_proc = next(iter(procs.values()))
    sims[ALL2ALL] = AerSimulator(noise_model=build_noise_model(ref_proc))
    rows, circuits = [], {}
    for (gid, p), d in inst.items():
        n, edges, tab, opt = d["n"], d["edges"], d["tab"], d["opt"]
        logical = build_qaoa(n, edges, d["gammas"], d["betas"])
        logical_2q = 2 * len(edges) * p                      # each RZZ = 2 CX in the CX basis
        targets = [(lab, pr) for lab, pr in procs.items() if pr["num_qubits"] >= n] + [(ALL2ALL, ref_proc)]
        for label, pr in targets:
            seeds = range(1) if label == ALL2ALL else range(n_seeds)
            best = None
            for s in seeds:
                t0 = time.perf_counter()
                comp, swaps = compile_all_to_all(logical, pr, s, opt_level) if label == ALL2ALL \
                    else compile_for(logical, pr, s, opt_level)
                t_comp = time.perf_counter() - t0
                m = circuit_metrics(comp)
                t0 = time.perf_counter()
                counts = sims[label].run(comp, shots=shots, seed_simulator=sim_seed + s).result().get_counts()
                t_sim = time.perf_counter() - t0
                probs = counts_to_probs(counts, n)
                mu, se, bestcut = cut_stats(probs, tab, shots)
                p_opt = float(sum(probs[int(b, 2)] for b in d["opt_bits"]))
                row = dict(graph=gid, p=p, processor=label, transpile_seed=s, depth=m["depth"],
                           two_qubit_gates=m["two_qubit_gates"], swaps=swaps,
                           extra_2q_vs_logical=m["two_qubit_gates"] - logical_2q,
                           physical_qubits_used=m["physical_qubits_used"], total_ops=m["total_ops"],
                           expected_cut=mu, expected_cut_se=se, approx_ratio_expected=mu / opt,
                           best_cut=bestcut, approx_ratio_best=bestcut / opt,
                           p_optimal=p_opt, p_optimal_se=proportion_se(p_opt, shots),
                           dist_fidelity=hellinger_fidelity(probs, d["ideal_probs"]),
                           ideal_expected_cut=d["ideal_exp"], random_baseline_ratio=d["random_exp"] / opt,
                           ideal_ratio=d["ideal_exp"] / opt, optimum=opt, shots=shots,
                           transpile_time_s=t_comp, sim_time_s=t_sim)
                if s == 0:   # semantic check: noiseless execution of the compiled circuit must match the ideal
                    ic = ideal_sim.run(comp, shots=200000, seed_simulator=sim_seed).result().get_counts()
                    row["noiseless_compiled_expected_cut"] = cut_stats(counts_to_probs(ic, n), tab, 200000)[0]
                rows.append(row)
                if best is None or m["two_qubit_gates"] < best[0]:
                    best = (m["two_qubit_gates"], comp, probs)
            circuits[(gid, p, label)] = dict(circuit=best[1], probs=best[2])
            log(f"{gid} p={p} {label:24s} done")
    return pd.DataFrame(rows), circuits


def summarise(runs):
    g = runs.groupby(["graph", "p", "processor"])
    agg = g.agg(swaps_mean=("swaps", "mean"), swaps_std=("swaps", "std"), swaps_min=("swaps", "min"),
                twoq_mean=("two_qubit_gates", "mean"), twoq_std=("two_qubit_gates", "std"),
                twoq_min=("two_qubit_gates", "min"),
                depth_mean=("depth", "mean"), depth_std=("depth", "std"), depth_min=("depth", "min"),
                ratio_mean=("approx_ratio_expected", "mean"), ratio_std=("approx_ratio_expected", "std"),
                ratio_best_mean=("approx_ratio_best", "mean"),
                p_opt_mean=("p_optimal", "mean"), p_opt_std=("p_optimal", "std"),
                fidelity_mean=("dist_fidelity", "mean"), fidelity_std=("dist_fidelity", "std"),
                transpile_time_mean=("transpile_time_s", "mean"), sim_time_mean=("sim_time_s", "mean"),
                qubits_used=("physical_qubits_used", "max"), n_seeds=("transpile_seed", "count"),
                ideal_ratio=("ideal_ratio", "first"), random_ratio=("random_baseline_ratio", "first")).reset_index()
    return agg.fillna(0.0)
