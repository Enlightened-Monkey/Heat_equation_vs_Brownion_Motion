from __future__ import annotations

import numpy as np

from .brownian_solver import BrownianSolver
from .pde_solver import PDESolver


class PyQtGraphSimulationVisualizer:
    """Render deterministic and stochastic grids side-by-side using PyQtGraph."""

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
        del gif_fps, gif_dpi

        if save_gif_path:
            raise ValueError("PyQtGraph renderer does not support GIF export. Use matplotlib renderer.")

        if not show_window:
            return

        try:
            import pyqtgraph as pg
            from pyqtgraph.Qt import QtCore, QtWidgets
        except ImportError as exc:
            raise RuntimeError(
                "PyQtGraph backend is unavailable. Install dependencies from requirements.txt."
            ) from exc

        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])

        pg.setConfigOptions(antialias=False, imageAxisOrder="row-major")

        vmin, vmax = self._compute_levels()

        window = pg.GraphicsLayoutWidget(title="2D Heat Propagation: PDE vs Biased Brownian")
        window.resize(1280, 680)

        pde_plot = window.addPlot(row=0, col=0, title="Deterministic PDE (FTCS)")
        brownian_plot = window.addPlot(row=0, col=1, title="Stochastic Biased Brownian")

        pde_plot.setLabel("bottom", "x")
        pde_plot.setLabel("left", "y")
        brownian_plot.setLabel("bottom", "x")
        brownian_plot.setLabel("left", "y")

        pde_image = pg.ImageItem(axisOrder="row-major")
        brownian_image = pg.ImageItem(axisOrder="row-major")
        pde_plot.addItem(pde_image)
        brownian_plot.addItem(brownian_image)

        cmap = pg.colormap.get("inferno")
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        pde_image.setLookupTable(lut)
        brownian_image.setLookupTable(lut)
        pde_image.setLevels((vmin, vmax))
        brownian_image.setLevels((vmin, vmax))

        color_bar_pde = pg.ColorBarItem(values=(vmin, vmax), colorMap=cmap, label="Temperature")
        color_bar_bro = pg.ColorBarItem(values=(vmin, vmax), colorMap=cmap, label="Temperature")
        color_bar_pde.setImageItem(pde_image, insert_in=pde_plot)
        color_bar_bro.setImageItem(brownian_image, insert_in=brownian_plot)

        frame_state = {"frame": 0}

        def _update() -> None:
            if frame_state["frame"] >= self.frames:
                timer.stop()
                return

            self.pde_solver.step(iterations=self.steps_per_frame)
            self.brownian_solver.step(iterations=self.steps_per_frame)

            pde_data = np.asarray(self.pde_solver.temperature)
            brownian_data = np.asarray(self.brownian_solver.temperature)
            pde_image.setImage(pde_data, autoLevels=False)
            brownian_image.setImage(brownian_data, autoLevels=False)

            dynamic_vmin, dynamic_vmax = self._compute_levels()
            pde_image.setLevels((dynamic_vmin, dynamic_vmax))
            brownian_image.setLevels((dynamic_vmin, dynamic_vmax))
            color_bar_pde.setLevels((dynamic_vmin, dynamic_vmax))
            color_bar_bro.setLevels((dynamic_vmin, dynamic_vmax))

            brownian_plot.setTitle(
                f"Stochastic Biased Brownian | particles={self.brownian_solver.active_particles}"
            )
            frame_state["frame"] += 1

        timer = QtCore.QTimer()
        timer.timeout.connect(_update)
        _update()
        timer.start(self.interval_ms)

        self._qt_refs = (app, window, pde_image, brownian_image, timer)

        window.show()
        app.exec()
