from __future__ import annotations

import argparse


PDE_PROFILES: dict[str, dict[str, float | int | bool]] = {
    "custom": {},
    "medium": {
        "pde_alpha_boost": 3.0,
        "pde_cooling_scale": 0.35,
    },
    "turbo": {
        "pde_alpha_boost": 18.0,
        "pde_cooling_scale": 0.08,
        "source_width": 10,
        "source_height": 5,
        "t_source": 85.0,
    },
}

BROWNIAN_PROFILES: dict[str, dict[str, float | int | bool]] = {
    "custom": {},
    "medium": {
        "emit_count": 340,
        "diffusion": 2.1,
        "brownian_grid_alpha": 0.17,
        "deposit_fraction": 0.017,
        "temperature_coupling": 0.05,
        "brownian_global_cooling": False,
        "contrast_percentile": 98.5,
    },
    "turbo": {
        "emit_count": 560,
        "particle_energy": 0.95,
        "diffusion": 11.5,
        "mobility": 0.42,
        "brownian_grid_alpha": 0.29,
        "deposit_fraction": 0.006,
        "temperature_coupling": 0.015,
        "brownian_global_cooling": False,
        "contrast_percentile": 96.0,
        "source_width": 10,
        "source_height": 5,
        "t_source": 85.0,
    },
}

from heat_sim import (
    BrownianSolver,
    EnvironmentGrid,
    PDESolver,
    PyQtGraphSimulationVisualizer,
    SimulationConfig,
    SimulationVisualizer,
)


def apply_cli_profiles(args: argparse.Namespace) -> None:
    pde_profile = PDE_PROFILES[args.pde_profile]
    for key, value in pde_profile.items():
        setattr(args, key, value)

    brownian_profile = BROWNIAN_PROFILES[args.brownian_profile]
    for key, value in brownian_profile.items():
        setattr(args, key, value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="2D heat transfer: PDE vs Brownian simulation")

    parser.add_argument("--nx", type=int, default=120, help="Grid width")
    parser.add_argument("--ny", type=int, default=90, help="Grid height")
    parser.add_argument("--alpha", type=float, default=0.30, help="Thermal diffusivity")
    parser.add_argument("--cooling-k", type=float, default=0.004, help="Newton cooling coefficient")
    parser.add_argument("--t-min", type=float, default=20.0, help="Ambient baseline temperature")
    parser.add_argument("--t-source", type=float, default=100.0, help="Fireplace temperature")
    parser.add_argument("--source-width", type=int, default=16, help="Fireplace width")
    parser.add_argument("--source-height", type=int, default=8, help="Fireplace height")
    parser.add_argument(
        "--second-source-enabled",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable secondary heat source in the lower-right corner",
    )
    parser.add_argument(
        "--two-room-layout",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable two-room floor plan with partition wall and door",
    )
    parser.add_argument(
        "--fireplace-room",
        type=str,
        choices=("left", "right"),
        default="left",
        help="Room where fireplace is placed when two-room layout is enabled",
    )
    parser.add_argument(
        "--partition-wall-thickness",
        type=int,
        default=2,
        help="Thickness of partition wall between rooms (in cells)",
    )
    parser.add_argument("--door-height", type=int, default=14, help="Door opening height in partition wall")
    parser.add_argument(
        "--door-center-ratio",
        type=float,
        default=0.72,
        help="Door vertical center position: 0.0=top, 1.0=bottom",
    )

    parser.add_argument("--emit-count", type=int, default=260, help="Particles emitted per step")
    parser.add_argument("--particle-energy", type=float, default=1.8, help="Initial particle energy")
    parser.add_argument("--deposit-fraction", type=float, default=0.03, help="Base particle deposit ratio")
    parser.add_argument(
        "--temperature-coupling",
        type=float,
        default=0.10,
        help="Extra deposit ratio in colder cells",
    )
    parser.add_argument("--particle-cutoff", type=float, default=0.01, help="Particle removal threshold")
    parser.add_argument("--mobility", type=float, default=0.22, help="Gradient drift mobility")
    parser.add_argument("--diffusion", type=float, default=1.50, help="Brownian diffusion coefficient")
    parser.add_argument(
        "--brownian-grid-alpha",
        type=float,
        default=0.10,
        help="Extra diffusion of Brownian temperature grid",
    )
    parser.add_argument(
        "--brownian-global-cooling",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable or disable global Newton cooling in Brownian solver",
    )

    parser.add_argument("--frames", type=int, default=900, help="Animation frames")
    parser.add_argument("--steps-per-frame", type=int, default=2, help="Solver steps per animation frame")
    parser.add_argument("--interval-ms", type=int, default=35, help="Frame delay in milliseconds")
    parser.add_argument(
        "--contrast-percentile",
        type=float,
        default=99.3,
        help="Dynamic upper color level percentile for visualization",
    )
    parser.add_argument(
        "--renderer",
        type=str,
        default="matplotlib",
        choices=("matplotlib", "pyqtgraph"),
        help="Visualization backend",
    )
    parser.add_argument("--save-gif", type=str, default=None, help="Output GIF path, e.g. outputs/simulation.gif")
    parser.add_argument("--gif-fps", type=int, default=20, help="GIF frames per second")
    parser.add_argument("--gif-dpi", type=int, default=110, help="GIF DPI")
    parser.add_argument("--no-show", action="store_true", help="Disable interactive window display")
    parser.add_argument("--cfl-safety", type=float, default=0.9, help="Safety multiplier for PDE dt")
    parser.add_argument(
        "--pde-alpha-boost",
        type=float,
        default=3.0,
        help="Multiplier for PDE thermal diffusivity to accelerate heat spread",
    )
    parser.add_argument(
        "--pde-cooling-scale",
        type=float,
        default=0.35,
        help="Scale factor for PDE cooling term (lower means slower PDE cooling)",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for stochastic solver")
    parser.add_argument(
        "--pde-profile",
        type=str,
        choices=tuple(PDE_PROFILES.keys()),
        default="custom",
        help="Preset for PDE strength (custom, medium, turbo)",
    )
    parser.add_argument(
        "--brownian-profile",
        type=str,
        choices=tuple(BROWNIAN_PROFILES.keys()),
        default="custom",
        help="Preset for Brownian transport strength (custom, medium, turbo)",
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()
    apply_cli_profiles(args)

    cfg = SimulationConfig(
        nx=args.nx,
        ny=args.ny,
        alpha=args.alpha,
        cooling_k=args.cooling_k,
        t_min=args.t_min,
        t_source=args.t_source,
        source_width=args.source_width,
        source_height=args.source_height,
        second_source_enabled=args.second_source_enabled,
        two_room_layout=args.two_room_layout,
        fireplace_room=args.fireplace_room,
        partition_wall_thickness=args.partition_wall_thickness,
        door_height=args.door_height,
        door_center_ratio=args.door_center_ratio,
    )

    pde_environment = EnvironmentGrid(cfg)
    pde_solver = PDESolver(
        pde_environment,
        cfl_safety=args.cfl_safety,
        alpha_boost=args.pde_alpha_boost,
        cooling_scale=args.pde_cooling_scale,
    )

    brownian_environment = EnvironmentGrid(cfg)
    brownian_solver = BrownianSolver(
        brownian_environment,
        dt=pde_solver.dt,
        emit_count=args.emit_count,
        particle_energy=args.particle_energy,
        deposit_fraction=args.deposit_fraction,
        temperature_coupling=args.temperature_coupling,
        particle_cutoff=args.particle_cutoff,
        mobility=args.mobility,
        diffusion=args.diffusion,
        grid_diffusion_alpha=args.brownian_grid_alpha,
        enable_global_cooling=args.brownian_global_cooling,
        seed=args.seed,
    )

    if args.renderer == "pyqtgraph":
        if args.save_gif:
            raise ValueError("GIF export is only supported by matplotlib renderer.")
        visualizer = PyQtGraphSimulationVisualizer(
            pde_solver,
            brownian_solver,
            frames=args.frames,
            steps_per_frame=args.steps_per_frame,
            interval_ms=args.interval_ms,
            contrast_percentile=args.contrast_percentile,
        )
    else:
        visualizer = SimulationVisualizer(
            pde_solver,
            brownian_solver,
            frames=args.frames,
            steps_per_frame=args.steps_per_frame,
            interval_ms=args.interval_ms,
            contrast_percentile=args.contrast_percentile,
        )
    visualizer.run(
        save_gif_path=args.save_gif,
        gif_fps=args.gif_fps,
        gif_dpi=args.gif_dpi,
        show_window=not args.no_show,
    )


if __name__ == "__main__":
    main()
