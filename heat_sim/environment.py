from __future__ import annotations

import numpy as np

from .config import SimulationConfig


class EnvironmentGrid:
    """Domain helpers shared by both simulation paradigms."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.source_rows, self.source_cols = config.source_bounds
        self.source_regions: list[tuple[slice, slice]] = [(self.source_rows, self.source_cols)]
        if config.second_source_enabled:
            self.second_source_rows, self.second_source_cols = config.second_source_bounds
            self.source_regions.append((self.second_source_rows, self.second_source_cols))
        else:
            self.second_source_rows, self.second_source_cols = slice(0, 0), slice(0, 0)

        self.wall_mask = np.zeros((config.ny, config.nx), dtype=bool)
        if config.two_room_layout:
            wall_cols = config.partition_column_bounds
            door_rows = config.door_row_bounds
            self.wall_mask[:, wall_cols] = True
            self.wall_mask[door_rows, wall_cols] = False

        self.source_mask = np.zeros((config.ny, config.nx), dtype=bool)
        for rows, cols in self.source_regions:
            self.source_mask[rows, cols] = True
        self.source_mask[self.wall_mask] = False

    def create_temperature_field(self) -> np.ndarray:
        field = np.full((self.config.ny, self.config.nx), self.config.t_min, dtype=np.float64)
        self.enforce_walls(field)
        self.apply_source(field)
        return field

    def apply_source(self, field: np.ndarray) -> None:
        for rows, cols in self.source_regions:
            field[rows, cols] = self.config.t_source
        self.enforce_walls(field)

    def apply_newton_cooling(self, field: np.ndarray, dt: float) -> None:
        field -= self.config.cooling_k * (field - self.config.t_min) * dt
        self.enforce_walls(field)

    def enforce_walls(self, field: np.ndarray) -> None:
        field[self.wall_mask] = self.config.t_min

    def compute_reflective_laplacian(self, field: np.ndarray) -> np.ndarray:
        cfg = self.config
        open_mask = ~self.wall_mask

        def _neighbor(axis: int, shift: int) -> tuple[np.ndarray, np.ndarray]:
            neighbor = np.roll(field, shift=shift, axis=axis)
            neighbor_open = np.roll(open_mask, shift=shift, axis=axis)

            # Remove wrap-around neighbors so external boundaries remain reflective.
            if axis == 0:
                if shift > 0:
                    neighbor_open[0, :] = False
                else:
                    neighbor_open[-1, :] = False
            else:
                if shift > 0:
                    neighbor_open[:, 0] = False
                else:
                    neighbor_open[:, -1] = False

            return neighbor, neighbor_open

        east, east_open = _neighbor(axis=1, shift=-1)
        west, west_open = _neighbor(axis=1, shift=1)
        north, north_open = _neighbor(axis=0, shift=-1)
        south, south_open = _neighbor(axis=0, shift=1)

        east_val = np.where(east_open, east, field)
        west_val = np.where(west_open, west, field)
        north_val = np.where(north_open, north, field)
        south_val = np.where(south_open, south, field)

        laplace_x = (east_val - 2.0 * field + west_val) / (cfg.dx * cfg.dx)
        laplace_y = (north_val - 2.0 * field + south_val) / (cfg.dy * cfg.dy)
        laplace = laplace_x + laplace_y
        laplace[self.wall_mask] = 0.0
        return laplace
