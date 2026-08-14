# Publication gate

The publication gate is a fail-closed check for the cleaned repository
surface. Run it from the repository root after regenerating the evidence:

```bash
python3 repro/src/verify_results.py
python3 repro/src/publication_gate.py --skip-producers
```

The gate checks:

- the final repository slug, paper title, author list, and source identifiers;
- the six claim statuses and their committed evidence directories;
- C1/C5 positive results and their independent negative controls;
- blocked status and missing-input records for C2/C3/C4/C6;
- the citation, author thank-you note, branch map, source audit, and research log;
- absence of tracked `.trackio` and stale root `logbook.json` state; and
- the local branch/remote naming surface and exact reachable commit identity.

`--skip-producers` verifies committed evidence without downloading the paper
or contacting external inventories. Without the flag, the gate first runs the
fixed cumulative producer command and then verifies its outputs. The gate does
not assert that a blocked benchmark has been reproduced.
