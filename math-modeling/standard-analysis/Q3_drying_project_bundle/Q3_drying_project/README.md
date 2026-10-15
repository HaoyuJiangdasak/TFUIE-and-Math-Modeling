# Q3 Drying Project

This project upgrades the already validated Q2 numerical core to Question 3.

## Numerical route

\[
\boxed{
\text{Q2 cylindrical cell-centered FVM}
+
\text{joint BDF}
+
\text{local coupled surface Picard}
+
\text{long-term boundary extension}
+
\text{full-domain terminal event}
}
\]

The Q2 core is copied as `src/q2_solver.py` and is not rewritten inside Q3.
`src/q3_solver.py` adds only the long-time environment, event detection,
Question-3 diagnostics, Table 5 generation, and `result3.xlsx` writing.

## Main boundary strategy

- 0-4 h: measured Attachment 1, piecewise-linear interpolation.
- after 4 h: constant mean of the measured 3-4 h plateau.

Alternative sensitivity strategies:

- last measured value held constant;
- 2.5-4 h mean held constant.

## Drying event

The formal discrete event is

\[
g(t)=C_{\max}(t)-0.15.
\]

`Cmax` is evaluated from:

- reconstructed axis value \(C(0,t)\);
- every cell-centered FVM state;
- reconstructed Robin surface value.

It is **not** based only on the coarser 0.1 cm output grid.

## Environment

```bash
conda env create -f environment.yml
conda activate q3_drying
python -m ipykernel install --user --name q3_drying --display-name "Python (q3_drying)"
```

or:

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate       # Windows
python -m pip install -U pip
python -m pip install -r requirements.txt
```

## Command-line run

From the project root:

```bash
python src/q3_solver.py \
  --env data/附件1.xlsx \
  --output outputs/result3.xlsx \
  --N 1280 \
  --boundary-strategy last_hour_mean
```

The exact drying end time is printed by the solver. `result3.xlsx` itself
keeps the required regular 60 s time grid and stops at the last 60 s sample
not exceeding the drying event.

## Recommended workflow

Open `notebooks/Q3_analysis.ipynb` and run the sections in order:

1. inspect the 0-4 h measurements and long-term extension;
2. run a moderate-grid baseline;
3. inspect \(C_{\max}(t)\) and the controlling location;
4. verify the local event crossing;
5. run `tdry` grid convergence;
6. run time/event tolerance sensitivity;
7. run long-term boundary sensitivity;
8. optionally compare with backward-Euler + block Picard;
9. run the final N=1280 production solve;
10. write `result3.xlsx`.



## Long-time surface nonlinear note

Q3 reaches much lower moisture than Q2. On very coarse grids the local Robin
Picard fixed-point map can lose contraction. The Q3 wrapper therefore keeps
Picard as the primary local method and, only when necessary, solves the same
scalar fixed-point equation with a bracketed continuation-root fallback that
selects the largest root connected to the near-surface interior state.

The solver reports `surface_brent_fallback_calls`. Development tests found no
fallback calls for N=640 and N=1280 event searches, while N=320 can require a
small number of late-stage fallbacks. This is one reason the formal Q3 grid
study starts at N=320 rather than at very coarse meshes.
