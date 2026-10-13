import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# --- Parameters ---
A, B, C = 10, 25, 8/3
dt = 0.03
N = 3000
x0, y0, z0 = 1.0, 1.0, 1.0

def deriv(x, y, z):
    dx = A * y - A * x
    dy = -x * z + B * x - y
    dz = x * y - C * z
    return dx, dy, dz

# --- Euler Method ---
def euler(N, dt):
    x, y, z = x0, y0, z0
    xs, zs = [x], [z]
    for _ in range(N):
        dx, dy, dz = deriv(x, y, z)
        x += dt * dx
        y += dt * dy
        z += dt * dz
        xs.append(x); zs.append(z)
    return np.array(xs), np.array(zs)

# --- Midpoint Method ---
def midpoint(N, dt):
    x, y, z = x0, y0, z0
    xs, zs = [x], [z]
    for _ in range(N):
        dx1, dy1, dz1 = deriv(x, y, z)
        xm = x + 0.5*dt*dx1
        ym = y + 0.5*dt*dy1
        zm = z + 0.5*dt*dz1
        dx2, dy2, dz2 = deriv(xm, ym, zm)
        x += dt * dx2
        y += dt * dy2
        z += dt * dz2
        xs.append(x); zs.append(z)
    return np.array(xs), np.array(zs)

# --- RK4 Method ---
def rk4(N, dt):
    x, y, z = x0, y0, z0
    xs, zs = [x], [z]
    for _ in range(N):
        k1 = deriv(x, y, z)
        k2 = deriv(x+0.5*dt*k1[0], y+0.5*dt*k1[1], z+0.5*dt*k1[2])
        k3 = deriv(x+0.5*dt*k2[0], y+0.5*dt*k2[1], z+0.5*dt*k2[2])
        k4 = deriv(x+dt*k3[0],     y+dt*k3[1],     z+dt*k3[2])
        x += dt*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6
        y += dt*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6
        z += dt*(k1[2]+2*k2[2]+2*k3[2]+k4[2])/6
        xs.append(x); zs.append(z)
    return np.array(xs), np.array(zs)

# --- Solve ---
ex, ez = euler(N, dt)
mx, mz = midpoint(N, dt)
rx, rz = rk4(N, dt)

# --- Plot ---
fig = plt.figure(figsize=(14, 10), facecolor="#0f0f13")
gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.38, wspace=0.32)

ax_main = fig.add_subplot(gs[0, :])   # Full top row → combined plot
ax_e    = fig.add_subplot(gs[1, 0])
ax_m    = fig.add_subplot(gs[1, 1])
ax_r    = fig.add_subplot(gs[1, 2])

COLORS  = {"euler": "#E24B4A", "mid": "#1D9E75", "rk4": "#378ADD"}
BG      = "#0f0f13"
PANEL   = "#1a1a22"
TEXT    = "#c8c8d4"
GRID    = "#2a2a36"

def style_ax(ax, title):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=TEXT, labelsize=8)
    for sp in ax.spines.values():
        sp.set_color(GRID)
    ax.set_xlabel("x", color=TEXT, fontsize=9)
    ax.set_ylabel("z", color=TEXT, fontsize=9)
    ax.set_title(title, color=TEXT, fontsize=10, pad=6)
    ax.grid(True, color=GRID, linewidth=0.5, alpha=0.7)

# Ana grafik
ax_main.set_facecolor(PANEL)
alpha = 0.65
ax_main.plot(ex, ez, color=COLORS["euler"], lw=0.7, alpha=alpha, label="Euler",    linestyle="--")
ax_main.plot(mx, mz, color=COLORS["mid"],   lw=0.7, alpha=alpha, label="Midpoint", linestyle="-.")
ax_main.plot(rx, rz, color=COLORS["rk4"],   lw=1.0, alpha=0.9,   label="RK4")
ax_main.set_xlabel("x", color=TEXT, fontsize=10)
ax_main.set_ylabel("z", color=TEXT, fontsize=10)
ax_main.set_title(f"Lorenz Attractor — z(x) Phase Portrait   |   A={A}, B={B}, C={C:.4f}, dt={dt}, N={N}",
                  color=TEXT, fontsize=11, pad=8)
ax_main.tick_params(colors=TEXT, labelsize=9)
for sp in ax_main.spines.values(): sp.set_color(GRID)
ax_main.grid(True, color=GRID, linewidth=0.5, alpha=0.7)
legend = ax_main.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TEXT, fontsize=9)

# Individual subplots
for ax, xs, zs, c, ttl in [
    (ax_e, ex, ez, COLORS["euler"], "Euler"),
    (ax_m, mx, mz, COLORS["mid"],   "Midpoint"),
    (ax_r, rx, rz, COLORS["rk4"],   "RK4"),
]:
    style_ax(ax, ttl)
    ax.plot(xs, zs, color=c, lw=0.6, alpha=0.85)

# Mark starting point
for ax, xs, zs, c in [
    (ax_e, ex, ez, COLORS["euler"]),
    (ax_m, mx, mz, COLORS["mid"]),
    (ax_r, rx, rz, COLORS["rk4"]),
]:
    ax.scatter([xs[0]], [zs[0]], color="white", s=18, zorder=5)

plt.suptitle("Lorenz System — Numerical Method Comparison",
             color="white", fontsize=13, fontweight="bold", y=0.98)

plt.savefig("lorenz_plot.png", dpi=150,
            bbox_inches="tight", facecolor=fig.get_facecolor())
print("Plot saved as 'lorenz_plot.png'.")
plt.show()
