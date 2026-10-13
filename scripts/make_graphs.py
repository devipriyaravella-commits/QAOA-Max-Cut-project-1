"""Generate the benchmark graphs (integer weights 1-5, fixed seed). Writes data/raw/graphs.json.
The organizer files promise '2-3 example graphs' but do not contain them, so these are team-generated.
If official graphs arrive, drop them into data/raw/graphs.json using the same schema."""
import json
import numpy as np

rng = np.random.default_rng(2026)
specs = [
    ("G1", "dense_5node", 5, [(0,1),(0,2),(0,3),(1,2),(1,3),(1,4),(2,4),(3,4)], True,
     "Dense: 8 edges on 5 nodes. Forces routing on both processors."),
    ("G2", "ring_chord_5node", 5, [(0,1),(1,2),(2,3),(3,4),(4,0),(0,2)], True,
     "Ring plus one chord."),
    ("G3", "A_native_tree_5node", 5, [(0,1),(1,2),(1,3),(3,4)], True,
     "Interaction graph identical to Processor A's coupling map: best case for A."),
    ("G4", "custom_6node", 6, [(0,1),(0,3),(1,2),(1,4),(2,5),(3,4),(4,5),(0,5),(2,3)], False,
     "6 vertices as in the PS text. Needs 6 qubits, so it can only run on Processor B (A has 5)."),
]
graphs = []
for gid, name, n, edges, common, note in specs:
    graphs.append({"id": gid, "name": name, "num_nodes": n, "common_benchmark": common, "note": note,
                   "edges": [[i, j, int(rng.integers(1, 6))] for i, j in edges]})
json.dump({"_meta": "Team-generated instances, integer weights in [1,5], seed 2026.", "graphs": graphs},
          open("data/raw/graphs.json", "w"), indent=2)
print(json.dumps(graphs, indent=1)[:600])
