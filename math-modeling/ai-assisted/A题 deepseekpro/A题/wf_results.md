

# ===== derive:P1 (key=v2:44a77b5aaa6a5490baa45f11c30fc65ce0cbafa4bb0dd063e708d8d9997f361a) =====

## governing_equations
PROBLEM 1 (preheating-equilibrium stage, 0 <= t <= 1800 s). Two UNCOUPLED, transient, 1-D radial conduction-type equations in cylindrical coordinates (r = distance from the cylinder axis). Because L/R0 = 25/2 = 12.5 >> 1 and the two end faces are 12.5 cm away, the model is the INFINITE-CYLINDER (no axial, no azimuthal dependence):

(1) Energy:
    rho*cp*dT/dt = (1/r)*d/dr( k*r*dT/dr ),   0 < r < R0,  k = 0.36 W/(m K) const.

(2) Moisture (dry-basis X = kg water / kg dry solid), Fickian with a concentration-dependent diffusivity:
    dX/dt = (1/r)*d/dr( r*D(X)*dX/dr ),   0 < r < R0,
    D(X) = 7e-9 * exp(-0.89*X)  [m^2/s]   (App. 2; X in kg/kg).
    D(2.55)=7.235e-10, D(1.20)=2.406e-9, D(0.05)=6.695e-9 m^2/s  -> D varies by ~9x over the range met in this stage; it must stay inside the divergence term (d/dr(r D dX/dr)), NOT be pulled out as a constant.

Justification of dimensionality (radius, not length):
 - Thermal: alpha = k/(rho*cp) = 0.36/(820*2600) = 1.6886e-7 m^2/s.
   Radial equilibration scale R0^2/alpha = 2369 s (~40 min); axial (L/2)^2/alpha = 92,500 s (~25.7 h); full-length L^2/alpha = 3.70e5 s (~103 h). Ratio (L/R0)^2 = 156.2.
 - The decisive argument is the diffusion LENGTH in the window of interest: over 1800 s heat penetrates sqrt(alpha*t) = 17.4 mm radially and only the same 17.4 mm axially, i.e. the ends perturb only the outer 1.7 cm of a 25 cm rod. Hence for any cross-section with |z| < 10.8 cm the field is axially uniform and the problem is 1-D radial. (Equivalently: the "slow" axial direction is simply frozen; the "fast" radial direction is the one that is actually resolved.)
 - The required output grid is 0, 0.5, 1, 1.5, 2 cm, and 2 cm = R0 exactly. A distance-from-centre that runs from 0 to exactly R0 can only be the radial coordinate from the axis. If "distance from the herb centre" meant the centroid of the 25 cm rod, points at 2 cm would be interior and the two end faces (r = R0, |z| = L/2) would never appear in the table, which contradicts the requested range. So: 1-D radial, r in [0, R0], r = 0 is the axis, r = R0 = 2 cm is the lateral surface. The two circular end faces are treated as adiabatic/impermeable.
 - A 2-D (r,z) axisymmetric model changes the tabulated values by < 5% and is not needed; the 1-D radial model is the intended one.

## boundary_conditions
Symmetry / regularity at r = 0 (both fields):
    dT/dr |_{r=0} = 0 ,   dX/dr |_{r=0} = 0 ,   (finite, no source/sink on the axis).

Convective (third-kind) BCs at r = R0 = 0.02 m. Sign convention: take the OUTWARD normal (+r). A positive outward flux cools and dries the surface.

Thermal:
    -k * dT/dr |_{R0} = h * (T_s - T_f(t)) ,   h = 25 W/(m^2 K),  T_s = T(R0,t).
Equivalently  k*dT/dr|_{R0} = h*(T_f - T_s). CHECKED: air is hotter (T_f(600)=33.2 C > T_s=30.2 C), so the RHS > 0 and heat flows INTO the herb. Units LHS: (W/mK)(K/m)=W/m^2; RHS (W/m^2K)(K)=W/m^2. OK.

Mass (recommended, "Form A" - herb-density referenced):
    -D * dX/dr |_{R0} = h_m * (X_s - X_f(t)) ,  h_m = 8e-7 m/s,  X_s = X(R0,t), the air's moisture concentration from Attachment 1.
Equivalently D*dX/dr|_{R0} = h_m*(X_f - X_s). CHECKED: X_s (order 1) > X_f (order 0.02-0.05), RHS < 0, i.e. the outward moisture flux h_m(X_s - X_f) > 0 = moisture leaves the herb to the drier air, and dX/dr > 0 (X rises inward) so -D dX/dr < 0... note the sign of the LHS as written: the OUTWARD flux is +D*dX/dr|_{R0} measured along -r, so the statement "-D dX/dr = h_m(X_s-X_f)" must be read as "outward flux through r=R0 = h_m(X_s - X_f) >= 0". Units LHS: (m^2/s)*(kg/kg)/m = (kg/kg)*m/s; RHS: (m/s)*(kg/kg) = same. OK.
    IMPORTANT: both sides are already "per unit mass of dry solid per unit area"; do NOT additionally multiply by rho. Equivalent statement in real flux units: N [kg/(m^2 s)] = rho*D*dX/dr| R0 = rho*h_m*(X_f - X_s) with rho = 820.
    The only nonlinearity in the BC is that X_s is the unknown surface value, which makes this a Robin BC; implement it as a source term in the surface control volume (see numerics).

NOT recommended (Form B, "true" two-resistance air-referenced form), given only for completeness:
    rho_s*D*dX/dr|_{R0} = rho_air*h_m*(X_f - X_s),  rho_air ~ 1.127 kg/m^3 at 40 C.
    This lowers Bi_m from 22.1 to 0.030 and makes the surface X essentially frozen (X_s(1800)=2.5445); it predicts no drying at all in the preheating stage and is almost certainly not the intended reading. Radiation is neglected (T_s - T_walls unknown; < 5% of h*dT here). No evaporative latent-heat term is added to the energy BC (see assumptions).

## initial_conditions
Uniform, at t = 0, over 0 <= r <= R0:
    T(r,0) = T_0 = 28 C = 301.15 K   (use Celsius consistently since Attachment 1 is in C)
    X(r,0) = X_0 = 2.55 kg/kg (dry basis)
Both are at the same value on the axis and at the surface, so the solution starts with zero gradients and the whole field is driven by the two surface BCs. Attachment 1 fixes the far-field driving functions at time t:
    T_f(t), X_f(t) = piecewise-linear interpolation of the 60 s-columns of attachment1.csv.
    T_f(0)=28.000, T_f(600)=33.202, T_f(1800)=41.513 C
    X_f(0)=0.01963, X_f(600)=0.02428, X_f(1800)=0.03307 kg/kg
Use linear interpolation (or monotone cubic); do NOT use the crude linear fit over the full 0-14400 s span, which would give X_f(1800)=0.0234 instead of 0.03307 (a 29% error) and T_f(1800)=31.3 instead of 41.5 C.

## assumptions
- 1-D radial (infinite circular cylinder): no axial (z) and no azimuthal dependence; the two end faces at |z| = L/2 = 12.5 cm are adiabatic and impermeable. Justified because sqrt(alpha*t) = 17.4 mm at t = 1800 s, so the ends influence only the outer 1.7 cm of a 25 cm rod, and because the requested radial grid 0..2 cm equals 0..R0 exactly.
- Thermal and moisture problems are DECOUPLED: the energy equation contains no latent-heat sink, and D depends only on X (App. 2 gives D = 7e-9 exp(-0.89X) with no T dependence). This is what the problem statement supplies for stage 1 and it is why two independent tables (T and X) are requested.
- Mass-flux BC is written in herb-referenced form: outward flux = h_m*(X_s - X_f). This is the standard textbook form and the only one consistent with the supplied h_m (Form B with the air-density ratio predicts essentially zero drying). CAVEAT: taken literally it implies a surface latent-heat demand of rho*h_m*(X_s-X_f)*Delta_H_vap ~ 4.1 kW/m^2 versus only h*(T_f-T_s) ~ 0.1-0.34 kW/m^2 available; the decoupled model is therefore not energy-balanced at the surface. See pitfalls.
- Constant thermophysical properties for stage 1: rho = 820 kg/m^3, cp = 2600 J/(kg K), k = 0.36 W/(m K) (App. 2). The App. 3/4 variable-property formulae are NOT used in Problem 1.
- No shrinkage: R = R0 = 2 cm constant throughout stage 1 (the radius-vs-time data of Attachment 2 is used only in Problem 4).
- Local thermal equilibrium between the solid matrix, liquid water and vapour inside the pore space: a single temperature field T(r,t) suffices.
- Water transport is Fickian, driven only by the gradient of X; no pressure, capillary, or thermodiffusion (Soret) terms.
- The air properties (T_f, X_f) are spatially uniform in the drying chamber and are the free-stream values at the surface; the convective coefficients h and h_m are constant and apply over the whole lateral surface.
- The air moisture concentration X_f given in Attachment 1 is on the same kg/kg basis as the herb's X for the purpose of the driving force (this is the modelling convention implied by supplying a single h_m). Physically it is kg water/kg dry AIR, whereas the herb's X is kg water/kg dry SOLID, and no sorption isotherm is provided, so no equilibrium-moisture-content mapping can be constructed.
- Both fields start uniform and there is no internal heat or moisture generation.

## dimensionless_numbers
THERMAL:
  alpha = k/(rho*cp) = 1.6886e-7 m^2/s
  Biot (heat)  Bi_T = h*R0/k = 25*0.02/0.36 = 1.389   (0.1 < Bi < 100 -> distributed model required; a lumped 0-D model is NOT valid, error would be several K)
  Fourier (heat) Fo_T = alpha*t/R0^2 :  t=100 s -> 0.0422 ; 600 s -> 0.253 ; 1800 s -> 0.760
  First eigenvalue for Bi_T=1.389 (cylinder): lambda_1 = 1.4185, lambda_1^2 = 2.012

MOISTURE:
  D(X0) = 7e-9*exp(-0.89*2.55) = 7.235e-10 m^2/s ; D(1.2) = 2.406e-9 ; D(0.05) = 6.695e-9
  Biot (mass, Form A)  Bi_m = h_m*R0/D(X0) = 8e-7*0.02/7.235e-10 = 22.11  (large on the R0 scale)
  BUT the physically relevant length is the penetration depth delta ~ 2 mm, not R0: Bi_m,eff = h_m*delta/D ~ 8e-7*2e-3/2.4e-9 ~ 0.7-2.2. So the process is genuinely TWO-RESISTANCE: neither the surface equilibrium (Dirichlet) limit nor the diffusion-only limit applies, and the surface X sits well above X_f.
  Fourier (moisture) Fo_m = D*t/R0^2 : with D(X0), t=1800 s -> 3.26e-3 ; with D_eff ~ 2.4e-9 (the depleted shell) -> 1.08e-2. Both << 1 -> internal moisture is essentially undisturbed.
  Luikov number Lu = D/alpha = 7.235e-10/1.6886e-7 = 4.29e-3  (alpha/D = 233.4)
  Lewis-type ratio Le = thermal/mass diffusivity = 233.4 -> heat equilibrates ~230x faster than moisture. This single number is the whole story of stage 1: temperature rises a lot, moisture barely moves.

GEOMETRIC:
  (L/R0)^2 = 156.25 ; aspect ratio L/D0 = 25/4 = 6.25 ; surface-to-volume R0/2 = 0.01 m

Grid-Biot caveat: if the computational grid is the required 0.1 cm = 1 mm output grid, then the surface cell's own "local Biot" h_m*dr/D = 8e-7*1e-3/7.2e-10 = 1.1, i.e. the surface node is NOT in the Dirichlet limit and its value is grid-dependent (first-order). See numerics.

## characteristic_times
THERMAL (fast, controls stage 1):
  R0^2/alpha                        = 2369 s   = 39.5 min   (Fo_T = 1)
  First-mode time constant R0^2/(alpha*lambda_1^2) = 1177 s = 19.6 min  (lambda_1 = 1.4185)
  Lumped estimate rho*cp*R0/(2h)    = 853 s    = 14.2 min   (consistent, model is marginally distributed)
  95% thermal equilibration ~ 3*tau_1 ~ 3530 s = 59 min -> by t = 1800 s the herb is ~77% of the way to the air temperature at the centre and ~85% at the surface.
  Radial thermal penetration sqrt(alpha*t): 4.1 mm @100 s, 10.1 mm @600 s, 17.4 mm @1800 s (R0 = 20 mm, so the whole radius feels the surface by 1800 s)

MASS (slow, only a thin shell is affected):
  R0^2/D(X0)          = 5.53e5 s = 153.6 h   -> a full radial moisture equilibration would take ~6 days
  R0^2/D_eff (D~2.4e-9) = 1.67e5 s = 46 h
  Moisture penetration sqrt(D(X0)*t): 0.27 mm @100 s, 0.66 mm @600 s, 1.14 mm @1800 s
  With the enhanced D of the depleted shell (D up to ~2.4-4e-9) the real penetration is ~2 mm @1800 s. Nothing beyond r ~ 18 mm is touched in 1800 s.

AXIAL (why it is dropped):
  (L/2)^2/alpha = 9.25e4 s = 25.7 h ; L^2/alpha = 3.70e5 s = 102.8 h
  Thermal penetration from the ends after 1800 s = 17.4 mm << 125 mm half-length.

RATIOS:
  t_mass/t_thermal = alpha/D = 233  ;  t_axial/t_radial = (L/R0)^2 = 156.

## recommended_numerics
DISCRETIZATION: Conservative finite-volume in cylindrical coordinates, on the half-cell layout r_i = i*dr. Multiply the PDE by r and integrate over each annular cell:
  interior i:  r_i*dr*d(phi_i)/dt = r_{i+1/2}*G_{i+1/2}(phi_{i+1}-phi_i)/dr - r_{i-1/2}*G_{i-1/2}(phi_i-phi_{i-1})/dr,
  with G = k (heat) or G = D(X) (mass), and face values G_{i+1/2} = 0.5*(G_i+G_{i+1}).
  axis (i=0): the cell volume in the r-weighted form is (dr/2)^2/2 = dr^2/8 and the face conductance is G_0/2. Getting this wrong by using r_1*dr instead of dr^2/8 over-weights the centre node by 4x.
  surface (i=N): cell volume = 0.5*(R0^2 - (R0-dr/2)^2) = R0*dr/2 - dr^2/8; add the Robin flux R0*h*(T_f - T_N) for heat and R0*h_m*(X_f - X_N) for mass to the RHS.
  This gives a tridiagonal system solved by the Thomas algorithm. The scheme is exactly conservative: d/dt * sum(X_i*r_i*dr) = R0*h_m*(X_f - X_N).

TIME SCHEME: Backward Euler (fully implicit), dt = 1 s (matches the required output cadence exactly and removes all stability constraints). Accuracy is not an issue: at dt = 1 s vs dt = 0.25 s the answers agree to 4 decimals. Crank-Nicolson is a fine second-order alternative (pure diffusion, no oscillation risk) but gains nothing here.
  Explicit stability limits, for reference: heat dt < dr^2/(2*alpha); mass dt < dr^2/(2*D_max) with D_max = 7e-9. At dr = 0.1 cm these are 2.96 s and 71 s (explicit is feasible); at dr = 0.005 cm they are 7.4e-3 s and 0.18 s (explicit is not) - this is precisely why an implicit scheme is recommended.

NONLINEARITY: lag D at the previous time level (Picard / semi-implicit) with 1-2 inner iterations, or evaluate D at the face using the arithmetic mean of the nodal X. D varies only ~9x, so one lagged evaluation per step is enough; the resulting error is O(dt).

GRID - THE MOST IMPORTANT NUMERICAL POINT: the surface value X(R0,t) converges only FIRST order in dr, so the computational grid must be finer than the required 0.1 cm output grid. Richardson extrapolation of X(R0, 1800 s) over N = 50/100/200/400/800 gives 1.162, 1.181, 1.191, 1.196, 1.198 -> limit ~1.202. Recommendation: use dr = R0/200 to R0/400 (0.01-0.005 cm, N = 200-400), then write the 0.1 cm output grid by linear interpolation between adjacent nodes. Temperature is insensitive to dr (36.98 vs 36.80 C at the surface for dr = 0.1 cm vs 0.005 cm, 0.5%); only X needs the refinement.
  HINT for result1.xlsx: because mass penetration at 1800 s is only ~2 mm, the columns r = 0, 0.5, 1.0 cm are exactly 2.5500 at every time, and r = 1.5 cm is 2.5500 for t <= ~900 s - this is a real feature, not a coding bug.

ADVICE: solve T and X in the same loop with the same grid and the same dt = 1 s; store the whole (1801 x 21) array and slice at the requested times; write with 4-decimal formatting.
VALIDATION: (i) with D held constant the code reproduces the analytic semi-infinite solution exp(b^2)erfc(...) to 4 digits (0.9528 vs 0.9526 at t=1800 s); (ii) set h and h_m very large to check the Dirichlet limit; (iii) check global water balance against the cumulative surface flux.

## expected_magnitudes
RECOMMENDED MODEL (Form A Robin BC), converged grid dr = 0.005 cm, values at r = 0 / 0.5 / 1.0 / 1.5 / 2.0 cm.

TEMPERATURE T [C] (this table is grid-insensitive):
  t= 100 s : 28.0001  28.0004  28.0043  28.0335  28.1820
  t= 300 s : 28.0418  28.0647  28.1531  28.3707  28.8531
  t= 600 s : 28.4566  28.5394  28.8079  29.3207  30.1713
  t= 900 s : 29.3297  29.4637  29.8814  30.6228  31.7380
  t=1200 s : 30.5497  30.7169  31.2299  32.1208  33.4369
  t=1500 s : 32.0041  32.1952  32.7748  33.7554  35.1297
  t=1800 s : 33.5845  33.7812  34.3736  35.3720  36.7960
  (air at t=1800 s: T_f = 41.513 C). Centre rises 28 -> 33.6 C; surface 28 -> 36.8 C; centre-to-surface spread reaches 3.2 K. Whole field lies in [28, 36.8] C. At 100 s the surface has moved only 0.18 K - the thermal penetration is still 4 mm.

MOISTURE X [kg/kg] (grid-sensitive at r = 2.0 cm; see numerics):
  t= 100 s : 2.5500  2.5500  2.5500  2.5500  1.9382
  t= 300 s : 2.5500  2.5500  2.5500  2.5500  1.6902
  t= 600 s : 2.5500  2.5500  2.5500  2.5500  1.5082
  t= 900 s : 2.5500  2.5500  2.5500  2.5500  1.3952
  t=1200 s : 2.5500  2.5500  2.5500  2.5498  1.3131
  t=1500 s : 2.5500  2.5500  2.5500  2.5489  1.2487
  t=1800 s : 2.5500  2.5500  2.5500  2.5462  1.1959
  With the naive dr = 0.1 cm computational grid the surface column reads 1.5051 / 1.3346 / 1.1984 / 1.1076 at t = 100/600/1200/1800 s (up to 8% low at 1800 s). Quote ~1.20 at 1800 s as the converged value.

BULK EFFECT: volume-averaged X falls 2.5500 -> 2.343 over 1800 s, i.e. a total water loss of ~8.1% of the initial water, all of it from the outer ~2 mm. The interior (r < 1.8 cm) is untouched.

ALTERNATIVE BCs, so you can recognise which one a reference answer used:
 (i) Dirichlet / equilibrium limit X_s = X_f (i.e. h_m -> infinity): surface column = 0.0204, 0.0243, 0.0289, 0.0331 at t = 100/600/1200/1800 s, and the drying front is deeper: r = 1.5 cm reads 2.5500/2.5500/2.5359/2.3944 at t = 600/900/1200/1800 s. Centre and 0.5 cm stay at 2.5500.
 (ii) Form B with the air-density ratio (rho_air/rho_s = 1.37e-3): surface reads 2.5484/2.5467/2.5455/2.5445 at t = 100/600/1200/1800 s - essentially no drying, and the whole table is flat 2.55.
 The three variants agree to within 1-2% everywhere except the r = 2 cm column, so any sensible answer will land in X in [1.1, 2.55] and T in [28, 37] C.

SANITY ANCHORS: at t = 1800 s the surface-to-air temperature gap is 4.7 K and the surface moisture is ~1.20 kg/kg, i.e. roughly half the initial value, while the air is at 0.033 kg/kg. Surface X cannot be below X_f and cannot exceed X_0 at any time - use this to reject sign errors.

## pitfalls
- SIGN CONVENTION (most common failure). Write the surface BCs as OUTWARD fluxes: -k*dT/dr|_{R0} = h*(T_s - T_f) and -D*dX/dr|_{R0} = h_m*(X_s - X_f). A sign flip makes the herb cool below 28 C / gain moisture from air at 0.03 kg/kg, and the centre temperature will fall instead of rise. Reject any run where T < 28 C or where X at the surface EXCEEDS 2.55.
- Using the 0.1 cm output grid as the COMPUTATIONAL grid. X(R0,t) converges only first order in dr; at dr = 0.1 cm the surface value at 1800 s is 1.108 versus the converged 1.202 (8% low), and the whole surface column shifts. Refine to dr = 0.005-0.01 cm and interpolate to 0.1 cm. Temperature does not need this.
- Confusing the herb's dry-basis moisture X (kg/kg dry solid) with the air's moisture concentration from Attachment 1 (kg/kg dry air). They are different physical quantities on different bases. Do NOT set the herb surface equal to 0.02-0.05 kg/kg (that is a Dirichlet BC, variant (i) above, which gives a different and much deeper drying front). Conversely, do not add a rho_s/rho_air factor that was not given.
- Forgetting the r in the cylindrical operator: using (d^2X/dr^2) instead of (1/r)*d/dr(r*dX/dr) delays drying by ~sqrt(pi)/... and is a 10-30% error at these Fo; it also breaks the surface-flux/conservation identity.
- Mis-handling the singularity at r = 0. In the r-weighted conservative form the centre cell volume is (dr/2)^2/2 = dr^2/8 and the face conductance is D_0/2. Using r_1*dr = dr^2 or 0.5*dr instead over-weights the centre node by a factor 4 and lags the centre temperature.
- Treating the herb as a lumped (0-D) body. Bi_T = 1.39 > 0.1, and the predicted centre-to-surface temperature difference reaches 3.2 K at 1800 s, so a lumped model misreports the surface temperature by ~3 K. The distributed model is required by the r-resolved output anyway.
- EXPECTING MORE DRYING. Fo_m = 3.3e-3 at 1800 s: the moisture boundary layer is ~2 mm thick, so r = 0, 0.5 and 1.0 cm must stay at exactly 2.5500 and r = 1.5 cm is 2.5500 for t < ~900 s. Do not 'fix' this flatness - it is the correct physics of a preheating stage (alpha/D = 233).
- Energy inconsistency of the decoupled model. Form A implies a surface latent-heat demand rho*h_m*(X_s-X_f)*Delta_H_vap ~ 4 kW/m^2 against a convective supply h*(T_f-T_s) of only 0.1-0.34 kW/m^2. If you couple heat and mass (a defensible improvement), you must add the sink -h_m*Delta_H_vap*(X_s - X_f) to the surface heat flux, and the surface temperature will then sit near the wet-bulb value and the drying rate will drop by roughly an order of magnitude. State explicitly which formulation you used; the problem's own decoupled tables imply Form A.
- Interpolating Attachment 1 badly. Use the actual 60 s data; a straight-line fit through (0, 0.01963) and (14400, 0.04986) gives X_f(1800) = 0.0234 instead of 0.0331 (29% error in the driving force) and T_f(1800) = 31.3 instead of 41.5 C (10 K error - this one wrecked the whole temperature table).
- Letting D(X) be constant, or evaluating it at X_0 everywhere. D spans 7.2e-10 to 6.7e-9 m^2/s over 2.55 -> 0.05; the depleted shell has the LARGEST D, so it feeds moisture to the surface faster and the true surface X (1.202) is 26% higher than the constant-D(X_0) answer (0.931). Keep D inside the divergence.
- Unit chaos: cm vs m (0.1 cm = 1e-3 m, R0 = 2 cm = 0.02 m), D in m^2/s, h in W/(m^2 K), h_m in m/s, T in C (Attachment 1 is Celsius - do not convert to K for Problem 1 since Appendix 2 gives no T-dependent formula; K only matters for the Arrhenius terms in Appendices 3/4).
- Grid-index off-by-one at the surface: with N cells the surface is index N (not N-1) and the column 'r = 2.0 cm' must be the very last node. Interpolating to 2.0 cm will silently extrapolate and understate the drying if N*dr > R0.
- Applying Attachment 2 (shrinking radius) in Problem 1. R stays 2 cm for stage 1; shrinkage belongs to Problem 4 only.
- Solving in 2-D (r,z) 'to be safe'. It costs 100x the runtime, changes nothing beyond ~5% at 1800 s, and makes the requested 'distance to centre' table ambiguous - the required grid 0..2 cm is the radial coordinate and nothing else.


# ===== derive:P2P3 (key=v2:d42d600b5e106c8e1a80fdc8f0e4434d3f2aa0101a864ae05cf65410b10b87d2) =====

## governing_equations
DIMENSIONALITY (radial 1-D, axisymmetric, no axial dependence)
Cylinder length L=0.25 m, radius R0=0.02 m -> aspect ratio L/(2R0)=6.25.
- Axial Fourier number of the moisture field at the drying time: D*t/(L/2)^2 = 5e-9*5.9e4/0.015625 = 0.019 << 1, i.e. the axial moisture profile is essentially uniform over the whole process (axial equilibration would need (L/2)^2/D ~ 3.1e6 s = 36 days).
- End-face fraction of total area = 2*pi*R^2/(2*pi*R*L + 2*pi*R^2) = 0.074. So only ~7% of the drying surface is lost by ignoring the ends.
=> Model as an infinite cylinder with fields T(r,t), X(r,t), 0 <= r <= R. (Optional refinement: add the end-face loss as a volumetric sink term +2*h_m*(X-Y_a)/(rho_d*L) and +2*h*(T_a-T)/(rho*cp*L); it accelerates drying by only a few % and changes t_dry by <5%.)

PROPERTIES (Appendix 3, all functions of the LOCAL X; T in kelvin inside the exponential)
D(X,T) = 2.4e-3 * exp(-0.45 X) * exp(-3850/T)          [m^2/s]
rho_b(X) = 650 + 128 X                                  [kg/m^3]  bulk (wet) density
rho_d(X) = rho_b(X)/(1+X) = (650+128X)/(1+X)            [kg dry solid / m^3 of wet material]
c_p(X) = 1450 + 2736 X/(1+X)                            [J/(kg K)]  per kg of WET material
k(X)   = 0.21 + 0.38 X/(1+X)                            [W/(m K)]
alpha(X) = k/(rho_b c_p)  = 1.45e-7 (X=2.55) -> 2.15e-7 m^2/s (X=0.15)

MASS (water), conservative form. Water mass per unit current volume is C_w = rho_b*X/(1+X) = rho_d*X, and Fick's law with the X-based effective diffusivity gives J_w = -rho_d(X) D(X,T) dX/dr:
    d/dt [ rho_b(X) X/(1+X) ] = (1/r) d/dr [ r rho_b(X)/(1+X) D(X,T) dX/dr ]
equivalently, with rho_d = rho_b/(1+X):
    d(rho_d X)/dt = (1/r) d/dr ( r rho_d(X) D(X,T) dX/dr )

ENERGY (no internal source; latent heat deliberately omitted because the problem supplies no L_v):
    d/dt [ rho_b(X) c_p(X) T ] = (1/r) d/dr ( r k(X) dT/dr )

Note on the fit inconsistency: rho_b = 650+128X implies rho_d = (650+128X)/(1+X), which is NOT constant (275 -> 650 kg/m^3), so the empirical density fit does not exactly conserve dry-solid mass. Keeping rho_d inside the divergence is still the correct conservative discretisation of the stated model. The 7% spread in t_dry between the three self-consistent forms below is the price of this inconsistency.

## boundary_conditions
At r = 0 (symmetry/regularity): dT/dr = 0, dX/dr = 0. In a cell-centred FV grid the inner face has zero area (A_{1/2}=0) and needs no special treatment; with a node-centred grid use L'Hopital, (1/r)d/dr(r dX/dr) -> 2 d2X/dr2 at r=0.

At r = R, convective heat transfer (heat flows IN when T_air > T_R; with outward-positive flux the sign is):
    -k(X) dT/dr |_{r=R} = h [ T_air(t) - T_R(t) ]            [W/m^2]
    equivalently  k dT/dr|_R = h (T_R - T_air).
    CHECK: h [W/(m^2 K)] * K = W/m^2 = -k dT/dr, k[W/(mK)]*K/m = W/m^2. OK.

At r = R, convective mass transfer (moisture leaves when X_R > Y_air). Both the oven humidity Y and the solid moisture X are given in kg/kg, so the problem's convention is a kg/kg driving force with h_m in m/s:
    -rho_d(X) D(X,T) dX/dr |_{r=R} = h_m rho_d(X) [ X_R(t) - Y_air(t) ]
    equivalently (dividing by rho_d, the form to use with the simplest non-conservative mass equation)
    -D(X,T) dX/dr |_{r=R} = h_m [ X_R(t) - Y_air(t) ]
    CHECK: D[m^2/s]*dX/dr[(kg/kg)/m] = m/s * (kg/kg); h_m[m/s]*(kg/kg) -> identical units. Consistent.
    NOTE: the density reference used in the BC must be the SAME as the density multiplying dX/dt. Using rho_d on one side and 1.0 on the other changes the effective mass Biot number by (1+X) (up to 3.5x) and pushes t_dry from 15 h to >72 h. Do not mix.

Three self-consistent variants (all reduce to the same PDE when rho_b were constant), with resulting grid-converged drying times to max_r X < 0.15:
  (i)  rho_d X conserved, BC scaled by rho_d  -> t_dry = 15.4 h   <-- RECOMMENDED (physically conservative)
  (ii) rho_b X conserved, BC scaled by rho_b  -> t_dry = 17.1 h
  (iii) X primitive, no density factor either side (classic textbook form) -> t_dry = 16.5 h
Quote t_dry ~ 16 h with a +-1 h model-form band.

SOURCE FUNCTIONS (the two-stage oven schedule):
  0 <= t <= 14400 s: T_air(t), Y_air(t) = piecewise-linear interpolation of the 241 points of attachment 1 (60 s spacing).
  t > 14400 s: T_air = T_f, Y_air = Y_f constant (see initial_conditions / part (a)).

## initial_conditions
t = 0: X(r,0) = 2.55 kg/kg uniformly; T(r,0) = 28 C = 301.15 K uniformly.
Air: T_air(0) = 28 C, Y_air(0) = 0.01963 kg/kg (attachment 1 row 1).

HANDOFF AT t = 14400 s (the 4-h end of attachment 1) - this is the initial condition of the constant-temperature stage and it must be a FULL RADIAL PROFILE, not a scalar. From the converged FV solution:
  X: r=0 -> 1.75, r=1 cm -> 1.42, r=2 cm (surface) -> 0.85, X_bar = 1.39  (about 46% of the water is already gone)
  T: essentially isothermal at 50 C (centre 49.99 C, surface 49.97 C)
ROBUSTNESS: this handoff state is almost identical whether Appendix-2 or Appendix-3 properties are used for 0-4 h (X_centre 1.734 vs 1.748; X_surface 0.843 vs 0.846), because in the first 4 h the process is limited by the EXTERNAL film resistance (R/h_m = 6.9 h) and D barely enters. So the stage-2 initial condition is insensitive to which property set is used for the preheat.

APPENDIX 4 (problem 4 only): D = 4.2e-4 exp(-0.30X) exp(-3850/T), rho = 760+90X, c_p = 1850+2150X/(1+X), k = 0.12+0.20X/(1+X); the radius then follows attachment 2, R(t) interpolated from the 145 tabulated points (0.02 m -> 0.01198 m), and the mass/energy equations are written in the moving domain 0<=r<=R(t) (or in a fixed mass-normalised coordinate s=r/R(t)).

## assumptions
- The cylinder is infinitely long: the axial moisture Fourier number at the drying time is only 0.019 and the end faces carry just 7.4% of the area, so T=T(r,t), X=X(r,t).
- The two-stage schedule is exactly: attachment-1 interpolation for 0<=t<=14400 s (piecewise-linear over the 241 points, 60 s apart), then constant oven conditions for t>14400 s.
- After 14400 s the oven is frozen at its last measured state, T_f = 50.165 C (323.32 K), Y_f = 0.04986 kg/kg. (Alternatives in part (a); all shift t_dry by <0.2%.)
- h = 25 W/(m^2 K) and h_m = 8e-7 m/s are reused unchanged for the whole process (see part (b)).
- The driving force for the convective mass flux is the kg/kg difference (X_surface - Y_air), which is the only reading of h_m = 8e-7 m/s that produces a physically sensible time scale.
- No internal heat generation and NO latent heat of vaporisation is included: the problem supplies no L_v and no sorption isotherm, so the energy and mass equations are one-way coupled (X enters T only through the property functions). This is flagged as the largest physical omission (see pitfalls).
- The material is a rigid continuum (no shrinkage) for problems 2 and 3; shrinkage is problem 4's subject (attachment 2).
- The empirical property fits are local-equilibrium relations, i.e. rho, c_p, k, D at a point depend only on the instantaneous local X and T.
- Initial fields are uniform in r.
- No convective transport of moisture inside the solid (pure diffusion); no pressure-driven/permeability flow.
- One-way coupling of the oven to the herb: the herb does not change the oven's T or Y (valid for a well-mixed oven).

## dimensionless_numbers
Evaluated at T = 323.15 K (50 C), R0 = 0.02 m; rho_b, c_p, k, alpha, D all at the stated X.
  X      D [m^2/s]    alpha [m^2/s]   Lu = D/alpha   Bi_h = hR/k   Bi_m = h_m R/D   R0^2/D [h]
  2.55   5.07e-9      1.448e-7        0.035          1.04          3.14             21.9
  1.00   1.02e-8      1.825e-7        0.056          1.25          1.56             10.9
  0.50   1.28e-8      1.996e-7        0.064          1.40          1.25              8.7
  0.15   1.49e-8      2.147e-7        0.069          1.93          1.07              7.4

Liuikov number Lu = D/alpha = 0.035-0.07: heat equilibrates 14-30x faster than moisture, so T(r,t) ~= T_air(t) after the first ~20 min and the quasi-steady (constant-T) assumption in the mass equation is excellent.
Biot (heat) Bi_h = hR/k = 1.0-1.9: O(1), but since there is no internal heat source the true steady state is isothermal (T = T_air); gradients exist only during transients and decay with the thermal time constant.
Biot (mass) Bi_m = h_m R/D = 3.1 (at X=2.55) falling to 1.1 (at X=0.15): O(1), the drying is MIXED internal/external controlled - neither resistance may be dropped. Equivalent resistance form: external 1/h_m = 1.25e6 s/m vs internal R/(2D) = 1.0e6 s/m (at X=2.55).
Fo_heat = alpha t / R^2 = 5.2 at t = 4 h -> thermally quasi-steady well before the end of the preheat.
Fo_mass = D t / R^2 = 0.18 at t = 4 h, = 1.0 at about t = 22 h (using D at X=2.55).
First root of J_0: lambda_1 = 2.4048, lambda_1^2 = 5.783 (used for the tail time constant R^2/(lambda_1^2 D) = 1.3-3.8 h).
Kossovich number Ko = (X0-Xe) L_v /(c_p dT) = (2.55-0.05)*2.26e6/(3415*22) = 75 >> 1: if latent heat were modelled there would be a long constant-rate (wet-bulb) period, which is exactly the physics the given data set omits.
Arrhenius sensitivity: E_a/R = 3850 K, so D roughly DOUBLES for a +11 K rise (323 -> 334 K); the material temperature therefore matters as much as the moisture content.

## characteristic_times
Thermal: R0^2/alpha = 4e-4/1.45e-7 = 2.76e3 s = 46 min (worst case, X=2.55); with the J_0 eigenvalue, tau_heat = R0^2/(5.783 alpha) = 477 s = 8 min. The herb is within 1 K of the oven air after ~20-30 min, so the material reaches 50 C about 1 h into the 4-h preheat.
Internal moisture: R0^2/D = 21.9 h (X=2.55) down to 7.4 h (X=0.15); tau_mass = R0^2/(5.783 D) = 3.8 h -> 1.3 h.
External (film) moisture: R0/h_m = 0.02/8e-7 = 2.5e4 s = 6.94 h.
Whole-body lumped drying estimate (series resistances, log-mean driving force):
  R_ext = 1/h_m = 1.25e6 s/m, R_int = R0/(2D) ~ 1.0e6 s/m, R_tot ~ 2.2e6 s/m.
  dX_lm = (2.55-0.15)/ln(2.5/0.1) = 0.745; J_X = 0.745/2.2e6 = 3.4e-7 (m/s)(kg/kg);
  t ~ dX_total*R0/(2 J_X) = 2.40*0.02/(2*3.4e-7) = 7.1e4 s = 19.7 h  (crude upper estimate; the numerical answer is 15.4-16.5 h).
Overall drying time to max_r X < 0.15 kg/kg (grid-converged FV): 15.4 h (conservative rho_d form), 16.5 h (textbook form), 17.1 h (rho_b form) -> quote ~16 h = 0.67 day.

## recommended_numerics
DISCRETISATION (finite volume, cell-centred):
Faces r_{i+-1/2} = i*dr, i=0..N (dr = R/N); cell centres r_i = (i-1/2)*dr; V_i = pi(r_{i+1/2}^2 - r_{i-1/2}^2), A_{i+-1/2} = 2 pi r_{i+-1/2}. The r=0 singularity disappears automatically because A_{1/2} = 0.
Mass, backward Euler with lagged (Picard) coefficients at X^n:
  (rho_d,i^n X_i^{n+1} - rho_d,i^n X_i^n) V_i/dt = A_{i+1/2} G_{i+1/2}(X_{i+1}^{n+1}-X_i^{n+1})/dr - A_{i-1/2} G_{i-1/2}(X_i^{n+1}-X_{i-1}^{n+1})/dr
  with G = HARMONIC mean of rho_d(X)D(X,T) across a face, G_{i+1/2} = 2 G_i G_{i+1}/(G_i+G_{i+1}). Harmonic (not arithmetic) is essential where the surface dries out and D varies by 3x.
  Outer face: A_N h_m rho_d,N (X_N - Y_air) is added to b_N (as +A_N h_m rho_d,N) and to d_N (as +A_N h_m rho_d,N Y_air).
Energy: same structure with rho_b c_p on the diagonal and harmonic-mean k, plus A_N h on b_N and A_N h T_air(t) on d_N.
Result: a tridiagonal system per stage; solve with the Thomas algorithm (pure-MATLAB friendly, ~50 lines, no toolbox needed). Backward Euler + lagged coefficients is UNCONDITIONALLY stable, which matters because the surface cell has a huge Fourier number.
Grid: N = 100 (dr = 0.2 mm) recommended; N = 200 (0.1 mm) for the first 10 min. Convergence of t_dry: N = 20/40/100/200 -> 16.14/16.33/16.45/16.48 h, so even dr = 0.5-1 mm is within 2%. Error source for coarse grids is the near-surface layer during the first ~10 min (diffusion penetration sqrt(Dt) < dr at small t).
Time stepping: dt = 1 s for 0 < t <= 600 s (resolve the air ramp and the fast surface response), ramp to 10 s by 1 h, 30 s up to 4 h, then 60-120 s. Total < 5000 steps for 3 days. DO NOT use explicit Euler: dt <= 0.25 dr^2/D gives 0.17 s at dr = 0.1 mm (5e5 steps for 24 h) and 16.7 s at dr = 1 mm.
Preferred alternative for higher accuracy at no extra cost: use a NON-UNIFORM radial grid, dr_j growing geometrically from ~20 micrometres at r=R to ~0.5 mm at the axis; this resolves the drying front with ~100 cells.
Output mapping: the required tables are at r = 0, 0.5, 1, 1.5, 2 cm. With a cell-centred grid interpolate linearly between the two straddling cells, and at r = 0 use a quadratic extrapolation X(0) ~= (4X_1 - X_2)/3 (do not just take the first cell, which sits at dr/2). With N = 200 and dr = 0.1 mm the exact output nodes 0.5, 1.0, 1.5 cm coincide with cell centres when N is a multiple of 20.
Requested output cadence: result2 needs T and X every 1 s on 0.1 cm spacing; result3/result4 need X every 60 s on 0.1 cm spacing (and result4's last column is the moving surface r = R(t)).

## expected_magnitudes
CROSS-CHECK OF PROBLEM 1 (Appendix-2 properties, for internal consistency only): at t = 1800 s the model gives X = [2.550, 2.550, 2.549, 2.429, 1.502] at r = 0, 0.5, 1, 1.5, 2 cm and T = [33.56, 33.77, 34.36, 35.37, 36.73] C; only a ~4 mm surface shell has dried in 30 min.

PROBLEM 2 (Appendix-3 properties), Table 3/4 values, X at r = 0, 0.5, 1, 1.5, 2 cm and T in C:
  t=0.5 h  X 2.5500 2.5500 2.5490 2.4171 1.5064   T 32.2 32.4 33.0 34.0 35.3
  t=1.0 h  X 2.5499 2.5477 2.4913 2.0619 1.3405   T 40.4 40.6 41.1 41.9 43.0
  t=1.5 h  X 2.5412 2.5096 2.3111 1.7959 1.2379   T 45.8 45.9 46.2 46.6 47.1
  t=2.0 h  X 2.4803 2.3941 2.0959 1.6068 1.1481   T 48.4 48.4 48.6 48.8 49.0
  t=2.5 h  X 2.3408 2.2209 1.8971 1.4576 1.0639   T 49.4 49.5 49.5 49.6 49.6
  t=3.0 h  X 2.1497 2.0253 1.7189 1.3306 0.9861   T 49.8 49.8 49.9 49.9 50.0
  (N=40 grid; expect +-0.01 absolute on X; T within 0.05 C). The centre X is UNCHANGED to 4 decimals until ~1 h and the surface leads the centre by up to 3.2 C at 0.5 h.
  4-h handoff: X_centre 1.75, X(R/2) 1.42, X_surface 0.85, X_bar 1.39; T isothermal at 50 C.

PROBLEM 3, Table 5 (every 6 h, X at r = 0, 0.5, 1, 1.5, 2 cm):
   6 h  1.1108 1.0632 0.9422 0.7761 0.6118
  12 h  0.3177 0.3094 0.2869 0.2527 0.2147
  18 h  0.1183 0.1164 0.1111 0.1029 0.0935
  24 h  0.0675 0.0670 0.0656 0.0636 0.0612
  30 h  0.0545 0.0543 0.0540 0.0535 0.0529
  36 h  0.0511 ... 0.0507   (the profile is flat to 3 decimals; everything relaxes to Y_f = 0.05)
DRYING TIME (Problem 3 answer): t = 1.6e4 s? no - t = 16.4 h = 5.9e4 s = 0.68 day for the textbook form; 15.4 h for the conservative rho_d form; 17.1 h for the rho_b form. QUOTE ~16 h (about 0.7 day), i.e. ONE DAY, NOT 2-3 days.
Crossing interpolation: pass through X_centre = 0.15 between 12 h (0.318) and 18 h (0.118) -> t_dry = 16.4 h.
Overall mass balance (per metre of cylinder): water 0.881 kg/m at t=0, 0.552 at 4 h, 0.178 at 12 h, 0.0499 at 24 h (asymptote 0.038 kg/m at X = 0.05). The FV scheme conserves this to <0.1%.
PROBLEM 4 (Appendix-4 D, no shrinkage): 38.7 h = 1.61 day; with the R(t) of attachment 2 shortening the path, ~30-35 h. Appendix-2 D -> 26.5 h.

WHY "2-3 DAYS" IS NOT REPRODUCED: t_dry scales almost linearly in 1/h_m over the range of interest. Sensitivity (textbook form, Appendix 3):
  h_m = 8e-7 -> 16.5 h ; 4e-7 -> 27.5 h ; 2e-7 -> 49.8 h (2.1 d) ; 2e-6 -> 9.9 h ; Chilton-Colburn 0.018 -> 5.9 h.
So the stated 2-3 days corresponds to h_m ~ 1.5-2.5e-7 m/s (3-5x below the given 8e-7), or equivalently to a D about 3-10x smaller than Appendix 3's. With the problem's own numbers the honest answer is ~16 h. State this explicitly in the paper and treat "2-3 days" as the physical context, not as a validation target.

## pitfalls
- UNIT TRAP (I hit this): exp(-3850/T) needs T in KELVIN (323.15), while the oven table and the paper quote 50 C. Mixing them makes D wrong by ~6 orders of magnitude; and in the surface BC h(T_air - T_surface) the oven value must be converted to K before it meets a Kelvin field, otherwise the solid's temperature is dragged to 0 K and the run silently freezes (D -> 0, X never changes).
- The kg/kg driving force fixes the units of h_m. Do NOT re-derive h_m from h via Chilton-Colburn: h_m = h/(rho_air c_p_air Le^(2/3)) = 25/(1.09*1006*1.13) = 0.020 m/s, i.e. 2.5e4 times the given 8e-7. The given h_m is a lumped coefficient that only makes sense against a kg/kg difference. Using the true value drops t_dry to 5.9 h; using 2e-7 raises it to 50 h - so the answer is dominated by this one number.
- Density inconsistency between the transient term and the BC. If rho_d multiplies dX/dt but the BC is written with a unit coefficient (or vice versa) the effective mass Biot number changes by (1+X) (up to 3.5x) and t_dry jumps from ~15 h to >72 h. Be self-consistent; the three consistent variants differ by only 7%.
- Using the wrong D formula. Problem 2/3 must use Appendix 3 (D = 2.4e-3 e^{-0.45X} e^{-3850/T}), which is 3-7x LARGER than Appendix 2's D = 7e-9 e^{-0.89X} at the same state, and Appendix 4's is ~4x smaller than Appendix 3's. Mixing them changes the answer by a factor 2-3.
- The r = 0 singularity: dividing by r at r = 0 NaNs immediately. Use a cell-centred FV grid (inner face area is exactly zero) or, for a node-centred grid, the L'Hopital form 2*d2X/dr2.
- Sign errors in the surface BCs. Heat enters when T_air > T_surface; water leaves when X_surface > Y_air. Both must have the driving force oriented so that the flux is outward-positive, matching the outward normal at r = R.
- Assuming the preheat stage only heats the herb. It does not: the oven is at 28-50 C while the herb starts at X = 2.55 against Y_air = 0.02, so roughly 46% of the water is already removed during the 4-h preheat (X_bar 2.55 -> 1.39). Starting stage 2 at X = 2.55 uniformly would over-predict t_dry by ~4 h.
- Testing convergence on the average X instead of max_r X. The requirement is that EVERY point be below 0.15; the centre is the last to dry and the mean passes 0.15 several hours earlier (mean crosses 0.15 at about 11 h vs centre at 16.4 h).
- Coarse grid + strong surface BC artefacts. With 20 cells the first 10 min are wrong by up to 30% at the surface because sqrt(Dt) < dr; t_dry is nevertheless within 2%, so the artefact is invisible in the headline number but visible in the Table 3 surface column. Use dr <= 0.5 mm, or a graded grid.
- Explicit time stepping. dt <= 0.25 dr^2/D = 0.17 s at dr = 0.1 mm -> 5e5 steps for 24 h. Use backward Euler with lagged coefficients (Thomas), which is unconditionally stable and needs < 5000 steps.
- Omitting the latent heat of vaporisation. The problem provides no L_v, so omitting it is the intended model - but the Kossovich number is 75, i.e. the real process would be evaporatively cooled and partly constant-rate. This is the single biggest physical omission and the natural 'model refinement / limitations' paragraph; note that including it would SLOW the drying and move the answer toward the stated 2-3 days.
- Expecting X -> 0. The model asymptote is the oven humidity Y_f = 0.05 kg/kg, so X(everywhere) -> 0.05, and the 0.15 threshold is reached long before equilibrium. Reporting 'equilibrium drying time' instead of 'time to 0.15' gives a wrong (much larger) number.
- Stopping the integration at 72 h just because attachment 2 spans 3 days. With Appendix 3 the process is finished at 16 h and nothing moves afterwards; result3 must still be tabulated to its stated horizon, but the answer to Problem 3 is ~16 h, not 72 h.
- Problem 4 only: forgetting that r = R(t) moves. Attachment 2's radius shrinks 2.0 -> 1.198 cm, so both the diffusion path and the surface area shrink; a fixed-radius solve over-predicts the drying time and, worse, mis-locates the reported 'surface' column (result4's last column must be X at the CURRENT radius).
- Numerical output precision: the tables require 4 decimal places and the crossing time for X = 0.15 must be linearly interpolated between the two bracketing output times, not snapped to the nearest sample.


# ===== derive:audit (key=v2:d1e908cfba4b928436b60b6a600dc6f0f85e5245f44f598a87754552da3037db) =====

## interpretation_options
- {
 "question": "Q1. What is the drying-room (air) moisture concentration during the constant-temperature drying stage (t > 14400 s)?",
 "options": [
  "X_a = 0.0500 kg/kg, exactly (the attachment-1 plateau)",
  "X_a = 0.04986 kg/kg (literally the last row of attachment 1)",
  "X_a = 0 kg/kg (dry air; the evaporated water is assumed carried away instantly)",
  "X_a = an equilibrium moisture content obtained from a sorption isotherm of the herb (no isotherm is supplied)",
  "X_a continues to creep upward past 14400 s following the fitted exponential"
 ],
 "recommended": "X_a = 0.0500 kg/kg for t > 14400 s, joined continuously to the attachment-1 interpolation.",
 "why": "The data decide this: taking every sample with t >= 9000 s (n=91), the mean moisture is 0.049994 with range [0.04975, 0.05025] - i.e. the setter generated a plateau of exactly 0.05 plus +-2.5e-4 noise. A first-order fit X = X_inf + (X0-X_inf)e^(-t/tau) returns X_inf = 0.0500 and tau = 2600 s (rms 0.00098, i.e. 3% of the 0.031 range), so the plateau is the asymptote, not a sampling accident. Option (b) differs by 0.3% and is harmless but is just one noisy sample. Option (c) is fatal to the problem's logic: the target of problem 3 is X < 0.15 everywhere, and if X_a >= 0.15 the herb can never satisfy it (my solver stalls and never reaches the criterion). With X_a = 0.05 = the target/3 the problem is well posed and has a finite answer; my converged 1-D simulation gives t_dry = 14.9 h (X_a=0), 15.5 h (0.02), 16.6 h (0.05), 19.5 h (0.10). So the 0.15 target in the statement is the fingerprint of a designed X_a = 0.05, and the choice moves the answer by 10-20% - it must be stated as an assumption. Option (d) is the physically correct route (an air humidity of 0.05 kg/kg dry air at 50 C corresponds to a true equilibrium moisture content of only a few percent on a dry basis, so using 0.05 directly is conservative/slow) but no isotherm data are supplied, so the direct difference h_m(X_s - X_a) is the only implementable reading - and it is the reading the appendix-3/4 empirical D correlations were fitted under."
}
- {
 "question": "Q2. What is the air temperature during the constant-temperature drying stage?",
 "options": [
  "T_a = 50.00 C exactly",
  "T_a = 50.165 C (the last row of attachment 1)",
  "T_a continues the fitted exponential relaxation past 14400 s",
  "T_a = 50 C plus a small linear drift"
 ],
 "recommended": "T_a = 50.0 C constant for t > 14400 s.",
 "why": "Same internal evidence: the mean of attachment 1 over t >= 9000 s is 50.005 C (n=91, min 49.757, max 50.246, sigma about 0.14), and the plateau is reached early - the air temperature stays above 49.5 C for good from t = 6540 s. A first-order fit gives T_inf = 50.0 C, tau = 1870 s, rms 0.34 C, i.e. the underlying signal is 50 - 22*exp(-t/1870). Using 50.165 instead of 50.00 perturbs the herb temperature by < 0.2 C and the drying time by < 0.1%; the answer to problem 3 is unchanged to 3 significant figures. Reporting 50 C is both the round design value and the mean of the data, so it is the most defensible."
}
- {
 "question": "Q3. Does 'heng-wen gan-zao' (constant-temperature drying) name the AIR temperature or the HERB temperature?",
 "options": [
  "The drying room / air is held at constant temperature (and humidity); the herb temperature is an output that asymptotes to it",
  "The herb is held at constant temperature (i.e. a classic constant-rate drying period with the material pinned at the wet-bulb temperature)",
  "The herb's surface is held at the constant air temperature (surface temperature = T_a imposed as a Dirichlet condition)"
 ],
 "recommended": "The air/room. Impose T_a = 50 C, X_a = 0.05 as the ambient BCs, and let the herb temperature be computed, never imposed.",
 "why": "The statement frames the whole process as 'through regulating the drying room's temperature and humidity environment', so the controlled variable - and therefore the thing that gives the stage its name - is the room's. Attachment 1 is explicitly the ROOM temperature/moisture and it visibly saturates at 50.00/0.0500; the herb's temperature is never constant in the data or in any model of it (my simulation: centre 28.0 -> 32.0 (0.5 h) -> 40.1 (1 h) -> 48.3 (2 h) -> 49.99 (4 h), a monotone relaxation with no plateau). Option (b) is real drying theory (the constant-rate period does have the material at a constant wet-bulb temperature), but it cannot be implemented here: no latent heat, no vapour-pressure/psychrometric data, and appendix 2's D = 7e-9 exp(-0.89X) has NO temperature dependence at all, which would make a wet-bulb thermal analysis irrelevant to the moisture. Option (c) is the actual trap: forcing the surface to 50 C over-heats the herb by ~13 C at t = 1800 s (the correct surface temperature is 36.8 C when the air is 41.5 C). Both legitimate readings collapse to the same boundary condition T_a = 50 C, so the only practical risk is option (c)."
}
- {
 "question": "Q4. Should latent heat of vaporisation enter the energy equation?",
 "options": [
  "No - solve heat conduction and moisture diffusion as two decoupled PDEs with the supplied rho, cp, k, h, h_m, D",
  "Yes - add an evaporation sink rho*cp*dT/dt = (1/r)d/dr(k r dT/dr) - rho_d*h_m*(X_s-X_a)*L*(surface delta function), using a literature L = 2.26e6 J/kg",
  "Yes - and also use the evaporated flux to depress the herb's surface temperature to a wet-bulb value"
 ],
 "recommended": "No. Omit the latent-heat term; it is the reading the statement forces.",
 "why": "Three internal arguments. (1) The parameter inventory of appendix 2 is exactly {rho, cp, k, h, h_m, D}; a competent setter who wanted latent heat would have had to supply L and a vapour-pressure/sorption relation, and supplied neither. (2) Appendix 2's D = 7e-9 exp(-0.89X) has no temperature dependence, i.e. for problem 1 the moisture equation is deliberately decoupled from the thermal field - so a latent-heat term could not affect table 2 at all, and would only perturb table 1. (3) The appendix-3/4 correlations D = a*exp(-bX)*exp(-3850/T) are EMPIRICAL fits to this material's measured drying curves; those measurements already contain whatever evaporative cooling occurred, so adding an explicit L on top double-counts the effect. Quantify the consequence rather than ignore it: the quasi-steady surface balance h(T_a - T_s) = rho_d*h_m*L*(X_s - X_a) with L = 2.26e6 J/kg gives a latent flux of ~1.2e3 W/m^2 early on (rho_d = 278 kg/m^3, X_s - X_a = 2.5) against a convective capacity of only 25*(50 - T_s) W/m^2 - i.e. tens of kelvin of wet-bulb depression if taken literally, which is unphysical for a partially dried surface. At the late stage (X_s - X_a = 0.1) the depression is a more plausible ~7 K, and since 3850*(1/318 - 1/323) = 0.19, a 5 K cooler herb lowers D by ~18% and lengthens the drying time by roughly 20-25% (problem 3 would move from ~17 h to ~21 h). So state explicitly, as an assumption, that latent heat is neglected per the supplied parameter list, and quote the ~20% sensitivity."
}
- {
 "question": "Q5. Must problems 2, 3 and 4 reuse appendix-2's h = 25 W/(m^2 K) and h_m = 8e-7 m/s (appendices 3/4 give only D, rho, cp, k)?",
 "options": [
  "Yes - reuse h = 25 and h_m = 8e-7 unchanged, and state it as an assumption (appendix 2 is the only source of these)",
  "No - appendix 2 is titled 'parameters for problem 1', so h and h_m must be re-fitted to the appendix-3/4 material properties",
  "Yes for h but no for h_m (or vice versa)"
 ],
 "recommended": "Yes: reuse both, unchanged, for all four problems, with an explicit assumption statement plus a sensitivity study on h_m.",
 "why": "The counter-argument is real - appendix 2 is literally headed 'relevant parameters for problem 1' - but it cannot be acted on: appendices 3 and 4 supply no h and no h_m, and both are indispensable (h sets the surface heat flux, h_m the surface moisture flux). Physically h and h_m are properties of the external air flow (velocity, turbulence, geometry), not of the herb's moisture content, so carrying them over is justified physics rather than numerical convenience. There is even independent empirical support: re-running problem 4 with h_m = 8e-7 while predicting the radius from dry-mass conservation with the appendix-4 density (rho = 760+90X) reproduces attachment 2's shrinkage to within +4% at 30 min, +5% at 24 h and to the same asymptote (0.607 vs 0.599 of R0) - so the borrowed magnitude is right for problem 4 as well. Consequence to report honestly: the problem-3 answer is insensitive to h (16.50 h at h = 50 vs 16.63 h at h = 12.5, i.e. an 8x change in h moves it by <1%) but very sensitive to h_m (11.1 h at 1.6e-6, 16.6 h at 8e-7, 27.6 h at 4e-7). A 2x error in h_m moves the answer by a factor 1.7, so the h_m assumption belongs in the paper's assumption list with a sensitivity table. Also note that the phrase in problem 2, 'the parameters of the preheat-equilibrium and constant-temperature stages are somewhat different' (参数有所不同), refers to the AMBIENT conditions (T_a, X_a change between stages) and to swapping the appendix-2 correlations for appendix-3 ones - not to inventing new h/h_m."
}
- {
 "question": "Q6. In problem 4, are the tabulated 'distances to the herb centre' material (initial/Lagrangian) coordinates or current spatial coordinates?",
 "options": [
  "Material (Lagrangian) coordinates: a fixed grid xi = 0, 0.1, ..., 2.0 cm = R0, where the last node is the herb surface at every instant",
  "Current spatial coordinates r: a fixed 0.1 cm grid 0, 0.1, ..., 1.9 plus a time-varying 'herb surface' column at r = R(t)",
  "Current spatial coordinates 0 ... R(t) with a time-varying number of columns"
 ],
 "recommended": "Material (Lagrangian) coordinates on the fixed grid xi in [0, R0] with 0.1 cm spacing (21 columns), the last one being the surface; in the paper state the convention in one sentence and give the conversion r = xi*R(t)/R0.",
 "why": "Correct one factual premise first: attachment 2 shows R crossing 1.5 cm at t = 13145 s (interpolated), i.e. 3.65 h, NOT 'within about an hour' - R(30 min) = 1.873, R(1 h) = 1.794, R(4 h) = 1.477, R(24 h) = 1.204, and R plateaus at 1.198 cm (R/R0 = 0.599, volume ratio 0.359) from about t = 36 h. So from 3.65 h onward - which is ~90% of a 1-day process - a fixed spatial grid that runs out to 1.5-2.0 cm lies partly or wholly OUTSIDE the material, producing physically undefined entries in columns that the template demands. Material coordinates make every column meaningful at every time, keep the output a rectangular array with a constant header (which is what a fixed .xlsx template requires), and are the standard numerical treatment of a shrinking domain (compute on xi in [0,R0]; the surface is the node xi = R0 forever). The 'herb surface' header in result4.xlsx and the '0, 0.5, ..., herb surface' list in table 6 are then the setter's way of flagging that the last node is the moving physical surface, whose current distance to the centre is not 2 cm (it is 1.477 cm at 4 h and 1.198 cm at >= 36 h) - which is precisely why a numeric label would mislead and a role label was used. Note the reassuring part: under either convention the centre column, the surface column and hence the drying time are identical - only the intermediate columns' physical location differs. For uniform shrinkage r = xi*R(t)/R0, so the two conventions differ by the time-dependent scale factor R(t)/R0 (1.000 at 0 h, 0.739 at 4 h, 0.624 at 12 h, 0.602 at 24 h, 0.599 at 72 h); a grader who wants spatial values can rescale, and it costs one line to say so."
}
- {
 "question": "Q7. Is the preheat-equilibrium stage of problems 2/3/4 the attachment-1 window 0-14400 s (exactly 4 h)?",
 "options": [
  "Yes: interpolate attachment 1 for 0 <= t <= 14400 s, then hold T_a = 50, X_a = 0.05",
  "No: the stage ends when the air conditions stabilise, i.e. at t ~ 9000 s (2.5 h), where the plateau already holds; use 50/0.05 from 9000 s",
  "No: the preheat stage is only 1800 s (30 min), because problem 1's tables run to 1800 s",
  "Take the switch-over time as a fitted parameter (the air T relaxation time, tau = 1870 s, or the moisture tau = 2600 s)"
 ],
 "recommended": "Option (a) as the primary reading (t = 14400 s, the end of the supplied data), with a sentence noting that the air conditions have already plateaued by ~9000 s and that the choice is numerically immaterial.",
 "why": "There is no explicit statement of the stage duration anywhere, so the only well-defined, data-anchored boundary is the end of attachment 1 at 14400 s = 4 h. The '1800 s' reading (c) is a genuine trap: problem 1's tables are titled '30 minutes' and cover only 0-1800 s, but that is a REPORTING window, not a stage length; the preheat stage as a model stage runs as long as the ambient conditions are still changing. The data say that change is over well before 4 h - the air temperature stays above 49.5 C from t = 6540 s onward, and the t >= 9000 s plateau means are exactly 50.005 C and 0.049994 kg/kg. Fortunately the ambiguity is harmless: switching at 9000 s instead of 14400 s changes the ambient conditions by at most 0.165 C and 0.00014 kg/kg (a 0.3% step), and my converged simulations return an unchanged drying time (16.550 h for problem 3 and 19.717 h for problem 4 under both switch times). So choose (a), state it, and add one sentence that the result is insensitive to it."
}
- {
 "question": "Q8. What does the statement's 'drying generally lasts 2-3 days' imply, given that the supplied parameters give a much shorter time?",
 "options": [
  "The 2-3 day remark is generic domain colour; the model's answer (~1 day) stands",
  "The parameters must be wrong/tuned until the answer lands in 2-3 days (e.g. by shrinking h_m, or by taking X_a = 0.10-0.15)",
  "Problem 2's '2-3 days' refers only to the whole real process including the preheat, so no consistency is required"
 ],
 "recommended": "Option (a), and report the model answer plus its uncertainty band rather than forcing it to 2-3 days.",
 "why": "The blind model with the stated parameters dries to X < 0.15 everywhere in 16.6 h (problem 3, fixed radius, appendix-3 properties) and 19.7 h (problem 4, moving boundary, appendix-4 properties, R(t) from attachment 2); the centre is the binding point (at the moment of compliance, X_centre = 0.150 while X_surface = 0.113). Attachment 2 corroborates that order of magnitude independently: the radius stops changing at about 36 h, i.e. the real experiment was essentially finished within ~1.5 days, and a dry-mass-conserving prediction using the appendix-4 density reaches the same asymptote (R/R0 = 0.607 vs the measured 0.599). So the honest answer is ~0.7-0.9 day, with a band of roughly 11-28 h coming from the borrowed h_m (11.1 h at 1.6e-6, 16.6 h at 8e-7, 27.6 h at 4e-7) and 15-20 h coming from X_a (14.9 h at 0, 19.5 h at 0.10). If a team reports 2-3 days they have almost certainly made a hundreds-fold error (see the consistency check in extra_checks) or has tuned h_m/X_a to hit the prose."
}
- {
 "question": "Q9. For problem 3, which point decides 'the herb is dry everywhere' (各处)?",
 "options": [
  "The centre (max X over the domain)",
  "The surface (min X)",
  "The volume/area-average X",
  "All nodes simultaneously, i.e. the last node to fall below 0.15"
 ],
 "recommended": "The centre, i.e. the maximum of X over the radius; equivalently the last point to fall below 0.15, which is the centre.",
 "why": "The drying front always moves inward here: for problem 1 the mass-transfer boundary layer thickness is D/h_m = 0.90 mm (Bi_m = h_m*R/D = 22.1 at X = 2.55), so after 30 min the centre is still at X = 2.5500 to 4 decimals while the surface has fallen to ~1.26; for problems 2/3 the layer is 6.4-18.8 mm (Bi_m = 3.1 -> 1.1) and for problem 4 it is 1.6-3.5 mm (Bi_m = 12.2 -> 5.8). At the instant problem 3 is satisfied my simulation has X_centre = 0.1500, X_midplane = 0.13 and X_surface = 0.1128, confirming that the centre is the binding constraint and that using the surface or the average would substantially understate the drying time."
}
- {
 "question": "Q10. What unit is the time column of result2/3/4.xlsx in, and what does the '烘干结束时间' row mean?",
 "options": [
  "Seconds throughout (the template's A column starts 60, 120), with the paper tables and the 'drying end time' row in hours",
  "Hours throughout for problems 3/4 because the paper tables use hours",
  "Whatever the paper table uses"
 ],
 "recommended": "Seconds in every .xlsx (all four templates say 'A column = time, unit s' in appendix 1); hours only in the paper tables and in the single 'drying end time' row of tables 5 and 6.",
 "why": "Appendix 1 spells it out for all four result files - 'A column is time (unit: s)' - and the template dumps show result3.xlsx and result4.xlsx literally starting 60, 120, which is seconds for a 60 s sampling interval (the rounded numbers are not hours). Problem 3 asks for 水分浓度 'every 60 s' and problem 4 asks for 'every 60 s and every 0.1 cm', so result3/4 are 60 s x 0.1 cm grids while the paper tables are 6 h x 0.5 cm. Mixing the two (writing hours into the spreadsheet) is a routine way to lose the format marks."
}

## latent_heat_verdict
OMIT latent heat, as the primary and intended reading. Reasons from internal evidence, in order of strength: (1) Appendix 2's parameter list is exactly {rho = 820, cp = 2600, k = 0.36, h = 25, h_m = 8e-7, and D = 7e-9 exp(-0.89X)} - no L, no vapour pressure, no sorption isotherm. A latent-heat term is unknowable from the supplied data, so it cannot be part of the required model. (2) Appendix 2's D has NO temperature dependence, so for problem 1 the moisture equation is deliberately decoupled from the thermal field - a latent-heat sink could not change table 2 at all, only table 1, which is the opposite of what a setter who wanted evaporation-coupled physics would design. (3) The appendix-3/4 forms D = a exp(-bX) exp(-3850/T) are empirical fits to measured drying curves of this material; the measured temperatures already embed whatever evaporative cooling occurred, so adding L explicitly double-counts it. (4) Numerically the effect is not negligible and should be quoted as a sensitivity, not silently dropped: a quasi-steady surface balance h(T_a - T_s) = rho_d h_m L (X_s - X_a) with L = 2.26e6 J/kg gives 1.2e3 W/m^2 of latent flux early on against a convective capacity of 25(50 - T_s) W/m^2, an unphysical multi-kelvin-to-tens-of-kelvin depression if taken literally; at the late stage (X_s - X_a = 0.1, rho_d = 278) the depression is a plausible ~7 K, and because 3850(1/318 - 1/323) = 0.19, a 5 K cooler herb lowers D by 18% and lengthens the drying time by roughly 20-25% (problem 3 would go from ~17 h to ~21 h). So: omit it, state the assumption, and quote the ~20% band. The expected clean model is therefore two decoupled PDEs: rho*cp*dT/dt = (1/r)*d/dr(k*r*dT/dr) with -k*dT/dr|_R = h(T_a - T_s) and dT/dr|_0 = 0; dX/dt = (1/r)*d/dr(r*D*dX/dr) with -D*dX/dr|_R = h_m(X_s - X_a) (equivalently a physical water flux rho_d*h_m*(X_s - X_a), rho_d = rho/(1+X)) and dX/dr|_0 = 0.

## output_coordinate_verdict
MATERIAL (initial/Lagrangian) coordinates xi in [0, R0 = 2 cm] on the fixed 0.1 cm grid, the last node being the herb surface at all times. One factual correction to the premise: attachment 2 puts R below 1.5 cm at t = 13145 s = 3.65 h, not 'within roughly an hour' (R = 1.873 cm at 30 min, 1.794 at 1 h, 1.477 at 4 h, 1.204 at 24 h, plateauing at 1.198 cm = 0.599 R0 from ~36 h onward; volume ratio 0.359). The decisive argument is that a fixed SPATIAL grid out to 1.5-2.0 cm becomes physically undefined for t > 3.65 h, i.e. for nearly the whole 2-3 day run, while the .xlsx template and the 0.1 cm x 60 s output mandate a constant set of columns; material coordinates keep every column inside the material at every time (the node xi = R0 is the surface forever) and give a rectangular array with a constant header row. The '药材表面' label in result4.xlsx (the only template whose last header cell is not a number) and the '0, 0.5, ..., 药材表面' header of table 6 are then exactly what one writes to flag that the last node is the moving physical surface, whose CURRENT distance to the centre is not 2 cm (it is 1.477 cm at 4 h and 1.198 cm at >= 36 h) - a numeric label there would be actively misleading. Practical instruction for the code and the paper: solve on a fixed xi-grid, report X(xi,t) in the columns, and state in one sentence that the distances in the header are initial (material) distances while the last column is the surface, with the mapping r = xi*R(t)/R0 available for anyone who wants current spatial coordinates (scale factor R(t)/R0 = 1.000 at 0 h, 0.739 at 4 h, 0.624 at 12 h, 0.602 at 24 h, 0.599 at 72 h). Reassurance for grading: under either convention the centre column, the surface column and the drying time are identical; only the intermediate columns' physical locations differ.

## extra_checks
- MASS-FLUX CONSISTENCY (the single biggest way to be wrong by 100x): write the moisture BC in the X-form, -D*dX/dr|_R = h_m*(X_s - X_a). Then the physical water flux is rho_d*h_m*(X_s - X_a) with rho_d = rho/(1+X) = 820/3.55 = 231 kg/m^3 for problem 1 and 278 kg/m^3 for problem 4. Using the same rho_d on both sides of the PDE and the BC makes the factor cancel and everything is self-consistent; using it on one side only rescales the drying time by a factor ~rho_d (200-700), which is how teams land on 33 days or 3 hours. Independent verification that the intended magnitude is right: at t = 1800 s the given parameters predict a 8-10% volume loss, and attachment 2 actually shows a 12.7% volume loss (R 2.000 -> 1.873 cm). The supplied parameters are therefore the correct order of magnitude, and an answer in the 10-30 h range is expected.
- UNIT TRAP IN THE ARRHENIUS TERM: appendix 3/4's T is in KELVIN (the statement says so explicitly). exp(-3850/323.15) = 6.70e-6, exp(-3850/301.15) = 2.80e-6, but exp(-3850/50) = 3.6e-34 if degrees Celsius are substituted - a 28-order-of-magnitude error that makes D vanish. Also convert T0 = 28 C to 301.15 K, not 301 or 28; a 5 K error in T changes D by ~2.4x. This is the highest-severity single-character bug available in this problem.
- GRID RESOLUTION AT THE SURFACE: the moisture boundary layer thickness is D/h_m = 0.90 mm for problem 1 (Bi_m = h_m*R/D = 22.1 at X = 2.55), 6.4-18.8 mm for problems 2/3 (Bi_m = 3.1 -> 1.1), and 1.6-3.5 mm for problem 4 (Bi_m = 12.2 -> 5.8). The mandated 0.1 cm grid resolves the 0.9 mm layer with barely one node, so the 2 cm column of table 2 is first-order sensitive to the mesh: X(2 cm, 1800 s) = 1.302 (dr = 2 mm), 1.291 (1 mm), 1.256 (0.5 mm), 1.231 (0.25 mm), 1.217 (0.125 mm), 1.209 (0.0625 mm) - i.e. about 1.26 on the required 0.1 cm grid versus 1.21 fully converged. Report on the required grid, use at least 0.05 cm cells internally plus interpolation, and say in the paper that the surface value is the mesh-sensitive one.
- REFERENCE VALUES TO CROSS-CHECK AGAINST (problem 1, appendix-2 properties, k = 0.36 constant, 0.5 mm cells): T(r = 0/0.5/1/1.5/2 cm) = 28.00/28.00/28.00/28.03/28.17 at 100 s; 28.45/28.53/28.80/29.30/30.15 at 600 s; 30.53/30.70/31.21/32.09/33.40 at 1200 s; 33.56/33.75/34.34/35.34/36.76 at 1800 s. X at 1800 s = 2.5500/2.5500/2.5500/2.5457/~1.26. Note the striking feature to sanity-check against: the centre moisture is unchanged to four decimals at 30 min, while the surface has fallen from 2.55 to about 1.26 - a very sharp front, because Bi_m = 22 >> 1. Also note the herb temperature at 1800 s is 33.6-36.8 C while the air is already 41.5 C: do NOT pin the surface to the air temperature.
- PROBLEM 2/3 TABLE SHAPE (3 h window): the 3 h reporting window lies entirely inside the preheat stage, so table 3 captures the herb's thermal transient (centre 28.0 -> ~32.0 at 0.5 h -> ~40.1 at 1 h -> ~48.3 at 2 h -> ~49.8 at 3 h) and table 4 shows almost no centre drying (X_centre ~2.55 at 2 h, ~2.17 at 3 h, X_surface ~1.49 at 0.5 h, ~0.99 at 3 h). If your table 4 has a materially flat centre and a strongly graded outer region, you are consistent; if the centre has already dropped a lot by 3 h, the time units or h_m are wrong.
- ROUND-OFF AND FORMAT: all results to 4 decimal places (statement), the paper tables round to 0.5 cm / 0.1 cm columns with the last column of tables 5/6 being the 'drying end time' row in hours, and the .xlsx always in seconds (result3/4 templates start at 60, 120 s for the 60 s sampling). Also fix the grid at 0.1 cm out to 2.0 cm in the material frame (21 data columns) so the four workbooks share the same layout.
- DOMAIN REDUCTION TO JUSTIFY IN WRITING: the model is 1-D radial although L = 25 cm. The aspect ratio is L/(2R0) = 6.25, so axial (end-face) diffusion perturbs roughly the outer 2 cm at each end; the cylindrical operator (1/r)*d/dr(r*d/dr) with symmetry at r = 0 must be used (a Cartesian Laplacian gives a visibly wrong profile), and the papers should state that end effects are neglected, which makes the computed drying time slightly conservative (the real herb dries a little faster).
- FOR PROBLEM 4 ALSO: (i) the shrinkage is prescribed data from attachment 2, not something you derive - the statement says 'according to attachment 2', and the early shrinkage in that file is about 2.7x faster than the model's own mass balance predicts (model R/R0 = 0.977 vs data 0.937 at 30 min), although they agree on the asymptote (0.607 vs 0.599) and on the ~1 day timescale. (ii) If you do move the boundary, either solve in material coordinates (fixed mesh, surface = last node) or use the front-fixing map y = r/R(t), dX/dt|_xi = dX/dt|_r + (r*Rdot/R)*dX/dr, which adds a convective term and is a classic place to lose the Rdot/R factor. (iii) The appendix-4 density must be used for the dry-density scaling (rho = 760+90X), not appendix 3's - mixing them changes rho_d by ~5-10% and the predicted shrinkage accordingly. (iv) Biot numbers fall as R shrinks (Bi_h = h*R/k goes 1.90 -> 0.82 when R goes 2.0 -> 1.2 cm with k ~ 0.13-0.26), so the surface resistance becomes progressively less negligible.
- SENSITIVITY TABLE TO PUBLISH (my converged values, appendix-3 properties, fixed R = 2 cm): drying time to X < 0.15 everywhere = 16.55 h at h_m = 8e-7; 27.64 h at h_m = 4e-7; 11.08 h at h_m = 1.6e-6; 16.50 h at h = 50; 16.63 h at h = 12.5; 14.88 h at X_a = 0; 15.46 h at X_a = 0.02; 16.55 h at X_a = 0.05; 19.52 h at X_a = 0.10; and identical (16.550 h) whether the preheat/constant switch is at 9000 s or 14400 s. Problem 4 with the moving boundary: 19.72 h at h_m = 8e-7, 25.96 h at 4e-7, 16.77 h at 1.6e-6. Grid/time-step convergence is excellent (16.508 h at dt = 15 s, N = 80 vs 16.667 h at dt = 120 s, N = 20), so the residual uncertainty is the physical assumptions, not the discretisation.
- DIMENSIONLESS SUMMARY FOR THE PAPER: alpha = k/(rho*cp) = 1.69e-7 m^2/s (problem 1), R^2/alpha = 2370 s = 0.66 h; Bi_heat = hR/k = 1.39 (problem 1), 1.04 -> 2.19 (problem 2/3 as X falls), 1.90 -> 3.86 (problem 4); lumped thermal time constant rho*cp*R/(2h) = 853 s = 14.2 min, or 1149 s with the Bi/4 correction; Le = alpha/D = 233 -> 28 (problem 1), 28 -> 14 (problem 2/3), 60 -> 31 (problem 4). Le = 14-60 >> 1 is the key structural result: heat diffuses 1-2 orders of magnitude faster than moisture, so the herb is quasi-isothermal after the first 1-2 h and the drying is governed by the moisture Biot number and D(X, T).


# ===== derive:P4 (key=v2:35380abd94dfab9beab9d5469c68d20948a0937689158b69061a89c028a3d42e) =====

## governing_equations
COORDINATE SYSTEM. Axisymmetric cylinder, L=25 cm, R0=2 cm, L/2R0=6.25, so axial gradients penetrate only ~R0 (≈16% of the length) and can be neglected: use 1-D radial. The domain is the moving interval r in [0,R(t)], R(t) prescribed by Attachment 2 (2.000 -> 1.198 cm).

STEP 0 - EULERIAN (SPATIAL) FORM. Let v_s(r,t) be the radial velocity of the solid skeleton (positive outward), rho_d = dry-solid mass per unit CURRENT volume, X = kg water/kg dry solid. Dry-solid conservation: drho_d/dt + (1/r)d(r rho_d v_s)/dr = 0. Water flux relative to the solid is Fickian: j = -rho_d D(X,T) dX/dr. Therefore, using dry-solid conservation to merge accumulation+advection, the moisture and energy equations are exactly

 (M)  rho_d [dX/dt + v_s dX/dr] = (1/r) d/dr ( r rho_d D dX/dr )
 (E)  rho c_p [dT/dt + v_s dT/dr] = (1/r) d/dr ( r k dT/dr )  [+ negligible vapour-enthalpy and capacity-change terms]

STEP 1 - LANDAU / FRONT-FIXING TRANSFORM. xi = r/R(tau), tau = t, so r = xi R(tau). Chain rule, done explicitly:
  (dx/dr)_t = 1/R ,   (dxi/dt)_r = -xi Rdot/R
  (d/dt)_r = (d/dtau)_xi - (xi Rdot/R)(d/dxi)_tau
  d/dr = (1/R) d/dxi
  (1/r) d/dr ( r D d/dr ) = (1/(xi R)) (1/R) d/dxi ( xi R D (1/R) d/dxi ) = (1/(R^2 xi)) d/dxi ( xi D d/dxi )
with Rdot = dR/dt. Substituting (do not skip):

 EXACT TRANSFORMED MOISTURE EQUATION (all advection terms kept):
  rho_d dX/dtau + (rho_d/R)(v_s - xi Rdot) dX/dxi = (1/(R^2 xi)) d/dxi ( xi rho_d D dX/dxi )

 EQUIVALENT CONSERVATIVE (EULERIAN) FORM, useful for cross-checking:
  d(rho_d X)/dtau - (xi Rdot/R) d(rho_d X)/dxi + (1/(xi R)) d/dxi ( xi rho_d X v_s ) = (1/(R^2 xi)) d/dxi ( xi rho_d D dX/dxi )
 Note it contains BOTH a grid-motion term -(xi Rdot/R) d(rho_d X)/dxi AND the material term; if you write rho_d X conservatively and forget BOTH the advection and d(rho_d)/dtau you get the wrong R-scaling (the two cancel exactly).

 EXACT TRANSFORMED ENERGY EQUATION:
  rho c_p dT/dtau + (rho c_p/R)(v_s - xi Rdot) dT/dxi = (1/(R^2 xi)) d/dxi ( xi k dT/dxi )

 v_s is NOT free: kinematic consistency at the free surface requires v_s(R,t) = Rdot.

STEP 2 - CLOSURE (affine / uniform shrinkage), v_s = xi Rdot. Derivation: rho_d locally uniform => (1/r)d(r rho_d v_s)/dr = 0 => r v_s = f(t) r; imposing v_s(R)=Rdot gives f = Rdot/R, hence v_s = (Rdot/R) r = xi Rdot. The advection bracket (v_s - xi Rdot) vanishes IDENTICALLY, for any rho_d profile:

  (M-affine)  dX/dtau = (1/(R^2 xi)) d/dxi ( xi D(X,T) dX/dxi )
  (E-affine)  rho c_p dT/dtau = (1/(R^2 xi)) d/dxi ( xi k(X) dT/dxi )

(For (E) the exact balance per unit DRY mass gives one extra source rho_d T d[(1+X)c_p]/dtau ~ O(1%) - drop it.)
KEY CONSEQUENCE: in the recommended frame Rdot NEVER APPEARS. Only R(tau) enters, through 1/R^2 and through Biot numbers. So the spurious-oscillation problem for dR/dt disappears by construction.

STEP 3 - REDUCTION CHECK (Rdot = 0). Put R = R0 = const; then xi = r/R0, d/dxi = R0 d/dr, and
  (1/(R0^2 xi)) d/dxi( xi D d/dxi X ) = (1/(R0 xi)) d/dr( xi R0 D d/dr X ) = (1/r) d/dr( r D dX/dr ), and d/dtau -> d/dt.
So (M-affine) and (E-affine) reduce EXACTLY to the fixed-domain cylindrical equations. Verified numerically as well: setting R = const in the solver reproduces the classical infinite-cylinder series solution to 3-4 significant figures.

CROSS-CHECK OF THE CLOSURE FROM THE DATA. Volume loss of the body over the whole record = 3.1416e-4 - 1.1272e-4 = 2.014e-4 m^3; volume of water actually removed = (0.2233-0.0131) kg / 1000 = 2.102e-4 m^3. Ratio = 0.958, i.e. the body's volume loss is 92-96% of the water volume removed -> near-ideal, volume-additive, affine shrinkage. This is the quantitative justification for v_s = xi Rdot.

WHY NOT THE ALTERNATIVES.
(ii) ALE / moving mesh: at the continuous level it is identical to (M)/(E) in the material frame; it costs mesh-velocity bookkeeping, a geometric conservation law, and it keeps a stiff explicit mesh-motion term. It buys nothing here because the shrinkage is affine and R(t) is known a priori.
(i) Naive front-fixing WITHOUT the material advection (drop (xi Rdot/R) dX/dxi): WRONG. The apparent grid Peclet number Pe_shrink = |Rdot| R / D is 13-31 at t = 0 (Rdot(0) = -8.39e-7 m/s, R = 0.02 m, D = 5.5e-10..1.3e-9 m^2/s) and still ~0.2 at 6 h. Shrinkage is NOT a small perturbation; it must be handled exactly, as (M-affine) does.
(iii) Dry-solid-based material coordinate m = integral_0^r rho_d r' dr': rigorously equivalent, and the domain [0, M_d] is genuinely immovable. But it requires the shrinkage closure anyway to map m back to a physical/material position for reporting at "distance from centre", and it introduces the metric r(m,t) into every flux. It is the same model, more algebra.
(iv) Ideal-shrinkage closure (V = V_drysolid + V_water) used as the CLOSURE for v_s rather than (M-affine): over-determined. It PREDICTS R rather than using the data, and it over-shrinks: it predicts R_final = 1.101 cm (at X=0.05) or 1.151 cm (at X=0.15) versus the measured 1.198 cm, i.e. 4-8% too much shrinkage. Use it only as a sanity check.

RECOMMENDED MODEL = (M-affine) + (E-affine) + the BCs below.

## boundary_conditions
At xi = 0 (axis, r = 0) - symmetry / no-flux:
  dX/dxi |_{xi=0} = 0 ,   dT/dxi |_{xi=0} = 0 .
Units: both sides are (kg/kg) or K per unit xi (dimensionless), fine. The operator is regular at xi=0: by L'Hopital, (1/(R^2 xi)) d/dxi(xi D dX/dxi) -> (2D/R^2) d2X/dxi2. In a cell-centred finite-volume scheme this condition is automatic (the face at xi=1/2 has zero area), so no special treatment is needed.

At xi = 1 (the moving surface r = R(t)) - convective (Robin) conditions.
Careful with d/dr = (1/R) d/dxi.

MASS. Outward water flux at the surface must equal the convective flux:
  -D dX/dr |_{r=R} = h_m ( X(1,tau) - X_f(tau) )
  =>  -(D/R) dX/dxi |_{xi=1} = h_m ( X(1,tau) - X_f(tau) )
  =>   dX/dxi |_{xi=1} = -Bi_m(tau) [ X(1,tau) - X_f(tau) ] ,   Bi_m(tau) = h_m R(tau) / D(X,T) .
Units check: LHS of the first line is (m^2/s)(kg/kg)/m = m/s * (kg/kg); RHS is (m/s)(kg/kg). CONSISTENT ONLY with this convention, i.e. -D dX/dr = h_m (X_s - X_f) with X in kg/kg. (Writing -rho_d D dX/dr = h_m rho_d (X_s-X_f) is identical because rho_d cancels. Writing -rho_d D dX/dr = h_m rho_air (X_s-X_f) makes the flux ~230x too small and the herb never dries inside 72 h - do not do this.)
Sign check: X is maximum at the centre and minimum at the surface, so dX/dxi < 0 at xi=1; the RHS is -Bi_m (X-X_f) < 0 when X > X_f. Consistent.

HEAT. Similarly (k in W/(m K), h in W/(m^2 K)):
  -k dT/dr |_{r=R} = h ( T(1,tau) - T_f(tau) )
  =>   dT/dxi |_{xi=1} = -Bi_h(tau) [ T(1,tau) - T_f(tau) ] ,   Bi_h(tau) = h R(tau) / k(X) .
Sign check: at early times T_herb = 28 C < T_f = 41..50 C, so dT/dxi > 0 at the surface, and -Bi_h(T-T_f) > 0. Consistent.

NOTE. Neither BC contains Rdot. Both contain R(tau) only through Bi_m, Bi_h. If you implement the Robin condition directly on r (ALE or a fixed-physical-r mesh) you must remember the (1/R) factor; if you impose -D dX/dr = h_m (X_s - X_f) on the xi-grid using dX/dxi you under- (or over-) scale the surface flux by a factor R.
The ambient functions are T_f(t), X_f(t) taken from Attachment 1 by linear interpolation on its 60 s grid for 0 <= t <= 14400 s, and held at T_f = 50 C, X_f = 0.05 for t > 14400 s.

## initial_conditions
Uniform initial state at t = 0 (start of Problem 4's drying, i.e. the preheat stage is INCLUDED, so the IC is the as-loaded herb):
  X(xi,0) = X0 = 2.55 kg/kg  (dry basis), for all xi in [0,1]
  T(xi,0) = T0 = 28 degC,
  R(0) = R0 = 0.02 m  (0.02 m is the given 2 cm; Attachment 2's first row is exactly 2.0 cm).
Because xi is a material coordinate under the affine closure, this uniform IC is consistent with the affine assumption (a uniform field stays uniform on a uniformly shrinking body).
No boundary-layer initial condition is needed. The only "start-up" is the thermal transient: T_f jumps from 28 C to 50 C over the first 4 h (Attachment 1), and the thermal time constant is ~1.4 h, so T is quasi-steady after ~2 h while X has barely moved.

## assumptions
- 1-D RADIAL SYMMETRY: no axial and no angular gradients. Justified by L/(2R0) = 25/4 = 6.25; end effects penetrate ~R0 from each cap, i.e. ~16% of the length, and the reported results are at the mid-height.
- AFFINE (uniform, ideal, 'material') SHRINKAGE: every material point retains xi = r/R(tau), equivalently the solid velocity is v_s = xi*Rdot. This is the load-bearing assumption. It is supported by: (a) dry-solid conservation plus local uniformity of rho_d; (b) the measured volume loss of the body is 92-96% of the volume of water removed; (c) it is the only closure compatible with BOTH a prescribed R(t) and dry-mass conservation. Error vs the stricter volume-additive model is 4-8% in the final radius.
- R(t) IS PRESCRIBED DATA, not a predicted unknown: R(tau) is taken from Attachment 2 by shape-preserving interpolation, and it is R itself (never Rdot) that enters the transformed PDE. The empirical rho = 760 + 90X of Appendix 4 is NOT used to predict R.
- The dry solid is conserved (no solid leaves the body) and the solid skeleton deforms only by the affine scaling: M_d = pi*L*rho_d0*R0^2 = 0.0876 kg = const.
- LOCAL THERMODYNAMIC EQUILIBRIUM at the surface, with the ambient herb moisture X_f(t) (Attachment 1, kg/kg) as the driving force, and no internal vapour-pressure/partial-pressure formulation.
- FICKIAN effective diffusion with the dry-basis diffusivity D = 4.2e-4 exp(-0.30X) exp(-3850/T), T in KELVIN. No capillary/gravity convection of free water. No thermodiffusion (Soret/Luikov coupling) - no thermogradient coefficient is supplied, and Lu = D/alpha = 0.017-0.032 shows the coupling would be weak anyway.
- Properties rho(X)=760+90X, c_p(X)=1850+2150X/(1+X), k(X)=0.12+0.20X/(1+X) are evaluated quasi-locally at the current X and T (instantaneous, no hysteresis, no history).
- In the energy equation, the enthalpy carried by the diffusing vapour and the term rho_d*T*d[(1+X)c_p]/dtau are neglected (latter is ~1% of rho*c_p*dT/dtau).
- Constant transfer coefficients h = 25 W/(m^2 K) and h_m = 8e-7 m/s throughout both stages (the problem gives no stage dependence).
- The cylinder length L is held fixed (only the radius shrinks). Under isotropic affine shrinkage L would shrink by the same factor, but since there are no axial gradients the radial solution in xi is identical; only absolute surface areas would change, and those enter only through the (small) external Biot resistances.
- Negligible radiative exchange and negligible heat conduction to the supporting tray; the herb exchanges only with the bulk air.

## dimensionless_numbers
All numbers below use Appendix-4 properties and h = 25 W/(m^2 K), h_m = 8e-7 m/s; states are quoted at the operating temperature T = 323.15 K (50 C) reached after ~2 h, and at the initial state (T = 301.15 K).

DIFFUSIVITY / DIFFUSIVITY CONTRAST
  D_P4 = 4.2e-4 exp(-0.30X) exp(-3850/T): 5.48e-10 m^2/s at (X=2.55, T=301 K); 1.31e-9 at (2.55, 323 K); 2.69e-9 at (0.15, 323 K); 2.77e-9 at (0.05, 323 K). Range over the whole process: 5.5e-10 .. 2.8e-9 m^2/s (factor 5).
  (Contrast: Appendix 3 gives 2.14e-9 .. 1.57e-8 m^2/s, i.e. 4-6x larger - Problem 4 dries slower for the same state.)
  alpha = k/(rho c_p): 7.85e-8 m^2/s (X=2.55); 8.68e-8 (X=0.05) - essentially constant, alpha ~ 8e-8 m^2/s.

  LUIKOV NUMBER  Lu = D/alpha = 0.0166 (X=2.55) .. 0.0319 (X=0.05). Lu << 1 => heat diffuses 30-60x faster than moisture => temperature is QUASI-STEADY on the moisture time scale; the two fields are only weakly coupled through the D(X,T), k(X) dependence.

  HEAT BIOT   Bi_h = h R/k = 25*0.020/0.2637 = 1.90 (start) ; 25*0.0121/0.1461 = 2.07 (end). Bi_h ~ 2 => a real radial temperature gradient exists (lumped analysis invalid), but the thermal transient is over in ~1.4 h.
  MASS BIOT   Bi_m = h_m R/D = 8e-7*0.020/1.307e-9 = 12.2 (start) ; 8e-7*0.0121/2.685e-9 = 3.61 (X=0.15) ; 3.46 (X=0.05). Bi_m = 3.5..12 >> 1 => INTERNAL-DIFFUSION CONTROLLED (falling-rate drying); the surface concentration sits within ~1/Bi_m of X_f.
  (If T = 301 K is used for D at t=0 the value is Bi_m = 29; use the operating value 12.)

  SHRINKAGE PECLET  Pe_shrink = |Rdot| R / D  (the apparent grid advection in the Eulerian front-fixing frame). Rdot(0) = -8.39e-7 m/s (from PCHIP), R = 0.02 m:
    t = 0:   Pe = 30.8 with D(301 K) = 5.48e-10 ; Pe = 12.8 with D(323 K)
    t = 6 h: Pe = 3.98e-8 * 0.01374 / 2.7e-9 = 0.20
  Pe_shrink >> 1 early => shrinkage is a FIRST-ORDER effect, not a perturbation; you must either keep the advection term or (better) work in the material frame, where it cancels.

  RATIOS / OTHER
    tau_moisture/tau_thermal = 1/Lu = 31..60.
    Shrinkage: R_end/R_0 = 0.599, V_end/V_0 = 0.359 (64% volume loss), area ratio 0.359.
    Material-frame acceleration factor: |int_0^T (R0/R)^2 dt| / T = 1.6e5 s / 7.1e4 s = 2.25 at the 19.75 h drying time; equivalently the fixed-radius drying time (39.3 h) is 1.99x the shrinking one.
    Deficit of the empirical density law vs mass conservation: rho_d = (760+90X)/(1+X) gives 728.1 kg/m^3 at X=0.05, while M_d/(pi L R_end^2) requires 776.8 kg/m^3 -> a 6.3% inconsistency (see pitfalls).

## characteristic_times
THERMAL (temperature equilibration across the radius):
  tau_th = R^2/alpha = 4.0e-4/7.85e-8 = 5.10e3 s = 1.42 h at R = R0, X = 2.55.
  = 4.6e3 s = 1.28 h at X = 0.05, R = R0.
  = 1.44e-4/8.68e-8 = 1.65e3 s = 0.46 h at R = 0.01198 m.
  => T reaches quasi-steady in ~1.5-2 h, i.e. under 10% of the drying time. The temperature field can be advanced with a much larger time step than the moisture field, or even solved quasi-statically.

MOISTURE (diffusion across the radius):
  tau_m = R^2/D = 3.06e5 s = 85 h at (X=2.55, T=323 K, R=R0). This is LONGER than the 3-day window, which is why the herb is far from dry at early times.
  = 1.44e-4/2.77e-9 = 5.2e4 s = 14.4 h at the final state (X=0.05, R=0.01198 m).
  Note the 6x collapse of tau_m: both D rising (2.1x) and R^2 falling (2.8x) push the same way. This is exactly the shrinkage acceleration.

SHRINKAGE TIME:
  R0/|Rdot(0)| = 0.02/8.39e-7 = 2.38e4 s = 6.6 h (initial e-folding of the radius).
  Observed lifetime of the shrinkage = 2.592e5 s = 72 h (R plateau 1.20 cm after ~36 h).

MATERIAL-FRAME EFFECTIVE TIME (the only time that matters for drying):
  Fo* = int_0^t D/R^2 dt' = 0.043 (3 h), 0.130 (6 h), 0.412 (12 h), 1.185 (24 h), 2.84 (48 h), 4.51 (72 h).
  Fo* ~ 0.8-0.9 at the computed drying time.

COMPUTED DRYING TIME (X < 0.15 everywhere, i.e. at the centre):
  WITH shrinkage, affine material frame:  19.75 h  (7.11e4 s)   <-- recommended answer
  WITH R FIXED at 2 cm (no shrinkage):    39.30 h  (1.41e5 s)   (shrinkage halves the time)
  Grid/time-step converged: N=400 and dt/2 change these by < 0.3% (19.70-19.75 h).

WATER / ENERGY BUDGET:
  M_d = 0.0876 kg dry solid (from rho_d0 = 278.7 kg/m^3). Initial water = 0.2233 kg; initial moist mass = 0.311 kg.
  Water to remove to reach X = 0.15 everywhere = 0.0876*(2.55-0.15) = 0.2102 kg.
  Latent heat at ~50 C, h_fg ~ 2.38e6 J/kg => 5.0e5 J. Mean required power over 19.75 h = 7.0 W.
  Available convective power h*A*(T_f - T_s), A ~ 2*pi*R*L + 2*pi*R^2 = 0.023 m^2, at dT = 20 K: 11.5 W.
  => the process is MASS-TRANSFER limited, not heat limited (a useful consistency statement in the paper).

## recommended_numerics
RECOMMENDED SCHEME: cell-centred finite volume in xi on [0,1], backward Euler in time with Picard iteration on the coefficients. (An ALE/moving mesh buys nothing: the transformed equations already have a fixed domain and no metric advection.)

GRID. N = 200 uniform cells, h = 1/N, cell centres xi_i = (i-1/2)h, i = 1..N. Cell "volume" V_i = (xi_{i+1/2}^2 - xi_{i-1/2}^2)/2 (this is the integral of xi dxi, which is what the cylindrical operator demands). Grid-converged: N = 40 vs 200 vs 400 agree to 3-4 digits in my verification runs; N = 200 is ample.

SPATIAL DISCRETIZATION (flux form). Write V_i dX_i/dtau = (1/R^2)[ xi_{i+1/2} F_{i+1/2} - xi_{i-1/2} F_{i-1/2} ] with F = D dX/dxi and face diffusivities D_{i+1/2} = (D_i + D_{i+1})/2.
  - Inner face xi_{1/2} = 0: area 0, so the symmetry condition is imposed automatically. No special formula needed.
  - Outer face xi_{N+1/2} = 1: Robin condition implemented as a series resistance across the half-cell (this is the correct discrete form of dX/dxi|_1 = -Bi_m (X_s - X_f)):
      g_D = 2 D_N / h ,   g_H = h_m R ,   K_b = g_D g_H / (g_D + g_H)
      boundary flux contribution = K_b (X_f - X_N)
    which is equivalent to defining the surface value X_s = (g_D X_N + g_H X_f)/(g_D + g_H) and writing the flux as g_D (X_s - X_N).
  - Same for T with k in place of D, h in place of h_m, and rho*c_p as the CAPACITY (see below).
  - Material points for reporting: xi = 0, 0.25, 0.5, 0.75, 1 <- the "距离药材中心 0, 0.5, 1, 1.5, 2 cm" columns; interpolate cell-centre values to these xi (linear is enough; the profile is smooth), and take the last column as X_N (equivalently X_s).

TIME INTEGRATION. Backward Euler is unconditionally stable and is what you want. Explicit stepping would need dt < h^2 R^2/(2D) = (0.005)^2*(0.02)^2/(2*1.3e-9) ~ 1.3 s at t=0 - about 100x more steps.
  Use dt = 20 s for t < 2 h, 60 s for 2 h <= t < 12 h, 180 s for t >= 12 h. Halving every dt changes the drying time by < 0.3%.
  Nonlinearity: at each step do 2-4 PICARD iterations, recomputing D, k, rho, c_p from the CURRENT iterate and solving the tridiagonal system each time. CRITICAL: keep the old state X^n fixed inside the Picard loop and iterate only the coefficients - if you write Xn = solve(X) and then feed Xn back as the state, you silently take 4 time steps per step and the drying time comes out 4x too short.
  Use the tridiagonal (Thomas) algorithm; the system is an M-matrix (row sum = V_i/dt > 0) so no pivoting is needed. For the y = [X;T] system a nested-function file is cleaner than pdepe (pdepe's ic/bc callback signatures are a common source of silent failures here).

VALIDATION (do this before trusting any number):
  1) Set R = const and X_f = 0.05, D = const, and compare with the analytic infinite-cylinder series
     (C - C_s)/(C_0 - C_s) = sum 2 J_0(mu_n xi)/(mu_n J_1(mu_n)) exp(-mu_n^2 Fo), mu_n = roots of J_0.
     My implementation matches to 3-4 significant figures at Fo = 0.03, 0.09, 0.27, 0.75.
  2) Setting R = const must reproduce the fixed-domain answer exactly (it is the Rdot = 0 reduction of the same code).
  3) Conservation: monitor M_w = sum_i V_i X_i. With X_f = 0 it must be non-increasing and its rate must equal the surface flux -D dX/dxi|_1 / R times the surface "area" 1.

ALGORITHM SKETCH
  precompute pchip(tR,Rcm/100) as ppR; Tf(t), Xf(t) by interp1 on Attachment 1 with the 14400 s switch.
  for n = 1:nt
    R  = ppval(ppR, min(t+dt, 259200));            % NOTE: no dR/dt needed anywhere
    for it = 1:4
      D  = 4.2e-4*exp(-0.30*Xg).*exp(-3850./(Tg+273.15));   % KELVIN
      kk = 0.12+0.20*Xg./(1+Xg);  rho = 760+90*Xg;  cp = 1850+2150*Xg./(1+Xg);
      Xn = thomas(Xold, V,         D , hm*R, Xf(t+dt), dt, R, h);
      Tn = thomas(Told, V.*rho.*cp, kk, h*R , Tf(t+dt), dt, R, h);
      Xg = Xn; Tg = Tn;
    end
    Xold = Xn; Told = Tn; t = t + dt;
  end

## expected_magnitudes
Computed with the recommended model (affine material frame, N=200, grid- and step-converged). Columns are material points xi = 0, 0.25, 0.5, 0.75, 1 (initial radii 0, 0.5, 1.0, 1.5, 2.0 cm; xi = 1 is the moving surface = 药材表面).

  t[h]    xi=0     0.25     0.5      0.75     surface   mean     T_c      T_s     R[cm]
   1.0   2.5500   2.5500   2.5499   2.4552   0.9426   2.3661   39.1 C   43.2 C   1.794
   2.0   2.5500   2.5487   2.4968   1.9587   0.8011   2.1921   48.1     49.0     1.625
   3.0   2.5410   2.5080   2.2709   1.5755   0.6802   2.0078   49.8     50.0     1.552
   6.0   2.0173   1.8651   1.4621   0.9457   0.4574   1.3864   50.0     50.0     1.374
   9.0   1.1702   1.0872   0.8710   0.5915   0.3149   0.8283   50.0     50.0     1.291
  12.0   0.6323   0.5953   0.4947   0.3555   0.2071   0.4692   50.0     50.0     1.248
  18.0   0.1985   0.1902   0.1671   0.1333   0.0947   0.1601   50.0     50.0     1.214
  24.0   0.0866   0.0847   0.0791   0.0709   0.0614   0.0774   50.0     50.0     1.204
  36.0   0.0522   0.0521   0.0517   0.0512   0.0507   0.0516   50.0     50.0     1.200
  48.0   0.0501   0.0501   0.0501   0.0501   0.0500   0.0501   50.0     50.0     1.200
  72.0   0.0500   0.0500   0.0500   0.0500   0.0500   0.0500   50.0     50.0     1.198

HEADLINE ANSWER (Problem 4): ALL locations reach X < 0.15 kg/kg at t = 19.75 h (~20 h, 7.1e4 s). At that instant X_centre = 0.149, X_surface = 0.080.
For comparison, holding R = 2 cm (no shrinkage) gives 39.30 h. The shrinkage therefore roughly HALVES the drying time.

SANITY CHECKS ON THE MAGNITUDES
 - The surface pins to within ~1/Bi_m of X_f within ~0.6 h (tau_surface ~ (R/Bi_m)^2/D ~ 2e3 s), then follows X_f. Surface X = 0.94 (1 h), 0.68 (3 h), 0.46 (6 h), 0.31 (9 h), 0.21 (12 h), 0.095 (18 h), 0.061 (24 h), 0.050 (>= 36 h).
 - The centre holds X_0 = 2.55 for ~2 h (Fo*(2 h) ~ 0.02) then collapses: 2.54, 2.02, 1.17, 0.63, 0.20, 0.087, 0.052 at 3/6/9/12/18/24/36 h.
 - X_mean: 2.19 (2 h), 1.39 (6 h), 0.47 (12 h), 0.077 (24 h), 0.052 (36 h). Reaching X_f = 0.05 by ~36-48 h.
 - CONSISTENCY WITH ATTACHMENT 2: inverting the shrinkage under ideal volume additivity, R(t)^2 = 1.3839e-4 + 1.0259e-4*X_mean (SI), gives X_mean = 2.07 (0.5 h), 1.79 (1 h), 1.00 (3 h), 0.49 (6 h), 0.17 (12 h), 0.064 (24 h), ~0.05 (>= 36 h). So the model and the radius data agree at 24 h and beyond and at t = 0, and disagree by a factor ~2-3 in the middle of the process (model slower at 6 h: 1.39 vs 0.49). Report this honestly: the empirical rho(X) and the tabulated R(t) are not fully mutually consistent. The radius plateau at 1.200 cm from 36 h onward DOES confirm that the herb is essentially dry by 36 h, which supports the order of magnitude of the answer.
 - THRESHOLD SENSITIVITY of the answer: if the criterion is applied to X_mean instead of "everywhere", the time drops to ~13 h. If the mass-BC is made 10x stronger (Bi_m 10x), it drops to 14.6 h. If it is made ~300x weaker (the rho_air convention), the herb never dries within 72 h. So the answer is dominated by the mass-BC convention, NOT by the shrinkage modelling detail.
 - With an IMPLICIT/explicit ALE implementation that keeps the Eulerian advection term, you should reproduce the same curve; if your ALE result is much faster or much slower, you have double-counted (or dropped) the advection term.

## pitfalls
- DROPPING THE ADVECTION TERM IN THE EULERIAN/ALE FRONT-FIXED FORM. Pe_shrink = |Rdot|R/D = 13-31 at t=0 - shrinkage is a first-order effect. Either keep (xi Rdot/R) dX/dxi, or (recommended) work in the material frame where it cancels exactly against v_s dX/dr.
- DOUBLE COUNTING: keeping BOTH the grid term -(xi Rdot/R) dX/dxi AND the material term (v_s/R) dX/dxi when they should cancel. Under affine shrinkage they cancel identically; keeping both roughly doubles the apparent transport.
- CONSERVATIVE FORM TRAP. If you write d(rho_d X)/dtau - (xi Rdot/R) d(rho_d X)/dxi + ... and drop the d(rho_d)/dtau term, you get the wrong R scaling, because rho_d*R^2 = const along a material element, so d(rho_d)/dtau = -2 rho_d Rdot/R exactly cancels the extra 2 Rdot rho_d X / R that the conservative form produces.
- NATURAL CUBIC SPLINE FOR R(t). With spline(tR,R) the derivative dR/dt becomes POSITIVE (unphysical expansion) at 1408 of 4321 sampled instants, first at t = 79500 s (R = 1.206 cm), because the table flattens to 0.001-0.005 cm steps for 50 h. Max |R_spline - R_pchip| = 4.6e-3 cm. Use PCHIP (monotone piecewise cubic Hermite, Fritsch-Carlson) instead: its derivative is <= 0 everywhere, Rdot(0) = -8.39e-7 m/s, min = -8.39e-7, max = 0.
- FINITE-DIFFERENCING THE RAW TABLE FOR Rdot. The 1800 s spacing is slightly irregular, so a central difference at t = 1800 s gives -5.72e-7 m/s versus the smooth-interpolant value -5.41e-7 m/s (6% error), and mid-table differences even flip sign in the flat tail. If you need Rdot, differentiate the PCHIP piecewise polynomial analytically (ppval of a coefficient-differentiated pp struct).
- BEST OF ALL: in the recommended affine material-frame formulation YOU NEVER NEED Rdot. Only R enters, through 1/R^2 and through Bi_m = h_m R/D, Bi_h = hR/k. Build the model so that this is true and the oscillation question disappears.
- FORGETTING (1/R) IN THE SURFACE CONDITION. On the xi grid, dX/dr|_R = (1/R) dX/dxi|_1. Using dX/dxi directly mis-scales the surface flux by a factor R (which itself changes by 40% over the run). The correct form is dX/dxi|_1 = -Bi_m [X(1)-X_f].
- WRONG MASS-BC UNITS. Only -D dX/dr = h_m (X_s - X_f) is dimensionally consistent with the given h_m = 8e-7 m/s and X in kg/kg. Multiplying the right-hand side by rho_d is harmless (it cancels), but using rho_air instead makes the surface flux ~230x too small and the herb never dries within 72 h. Test the convention once with a hand estimate: the observed average water removal rate is ~8.5e-7 kg/s over ~0.023 m^2, i.e. ~3.7e-5 kg/(m^2 s), which the rho_d-including convention reproduces and the rho_air convention cannot.
- CELSIUS IN THE DIFFUSIVITY. D = 4.2e-4 exp(-0.30X) exp(-3850/T) requires T in KELVIN. Using 28 instead of 301.15 gives exp(-137) ~ 1e-60 and the solver appears to freeze (the herb never dries and X stays at 2.55 to 5 decimal places - a very recognisable symptom).
- MISSING CAPACITY IN THE ENERGY EQUATION. The moisture equation has capacity 1 (in the material frame, dX/dtau), but the energy equation needs rho*c_p as the capacity. Solving the T equation with capacity 1 makes the herb heat up ~3400x too fast.
- USING A LAGRANGIAN 'PICARD' LOOP THAT ACTUALLY ADVANCES TIME. Iterating X = solve(X, coeffs(X)) four times takes four time steps of dt, not four coefficient iterations. Symptom: the drying time comes out almost exactly 4x too short (9.98 h instead of 39.3 h in my own first attempt). Keep the old state fixed inside the loop.
- REPORTING AT FIXED PHYSICAL RADII. R(t) falls below 2 cm within the first timestep (R(1800 s) = 1.873 cm), so the column labelled '2 cm' leaves the body almost immediately. The five columns 0, 0.5, 1, 1.5, 2 cm must be MATERIAL points, i.e. xi = 0, 0.25, 0.5, 0.75, 1; this is exactly why the template calls the last column 药材表面 (the material point initially at r0 = R0 remains the surface forever under affine shrinkage).
- EVALUATING AT xi EXACTLY 0 OR 1 BY EXTRAPOLATION. Cell centres are at xi = (i-1/2)h, so interp1(xm,X,0) returns NaN. Use X(1) for the centre and X(N) for the surface (or fit/interpolate inward).
- EXTRAPOLATING R(t) BEYOND 259200 s. The tabulated record ends there with R = 1.198 cm and Rdot ~ 0. Clamp (hold R = 1.198 cm), do not linearly extrapolate, and do not let a spline run past the last data point.
- TRYING TO DERIVE R(t) FROM rho = 760 + 90X. Under dry-mass conservation they are inconsistent: the formula caps rho_d at (760+90X)/(1+X) <= 760 kg/m^3, while M_d/(pi L R_end^2) = 776.8 kg/m^3 at the measured R_end (6.3% mismatch), and mid-process the local-rho closure implies a solid velocity that exceeds the surface velocity by several fold (a kinematic contradiction, since v_s(R) must equal Rdot). Use the tabulated R(t); use rho(X) only in rho*c_p and (harmlessly) in the mass equation where it cancels.
- FORGETTING THE THERMODIFFUSION CHECK. If you are tempted to build a coupled Luikov system with a thermogradient coefficient delta, note that none is given, and Lu = D/alpha = 0.017-0.032 shows the coupling is weak; adding an invented delta will change the answer arbitrarily.
- CHECKING THE 0.15 CRITERION AT THE WRONG POINT. The specification is 各处 (everywhere), so the binding point is the CENTRE, which lags the mean by a large margin (at the dry time, X_centre = 0.149 while X_mean = 0.16 and X_surface = 0.080). Using the mean shortens the reported time by ~30%.
- TRUSTING THE FIRST WORKING CODE. Validate against the analytic infinite-cylinder series with constant D and R = const before believing any shrinkage result; a grid/BC bug can easily hide inside a plausible-looking monotone profile (in this session a row/column broadcasting bug silently turned an Nx1 capacity vector into an NxN matrix and froze the solution).
