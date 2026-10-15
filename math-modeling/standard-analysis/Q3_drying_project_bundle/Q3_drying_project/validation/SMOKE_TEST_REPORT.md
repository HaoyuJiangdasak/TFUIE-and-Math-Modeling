# Q3 Smoke-Test Report

This report records implementation tests only. The values below are **development checks**, not final paper numbers.

## 1. Long-term boundary reconstruction

From `附件1.xlsx`:

- measured range: 0-14400 s = 4 h;
- sample interval: 60 s;
- 3-4 h temperature mean: 49.9989344262 degC;
- 3-4 h moisture-datum mean: 0.04998754098.

The main Q3 strategy uses measured piecewise-linear data through 4 h and holds these two means constant afterward.

## 2. Event-only development runs

Using a deliberately faster preview configuration:

```text
segment_at_data_knots = False
rtol = 2e-8
atol = 2e-10
max_step_data = 30 s
max_step_long = 300 s
refine_event = False (except where stated)
```

the event estimates were:

| N | tdry / h | Event location |
|---:|---:|---:|
| 320 | 57.6681463 | 0 cm |
| 640 | 57.5164150 | 0 cm |
| 1280 | 57.4852536 | 0 cm |

Approximate event-time differences:

- 320 -> 640: about 546 s;
- 640 -> 1280: about 112 s.

The difference ratio is about 4.87, corresponding to an observed convergence order a little above 2 in this development run. Final paper values must be regenerated with the stricter production configuration.

## 3. Local event refinement

For the N=320 development solve:

- baseline terminal event: about 207605.326532 s;
- refined event: about 207605.326552 s;
- refinement shift: about 2.0e-5 s.

This confirms that the terminal root is not limited by the 60 s result output cadence.

## 4. Full output test

A complete N=320 development solution was generated to the event.

- exact event: 207605.326552 s = 57.6681463 h;
- last regular 60 s output: 207600 s;
- result array: 3461 time rows x 21 radial locations;
- all sampled C values are positive;
- every sampled radius decreases monotonically in time;
- monitored full-state Cmax decreases monotonically;
- monitored maximum location is at the axis for the entire run.

Table-5 tail from the development solve:

| Time | C(0 cm) | C(0.5 cm) | C(1 cm) | C(1.5 cm) | C(2 cm) |
|---|---:|---:|---:|---:|---:|
| 48 h | 0.1620 | 0.1594 | 0.1509 | 0.1338 | 0.0537 |
| 54 h | 0.1541 | 0.1517 | 0.1439 | 0.1281 | 0.0530 |
| Dry end | 0.1500 | 0.1477 | 0.1403 | 0.1251 | 0.0527 |

## 5. Important low-moisture surface finding

The nonlinear Robin algebraic equation can have multiple mathematical roots. This is already visible at the initial state. The Q2 local Picard iteration, initialized from the near-surface interior concentration, naturally follows the largest/high-moisture root.

During Q3, very coarse meshes can make this Picard map lose contraction before the center reaches the drying threshold:

- N=80: long-time BDF cannot reliably reach the event with pure coarse-grid surface Picard;
- N=160: similarly too coarse for a reliable formal event-time convergence point;
- N=320: reaches the event, but the robust continuation-root fallback is occasionally used late in drying;
- N=640 and N=1280 development event runs: no fallback was required; local Picard itself reached the terminal event.

Therefore the recommended formal Q3 grid sequence is:

\[
\boxed{N=320,\ 640,\ 1280}
\]

not 80/160.

The fallback does **not** change the Robin equation. If Picard loses contraction, it solves the same scalar fixed-point equation and explicitly selects the largest root connected to the near-surface interior state. The number of fallback calls is reported in solver statistics.

## 6. What remains before final reporting

Run the strict production configuration in `Q3_analysis.ipynb`:

```text
rtol = 1e-9
atol = 1e-11
max_step_data = 5 s
max_step_long = 60 s
event_max_step = 5 s
segment_at_data_knots = True
```

and complete:

1. 320/640/1280 event-time grid convergence;
2. tighter BDF/event sensitivity;
3. three long-term boundary strategies;
4. physical and balance diagnostics;
5. final N=1280 production solution;
6. official `result3.xlsx` template filling if the template is provided.

