from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SimulationConfig:
    """Configuration shared by deterministic and stochastic models."""

    nx: int = 120
    ny: int = 90
    dx: float = 1.0
    dy: float = 1.0
    alpha: float = 0.22
    cooling_k: float = 0.015
    t_min: float = 20.0
    t_source: float = 100.0
    source_width: int = 16
    source_height: int = 8
    second_source_enabled: bool = True
    two_room_layout: bool = False
    fireplace_room: str = "left"
    partition_wall_thickness: int = 2
    door_height: int = 14
    door_center_ratio: float = 0.72

    def __post_init__(self) -> None:
        if self.nx <= 4 or self.ny <= 4:
            raise ValueError("Grid dimensions must be greater than 4.")
        if self.dx <= 0.0 or self.dy <= 0.0:
            raise ValueError("Grid spacing must be positive.")
        if self.alpha <= 0.0:
            raise ValueError("Thermal diffusivity alpha must be positive.")
        if self.cooling_k < 0.0:
            raise ValueError("Cooling coefficient k cannot be negative.")
        if self.source_width <= 0 or self.source_height <= 0:
            raise ValueError("Heat source dimensions must be positive.")
        if self.source_width >= self.nx or self.source_height >= self.ny:
            raise ValueError("Heat source must fit inside the simulation grid.")
        if self.fireplace_room not in {"left", "right"}:
            raise ValueError("fireplace_room must be either 'left' or 'right'.")
        if self.partition_wall_thickness <= 0:
            raise ValueError("partition_wall_thickness must be positive.")
        if self.partition_wall_thickness >= self.nx - 2:
            raise ValueError("partition_wall_thickness is too large for current grid width.")
        if self.door_height <= 0:
            raise ValueError("door_height must be positive.")
        if self.door_height >= self.ny - 2:
            raise ValueError("door_height must be smaller than grid height.")
        if not 0.0 <= self.door_center_ratio <= 1.0:
            raise ValueError("door_center_ratio must be in range [0.0, 1.0].")

        if self.two_room_layout:
            left_cols, right_cols = self.room_column_bounds
            room_width = (left_cols.stop - left_cols.start) if self.fireplace_room == "left" else (right_cols.stop - right_cols.start)
            if self.source_width >= room_width:
                raise ValueError("Heat source is too wide to fit into one room with current wall thickness.")

    @property
    def source_bounds(self) -> tuple[slice, slice]:
        """Return [rows, cols] slices for the fireplace area."""

        row_start = max(0, self.ny - self.source_height - 2)
        row_stop = min(self.ny, row_start + self.source_height)

        if self.two_room_layout:
            left_cols, right_cols = self.room_column_bounds
            room_cols = left_cols if self.fireplace_room == "left" else right_cols
            room_width = room_cols.stop - room_cols.start
            col_start = room_cols.start + (room_width - self.source_width) // 2
        else:
            col_start = (self.nx - self.source_width) // 2

        col_stop = col_start + self.source_width
        return slice(row_start, row_stop), slice(col_start, col_stop)

    @property
    def second_source_bounds(self) -> tuple[slice, slice]:
        """Return [rows, cols] slices for the secondary source in lower-right corner."""

        row_stop = self.ny - 2
        row_start = max(0, row_stop - self.source_height)
        col_stop = self.nx - 2
        col_start = max(0, col_stop - self.source_width)
        return slice(row_start, row_stop), slice(col_start, col_stop)

    @property
    def partition_column_bounds(self) -> slice:
        usable_width = self.nx - self.partition_wall_thickness
        left_width = usable_width // 2
        wall_start = left_width
        wall_stop = wall_start + self.partition_wall_thickness
        return slice(wall_start, wall_stop)

    @property
    def room_column_bounds(self) -> tuple[slice, slice]:
        wall_cols = self.partition_column_bounds
        left_room = slice(0, wall_cols.start)
        right_room = slice(wall_cols.stop, self.nx)
        return left_room, right_room

    @property
    def door_row_bounds(self) -> slice:
        center_row = int(round((self.ny - 1) * self.door_center_ratio))
        row_start = center_row - self.door_height // 2
        row_start = min(max(1, row_start), self.ny - self.door_height - 1)
        row_stop = row_start + self.door_height
        return slice(row_start, row_stop)
