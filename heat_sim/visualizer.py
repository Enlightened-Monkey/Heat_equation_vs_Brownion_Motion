from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from .brownian_solver import BrownianSolver
from .pde_solver import PDESolver


class SimulationVisualizer:
    """Render deterministic and stochastic grids side-by-side."""

    def __init__(
        self,
        pde_solver: PDESolver,
        brownian_solver: BrownianSolver,
        frames: int = 900,
        steps_per_frame: int = 1,
        interval_ms: int = 35,
        contrast_percentile: float = 99.0,
    ) -> None:
        self.pde_solver = pde_solver
        self.brownian_solver = brownian_solver
        self.frames = frames
        self.steps_per_frame = steps_per_frame
        self.interval_ms = interval_ms
        self.contrast_percentile = contrast_percentile

    def _compute_levels(self) -> tuple[float, float]:
        cfg = self.pde_solver.environment.config
        mask = self.pde_solver.environment.source_mask | self.pde_solver.environment.wall_mask

        pde_vals = self.pde_solver.temperature[~mask]
        brown_vals = self.brownian_solver.temperature[~mask]
        merged = [pde_vals, brown_vals]
        merged = [arr for arr in merged if arr.size > 0]

        if not merged:
            return cfg.t_min, max(cfg.t_min + 1.0, cfg.t_source)

        percentile = float(np.percentile(np.concatenate(merged), self.contrast_percentile))
        vmax = max(cfg.t_min + 1.0, percentile)
        return cfg.t_min, vmax

    def run(
        self,
        save_gif_path: str | None = None,
        gif_fps: int = 20,
        gif_dpi: int = 110,
        show_window: bool = True,
    ) -> None:
        vmin, vmax = self._compute_levels()

        fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
        fig.suptitle("2D Heat Propagation: PDE vs Biased Brownian", fontsize=14)

        pde_img = axes[0].imshow(
            self.pde_solver.temperature,
            cmap="inferno",
            vmin=vmin,
            vmax=vmax,
            origin="lower",
            interpolation="nearest",
        )
        brown_img = axes[1].imshow(
            self.brownian_solver.temperature,
            cmap="inferno",
            vmin=vmin,
            vmax=vmax,
            origin="lower",
            interpolation="nearest",
        )

        axes[0].set_title("Deterministic PDE (FTCS)")
        axes[1].set_title("Stochastic Biased Brownian")
        for ax in axes:
            ax.set_xlabel("x")
            ax.set_ylabel("y")

        pde_cbar = fig.colorbar(pde_img, ax=axes[0], fraction=0.046, pad=0.04, label="Temperature")
        brown_cbar = fig.colorbar(brown_img, ax=axes[1], fraction=0.046, pad=0.04, label="Temperature")

        def update(_frame: int):
            self.pde_solver.step(iterations=self.steps_per_frame)
            self.brownian_solver.step(iterations=self.steps_per_frame)

            pde_img.set_data(self.pde_solver.temperature)
            brown_img.set_data(self.brownian_solver.temperature)

            dynamic_vmin, dynamic_vmax = self._compute_levels()
            pde_img.set_clim(dynamic_vmin, dynamic_vmax)
            brown_img.set_clim(dynamic_vmin, dynamic_vmax)
            pde_cbar.update_normal(pde_img)
            brown_cbar.update_normal(brown_img)

            axes[1].set_title(
                f"Stochastic Biased Brownian | particles={self.brownian_solver.active_particles}"
            )
            return (pde_img, brown_img)

        animation = FuncAnimation(
            fig,
            update,
            frames=self.frames,
            interval=self.interval_ms,
            blit=False,
            repeat=False,
        )

        # Keep a strong reference to avoid animation garbage collection.
        self._animation = animation

        if save_gif_path:
            output_path = Path(save_gif_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            animation.save(output_path, writer="pillow", fps=gif_fps, dpi=gif_dpi)

        if show_window:
            plt.show()
        else:
            plt.close(fig)
