# Phase 1 Project Report

## PS-01 / O1: Max-Cut on Weighted Graphs

### QAOA Circuit Construction and SWAP Bottleneck Analysis

**Track:** Quantum Optimization  
**Framework:** Qiskit and Qiskit Aer  
**Language:** Python  
**Experiment notebook:** `main.ipynb`

**Team name:** `Ravella Devi Priya`  
**Team members:** `KASARLA HASWANTH,Shaik Atiq Rehaman,Rachuri Manogna`  

---

## 1. Problem and Experimental Setup

### 1.1 Problem statement

The weighted Max-Cut problem partitions the vertices of an undirected weighted graph into two sets so that the total weight of edges crossing between the sets is maximized.

For a graph \(G=(V,E)\), the cut value is

\[
C(x)=\sum*{(i,j)\in E} w*{ij}[x_i\ne x_j],
\]

where \(w\_{ij}\) is the weight of edge \((i,j)\), and \(x_i\in\{0,1\}\) identifies the partition assigned to vertex \(i\). The exact optimum is computed by brute-force enumeration and used as a classical benchmark.

### 1.2 Benchmark graphs

The benchmark graphs use integer edge weights from 1 to 5. They are team-generated instances because official graph instances were not present in the supplied project materials; the input audit is documented in `docs/INPUT_AUDIT.md`.

| Graph | Instance              | Vertices | Edges | Total edge weight | Exact optimum | Evaluated on |
| ----- | --------------------- | -------: | ----: | ----------------: | ------------: | ------------ |
| G1    | `dense_5node`         |        5 |     8 |                19 |            15 | A and B      |
| G2    | `ring_chord_5node`    |        5 |     6 |                24 |            22 | A and B      |
| G3    | `A_native_tree_5node` |        5 |     4 |                14 |            14 | A and B      |
| G4    | `custom_6node`        |        6 |     9 |                28 |            28 | B only       |

Processor A has five qubits, so G4 is evaluated only on Processor B, which has nine qubits. G3 is a control instance whose interaction graph matches Processor A's tree-shaped coupling map.

### 1.3 Processor configurations

**Processor A**

- Five physical qubits.
- Coupling edges: (0,1), (1,2), (1,3), and (3,4).
- Tree-shaped connectivity with four couplings.

**Processor B**

- Nine physical qubits.
- Twelve coupling edges.
- A more connected, heavy-hex-inspired topology.

The processor configurations specify the basis gates `rz`, `sx`, `x`, and `cx`. The all-to-all reference removes the connectivity restriction to provide a comparison for routing overhead. It is a simulation reference, not an official hardware processor.

### 1.4 Noise assumptions

The simulations use the following assumed noise parameters on both processors:

| Noise component                 | Assumed value |
| ------------------------------- | ------------: |
| Single-qubit depolarizing error |          0.1% |
| CX depolarizing error           |          0.5% |
| Readout error \(P(1\mid0)\)     |            1% |
| Readout error \(P(0\mid1)\)     |            2% |

These values are assumptions and should not be represented as official frozen processor specifications unless confirmed by the organizers.

### 1.5 Experimental procedure

The workflow is:

1. Load the weighted graph instances.
2. Compute each graph's exact classical Max-Cut optimum.
3. Construct QAOA circuits at depths \(p=1\) and \(p=2\).
4. Optimize the QAOA parameters on a noiseless simulator using COBYLA with 20 seeded restarts.
5. Reuse the optimized parameters in the relevant processor comparisons.
6. Transpile for Processor A, Processor B, and the all-to-all reference.
7. Use transpiler seeds 0–9 and optimization level 1 for processor experiments.
8. Execute noisy simulations using 4096 shots.
9. Calculate solution-quality and circuit-resource metrics.
10. Export CSV summaries and plots.

The reported environment lists Qiskit 2.5.2 and Qiskit Aer 0.17.2; see `requirements-lock.txt` for the project's pinned dependencies.

### 1.6 SWAP counting

Routing SWAPs are counted before decomposition. A SWAP can be decomposed into three CX gates when CX is the available entangling basis operation. The final two-qubit gate count is recorded separately from the SWAP count.

Connectivity validation and logical-equivalence validation are separate requirements: a circuit can use only allowed physical couplings and still require a separate check that the compiled circuit preserves the intended logical behavior.

---

## 2. Results

The tables below are based on the uploaded `final_comparison(1).csv`, `summary_by_graph.csv`, `classical_baseline.csv`, and `quality_significance.csv` files. They should be regenerated if the experiment is rerun and its outputs change.

### 2.1 Aggregate comparison for G1–G3

The following values summarize the common five-vertex benchmark set. Processor results average over ten transpiler seeds; the all-to-all reference is recorded as a single reference run for each graph and depth.

| Metric                            | QAOA depth | Processor A | Processor B |   B − A | All-to-all reference |
| --------------------------------- | ---------: | ----------: | ----------: | ------: | -------------------: |
| Expected-cut approximation ratio  |          1 |      0.7637 |      0.7661 | +0.0024 |               0.7652 |
| Expected-cut approximation ratio  |          2 |      0.8398 |      0.8496 | +0.0097 |               0.8505 |
| Probability of optimal cut        |          1 |      0.2135 |      0.2138 | +0.0003 |               0.2111 |
| Probability of optimal cut        |          2 |      0.4007 |      0.4137 | +0.0130 |               0.4102 |
| Distribution fidelity vs. ideal   |          1 |      0.9829 |      0.9849 | +0.0020 |               0.9838 |
| Distribution fidelity vs. ideal   |          2 |      0.9589 |      0.9696 | +0.0108 |               0.9706 |
| Circuit depth                     |          1 |       36.67 |       29.07 |   -7.60 |                26.00 |
| Circuit depth                     |          2 |       66.37 |       51.97 |  -14.40 |                45.00 |
| CX gates                          |          1 |       18.00 |       13.40 |   -4.60 |                12.00 |
| CX gates                          |          2 |       39.03 |       27.13 |  -11.90 |                24.00 |
| Routing SWAPs                     |          1 |        2.00 |        0.47 |   -1.53 |                    0 |
| Routing SWAPs                     |          2 |        5.03 |        1.07 |   -3.97 |                    0 |
| Extra two-qubit gates vs. logical |          1 |        6.00 |        1.40 |   -4.60 |                    0 |
| Extra two-qubit gates vs. logical |          2 |       15.03 |        3.13 |  -11.90 |                    0 |
| Physical qubits used              |    1 and 2 |           5 |           5 |       0 |                    5 |

The main observed pattern is that Processor B has lower average SWAP counts, CX counts, and circuit depth than Processor A in the common benchmark set. The all-to-all reference has the lowest reported routing-related resource cost.

### 2.2 Per-graph comparison

The following table uses the graph-level summaries and shot-noise significance results in the uploaded CSV files. Approximation ratios are expected cut divided by exact optimum.

| Graph | Depth | SWAPs A | SWAPs B | CX A | CX B | Ratio A | Ratio B |   B − A | z-score |
| ----- | ----: | ------: | ------: | ---: | ---: | ------: | ------: | ------: | ------: |
| G1    |     1 |     3.0 |     1.4 | 25.0 | 20.2 |  0.8065 |  0.8110 | +0.0045 |    1.09 |
| G1    |     2 |     8.1 |     3.2 | 56.3 | 41.4 |  0.8407 |  0.8498 | +0.0090 |    2.11 |
| G2    |     1 |     3.0 |     0.0 | 21.0 | 12.0 |  0.7415 |  0.7459 | +0.0044 |    0.93 |
| G2    |     2 |     7.0 |     0.0 | 44.8 | 24.0 |  0.8194 |  0.8422 | +0.0228 |    4.72 |
| G3    |     1 |     0.0 |     0.0 |  8.0 |  8.0 |  0.7432 |  0.7413 | -0.0018 |   -0.37 |
| G3    |     2 |     0.0 |     0.0 | 16.0 | 16.0 |  0.8594 |  0.8568 | -0.0026 |   -0.56 |

The z-scores are the values recorded in `quality_significance.csv`. They are based on the project's stated shot-noise comparison and should not be interpreted as a comprehensive statistical analysis across all sources of experimental variability.

### 2.3 G4: six-vertex instance

G4 is evaluated on Processor B only. Its reported means are:

| Metric                                          | Depth 1 | Depth 2 |
| ----------------------------------------------- | ------: | ------: |
| Routing SWAPs on Processor B                    |     2.1 |     5.8 |
| CX gates on Processor B                         |    24.3 |    53.4 |
| CX gates in all-to-all reference                |      18 |      36 |
| Circuit depth on Processor B                    |    37.9 |    83.1 |
| Expected-cut approximation ratio on Processor B |  0.6947 |  0.6909 |
| Ideal approximation ratio                       |  0.7201 |  0.7362 |

For this instance, the noisy approximation ratio at depth 2 is lower than at depth 1 in the recorded Processor B results. This illustrates that adding QAOA layers does not guarantee improved noisy performance.

### 2.4 Generated artifacts

Numerical outputs are stored under `results/tables/`, including:

- `all_runs.csv` — individual experiment records.
- `summary_by_graph.csv` — graph-level means and variability.
- `final_comparison.csv` — aggregate processor comparison.
- `classical_baseline.csv` — graph sizes, weights, and exact optima.
- `processor_a_metrics.csv` and `processor_b_metrics.csv` — processor experiment records.
- `qaoa_parameters.csv` — optimized parameters and ideal metrics.
- `quality_significance.csv` — recorded pairwise quality comparison statistics.

Figures are stored under `results/figures/`, including `AB_performance.png`, `architecture_tradeoffs.png`, `problem_graphs.png`, processor topology diagrams, circuit diagrams, the output distribution, and the QAOA parameter landscape.

---

## 3. Interpretation and Discussion

### 3.1 Connectivity and compilation cost

In the common benchmark set at \(p=2\), the recorded mean CX count is 39.03 for Processor A and 27.13 for Processor B. The mean circuit depths are 66.37 and 51.97, respectively.

These results are consistent with the difference in connectivity: Processor A has four couplings in a tree, while Processor B has twelve couplings and additional cycles. The data support the conclusion that connectivity is associated with compilation cost for these tested instances. They do not establish that connectivity is the only possible cause of every difference.

### 3.2 Routing overhead

The average SWAP count on Processor A increases from 2.00 at \(p=1\) to 5.03 at \(p=2\). Processor B increases from 0.47 to 1.07 over the same depths.

The additional routing operations increase the number of two-qubit gates and can increase circuit depth. Since two-qubit operations are subject to the assumed noise model, additional routing may also affect the measured output distribution.

The measured `extra_2q_vs_logical` column should be used to quantify the relationship between routing SWAPs and additional CX gates rather than assuming a perfect three-CX increase for every SWAP in every optimized output circuit.

### 3.3 Control case G3

G3's interaction graph matches Processor A's coupling topology. The recorded results show zero SWAPs and equal CX counts on A and B at both tested depths.

The approximation ratios are close: at \(p=2\), 0.8594 on Processor A and 0.8568 on Processor B. This control case illustrates that a suitable match between logical interactions and hardware couplings can reduce routing overhead.

### 3.4 Solution quality

For G2 at \(p=2\), the recorded expected-cut approximation ratios are 0.8194 on Processor A, 0.8422 on Processor B, and 0.8390 in the all-to-all reference. Processor B is therefore comparable to the reference in this particular noisy simulation and slightly higher in the recorded ratio. This does not establish that Processor B is generally better than an unrestricted-connectivity device.

For G1 at \(p=2\), the recorded ratios are 0.8407 on A and 0.8498 on B. For G3, the difference is small and negative for B relative to A. The observed quality differences vary by graph and depth.

The reported z-score for G2 at \(p=2\) is approximately 4.72 under the project's shot-noise calculation. This is evidence of a difference under that calculation's assumptions, not proof that every source of uncertainty has been accounted for.

### 3.5 Effect of QAOA depth

For G1–G3, the aggregate expected-cut approximation ratio increases from 0.7637 to 0.8398 on Processor A and from 0.7661 to 0.8496 on Processor B when moving from \(p=1\) to \(p=2\).

This improvement comes with larger circuits and more routing overhead. G4 demonstrates an important exception: its recorded Processor B approximation ratio decreases from 0.6947 at \(p=1\) to 0.6909 at \(p=2\). Increasing QAOA depth is therefore not guaranteed to improve the noisy result for every graph.

### 3.6 Processor B and the all-to-all reference

The all-to-all reference has zero routing SWAPs and lower reported CX counts than either constrained processor. Processor B reduces routing overhead compared with Processor A but still incurs SWAPs for some graphs, including G1 and G4.

This supports the conclusion that additional connectivity can reduce routing cost without necessarily eliminating it.

---

## 4. Phase 2 Readiness and Future Work

The experiments identify several directions for further investigation.

### 4.1 Connectivity-aware initial layout

Compare alternative logical-to-physical initial layouts and measure their effects on SWAP count, CX count, and circuit depth.

### 4.2 Routing and gate-count optimization

Test alternative routing heuristics and gate-aware compilation strategies. Keep the problem instances, parameters, and measurement settings fixed when comparing approaches.

### 4.3 Parameter optimization and depth

Explore alternative parameter initializations, more optimization restarts, and noise-aware parameter optimization. Evaluate whether additional QAOA layers improve quality enough to justify their circuit cost.

### 4.4 Statistical robustness

Use additional repetitions or seeds and report uncertainty intervals. Separate variation from finite-shot sampling from variation caused by transpilation and optimization choices.

### 4.5 Additional processor configurations

When a new processor configuration becomes available, repeat the same benchmark and metrics where the graph fits the available qubit count. No properties of an unavailable future processor are assumed in this report.

---

## 5. Limitations

1. **Assumed noise parameters:** The noise values are assumptions rather than confirmed frozen official specifications. Absolute approximation ratios may change under different noise settings.

2. **Team-generated benchmark graphs:** The supplied project materials did not include official graph instances. Results should be described as results on team-generated graphs.

3. **Graph size:** G4 has six vertices and cannot be evaluated on Processor A's five-qubit configuration using the current representation.

4. **Parameter optimization:** COBYLA with twenty restarts does not guarantee a global optimum. Parameter quality depends on the optimization landscape and initial conditions.

5. **Simulator-based evaluation:** The experiments use Qiskit Aer. Simulator wall-clock time is not quantum hardware execution time.

6. **Finite-shot sampling:** The noisy simulations use 4096 shots per experiment, so measured cut values and probabilities have sampling uncertainty.

7. **Compiler settings:** The reported processor experiments use optimization level 1 and ten transpiler seeds. Other settings may produce different results.

8. **Noise attribution:** The experiment does not fully isolate gate errors, readout errors, and routing overhead from one another.

9. **All-to-all reference:** The all-to-all configuration is an idealized reference, not a physical processor specification.

10. **Validation scope:** Passing tests supports the properties covered by those tests. It does not independently prove every numerical claim or scientific interpretation in this report.

---

## 6. Reproducibility and Validation

### 6.1 Environment

The project lock file records Qiskit 2.5.2 and Qiskit Aer 0.17.2. Consult `requirements-lock.txt` for the full dependency versions.

### 6.2 Running the experiment

Install dependencies from the project root:

```bash
python -m pip install -r requirements.txt
```

Launch the notebook:

```bash
python -m notebook main.ipynb
```

Run all cells from top to bottom and wait for execution to finish.

### 6.3 Running tests

Run the test suite with:

```bash
python -m pytest -q tests
```

Retain the actual terminal summary as evidence of which automated tests passed.

### 6.4 Recorded seeds

The original experiment configuration records:

- Parameter optimization seed: 7.
- Simulator seed: 2026.
- Transpiler seeds: 0–9 for processor experiments.

Confirm these settings against the current notebook and source code if the experiment configuration changes.

### 6.5 Output and semantic checks

After running the notebook, confirm that the expected CSV files and figures exist and that the report values agree with the latest generated outputs.

The connectivity check verifies that two-qubit gates use allowed couplings. A separate noiseless semantic check is needed to confirm that the compiled circuit preserves the intended logical behavior. Any changed routing implementation should be revalidated before its results are treated as final.

---

## 7. Conclusion

This project investigates weighted Max-Cut using QAOA and compares the compilation costs of two processor topologies against an all-to-all simulation reference.

The recorded experiments combine exact classical optima, noiseless parameter optimization, processor-aware transpilation, noisy simulation, and circuit-resource and solution-quality metrics.

For the common G1–G3 benchmark set, Processor B has lower mean SWAP counts, CX counts, and circuit depth than Processor A. The control case G3 shows that a match between the problem interaction graph and processor topology can avoid routing SWAPs. G4 also shows that increasing QAOA depth does not necessarily improve the noisy approximation ratio.

These conclusions apply to the team-generated benchmark graphs, assumed noise model, compiler settings, and simulation environment described in this report. The final submission should preserve the distinction between measured results, assumptions, and proposed future work.

---

## 8. Acknowledgements and AI Assistance Disclosure

This project uses Qiskit and Qiskit Aer for quantum circuit construction and simulation, together with Python scientific-computing libraries for analysis and visualization.

AI tools were used to assist with code development, debugging, technical explanations, and project documentation. The team executed the code, reviewed the generated outputs, and tested the implementation. This statement should be retained only to the extent that it accurately describes the team's work and complies with the challenge's disclosure requirements.
