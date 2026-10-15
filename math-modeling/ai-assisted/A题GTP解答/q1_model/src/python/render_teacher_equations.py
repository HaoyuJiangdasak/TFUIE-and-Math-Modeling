"""Render model equations as high-resolution PNGs for the teacher DOCX."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
MODEL_DIR = SCRIPT_DIR.parents[1]
ASSET_DIR = MODEL_DIR / "output" / "teacher_doc_assets"

EQUATIONS = {
    "heat_pde": (
        r"$\rho c_p\frac{\partial T}{\partial t}="
        r"\frac{1}{r}\frac{\partial}{\partial r}"
        r"\left(rk\frac{\partial T}{\partial r}\right),\quad 0<r<R$"
    ),
    "moisture_pde": (
        r"$\frac{\partial X}{\partial t}="
        r"\frac{1}{r}\frac{\partial}{\partial r}"
        r"\left(rD(X)\frac{\partial X}{\partial r}\right)$"
    ),
    "diffusivity": (
        r"$D(X)=7\times10^{-9}\exp\!\left(-\frac{0.89}{X}\right)"
        r"\;\mathrm{m^2\,s^{-1}}$"
    ),
    "initial_center": (
        r"$T(r,0)=28\,^{\circ}\mathrm{C},\quad X(r,0)=2.55;"
        r"\qquad T_r(0,t)=0,\quad X_r(0,t)=0$"
    ),
    "surface_robin": (
        r"$-kT_r(R,t)=h_T[T_s-T_\infty(t)],\qquad"
        r"-D(X_s)X_r(R,t)=h_m[X_s-X_\infty(t)]$"
    ),
    "boundary_fit": (
        r"$y(t)=y_0+(y_\infty-y_0)"
        r"\left[1-\exp\!\left(-\left(\frac{t}{\tau}\right)^\beta\right)\right]$"
    ),
    "crank_nicolson": (
        r"$\left(\frac{M}{\Delta t}-\frac{1}{2}L^{n+1}\right)u^{n+1}="
        r"\left(\frac{M}{\Delta t}+\frac{1}{2}L^n\right)u^n+b^{n+\frac{1}{2}}$"
    ),
    "pinn_loss": (
        r"$\mathcal{L}=\lambda_f\,\mathrm{MSE}(f)+"
        r"\lambda_0\,\mathrm{MSE}(IC)+\lambda_b\,\mathrm{MSE}(BC)$"
    ),
}


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, equation in EQUATIONS.items():
        fig = plt.figure(figsize=(9.0, 0.9), facecolor="white")
        fig.text(0.5, 0.5, equation, ha="center", va="center", fontsize=18, color="#111827")
        path = ASSET_DIR / f"{name}.png"
        fig.savefig(path, dpi=240, bbox_inches="tight", pad_inches=0.12, facecolor="white")
        plt.close(fig)
        from PIL import Image

        with Image.open(path) as image:
            manifest[name] = {"path": str(path), "width": image.width, "height": image.height}
    (ASSET_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
