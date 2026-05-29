from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import numpy as np

from .environment import EnvironmentGrid


@dataclass(slots=True)
class ParticleCloud:
    positions: np.ndarray
    energies: np.ndarray


class BrownianSolver:
    """Biased Brownian particles with gradient drift and energy deposition."""

    def __init__(
        self,
        environment: EnvironmentGrid,
        dt: float,
        emit_count: int = 120,
        particle_energy: float = 1.8,
        deposit_fraction: float = 0.03,
        temperature_coupling: float = 0.10,
        particle_cutoff: float = 0.01,
        mobility: float = 0.22,
        diffusion: float = 1.25,
        grid_diffusion_alpha: float = 0.06,
        enable_global_cooling: bool = True,
        max_particles: int = 220_000,
        seed: int | None = 42,
    ) -> None:
        self.environment = environment
        self.temperature = environment.create_temperature_field()
        self.dt = dt

        self.emit_count = emit_count
        self.particle_energy = particle_energy
        self.deposit_fraction = deposit_fraction
        self.temperature_coupling = temperature_coupling
        self.particle_cutoff = particle_cutoff
        self.mobility = mobility
        self.diffusion = diffusion
        self.grid_diffusion_alpha = grid_diffusion_alpha
        self.enable_global_cooling = enable_global_cooling
        self.max_particles = max_particles

        self.rng = np.random.default_rng(seed)
        self.particles = ParticleCloud(
            positions=np.empty((0, 2), dtype=np.float64),
            energies=np.empty((0,), dtype=np.float64),
        )

        source_indices = np.argwhere(self.environment.source_mask)
        if source_indices.size == 0:
            raise ValueError("Heat source mask is empty.")
        self.source_positions = source_indices.astype(np.float64)

        max_alpha = 0.5 / (
            self.dt
            * (
                1.0 / (self.environment.config.dx * self.environment.config.dx)
                + 1.0 / (self.environment.config.dy * self.environment.config.dy)
            )
        )
        if self.grid_diffusion_alpha < 0.0:
            raise ValueError("grid_diffusion_alpha cannot be negative.")
        if self.grid_diffusion_alpha > max_alpha:
            raise ValueError(
                f"grid_diffusion_alpha={self.grid_diffusion_alpha:.4f} exceeds stable limit {max_alpha:.4f}."
            )

    @property
    def active_particles(self) -> int:
        return int(self.particles.energies.size)

    def step(self, iterations: int = 1) -> np.ndarray:
        for _ in range(iterations):
            self._emit_particles()
            self._move_particles()
            self._deposit_particle_energy()
            self._diffuse_temperature_field()
            self._prune_particles()

            if self.enable_global_cooling:
                self.environment.apply_newton_cooling(self.temperature, self.dt)
                np.maximum(self.temperature, self.environment.config.t_min, out=self.temperature)
            self.environment.apply_source(self.temperature)

        return self.temperature

    def _emit_particles(self) -> None:
        pick_idx = self.rng.integers(0, self.source_positions.shape[0], size=self.emit_count)
        base_pos = self.source_positions[pick_idx]
        jitter = self.rng.random((self.emit_count, 2))
        new_positions = base_pos + jitter
        new_energies = np.full((self.emit_count,), self.particle_energy, dtype=np.float64)

        self.particles.positions = np.vstack((self.particles.positions, new_positions))
        self.particles.energies = np.concatenate((self.particles.energies, new_energies))

    def _move_particles(self) -> None:
        if self.active_particles == 0:
            return

        cfg = self.environment.config
        previous_positions = self.particles.positions.copy()
        rows = np.clip(self.particles.positions[:, 0].astype(np.int32), 0, cfg.ny - 1)
        cols = np.clip(self.particles.positions[:, 1].astype(np.int32), 0, cfg.nx - 1)

        grad_parts = np.gradient(self.temperature, cfg.dy, cfg.dx)
        grad_y = cast(np.ndarray, grad_parts[0])
        grad_x = cast(np.ndarray, grad_parts[1])
        drift = np.column_stack((-grad_y[rows, cols], -grad_x[rows, cols]))
        drift *= self.mobility * self.dt

        noise_scale = np.sqrt(2.0 * self.diffusion * self.dt)
        noise = self.rng.normal(loc=0.0, scale=noise_scale, size=self.particles.positions.shape)

        self.particles.positions += drift + noise
        self.particles.positions[:, 0] = np.clip(self.particles.positions[:, 0], 0.0, cfg.ny - 1e-6)
        self.particles.positions[:, 1] = np.clip(self.particles.positions[:, 1], 0.0, cfg.nx - 1e-6)

        new_rows = np.clip(self.particles.positions[:, 0].astype(np.int32), 0, cfg.ny - 1)
        new_cols = np.clip(self.particles.positions[:, 1].astype(np.int32), 0, cfg.nx - 1)
        hit_wall = self.environment.wall_mask[new_rows, new_cols]
        self.particles.positions[hit_wall] = previous_positions[hit_wall]

    def _deposit_particle_energy(self) -> None:
        if self.active_particles == 0:
            return

        cfg = self.environment.config
        rows = np.clip(self.particles.positions[:, 0].astype(np.int32), 0, cfg.ny - 1)
        cols = np.clip(self.particles.positions[:, 1].astype(np.int32), 0, cfg.nx - 1)

        # Cold cells absorb more energy, so particles survive longer near the source
        # and release more once they reach underheated areas.
        local_temp = self.temperature[rows, cols]
        temp_span = max(cfg.t_source - cfg.t_min, 1e-9)
        coldness = np.clip((cfg.t_source - local_temp) / temp_span, 0.0, 1.0)
        effective_fraction = np.clip(
            self.deposit_fraction + self.temperature_coupling * coldness,
            0.0,
            1.0,
        )
        deposited = self.particles.energies * effective_fraction
        np.add.at(self.temperature, (rows, cols), deposited)
        self.particles.energies -= deposited

    def _prune_particles(self) -> None:
        if self.active_particles == 0:
            return

        alive_mask = self.particles.energies >= self.particle_cutoff
        self.particles.positions = self.particles.positions[alive_mask]
        self.particles.energies = self.particles.energies[alive_mask]

        if self.active_particles <= self.max_particles:
            return

        keep_idx = np.argpartition(self.particles.energies, -self.max_particles)[-self.max_particles:]
        self.particles.positions = self.particles.positions[keep_idx]
        self.particles.energies = self.particles.energies[keep_idx]

    def _diffuse_temperature_field(self) -> None:
        if self.grid_diffusion_alpha <= 0.0:
            return

        t = self.temperature
        laplace = self.environment.compute_reflective_laplacian(t)
        next_t = t + self.dt * self.grid_diffusion_alpha * laplace
        self.environment.enforce_walls(next_t)

        self.temperature = next_t
