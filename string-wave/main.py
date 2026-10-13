"""1D wave equation on a string solved with the MidPoint method."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


# Physical and numerical parameters
RHO = 1.0
T = 1.0
L = np.pi
N = 100
DT = 0.005
N_STEPS = 4000
C = np.sqrt(T / RHO)
DX = L / N


# Acceleration from the discretized wave equation
def acceleration(u):
    a = np.zeros_like(u)
    a[1:-1] = C ** 2 * (u[2:] - 2 * u[1:-1] + u[:-2]) / DX ** 2
    return a


# Single MidPoint integration step for du/dt = v, dv/dt = a(u)
def midpoint_step(u, v, dt):
    a1 = acceleration(u)
    u_mid = u + v * (dt / 2.0)
    v_mid = v + a1 * (dt / 2.0)
    a2 = acceleration(u_mid)
    u_new = u + v_mid * dt
    v_new = v + a2 * dt
    u_new[0] = 0.0
    u_new[-1] = 0.0
    v_new[0] = 0.0
    v_new[-1] = 0.0
    return u_new, v_new


# Discrete kinetic energy
def kinetic_energy(v):
    return RHO * DX / 2.0 * np.sum(v[1:-1] ** 2)


# Discrete potential energy
def potential_energy(u):
    du = np.diff(u)
    return T / (2.0 * DX) * np.sum(du ** 2)


# CFL stability check
def check_stability(dt):
    cfl = C * dt / DX
    return cfl, cfl <= 1.0


# Run the full simulation and collect history
def run_simulation():
    x = np.linspace(0.0, L, N + 1)
    u = np.sin(x)
    v = np.zeros_like(u)
    u[0] = u[-1] = 0.0

    times = np.zeros(N_STEPS + 1)
    Ek_hist = np.zeros(N_STEPS + 1)
    Ep_hist = np.zeros(N_STEPS + 1)
    Et_hist = np.zeros(N_STEPS + 1)
    u_hist = np.zeros((N_STEPS + 1, N + 1))

    Ek_hist[0] = kinetic_energy(v)
    Ep_hist[0] = potential_energy(u)
    Et_hist[0] = Ek_hist[0] + Ep_hist[0]
    u_hist[0] = u

    for n in range(1, N_STEPS + 1):
        u, v = midpoint_step(u, v, DT)
        times[n] = n * DT
        Ek_hist[n] = kinetic_energy(v)
        Ep_hist[n] = potential_energy(u)
        Et_hist[n] = Ek_hist[n] + Ep_hist[n]
        u_hist[n] = u

    return x, times, u_hist, Ek_hist, Ep_hist, Et_hist


# Energy plot with relative drift on a secondary axis
def plot_energies(times, Ek, Ep, Et, path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7),
                                   gridspec_kw={"height_ratios": [3, 1]})

    ax1.plot(times, Ek, label="Kinetic $E_k$", color="#1f77b4", linewidth=1.5)
    ax1.plot(times, Ep, label="Potential $E_p$", color="#ff7f0e", linewidth=1.5)
    ax1.plot(times, Et, label="Total $E_t$", color="#2ca02c", linewidth=2.5)
    ax1.set_xlabel("Time t")
    ax1.set_ylabel("Energy")
    ax1.set_title("String energies (MidPoint method)")
    ax1.legend(loc="center right")
    ax1.grid(True, alpha=0.3)
    ax1.margins(x=0)

    drift = (Et - Et[0]) / Et[0]
    ax2.plot(times, drift, color="#d62728", linewidth=1.2)
    ax2.axhline(0, color="black", linewidth=0.5, linestyle="--")
    ax2.set_xlabel("Time t")
    ax2.set_ylabel("Relative drift")
    ax2.set_title("Total energy drift  $(E_t - E_t^0) / E_t^0$")
    ax2.grid(True, alpha=0.3)
    ax2.margins(x=0)
    ax2.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


# String snapshots arranged in a clean grid (no overlap)
def plot_snapshots_grid(x, times, u_hist, path):
    n_snap = 6
    indices = np.linspace(0, len(times) - 1, n_snap).astype(int)

    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
    y_max = np.max(np.abs(u_hist)) * 1.1

    for ax, idx in zip(axes.flat, indices):
        ax.plot(x, u_hist[idx], color="#1f77b4", linewidth=1.8)
        ax.fill_between(x, u_hist[idx], alpha=0.15, color="#1f77b4")
        ax.axhline(0, color="black", linewidth=0.5, linestyle="--", alpha=0.6)
        ax.set_title(f"t = {times[idx]:.2f}")
        ax.set_ylim(-y_max, y_max)
        ax.grid(True, alpha=0.3)

    for ax in axes[-1, :]:
        ax.set_xlabel("x")
    for ax in axes[:, 0]:
        ax.set_ylabel("u(x, t)")

    fig.suptitle("String displacement snapshots", fontsize=13, y=1.0)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


# Combined snapshot lines on one axis with viridis colors
def plot_snapshots_overlay(x, times, u_hist, path):
    n_snap = 5
    indices = np.linspace(0, len(times) - 1, n_snap).astype(int)
    cmap = plt.cm.viridis(np.linspace(0, 0.9, n_snap))

    plt.figure(figsize=(11, 6))
    for color, idx in zip(cmap, indices):
        plt.plot(x, u_hist[idx], color=color, linewidth=2,
                 label=f"t = {times[idx]:.2f}")
    plt.axhline(0, color="black", linewidth=0.5, linestyle="--", alpha=0.6)
    plt.xlabel("x")
    plt.ylabel("u(x, t)")
    plt.title("String displacement at selected times")
    plt.legend(loc="upper right", framealpha=0.9)
    plt.grid(True, alpha=0.3)
    plt.margins(x=0)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


# Space-time heatmap
def plot_heatmap(x, times, u_hist, path):
    plt.figure(figsize=(11, 6))
    extent = [x[0], x[-1], times[-1], times[0]]
    im = plt.imshow(u_hist, aspect="auto", extent=extent, cmap="RdBu_r")
    plt.colorbar(im, label="u(x, t)")
    plt.xlabel("x")
    plt.ylabel("t")
    plt.title("Space-time evolution of u(x, t)")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


# Numerical summary table rendered as a figure
def plot_summary_table(times, Ek, Ep, Et, cfl, path):
    sample_idx = np.linspace(0, len(times) - 1, 11).astype(int)
    rows = []
    for idx in sample_idx:
        rows.append([
            f"{times[idx]:.3f}",
            f"{Ek[idx]:.6f}",
            f"{Ep[idx]:.6f}",
            f"{Et[idx]:.6f}",
            f"{(Et[idx] - Et[0]) / Et[0]:+.3e}",
        ])

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.axis("off")

    title = (f"Simulation summary  |  rho={RHO}, T={T}, c={C:.3f}, "
             f"L=pi, N={N}, dx={DX:.4f}, dt={DT}, CFL={cfl:.4f}")
    ax.set_title(title, fontsize=11, pad=18)

    col_labels = ["t", "E_k", "E_p", "E_t", "Relative drift"]
    table = ax.table(cellText=rows, colLabels=col_labels,
                     loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.6)

    for j in range(len(col_labels)):
        cell = table[(0, j)]
        cell.set_facecolor("#34495e")
        cell.set_text_props(color="white", fontweight="bold")

    for i in range(1, len(rows) + 1):
        for j in range(len(col_labels)):
            cell = table[(i, j)]
            cell.set_facecolor("#f7f9fc" if i % 2 == 0 else "#ffffff")

    plt.tight_layout()
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()


# Combined dashboard: parameters, energies, displacement, drift in one figure
def plot_dashboard(x, times, u_hist, Ek, Ep, Et, cfl, path):
    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(3, 2, figure=fig, hspace=0.55, wspace=0.25,
                  height_ratios=[1, 1.2, 1])

    # Parameters panel
    ax_par = fig.add_subplot(gs[0, 0])
    ax_par.axis("off")
    params = [
        ["rho", f"{RHO}"],
        ["T", f"{T}"],
        ["c", f"{C:.4f}"],
        ["L", "pi"],
        ["N", f"{N}"],
        ["dx", f"{DX:.4f}"],
        ["dt", f"{DT}"],
        ["steps", f"{N_STEPS}"],
        ["CFL", f"{cfl:.4f}"],
        ["stable", "yes" if cfl <= 1 else "no"],
    ]
    tbl = ax_par.table(cellText=params, colLabels=["Parameter", "Value"],
                       loc="center", cellLoc="center", bbox=[0.0, 0.0, 1.0, 0.88])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    for j in range(2):
        tbl[(0, j)].set_facecolor("#34495e")
        tbl[(0, j)].set_text_props(color="white", fontweight="bold")
    ax_par.text(0.5, 0.97, "Simulation parameters", ha="center", va="top",
                fontsize=12, fontweight="bold", transform=ax_par.transAxes)

    # Energy summary panel
    ax_es = fig.add_subplot(gs[0, 1])
    ax_es.axis("off")
    e_summary = [
        ["E_t initial", f"{Et[0]:.6e}"],
        ["E_t final", f"{Et[-1]:.6e}"],
        ["max E_k", f"{Ek.max():.6e}"],
        ["max E_p", f"{Ep.max():.6e}"],
        ["abs drift", f"{(Et[-1] - Et[0]):+.3e}"],
        ["rel drift", f"{(Et[-1] - Et[0]) / Et[0]:+.3e}"],
    ]
    tbl2 = ax_es.table(cellText=e_summary, colLabels=["Quantity", "Value"],
                       loc="center", cellLoc="center", bbox=[0.0, 0.0, 1.0, 0.88])
    tbl2.auto_set_font_size(False)
    tbl2.set_fontsize(10)
    for j in range(2):
        tbl2[(0, j)].set_facecolor("#34495e")
        tbl2[(0, j)].set_text_props(color="white", fontweight="bold")
    ax_es.text(0.5, 0.97, "Energy summary", ha="center", va="top",
               fontsize=12, fontweight="bold", transform=ax_es.transAxes)

    # Energy time series
    ax_e = fig.add_subplot(gs[1, :])
    ax_e.plot(times, Ek, label="$E_k$", color="#1f77b4", linewidth=1.4)
    ax_e.plot(times, Ep, label="$E_p$", color="#ff7f0e", linewidth=1.4)
    ax_e.plot(times, Et, label="$E_t$", color="#2ca02c", linewidth=2.2)
    ax_e.set_xlabel("Time t")
    ax_e.set_ylabel("Energy")
    ax_e.set_title("Energies over time")
    ax_e.legend(loc="center right")
    ax_e.grid(True, alpha=0.3)
    ax_e.margins(x=0)

    # String snapshots
    ax_s = fig.add_subplot(gs[2, 0])
    n_snap = 5
    indices = np.linspace(0, len(times) - 1, n_snap).astype(int)
    cmap = plt.cm.viridis(np.linspace(0, 0.9, n_snap))
    for color, idx in zip(cmap, indices):
        ax_s.plot(x, u_hist[idx], color=color, linewidth=1.6,
                  label=f"t = {times[idx]:.2f}")
    ax_s.axhline(0, color="black", linewidth=0.5, linestyle="--", alpha=0.5)
    ax_s.set_xlabel("x")
    ax_s.set_ylabel("u(x, t)")
    ax_s.set_title("String shape at selected times")
    ax_s.legend(loc="upper right", fontsize=8, framealpha=0.9)
    ax_s.grid(True, alpha=0.3)
    ax_s.set_xlim(0, L)

    # Drift
    ax_d = fig.add_subplot(gs[2, 1])
    drift = (Et - Et[0]) / Et[0]
    ax_d.plot(times, drift, color="#d62728", linewidth=1.2)
    ax_d.axhline(0, color="black", linewidth=0.5, linestyle="--")
    ax_d.set_xlabel("Time t")
    ax_d.set_ylabel("Relative drift")
    ax_d.set_title("Total energy relative drift")
    ax_d.grid(True, alpha=0.3)
    ax_d.margins(x=0)
    ax_d.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

    fig.suptitle("Wave equation on a string  -  MidPoint method dashboard",
                 fontsize=14, y=0.995)
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()


def main():
    cfl, ok = check_stability(DT)
    print(f"CFL = c*dt/dx = {cfl:.4f}, stable: {ok}")

    x, times, u_hist, Ek, Ep, Et = run_simulation()

    print(f"E_total at t=0    : {Et[0]:.6e}")
    print(f"E_total at t=t_end: {Et[-1]:.6e}")
    print(f"Relative drift    : {(Et[-1] - Et[0]) / Et[0]:.3e}")

    plot_energies(times, Ek, Ep, Et, "energies.png")
    plot_snapshots_grid(x, times, u_hist, "snapshots_grid.png")
    plot_snapshots_overlay(x, times, u_hist, "snapshots_overlay.png")
    plot_heatmap(x, times, u_hist, "heatmap.png")
    plot_summary_table(times, Ek, Ep, Et, cfl, "summary_table.png")
    plot_dashboard(x, times, u_hist, Ek, Ep, Et, cfl, "dashboard.png")

    print("\nGenerated files:")
    for f in ["energies.png", "snapshots_grid.png", "snapshots_overlay.png",
              "heatmap.png", "summary_table.png", "dashboard.png"]:
        print(f"  - {f}")


if __name__ == "__main__":
    main()