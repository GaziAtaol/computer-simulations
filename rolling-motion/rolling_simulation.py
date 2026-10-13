from math import sin, radians
import matplotlib.pyplot as plt

# ── Parameters ────────────────────────────────────────────────────────────────
G         = 9.81    # gravitational acceleration  [m/s²]
THETA_DEG = 30.0    # incline angle               [°]
R         = 0.01     # sphere radius               [m]
L         = 10.0     # ramp length                 [m]  (simulation stops when s reaches this)
DT        = 0.001   # time step                   [s]
T_MAX     = 10.0    # maximum simulation time     [s]

THETA = radians(THETA_DEG)
OBJECTS = {
    "Solid Sphere (I=2/5·mr²)":  2 / 5,
    "Hollow Sphere (I=2/3·mr²)": 2 / 3,
}

# ── Physics functions ─────────────────────────────────────────────────────────
def calc_acceleration(i_factor: float) -> float:

    return G * sin(THETA) / (1.0 + i_factor)

def derivatives(state: list[float], a: float) -> list[float]:

    _, v, _, omega = state
    return [v, a, omega, a / R]

def midpoint_step(state: list[float], a: float, dt: float) -> list[float]:

    k1  = derivatives(state, a)
    y_m = [state[i] + (dt / 2.0) * k1[i] for i in range(4)]
    k2  = derivatives(y_m, a)
    return [state[i] + dt * k2[i] for i in range(4)]

def simulate(i_factor: float) -> dict:

    a = calc_acceleration(i_factor)

    t     = 0.0
    state = [0.0, 0.0, 0.0, 0.0]   # [s, v, alpha, omega] initial conditions

    ts, ss, vs, alphas, omegas = [t], [0.0], [0.0], [0.0], [0.0]

    while state[0] < L and t < T_MAX:
        state  = midpoint_step(state, a, DT)
        t     += DT

        ts.append(t)
        ss.append(state[0])
        vs.append(state[1])
        alphas.append(state[2])
        omegas.append(state[3])

    return {"t": ts, "s": ss, "v": vs, "alpha": alphas, "omega": omegas,
            "a": a, "arrival_time": t}

# ── Visualization ─────────────────────────────────────────────────────────────

def plot_results(results: dict[str, dict]) -> None:
    colors  = ["royalblue", "tomato"]
    styles  = ["-",         "--"]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(
        f"Objects Rolling on an Inclined Plane  "
        f"(θ={THETA_DEG}°, r={R} m, L={L} m)\n"
        "Numerical Method: Midpoint (RK2)",
        fontsize=13, fontweight="bold"
    )

    panels = [
        (axes[0, 0], "s",     "Position  s [m]",          "Position – Time"),
        (axes[0, 1], "v",     "Velocity  v [m/s]",        "Velocity – Time"),
        (axes[1, 0], "alpha", "Rotation angle  α [rad]",  "Angle – Time"),
        (axes[1, 1], "omega", "Angular velocity  ω [rad/s]", "Angular Velocity – Time"),
    ]

    for (ax, key, ylabel, title), color, style in zip(panels, colors * 2, styles * 2):
        for (label, data), col, ls in zip(results.items(), colors, styles):
            ax.plot(data["t"], data[key], color=col, linestyle=ls,
                    linewidth=1.8, label=label)
        ax.set_xlabel("Time  t [s]")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("rolling_simulation.png", dpi=150)
    plt.show()
    print("Plot saved as 'rolling_simulation.png'.")

# ── Main program ──────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Inclined Plane Simulation — Midpoint Method")
    print("=" * 60)
    print(f"  g = {G} m/s²  |  θ = {THETA_DEG}°  |  r = {R} m")
    print(f"  Ramp length L = {L} m  |  Δt = {DT} s")
    print("-" * 60)

    results = {}
    for name, i_factor in OBJECTS.items():
        data = simulate(i_factor)
        results[name] = data
        print(f"\n{name}")
        print(f"  Acceleration      : a = {data['a']:.4f} m/s²")
        print(f"  Final velocity    : v = {data['v'][-1]:.4f} m/s")
        print(f"  Arrival time      : t = {data['arrival_time']:.4f} s")
        print(f"  Final angular vel : ω = {data['omega'][-1]:.4f} rad/s")
        print(f"  Verification ω=v/r: {data['v'][-1]/R:.4f} rad/s")

    print("\n" + "=" * 60)
    print("  Solid sphere arrives first because it has a smaller")
    print("  moment of inertia (2/5 < 2/3).")
    print("=" * 60)

    plot_results(results)

if __name__ == "__main__":
    main()
