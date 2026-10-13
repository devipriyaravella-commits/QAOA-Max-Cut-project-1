# QFF 2026 Phase 1 — PS-01 / O1: Max-Cut on Weighted Graphs

**Project Title:** Max-Cut on Weighted Graphs: QAOA Circuit Construction and SWAP Bottleneck Analysis
**Track:** Quantum Optimization
**Framework:** Qiskit
**Language:** Python

**Team Name:** `<YOUR_TEAM_NAME>`
**Team Members:** `<TEAM_MEMBER_NAMES>`
**Repository:** `<YOUR_GITHUB_REPOSITORY_URL>`

---

## 1. Project Overview

This project investigates the application of the Quantum Approximate Optimization Algorithm (QAOA) to the weighted Max-Cut problem. It evaluates how processor connectivity and circuit routing influence quantum circuit depth, two-qubit gate count, SWAP overhead, and solution quality.

The project compares three execution configurations:

- **Processor A:** A five-qubit processor with a tree-like connectivity topology.
- **Processor B:** A nine-qubit processor with a heavy-hex-inspired connectivity topology.
- **All-to-all reference:** A simulation reference without hardware connectivity restrictions, used to study the overhead introduced by routing.

The same optimized QAOA parameters and experimental settings are used across the relevant processor comparisons to help isolate the impact of connectivity.

## 2. Objectives

1. Formulate weighted Max-Cut as a quantum optimization problem.
2. Construct and evaluate QAOA circuits for multiple weighted graphs.
3. Compute exact classical Max-Cut solutions for benchmarking.
4. Compile circuits against different processor coupling maps.
5. Measure routing SWAPs, two-qubit gates, circuit depth, and physical qubit usage.
6. Compare approximation ratios, optimal-cut probabilities, and output-distribution fidelity.
7. Analyze the relationship between processor topology and quantum circuit execution overhead.
8. Validate the implementation using automated tests and noiseless simulation checks.

## 3. Technologies Used

- Python
- Qiskit
- Qiskit Aer
- NumPy
- SciPy
- Pandas
- Matplotlib
- NetworkX
- Jupyter Notebook
- Pytest

## 4. Repository Structure

```text
qff-maxcut-phase1/
├── main.ipynb
├── README.md
├── report.md
├── requirements.txt
├── requirements-lock.txt
├── data/
│   ├── raw/
│   │   └── graphs.json
│   └── processed/
├── processors/
│   ├── processor_A.json
│   └── processor_B.json
├── src/
│   ├── __init__.py
│   ├── problem.py
│   ├── processors.py
│   ├── routing.py
│   ├── metrics.py
│   ├── experiment.py
│   └── visualization.py
├── scripts/
│   ├── make_graphs.py
│   └── make_assets.py
├── tests/
├── results/
│   ├── tables/
│   │   ├── all_runs.csv
│   │   ├── classical_baseline.csv
│   │   ├── final_comparison.csv
│   │   ├── processor_a_metrics.csv
│   │   ├── qaoa_parameters.csv
│   │   ├── quality_significance.csv
│   │   └── summary_by_graph.csv
│   └── figures/
│       ├── AB_performance.png
│       ├── architecture_tradeoffs.png
│       ├── distributions_G1_p1.png
│       ├── logical_circuit_G1_p1.png
│       ├── problem_graphs.png
│       ├── processor_a_graph.png
│       ├── processor_b_graph.png
│       ├── qaoa_landscape_G1_p1.png
│       ├── transpiled_A_G1_p1.png
│       └── transpiled_B_G1_p1.png
├── assets/
└── docs/
    └── INPUT_AUDIT.md
```

*Note: This tree represents the intended organization. Some generated files or directories may differ depending on the scripts and notebook version.*

## 5. Problem Statement

Given a weighted undirected graph (G=(V,E)), the objective is to divide its vertices into two sets so that the total weight of edges crossing between the sets is maximized.

The weighted cut value is

[
C(x)=\sum\_{(i,j)\in E}w\_{ij}[x_i\ne x_j],
]

where (w\_{ij}) is the weight of edge ((i,j)), and (x_i\in{0,1}) identifies the partition assigned to vertex (i).

An edge contributes its weight when its endpoints belong to different partitions.

## 6. Methodology

### 6.1 Graph generation

The project uses benchmark weighted graphs stored in `data/raw/graphs.json`. The graph set includes different structures so that the effect of processor connectivity can be studied.

The README and accompanying report should identify these as team-generated benchmarks unless official benchmark graphs are independently provided.

### 6.2 Classical baseline

The exact Max-Cut optimum is calculated by enumerating possible vertex partitions. These exact solutions provide reference values for evaluating QAOA solution quality.

### 6.3 QAOA construction

QAOA alternates between a cost unitary and a mixing unitary. The project evaluates circuit depths (p=1) and (p=2).

The cost Hamiltonian for weighted Max-Cut can be written as

[
H_C=\sum\_{(i,j)\in E}\frac{w\_{ij}}{2}(I-Z_iZ_j).
]

The mixer Hamiltonian is

[
H_M=\sum\_{i\in V}X_i.
]

The QAOA circuit starts with a uniform superposition and alternates cost and mixer operations according to the selected parameters.

### 6.4 Parameter optimization

The QAOA parameters are optimized using a classical optimization routine. The resulting parameters are saved in `results/tables/qaoa_parameters.csv` and reused for the applicable processor comparisons.

### 6.5 Processor-aware compilation

The circuits are transpiled for Processor A and Processor B using their declared basis gates and connectivity maps. An all-to-all compilation provides a reference for estimating connectivity-related overhead.

Routing SWAPs, two-qubit gate counts, circuit depth, and physical qubit usage are measured to evaluate compilation cost.

### 6.6 Simulation and noise

Qiskit Aer is used to simulate circuit execution. The processor configurations include noise assumptions documented in the processor JSON files.

The noise parameters must be described as assumptions unless independently confirmed by official challenge documentation.

## 7. Evaluation Metrics

| Metric                  | Purpose                                                     |
| ----------------------- | ----------------------------------------------------------- |
| Expected cut value      | Average cut value obtained from sampled solutions           |
| Best observed cut       | Highest cut value observed in the samples                   |
| Approximation ratio     | Solution quality relative to the exact optimum              |
| Optimal-cut probability | Probability of measuring an optimal solution                |
| Distribution fidelity   | Similarity between ideal and evaluated output distributions |
| SWAP count              | Routing overhead introduced during compilation              |
| Two-qubit gate count    | Cost of entangling operations                               |
| Circuit depth           | Number of sequential circuit layers                         |
| Physical qubits used    | Number of physical qubits occupied                          |
| Execution time          | Time spent compiling or simulating circuits                 |

The approximation ratio is

[
r=\frac{\mathbb{E}[C]}{C\_{\mathrm{opt}}},
]

where (C\_{\mathrm{opt}}) is the exact maximum cut value.

## 8. Results and Visualizations

The experiment produces result tables and figures under `results/`.

### Result tables

- `all_runs.csv` — individual experiment records.
- `summary_by_graph.csv` — aggregated metrics by graph, depth, and processor.
- `final_comparison.csv` — processor comparison results.
- `classical_baseline.csv` — classical benchmark results.
- `processor_a_metrics.csv` — Processor A metrics.
- `qaoa_parameters.csv` — optimized QAOA parameters.
- `quality_significance.csv` — statistical comparison outputs.

### Figures

**Processor comparison**

**Architecture trade-offs**

**Benchmark graph structures**

**Processor A topology**

**Processor B topology**

**QAOA parameter landscape**

**Output distribution**

**Logical circuit**

**Transpiled circuit for Processor A**

**Transpiled circuit for Processor B**

*Interpretation of all plots should be based on the latest generated CSV files and figures. Do not use previously reported numerical values unless they match the current experiment output.*

## 9. Installation and Execution

### Prerequisites

Install a compatible Python version and Git. Use a virtual environment to keep project dependencies isolated.

### Install dependencies

On Windows Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

If the activation command does not work in your shell, activate the environment using the appropriate command for your terminal.

### Run the notebook

From the project root:

```bash
python -m pip install notebook
python -m notebook main.ipynb
```

In Jupyter Notebook, select **Kernel → Restart Kernel and Run All Cells**. Wait until all cells finish executing.

### Run the automated tests

```bash
python -m pytest -q tests
```

A successful test summary indicates that the tests executed by this command passed.

### Review generated outputs

```bash
ls results/tables
ls results/figures
```

## 10. Correctness and Validation

The project includes automated tests and simulation-based checks. Before submission, verify that:

1. The graph files load successfully.
2. Exact classical optima agree with independently checked benchmark values.
3. The QAOA objective and circuit conventions are consistent.
4. Compiled two-qubit gates respect the target processor coupling maps.
5. Routing SWAP counts are recorded before SWAP decomposition.
6. Noiseless compiled circuits reproduce the ideal result within the project's specified tolerance.
7. CSV tables and plots are generated from the latest notebook execution.
8. The automated test suite completes successfully.

A passing test suite is evidence for the checks it contains; it does not independently prove every scientific conclusion.

## 11. Limitations

- Processor noise values are assumptions unless confirmed by the organizers.
- Team-generated benchmark graphs may not represent official challenge input graphs.
- Simulator results do not guarantee equivalent performance on real quantum hardware.
- Finite-shot sampling introduces statistical uncertainty.
- Compilation results may vary with transpiler seeds and optimization settings.
- Comparisons should account for graph size and whether each graph fits the processor's available qubits.
- Numerical conclusions must be derived from the current result files.

## 12. Conclusion

This project develops a reproducible workflow for investigating QAOA on weighted Max-Cut problems and comparing the compilation overhead of different processor topologies.

By combining exact classical baselines, parameter optimization, connectivity-aware compilation, simulation, and statistical metrics, the workflow supports a systematic study of how connectivity affects circuit resources and solution quality.

The final conclusions should be supported by the latest experiment tables, figures, correctness checks, and automated test results.

## 13. Acknowledgements and AI Assistance Disclosure

This project uses Qiskit and Qiskit Aer for quantum circuit construction and simulation, together with Python scientific-computing libraries for analysis and visualization.




