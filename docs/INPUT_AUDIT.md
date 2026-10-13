# Input audit - what the organizer files say, where they conflict, what this repo does

Files checked: `Challenge_Guide_Phase_1.pdf` (Starter Guide), `Problem_Statment_Details.pdf` (Universal Challenge Framework + all PSs),
`Processor_AB_Benchmark_Configuration_FINAL.pdf`, the two screenshots (PS-01 selection page, guide section 3), and the earlier repo zip.

| # | Finding | Evidence | What this repo does |
|---|---|---|---|
| 1 | **PS-01 says 6 vertices, but Processor A has only 5 qubits.** A 6-node QAOA cannot be run on A. | PS-O1 "graph of 6 vertices"; Config PDF sec. 3 `PHYSICAL_QUBITS = 5` | Common benchmark = three 5-node graphs (G1-G3) that fit A and B. A 6-node graph (G4) is included as a **Processor-B-only** extension. Worth asking the organizers which they intend. |
| 2 | **The "2-3 example graphs" are not in any supplied file.** | PS-O1 "Provide 2-3 example graphs (edge-list form)... integer weights 1-5" | Team-generated graphs, integer weights 1-5, fixed seed (`scripts/make_graphs.py`). Same schema, so official graphs can be dropped into `data/raw/graphs.json`. |
| 3 | **Noise parameters are not frozen and conflict.** CX error ~0.5% (exec. summary), p=0.005 (PS-S3), p=0.01 (Starter Guide *illustrative* code). Readout error never specified. | Config PDF sec. 1 and the "IMPORTANT STATUS" box | Used 2Q = 0.5%, 1Q = 0.1%, readout from the Starter Guide example. Marked `ASSUMED` in both processor JSONs; identical for A and B (asserted in notebook + tests). Change in one place if a kit is published. |
| 4 | Processor A described as a **linear chain** in older text, but the official map is a **branching tree** (hub q1). B described differently in older text; simulation uses **9 qubits**. | Config PDF secs. 1-4 | Used the corrected official maps: A edges (0,1),(1,2),(1,3),(3,4); B 12 edges. Tests assert them. The Starter Guide's `toy_5q_line` is only a teaching example and is not used. |
| 5 | Processor B is called "heavy-hex-inspired" but is **denser than real heavy-hex** (q6 has degree 5; triangles 1-2-6 and 2-5-6). | B edge list | Treated as given. Don't claim B is a true heavy-hex lattice in the report. |
| 6 | Rubric awards 30 pts for **Phase 2 readiness / Processor C**, while the Starter Guide says Phase 1 ends at the A/B comparison; one rubric example mentions "C's 2 swaps". Processor C is undisclosed. | Framework doc, Judging Rubric vs Starter Guide sec. 21 | `report.md` has a "Phase 2 readiness" section with bottleneck findings, without inventing Processor C details. |
| 7 | Submission requires report **"in notebook or PDF"**. | Framework doc, Submission | The written findings are in the last notebook cell **and** in `report.md`. |
| 8 | Starter Guide repo layout lists `eq_bell_*` PNGs - they belong to the Bell-state study, not Max-Cut. | Guide sec. 3, screenshot | `assets/qff_phase1_latex_images/` now holds Max-Cut/QAOA equation images + a pipeline diagram. |
| 9 | Deadline: **Oct 13, 11:59 PM**. | Framework doc, Timeline | - |
| 10 | Earlier zip problems: contained a **715 MB `.venv`**, `.ipynb_checkpoints`, two stray empty files (`python`, `where`), and a Windows-only CRLF lockfile with unverified pins. | Uploaded zip listing | Removed; `.gitignore` excludes them; new `requirements-lock.txt` lists tested versions. |
