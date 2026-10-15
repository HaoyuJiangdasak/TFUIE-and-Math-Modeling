"""Physics-informed neural network for Question 1.

【交叉验证模型——请老师检查】
The PINN is trained only from the governing equations and initial/boundary
conditions.  The MATLAB CN/FVM solution is loaded only after training to
compute independent numerical cross-validation metrics.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.nn import functional as F


torch.set_default_dtype(torch.float64)


class MLP(nn.Module):
    def __init__(self, width: int = 48, depth: int = 4) -> None:
        super().__init__()
        layers: list[nn.Module] = [nn.Linear(2, width), nn.Tanh()]
        for _ in range(depth - 1):
            layers.extend([nn.Linear(width, width), nn.Tanh()])
        layers.append(nn.Linear(width, 1))
        self.network = nn.Sequential(*layers)
        self.apply(self._initialize)

    @staticmethod
    def _initialize(module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.xavier_normal_(module.weight)
            nn.init.zeros_(module.bias)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)


def boundary_value(t_seconds: torch.Tensor, row) -> torch.Tensor:
    if isinstance(row, dict):
        times = row["time"]
        values = row["value"]
        flat_time = t_seconds.reshape(-1)
        right = torch.searchsorted(times, flat_time, right=True).clamp(1, len(times) - 1)
        left = right - 1
        weight = (flat_time - times[left]) / (times[right] - times[left])
        interpolated = values[left] + weight * (values[right] - values[left])
        return interpolated.reshape_as(t_seconds)
    y0 = float(row["y0"])
    y_steady = float(row["ySteady"])
    tau = float(row["tau_s"])
    beta = float(row["beta"])
    return y0 + (y_steady - y0) * (1.0 - torch.exp(-((t_seconds / tau) ** beta)))


def temperature_field(model: nn.Module, x: torch.Tensor, tau: torch.Tensor) -> torch.Tensor:
    raw = model(torch.cat([x, tau], dim=1))
    return tau * torch.sigmoid(raw)


def moisture_field(model: nn.Module, x: torch.Tensor, tau: torch.Tensor) -> torch.Tensor:
    raw = model(torch.cat([x, tau], dim=1))
    return torch.exp(-tau * F.softplus(raw))


def derivative(output: torch.Tensor, input_: torch.Tensor) -> torch.Tensor:
    return torch.autograd.grad(
        output,
        input_,
        grad_outputs=torch.ones_like(output),
        create_graph=True,
        retain_graph=True,
    )[0]


def make_training_points(n_interior: int, n_boundary: int, seed: int) -> dict[str, torch.Tensor]:
    engine = torch.quasirandom.SobolEngine(2, scramble=True, seed=seed)
    interior = engine.draw(n_interior)
    eps = 2.0e-3
    x = (eps + (1.0 - eps) * interior[:, 0:1]).requires_grad_(True)
    tau = (1.0e-4 + (1.0 - 1.0e-4) * interior[:, 1:2]).requires_grad_(True)
    tau_boundary = torch.linspace(1.0e-4, 1.0, n_boundary).reshape(-1, 1).requires_grad_(True)
    center = torch.zeros_like(tau_boundary).requires_grad_(True)
    surface = torch.ones_like(tau_boundary).requires_grad_(True)
    return {
        "x": x,
        "tau": tau,
        "tau_boundary": tau_boundary,
        "center": center,
        "surface": surface,
    }


def temperature_loss(
    model: nn.Module,
    points: dict[str, torch.Tensor],
    fit_row: pd.Series,
) -> tuple[torch.Tensor, dict[str, float]]:
    radius = 0.02
    alpha = 0.36 / (820.0 * 2600.0)
    final_time = 1800.0
    biot = 25.0 * radius / 0.36
    temperature_scale = 25.0
    fourier = alpha * final_time / radius**2

    x, tau = points["x"], points["tau"]
    theta = temperature_field(model, x, tau)
    theta_tau = derivative(theta, tau)
    theta_x = derivative(theta, x)
    theta_xx = derivative(theta_x, x)
    residual = theta_tau - fourier * (theta_xx + theta_x / x)

    tau_b = points["tau_boundary"]
    center = points["center"]
    surface = points["surface"]
    theta_center = temperature_field(model, center, tau_b)
    center_gradient = derivative(theta_center, center)
    theta_surface = temperature_field(model, surface, tau_b)
    surface_gradient = derivative(theta_surface, surface)
    furnace = boundary_value(tau_b * final_time, fit_row)
    furnace_theta = (furnace - 28.0) / temperature_scale
    surface_residual = surface_gradient - biot * (furnace_theta - theta_surface)

    pde = torch.mean(residual**2)
    bc_center = torch.mean(center_gradient**2)
    bc_surface = torch.mean(surface_residual**2)
    loss = pde + 5.0 * bc_center + 10.0 * bc_surface
    return loss, {
        "pde": float(pde.detach()),
        "center": float(bc_center.detach()),
        "surface": float(bc_surface.detach()),
    }


def moisture_loss(
    model: nn.Module,
    points: dict[str, torch.Tensor],
    fit_row: pd.Series,
) -> tuple[torch.Tensor, dict[str, float]]:
    radius = 0.02
    final_time = 1800.0
    transfer = 8.0e-7
    initial_moisture = 2.55

    x, tau = points["x"], points["tau"]
    u = moisture_field(model, x, tau)
    u_tau = derivative(u, tau)
    u_x = derivative(u, x)
    moisture = initial_moisture * u
    diffusivity = 7.0e-9 * torch.exp(-0.89 / torch.clamp(moisture, min=1.0e-8))
    radial_flux = x * diffusivity * u_x
    radial_flux_x = derivative(radial_flux, x)
    residual = u_tau - final_time / radius**2 * radial_flux_x / x

    tau_b = points["tau_boundary"]
    center = points["center"]
    surface = points["surface"]
    u_center = moisture_field(model, center, tau_b)
    center_gradient = derivative(u_center, center)
    u_surface = moisture_field(model, surface, tau_b)
    surface_gradient = derivative(u_surface, surface)
    surface_moisture = initial_moisture * u_surface
    surface_diffusivity = 7.0e-9 * torch.exp(-0.89 / surface_moisture)
    furnace = boundary_value(tau_b * final_time, fit_row)
    surface_residual = (
        surface_diffusivity / (transfer * radius) * surface_gradient
        + u_surface
        - furnace / initial_moisture
    )

    pde = torch.mean(residual**2)
    bc_center = torch.mean(center_gradient**2)
    bc_surface = torch.mean(surface_residual**2)
    loss = pde + 5.0 * bc_center + 20.0 * bc_surface
    return loss, {
        "pde": float(pde.detach()),
        "center": float(bc_center.detach()),
        "surface": float(bc_surface.detach()),
    }


def train_model(
    model: nn.Module,
    loss_function,
    points: dict[str, torch.Tensor],
    fit_row: pd.Series,
    adam_epochs: int,
    lbfgs_iterations: int,
    label: str,
) -> tuple[list[float], dict[str, float]]:
    history: list[float] = []
    optimizer = torch.optim.Adam(model.parameters(), lr=1.0e-3)
    last_terms: dict[str, float] = {}
    for epoch in range(1, adam_epochs + 1):
        optimizer.zero_grad(set_to_none=True)
        loss, last_terms = loss_function(model, points, fit_row)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=100.0)
        optimizer.step()
        history.append(float(loss.detach()))
        if epoch == 1 or epoch % 250 == 0:
            print(f"{label} Adam {epoch:5d}: loss={history[-1]:.6e} terms={last_terms}", flush=True)

    optimizer_lbfgs = torch.optim.LBFGS(
        model.parameters(),
        lr=0.8,
        max_iter=lbfgs_iterations,
        max_eval=lbfgs_iterations * 2,
        tolerance_grad=1.0e-10,
        tolerance_change=1.0e-12,
        history_size=75,
        line_search_fn="strong_wolfe",
    )

    calls = 0

    def closure() -> torch.Tensor:
        nonlocal calls, last_terms
        optimizer_lbfgs.zero_grad(set_to_none=True)
        loss, last_terms = loss_function(model, points, fit_row)
        loss.backward()
        calls += 1
        if calls % 50 == 0:
            print(f"{label} LBFGS call {calls:4d}: loss={float(loss.detach()):.6e}", flush=True)
        return loss

    optimizer_lbfgs.step(closure)
    final_loss, last_terms = loss_function(model, points, fit_row)
    history.append(float(final_loss.detach()))
    print(f"{label} final: loss={history[-1]:.6e} terms={last_terms}", flush=True)
    return history, last_terms


@torch.no_grad()
def predict(model_t: nn.Module, model_x: nn.Module, radius_cm: np.ndarray, time_s: np.ndarray):
    x = torch.as_tensor(radius_cm.reshape(-1, 1) / 2.0)
    tau = torch.as_tensor(time_s.reshape(-1, 1) / 1800.0)
    temperature = 28.0 + 25.0 * temperature_field(model_t, x, tau)
    moisture = 2.55 * moisture_field(model_x, x, tau)
    return temperature.numpy().ravel(), moisture.numpy().ravel()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adam-epochs", type=int, default=1800)
    parser.add_argument("--lbfgs-iterations", type=int, default=250)
    parser.add_argument("--interior-points", type=int, default=1200)
    parser.add_argument("--boundary-points", type=int, default=240)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    torch.manual_seed(2026)
    np.random.seed(2026)
    script_dir = Path(__file__).resolve().parent
    model_dir = script_dir.parents[1]
    results_dir = model_dir / "output" / "results"
    figures_dir = model_dir / "output" / "figures"
    metrics_dir = model_dir / "output" / "metrics"
    models_dir = model_dir / "output" / "models"
    for directory in (results_dir, figures_dir, metrics_dir, models_dir):
        directory.mkdir(parents=True, exist_ok=True)

    fit_table = pd.read_csv(metrics_dir / "boundary_fit_parameters.csv")
    fit_table["variable"] = fit_table["variable"].astype(str).str.strip()
    fit_t = fit_table.loc[fit_table["variable"] == "temperature"].iloc[0]
    fit_x = fit_table.loc[fit_table["variable"] == "moisture"].iloc[0]
    attachment = pd.read_excel(model_dir.parent / "A题" / "附件" / "附件1.xlsx")
    temperature_boundary = {
        "time": torch.as_tensor(attachment.iloc[:, 0].to_numpy(dtype=float).copy()),
        "value": torch.as_tensor(attachment.iloc[:, 1].to_numpy(dtype=float).copy()),
    }

    point_seed = 9090 if args.validate_only else 2026
    points_t = make_training_points(args.interior_points, args.boundary_points, point_seed)
    points_x = make_training_points(args.interior_points, args.boundary_points, point_seed + 1)
    model_t = MLP()
    model_x = MLP()

    metrics_file = metrics_dir / "pinn_validation_metrics.json"
    if args.validate_only:
        checkpoint = torch.load(models_dir / "q1_pinn_models.pt", map_location="cpu")
        model_t.load_state_dict(checkpoint["temperature"])
        model_x.load_state_dict(checkpoint["moisture"])
        final_t, terms_t = temperature_loss(model_t, points_t, temperature_boundary)
        final_x, terms_x = moisture_loss(model_x, points_x, fit_x)
        history_t = [float(final_t.detach())]
        history_x = [float(final_x.detach())]
        if metrics_file.exists():
            previous_metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
            training_seconds = float(previous_metrics.get("training_seconds", 0.0))
        else:
            training_seconds = 0.0
    else:
        start = time.perf_counter()
        history_t, terms_t = train_model(
            model_t,
            temperature_loss,
            points_t,
            temperature_boundary,
            args.adam_epochs,
            args.lbfgs_iterations,
            "Temperature",
        )
        history_x, terms_x = train_model(
            model_x,
            moisture_loss,
            points_x,
            fit_x,
            args.adam_epochs,
            args.lbfgs_iterations,
            "Moisture",
        )
        training_seconds = time.perf_counter() - start

    reference_t = pd.read_excel(results_dir / "result1_cn.xlsx", sheet_name="温度")
    reference_x = pd.read_excel(results_dir / "result1_cn.xlsx", sheet_name="水分浓度")
    time_values = reference_t.iloc[:, 0].to_numpy(dtype=float)
    radius_values = np.asarray([float(c) for c in reference_t.columns[1:]], dtype=float)
    mesh_time, mesh_radius = np.meshgrid(time_values, radius_values, indexing="ij")
    predicted_t, predicted_x = predict(
        model_t, model_x, mesh_radius.ravel(), mesh_time.ravel()
    )
    predicted_t = predicted_t.reshape(mesh_time.shape)
    predicted_x = predicted_x.reshape(mesh_time.shape)
    cn_t = reference_t.iloc[:, 1:].to_numpy(dtype=float)
    cn_x = reference_x.iloc[:, 1:].to_numpy(dtype=float)
    error_t = predicted_t - cn_t
    error_x = predicted_x - cn_x

    sample_times = np.array([100, 300, 600, 900, 1200, 1500, 1800], dtype=float)
    sample_radii = np.array([0, 0.5, 1.0, 1.5, 2.0], dtype=float)
    sample_time_mesh, sample_radius_mesh = np.meshgrid(sample_times, sample_radii, indexing="ij")
    sample_pred_t, sample_pred_x = predict(
        model_t, model_x, sample_radius_mesh.ravel(), sample_time_mesh.ravel()
    )
    time_lookup = {float(value): index for index, value in enumerate(time_values)}
    radius_lookup = {float(value): index for index, value in enumerate(radius_values)}
    sample_cn_t = np.array([
        cn_t[time_lookup[float(t)], radius_lookup[float(r)]]
        for t, r in zip(sample_time_mesh.ravel(), sample_radius_mesh.ravel())
    ])
    sample_cn_x = np.array([
        cn_x[time_lookup[float(t)], radius_lookup[float(r)]]
        for t, r in zip(sample_time_mesh.ravel(), sample_radius_mesh.ravel())
    ])
    sample_rows = pd.DataFrame(
        {
            "time_s": sample_time_mesh.ravel(),
            "radius_cm": sample_radius_mesh.ravel(),
            "CN_temperature_C": sample_cn_t,
            "PINN_temperature_C": sample_pred_t,
            "temperature_difference_C": sample_pred_t - sample_cn_t,
            "CN_moisture_kgkg": sample_cn_x,
            "PINN_moisture_kgkg": sample_pred_x,
            "moisture_difference_kgkg": sample_pred_x - sample_cn_x,
        }
    )
    sample_rows.to_csv(results_dir / "pinn_requested_samples.csv", index=False)

    metrics = {
        "torch_version": torch.__version__,
        "device": "cpu",
        "validation_only_run": args.validate_only,
        "training_seconds": training_seconds,
        "adam_epochs_per_network": args.adam_epochs,
        "lbfgs_max_iterations_per_network": args.lbfgs_iterations,
        "interior_collocation_points": args.interior_points,
        "boundary_collocation_points": args.boundary_points,
        "physics_residual_points": "unseen Sobol points" if args.validate_only else "training points",
        "temperature_boundary_method": "piecewise-linear interpolation of Attachment 1",
        "temperature_final_physics_loss": history_t[-1],
        "moisture_final_physics_loss": history_x[-1],
        "temperature_loss_terms": terms_t,
        "moisture_loss_terms": terms_x,
        "temperature_vs_cn_rmse_C": float(np.sqrt(np.mean(error_t**2))),
        "temperature_vs_cn_mae_C": float(np.mean(np.abs(error_t))),
        "temperature_vs_cn_max_abs_C": float(np.max(np.abs(error_t))),
        "moisture_vs_cn_rmse_kgkg": float(np.sqrt(np.mean(error_x**2))),
        "moisture_vs_cn_mae_kgkg": float(np.mean(np.abs(error_x))),
        "moisture_vs_cn_max_abs_kgkg": float(np.max(np.abs(error_x))),
        "interpretation": (
            "PINN-CN agreement is a cross-method numerical check of the same PDE. "
            "It is not experimental validation because no internal material observations were provided."
        ),
    }
    metrics_file.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if not args.validate_only:
        torch.save(
            {"temperature": model_t.state_dict(), "moisture": model_x.state_dict()},
            models_dir / "q1_pinn_models.pt",
        )

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    if args.validate_only:
        labels = ["T PDE", "T center", "T surface", "X PDE", "X center", "X surface"]
        values = [
            terms_t["pde"],
            terms_t["center"],
            terms_t["surface"],
            terms_x["pde"],
            terms_x["center"],
            terms_x["surface"],
        ]
        axes[0].bar(np.arange(len(values)), values, color=["C0"] * 3 + ["C1"] * 3)
        axes[0].set_xticks(np.arange(len(values)), labels, rotation=30, ha="right")
        axes[0].set_yscale("log")
        axes[0].set_ylabel("Mean squared residual")
        axes[0].set_title("Final PINN physics residuals")
    else:
        axes[0].semilogy(history_t, label="Temperature")
        axes[0].semilogy(history_x, label="Moisture")
        axes[0].set_xlabel("Optimizer step")
        axes[0].set_ylabel("Physics loss")
        axes[0].legend()
        axes[0].set_title("PINN training")
    axes[0].grid(True, alpha=0.3)
    for radius_index, radius in enumerate(radius_values[::5]):
        column = radius_index * 5
        color = f"C{radius_index}"
        axes[1].plot(
            time_values / 60.0,
            cn_x[:, column],
            "-",
            color=color,
            linewidth=1.3,
            label=f"r={radius:g} cm",
        )
        axes[1].plot(time_values / 60.0, predicted_x[:, column], "--", color=color, linewidth=1.0)
    axes[1].set_xlabel("Time (min)")
    axes[1].set_ylabel("Moisture (kg/kg)")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=8, ncol=2)
    axes[1].set_title("CN solid / PINN dashed")
    fig.tight_layout()
    fig.savefig(figures_dir / "pinn_training_and_validation.png", dpi=180)
    plt.close(fig)

    print(json.dumps(metrics, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
