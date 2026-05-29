from __future__ import annotations

import math

import numpy as np

from .environment import EnvironmentGrid


class PDESolver:
    """FTCS solver for 2D heat equation with global Newton cooling."""

    def __init__(
        self,
        environment: EnvironmentGrid,
        cfl_safety: float = 0.9,
        alpha_boost: float = 1.0,
        cooling_scale: float = 1.0,
    ) -> None:
        self.environment = environment
        self.temperature = environment.create_temperature_field()
        if alpha_boost <= 0.0:
            raise ValueError("alpha_boost must be positive.")
        if cooling_scale < 0.0:
            raise ValueError("cooling_scale cannot be negative.")
        self.alpha_boost = alpha_boost
        self.cooling_scale = cooling_scale
        self.cfl_safety = cfl_safety
        self.dt = self.compute_stable_dt(cfl_safety=cfl_safety)

    def compute_stable_dt(self, cfl_safety: float = 0.9) -> float:
        """Compute explicit 2D FTCS stable time step using the CFL criterion."""

        cfg = self.environment.config
        numerator = cfg.dx * cfg.dx * cfg.dy * cfg.dy
        denominator = 2.0 * cfg.alpha * (cfg.dx * cfg.dx + cfg.dy * cfg.dy)
        raw_dt = numerator / denominator
        return cfl_safety * raw_dt

    def step(self, iterations: int = 1) -> np.ndarray:
        cfg = self.environment.config
        effective_alpha = cfg.alpha * self.alpha_boost
        effective_cooling = cfg.cooling_k * self.cooling_scale
        substeps = max(1, int(math.ceil(self.alpha_boost * self.cfl_safety)))
        dt_sub = self.dt / substeps

        for _ in range(iterations):
            for _sub in range(substeps):
                t = self.temperature
                laplace = self.environment.compute_reflective_laplacian(t)
                cooling = -effective_cooling * (t - cfg.t_min)
                cooling[self.environment.wall_mask] = 0.0
                next_t = t + dt_sub * (effective_alpha * laplace + cooling)

                np.maximum(next_t, cfg.t_min, out=next_t)
                self.environment.apply_source(next_t)
                self.environment.enforce_walls(next_t)
                self.temperature = next_t

        return self.temperature
