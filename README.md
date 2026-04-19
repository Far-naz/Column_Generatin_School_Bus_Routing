# School Bus Routing (SBR)

This project models and solves a school bus routing problem with minimizing the total walking distance of students from their home to the pickup stops.

## What This Repo Includes

- Main MIP model (exact): solve the routing model directly.
- Column generation / branch-and-price components.
- Data serializers for schools, students, and bus stops.
- Map visualization interface using Folium.

## Project Structure

- `src/module/`: core data models (`InputModel`, `Route`, stops, branches, result types).
- `src/branch_and_price/`: restricted master problem, pricing, branch-and-bound flow.
- `src/math_modelling/`: main exact MIP model.
- `src/serializer/`: readers for schools/students/stops.
- `src/helper/`: logger setup and helper utilities.
- `src/map_interface.py`: interactive map output (HTML via Folium).
- `src/test_models.py`: script entry for solving a configured instance.
- `data/`: input CSV files.

## Requirements

Recommended Python: 3.10+

Install requirments:

```bash
pip install m- requirements.txt
```

Note: `gurobipy` requires a valid Gurobi installation and license.

## Run

From project root:

```bash
python src/test_models.py
```

This builds an `InputModel`, runs the configured solver path, and prints route statistics.

## Generate Map

From project root:

```bash
python src/map_interface.py
```

This creates an HTML map file and opens it in a browser (if enabled in script settings).

## Logging

Logger files are written under:

- `src/logs/`

Current logger behavior: each run creates a new timestamped log file.

## Column Generation Fallback Logic

In column generation, heuristic pricing is attempted first.
If heuristic pricing cannot produce a route, exact pricing is attempted as fallback:

- If exact pricing succeeds, the process continues.
- If exact pricing also fails, the run is flagged/stopped by result mode.

## Common Troubleshooting

### `ModuleNotFoundError: No module named 'src'`

Use the project-root run style shown above (`python src/...`) or run module-style commands consistently from root.

### Duplicate-looking logs

If multiple runs are executed, check separate timestamped files in `src/logs/`.

## Notes

- Some scripts are run-oriented rather than packaged as CLI commands.
- Prefer using the root-level execution commands in this README to avoid import path issues.
